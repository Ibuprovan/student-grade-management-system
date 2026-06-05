"""
成绩 API 集成测试

测试成绩管理 API 的完整功能，包括：
- 录入单条成绩
- 批量录入成绩
- 查询单条成绩
- 修改成绩
- 删除成绩
- 按学生查询成绩
- 按班级查询成绩
- 按科目查询成绩
- 组合条件查询成绩
"""

from contextlib import asynccontextmanager
from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db
from src.core.exceptions import AppException
from src.api.exception_handlers import (
    app_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from src.models import Student, Grade


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

    # 注册路由
    from src.api.routes.students import router as students_router
    from src.api.routes.grades import router as grades_router
    test_app.include_router(students_router)
    test_app.include_router(grades_router)

    # 覆盖数据库依赖
    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as c:
        yield c

    # 清理
    test_app.dependency_overrides.clear()


@pytest.fixture
def sample_student():
    """示例学生数据"""
    return {
        "student_id": "20260001",
        "name": "张三",
        "gender": "男",
        "class_name": "三年一班",
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
            "class_name": "三年一班",
            "enrollment_year": 2026,
        },
        {
            "student_id": "20260002",
            "name": "李四",
            "gender": "女",
            "class_name": "三年一班",
            "enrollment_year": 2026,
        },
        {
            "student_id": "20260003",
            "name": "王五",
            "gender": "男",
            "class_name": "三年二班",
            "enrollment_year": 2026,
        },
    ]


@pytest.fixture
def sample_grade():
    """示例成绩数据"""
    return {
        "student_id": "20260001",
        "subject": "数学",
        "score": 95.5,
        "exam_type": "期中",
        "exam_date": "2026-04-15",
    }


@pytest.fixture
def sample_grades():
    """多个示例成绩数据"""
    return [
        {
            "student_id": "20260001",
            "subject": "数学",
            "score": 95.5,
            "exam_type": "期中",
            "exam_date": "2026-04-15",
        },
        {
            "student_id": "20260001",
            "subject": "语文",
            "score": 88.0,
            "exam_type": "期中",
            "exam_date": "2026-04-15",
        },
        {
            "student_id": "20260002",
            "subject": "数学",
            "score": 72.5,
            "exam_type": "期中",
            "exam_date": "2026-04-15",
        },
    ]


