"""
学生 API 集成测试

测试学生管理 API 的完整功能，包括：
- 创建学生
- 查询学生列表
- 查询单个学生
- 更新学生
- 删除学生
- 搜索学生
"""

from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db
from src.core.security import hash_password
from src.core.exceptions import AppException
from src.api.exception_handlers import (
    app_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from src.models import Student, Grade
from src.models.user import User


@pytest.fixture(scope="function")
def test_engine():
    """创建测试数据库引擎

    使用 StaticPool 确保 in-memory SQLite 的所有连接共享同一个数据库实例，
    否则每个新连接会创建一个全新的空数据库（经典 SQLite 内存测试坑）。
    """
    engine = create_engine(
        "sqlite://",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # 启用 SQLite 外键约束
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # 创建所有表（确保模型已注册）
    import src.models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    yield engine

    # 清理
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """创建测试数据库会话"""
    TestSessionLocal = sessionmaker(bind=test_engine)
    session = TestSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(autouse=True)
def seed_users(db_session):
    """创建测试用户数据

    每个测试前自动创建三个默认用户：admin、teacher、student。
    """
    users = [
        User(
            username="admin",
            hashed_password=hash_password("admin123"),
            role="admin",
            is_active=True,
        ),
        User(
            username="teacher",
            hashed_password=hash_password("teacher123"),
            role="teacher",
            is_active=True,
        ),
        User(
            username="student",
            hashed_password=hash_password("student123"),
            role="student",
            is_active=True,
        ),
    ]
    db_session.add_all(users)
    db_session.commit()


@pytest.fixture(scope="function")
def client(test_engine):
    """创建测试客户端"""
    # 创建测试数据库会话工厂
    TestSessionLocal = sessionmaker(bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # 创建不带 lifespan 的测试专用 FastAPI app
    @asynccontextmanager
    async def _noop_lifespan(app):
        yield

    test_app = FastAPI(title="Test App", lifespan=_noop_lifespan)

    # 注册异常处理器
    test_app.add_exception_handler(AppException, app_exception_handler)
    test_app.add_exception_handler(RequestValidationError, validation_exception_handler)
    test_app.add_exception_handler(Exception, general_exception_handler)

    # 注册路由（包含认证路由，用于登录获取 Token）
    from src.api.routes.auth import router as auth_router
    from src.api.routes.students import router as students_router
    test_app.include_router(auth_router)
    test_app.include_router(students_router)

    # 覆盖数据库依赖
    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as c:
        yield c

    # 清理
    test_app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """获取管理员认证请求头

    通过登录接口获取 Access Token，返回 Authorization 请求头。
    """
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_student():
    """示例学生数据"""
    return {
        "student_id": "20260001",
        "name": "张三",
        "gender": "男",
        "class_name": "2026级1班",
        "enrollment_year": 2026,
    }


@pytest.fixture
def sample_students():
    """多个示例学生数据"""
    return [
        {
            "student_id": "20260001",
            "name": "张三",
            "gender": "男",
            "class_name": "2026级1班",
            "enrollment_year": 2026,
        },
        {
            "student_id": "20260002",
            "name": "李四",
            "gender": "女",
            "class_name": "2026级1班",
            "enrollment_year": 2026,
        },
        {
            "student_id": "20260003",
            "name": "王五",
            "gender": "男",
            "class_name": "2026级2班",
            "enrollment_year": 2026,
        },
    ]


class TestStudentAPI:
    """学生 API 测试类"""

    def test_create_student(self, client, auth_headers, sample_student):
        """测试创建学生"""
        response = client.post("/api/v1/students", json=sample_student, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["student_id"] == "20260001"
        assert data["data"]["name"] == "张三"

    def test_create_student_duplicate(self, client, auth_headers, sample_student):
        """测试创建重复学号的学生"""
        # 先创建一个学生
        client.post("/api/v1/students", json=sample_student, headers=auth_headers)

        # 尝试创建相同学号的学生
        response = client.post("/api/v1/students", json=sample_student, headers=auth_headers)

        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "DUPLICATE"

    def test_create_student_invalid_data(self, client, auth_headers):
        """测试创建学生时数据无效"""
        invalid_data = {
            "student_id": "invalid",
            "name": "张三",
            "gender": "男",
            "class_name": "2026级1班",
            "enrollment_year": 2026,
        }

        response = client.post("/api/v1/students", json=invalid_data, headers=auth_headers)

        assert response.status_code == 422

    def test_get_student_list(self, client, auth_headers, sample_students):
        """测试获取学生列表"""
        # 先创建多个学生
        for student in sample_students:
            client.post("/api/v1/students", json=student, headers=auth_headers)

        # 获取列表
        response = client.get("/api/v1/students", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 3
        assert len(data["data"]["items"]) == 3

    def test_get_student_list_with_pagination(self, client, auth_headers, sample_students):
        """测试学生列表分页"""
        # 先创建多个学生
        for student in sample_students:
            client.post("/api/v1/students", json=student, headers=auth_headers)

        # 获取第一页
        response = client.get("/api/v1/students?page=1&page_size=2", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 3
        assert len(data["data"]["items"]) == 2
        assert data["data"]["page"] == 1
        assert data["data"]["page_size"] == 2
        assert data["data"]["total_pages"] == 2

    def test_get_student_list_with_class_filter(self, client, auth_headers, sample_students):
        """测试按班级筛选学生列表"""
        # 先创建多个学生
        for student in sample_students:
            client.post("/api/v1/students", json=student, headers=auth_headers)

        # 按班级筛选
        response = client.get("/api/v1/students?class_name=2026级1班", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 2

    def test_get_student(self, client, auth_headers, sample_student):
        """测试查询单个学生"""
        # 先创建学生
        client.post("/api/v1/students", json=sample_student, headers=auth_headers)

        # 查询学生
        response = client.get("/api/v1/students/20260001", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["student_id"] == "20260001"
        assert data["data"]["name"] == "张三"

    def test_get_student_not_found(self, client, auth_headers):
        """测试查询不存在的学生"""
        response = client.get("/api/v1/students/99999999", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "NOT_FOUND"

    def test_update_student(self, client, auth_headers, sample_student):
        """测试更新学生信息"""
        # 先创建学生
        client.post("/api/v1/students", json=sample_student, headers=auth_headers)

        # 更新学生信息
        update_data = {"name": "张三丰"}
        response = client.put("/api/v1/students/20260001", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "张三丰"

    def test_update_student_not_found(self, client, auth_headers):
        """测试更新不存在的学生"""
        update_data = {"name": "张三丰"}
        response = client.put("/api/v1/students/99999999", json=update_data, headers=auth_headers)

        assert response.status_code == 404

    def test_delete_student(self, client, auth_headers, sample_student):
        """测试删除学生"""
        # 先创建学生
        client.post("/api/v1/students", json=sample_student, headers=auth_headers)

        # 删除学生
        response = client.delete("/api/v1/students/20260001", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # 验证学生已被删除
        response = client.get("/api/v1/students/20260001", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_student_not_found(self, client, auth_headers):
        """测试删除不存在的学生"""
        response = client.delete("/api/v1/students/99999999", headers=auth_headers)

        assert response.status_code == 404

    def test_search_students(self, client, auth_headers, sample_students):
        """测试搜索学生"""
        # 先创建多个学生
        for student in sample_students:
            client.post("/api/v1/students", json=student, headers=auth_headers)

        # 搜索
        response = client.get("/api/v1/students/search?keyword=张", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["items"]) == 1
        assert data["data"]["items"][0]["name"] == "张三"

    def test_search_students_by_student_id(self, client, auth_headers, sample_students):
        """测试按学号搜索学生"""
        # 先创建多个学生
        for student in sample_students:
            client.post("/api/v1/students", json=student, headers=auth_headers)

        # 搜索
        response = client.get("/api/v1/students/search?keyword=20260001", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) == 1
        assert data["data"]["items"][0]["student_id"] == "20260001"

    def test_search_students_with_class_filter(self, client, auth_headers, sample_students):
        """测试搜索学生时按班级筛选"""
        # 先创建多个学生
        for student in sample_students:
            client.post("/api/v1/students", json=student, headers=auth_headers)

        # 搜索并按班级筛选
        response = client.get(
            "/api/v1/students/search?keyword=2026&class_name=2026级1班",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) == 2

    def test_search_students_no_results(self, client, auth_headers, sample_students):
        """测试搜索学生无结果"""
        # 先创建多个学生
        for student in sample_students:
            client.post("/api/v1/students", json=student, headers=auth_headers)

        # 搜索不存在的关键词
        response = client.get("/api/v1/students/search?keyword=赵六", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) == 0

    def test_search_students_with_pagination(self, client, auth_headers, sample_students):
        """测试搜索学生分页"""
        # 先创建多个学生
        for student in sample_students:
            client.post("/api/v1/students", json=student, headers=auth_headers)

        # 搜索并分页
        response = client.get(
            "/api/v1/students/search?keyword=2026&page=1&page_size=2",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 3
        assert len(data["data"]["items"]) == 2
        assert data["data"]["page"] == 1
        assert data["data"]["page_size"] == 2
        assert data["data"]["total_pages"] == 2