class TestGradeAPI:
    """成绩 API 测试类"""

    def _create_student(self, client, student_data):
        """辅助方法：创建学生"""
        return client.post("/api/v1/students", json=student_data)

    # ==================== 单条成绩录入测试 ====================

    def test_create_grade(self, client, sample_student, sample_grade):
        """测试录入单条成绩"""
        # 先创建学生
        self._create_student(client, sample_student)

        # 录入成绩
        response = client.post("/api/v1/grades", json=sample_grade)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["student_id"] == "20260001"
        assert data["data"]["subject"] == "数学"
        assert data["data"]["score"] == 95.5
        assert data["message"] == "成绩录入成功"

    def test_create_grade_student_not_found(self, client, sample_grade):
        """测试录入成绩时学生不存在"""
        response = client.post("/api/v1/grades", json=sample_grade)

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "NOT_FOUND"

    def test_create_grade_duplicate(self, client, sample_student, sample_grade):
        """测试录入重复成绩"""
        # 先创建学生
        self._create_student(client, sample_student)

        # 第一次录入成绩
        client.post("/api/v1/grades", json=sample_grade)

        # 尝试重复录入
        response = client.post("/api/v1/grades", json=sample_grade)

        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "DUPLICATE"

    def test_create_grade_invalid_subject(self, client, sample_student):
        """测试录入成绩时科目无效"""
        self._create_student(client, sample_student)

        invalid_data = {
            "student_id": "20260001",
            "subject": "无效科目",
            "score": 95.5,
            "exam_type": "期中",
            "exam_date": "2026-04-15",
        }

        response = client.post("/api/v1/grades", json=invalid_data)

        assert response.status_code == 422

    def test_create_grade_invalid_exam_type(self, client, sample_student):
        """测试录入成绩时考试类型无效"""
        self._create_student(client, sample_student)

        invalid_data = {
            "student_id": "20260001",
            "subject": "数学",
            "score": 95.5,
            "exam_type": "无效类型",
            "exam_date": "2026-04-15",
        }

        response = client.post("/api/v1/grades", json=invalid_data)

        assert response.status_code == 422

    # ==================== 批量录入成绩测试 ====================

    def test_batch_create_grades(self, client, sample_students):
        """测试批量录入成绩"""
        # 创建学生
        for student in sample_students:
            self._create_student(client, student)

        # 批量录入成绩
        batch_data = {
            "subject": "数学",
            "exam_type": "期中",
            "exam_date": "2026-04-15",
            "grades": [
                {"student_id": "20260001", "score": 95.5},
                {"student_id": "20260002", "score": 88.0},
                {"student_id": "20260003", "score": 72.5},
            ],
        }

        response = client.post("/api/v1/grades/batch", json=batch_data)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 3
        assert data["data"]["success_count"] == 3
        assert data["data"]["fail_count"] == 0

    def test_batch_create_grades_partial_failure(self, client, sample_students):
        """测试批量录入成绩部分失败"""
        # 只创建部分学生
        self._create_student(client, sample_students[0])
        self._create_student(client, sample_students[1])

        batch_data = {
            "subject": "数学",
            "exam_type": "期中",
            "exam_date": "2026-04-15",
            "grades": [
                {"student_id": "20260001", "score": 95.5},
                {"student_id": "20260002", "score": 88.0},
                {"student_id": "20260003", "score": 72.5},  # 不存在的学生
            ],
        }

        response = client.post("/api/v1/grades/batch", json=batch_data)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 3
        assert data["data"]["success_count"] == 2
        assert data["data"]["fail_count"] == 1

    # ==================== 查询单条成绩测试 ====================

    def test_get_grade(self, client, sample_student, sample_grade):
        """测试查询单条成绩"""
        self._create_student(client, sample_student)

        # 先录入成绩
        create_response = client.post("/api/v1/grades", json=sample_grade)
        grade_id = create_response.json()["data"]["grade_id"]

        # 查询成绩
        response = client.get(f"/api/v1/grades/{grade_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["grade_id"] == grade_id
        assert data["data"]["student_id"] == "20260001"
        assert data["data"]["subject"] == "数学"

    def test_get_grade_not_found(self, client):
        """测试查询不存在的成绩"""
        response = client.get("/api/v1/grades/99999")

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "NOT_FOUND"

    # ==================== 修改成绩测试 ====================

    def test_update_grade(self, client, sample_student, sample_grade):
        """测试修改成绩"""
        self._create_student(client, sample_student)

        # 先录入成绩
        create_response = client.post("/api/v1/grades", json=sample_grade)
        grade_id = create_response.json()["data"]["grade_id"]

        # 修改成绩
        update_data = {"score": 98.0}
        response = client.put(f"/api/v1/grades/{grade_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["score"] == 98.0
        assert data["message"] == "成绩更新成功"

    def test_update_grade_not_found(self, client):
        """测试修改不存在的成绩"""
        update_data = {"score": 98.0}
        response = client.put("/api/v1/grades/99999", json=update_data)

        assert response.status_code == 404

    # ==================== 删除成绩测试 ====================

    def test_delete_grade(self, client, sample_student, sample_grade):
        """测试删除成绩"""
        self._create_student(client, sample_student)

        # 先录入成绩
        create_response = client.post("/api/v1/grades", json=sample_grade)
        grade_id = create_response.json()["data"]["grade_id"]

        # 删除成绩
        response = client.delete(f"/api/v1/grades/{grade_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "成绩记录删除成功"

        # 验证成绩已被删除
        response = client.get(f"/api/v1/grades/{grade_id}")
        assert response.status_code == 404

    def test_delete_grade_not_found(self, client):
        """测试删除不存在的成绩"""
        response = client.delete("/api/v1/grades/99999")

        assert response.status_code == 404

    # ==================== 按学生查询成绩测试 ====================

    def test_get_grades_by_student(self, client, sample_student, sample_grades):
        """测试按学生查询成绩"""
        self._create_student(client, sample_student)

        # 录入该学生的成绩
        for grade in sample_grades:
            if grade["student_id"] == "20260001":
                client.post("/api/v1/grades", json=grade)

        # 按学生查询
        response = client.get("/api/v1/grades/student/20260001")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2  # 数学和语文

    def test_get_grades_by_student_empty(self, client, sample_student):
        """测试按学生查询成绩（无成绩记录）"""
        self._create_student(client, sample_student)

        response = client.get("/api/v1/grades/student/20260001")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 0

    # ==================== 按班级查询成绩测试 ====================

    def test_get_grades_by_class(self, client, sample_students, sample_grades):
        """测试按班级查询成绩"""
        # 创建学生
        for student in sample_students:
            self._create_student(client, student)

        # 录入成绩
        for grade in sample_grades:
            client.post("/api/v1/grades", json=grade)

        # 按班级查询
        response = client.get("/api/v1/grades/class/三年一班")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # 三年一班有 3 条成绩：20260001-数学, 20260001-语文, 20260002-数学
        assert data["data"]["total"] == 3

    def test_get_grades_by_class_with_subject_filter(
        self, client, sample_students, sample_grades
    ):
        """测试按班级和科目筛选查询成绩"""
        # 创建学生
        for student in sample_students:
            self._create_student(client, student)

        # 录入成绩
        for grade in sample_grades:
            client.post("/api/v1/grades", json=grade)

        # 按班级和科目查询
        response = client.get("/api/v1/grades/class/三年一班?subject=数学")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 2

    # ==================== 按科目查询成绩测试 ====================

    def test_get_grades_by_subject(self, client, sample_students, sample_grades):
        """测试按科目查询成绩"""
        # 创建学生
        for student in sample_students:
            self._create_student(client, student)

        # 录入成绩
        for grade in sample_grades:
            client.post("/api/v1/grades", json=grade)

        # 按科目查询
        response = client.get("/api/v1/grades/subject/数学")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 2  # 20260001-数学, 20260002-数学

    def test_get_grades_by_subject_with_exam_type_filter(
        self, client, sample_students, sample_grades
    ):
        """测试按科目和考试类型筛选查询成绩"""
        # 创建学生
        for student in sample_students:
            self._create_student(client, student)

        # 录入成绩
        for grade in sample_grades:
            client.post("/api/v1/grades", json=grade)

        # 按科目和考试类型查询
        response = client.get("/api/v1/grades/subject/数学?exam_type=期中")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 2

    # ==================== 组合条件查询成绩测试 ====================

    def test_search_grades(self, client, sample_students, sample_grades):
        """测试组合条件查询成绩"""
        # 创建学生
        for student in sample_students:
            self._create_student(client, student)

        # 录入成绩
        for grade in sample_grades:
            client.post("/api/v1/grades", json=grade)

        # 组合查询
        response = client.get("/api/v1/grades/search?class_name=三年一班&subject=数学")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 2

    def test_search_grades_with_pagination(
        self, client, sample_students, sample_grades
    ):
        """测试组合条件查询分页"""
        # 创建学生
        for student in sample_students:
            self._create_student(client, student)

        # 录入成绩
        for grade in sample_grades:
            client.post("/api/v1/grades", json=grade)

        # 第一页
        response = client.get(
            "/api/v1/grades/search?subject=数学&page=1&page_size=1"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 2
        assert len(data["data"]["items"]) == 1
        assert data["data"]["page"] == 1
        assert data["data"]["page_size"] == 1
        assert data["data"]["total_pages"] == 2

    def test_search_grades_no_filters(self, client, sample_students, sample_grades):
        """测试无筛选条件查询所有成绩"""
        # 创建学生
        for student in sample_students:
            self._create_student(client, student)

        # 录入成绩
        for grade in sample_grades:
            client.post("/api/v1/grades", json=grade)

        # 无筛选条件查询
        response = client.get("/api/v1/grades/search")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 3

    def test_search_grades_no_results(self, client, sample_students, sample_grades):
        """测试查询无结果"""
        # 创建学生
        for student in sample_students:
            self._create_student(client, student)

        # 录入成绩
        for grade in sample_grades:
            client.post("/api/v1/grades", json=grade)

        # 查询不存在的班级
        response = client.get("/api/v1/grades/search?class_name=三年三班")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 0
        assert len(data["data"]["items"]) == 0
