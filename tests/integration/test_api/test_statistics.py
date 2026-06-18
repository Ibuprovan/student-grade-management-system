"""
统计分析 API 集成测试

测试统计分析 API 的完整功能，包括：
- 平均分统计
- 最高分/最低分统计
- 及格率/优秀率统计
- 综合统计报告
- 单科排名
- 总分排名
- 通用统计查询
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
    """创建测试数据库引擎"""
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

    # 创建所有表
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
    TestSessionLocal = sessionmaker(bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

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
    from src.api.routes.grades import router as grades_router
    from src.api.routes.statistics import router as statistics_router
    test_app.include_router(auth_router)
    test_app.include_router(students_router)
    test_app.include_router(grades_router)
    test_app.include_router(statistics_router)

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
def sample_students():
    """多个示例学生数据"""
    return [
        {"student_id": "20260001", "name": "张三", "gender": "男", "class_name": "2026级1班", "enrollment_year": 2026},
        {"student_id": "20260002", "name": "李四", "gender": "女", "class_name": "2026级1班", "enrollment_year": 2026},
        {"student_id": "20260003", "name": "王五", "gender": "男", "class_name": "2026级1班", "enrollment_year": 2026},
        {"student_id": "20260004", "name": "赵六", "gender": "女", "class_name": "2026级2班", "enrollment_year": 2026},
        {"student_id": "20260005", "name": "钱七", "gender": "男", "class_name": "2026级2班", "enrollment_year": 2026},
    ]


@pytest.fixture
def sample_grades():
    """多个示例成绩数据"""
    return [
        {"student_id": "20260001", "subject": "数学", "score": 95.0, "exam_type": "期中", "exam_date": "2026-04-15"},
        {"student_id": "20260001", "subject": "语文", "score": 88.0, "exam_type": "期中", "exam_date": "2026-04-15"},
        {"student_id": "20260002", "subject": "数学", "score": 72.0, "exam_type": "期中", "exam_date": "2026-04-15"},
        {"student_id": "20260002", "subject": "语文", "score": 91.0, "exam_type": "期中", "exam_date": "2026-04-15"},
        {"student_id": "20260003", "subject": "数学", "score": 58.0, "exam_type": "期中", "exam_date": "2026-04-15"},
        {"student_id": "20260003", "subject": "语文", "score": 65.0, "exam_type": "期中", "exam_date": "2026-04-15"},
        {"student_id": "20260004", "subject": "数学", "score": 85.0, "exam_type": "期中", "exam_date": "2026-04-15"},
        {"student_id": "20260004", "subject": "语文", "score": 78.0, "exam_type": "期中", "exam_date": "2026-04-15"},
        {"student_id": "20260005", "subject": "数学", "score": 45.0, "exam_type": "期中", "exam_date": "2026-04-15"},
        {"student_id": "20260005", "subject": "语文", "score": 82.0, "exam_type": "期中", "exam_date": "2026-04-15"},
    ]


class TestStatisticsAPI:
    """统计分析 API 测试类"""

    def _create_student(self, client, student_data, headers):
        """辅助方法：创建学生"""
        return client.post("/api/v1/students", json=student_data, headers=headers)

    def _create_grade(self, client, grade_data, headers):
        """辅助方法：创建成绩"""
        return client.post("/api/v1/grades", json=grade_data, headers=headers)

    def _setup_test_data(self, client, students, grades, headers):
        """辅助方法：创建测试数据"""
        for student in students:
            self._create_student(client, student, headers)
        for grade in grades:
            self._create_grade(client, grade, headers)

    # ==================== 平均分统计测试 ====================

    def test_get_average(self, client, auth_headers, sample_students, sample_grades):
        """测试平均分统计"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get("/api/v1/statistics/average", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["count"] == 10
        assert data["data"]["average"] == 75.9

    def test_get_average_by_class(self, client, auth_headers, sample_students, sample_grades):
        """测试按班级统计平均分"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get("/api/v1/statistics/average?class_name=2026级1班", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["count"] == 6
        assert data["data"]["class_name"] == "2026级1班"

    def test_get_average_by_subject(self, client, auth_headers, sample_students, sample_grades):
        """测试按科目统计平均分"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get("/api/v1/statistics/average?subject=数学", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["count"] == 5

    def test_get_average_no_data(self, client, auth_headers):
        """测试无数据时平均分统计"""
        response = client.get("/api/v1/statistics/average", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["count"] == 0
        assert data["data"]["average"] == 0.0

    # ==================== 最高分统计测试 ====================

    def test_get_max_score(self, client, auth_headers, sample_students, sample_grades):
        """测试最高分统计"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get("/api/v1/statistics/max", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["max_score"] == 95.0
        assert data["data"]["student_id"] == "20260001"
        assert data["data"]["student_name"] == "张三"

    def test_get_max_score_by_class(self, client, auth_headers, sample_students, sample_grades):
        """测试按班级统计最高分"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get("/api/v1/statistics/max?class_name=2026级2班", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["max_score"] == 85.0
        assert data["data"]["student_id"] == "20260004"

    # ==================== 最低分统计测试 ====================

    def test_get_min_score(self, client, auth_headers, sample_students, sample_grades):
        """测试最低分统计"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get("/api/v1/statistics/min", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["min_score"] == 45.0
        assert data["data"]["student_id"] == "20260005"

    # ==================== 及格率统计测试 ====================

    def test_get_pass_rate(self, client, auth_headers, sample_students, sample_grades):
        """测试及格率统计"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get("/api/v1/statistics/pass-rate", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_count"] == 10
        assert data["data"]["passed_count"] == 8
        assert data["data"]["pass_rate"] == 80.0

    def test_get_pass_rate_by_class(self, client, auth_headers, sample_students, sample_grades):
        """测试按班级统计及格率"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get("/api/v1/statistics/pass-rate?class_name=2026级1班", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total_count"] == 6

    # ==================== 优秀率统计测试 ====================

    def test_get_excellent_rate(self, client, auth_headers, sample_students, sample_grades):
        """测试优秀率统计"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get("/api/v1/statistics/excellent-rate", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_count"] == 10
        assert data["data"]["excellent_count"] == 2
        assert data["data"]["excellent_rate"] == 20.0

    # ==================== 综合统计报告测试 ====================

    def test_get_report(self, client, auth_headers, sample_students, sample_grades):
        """测试综合统计报告"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get("/api/v1/statistics/report", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        stats = data["data"]["statistics"]
        assert stats["count"] == 10
        assert stats["average"] == 75.9
        assert stats["max_score"] == 95.0
        assert stats["min_score"] == 45.0
        assert stats["pass_rate"] == 80.0
        assert stats["excellent_rate"] == 20.0

        # 检查分数分布
        dist = stats["score_distribution"]
        assert dist["0-59"] == 2
        assert dist["90-100"] == 2

        # 检查优秀学生
        assert len(data["data"]["top_students"]) == 5

    def test_get_report_with_top_n(self, client, auth_headers, sample_students, sample_grades):
        """测试综合统计报告（指定优秀学生数量）"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get("/api/v1/statistics/report?top_n=3", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["top_students"]) == 3

    def test_get_report_by_class(self, client, auth_headers, sample_students, sample_grades):
        """测试班级综合统计报告"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get("/api/v1/statistics/report?class_name=2026级1班", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["class_name"] == "2026级1班"
        assert data["data"]["statistics"]["count"] == 6

    # ==================== 单科排名测试 ====================

    def test_get_subject_ranking(self, client, auth_headers, sample_students, sample_grades):
        """测试单科排名"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get("/api/v1/statistics/ranking/subject?subject=数学&exam_type=期中", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_count"] == 5
        assert len(data["data"]["rankings"]) == 5

        # 验证排序
        rankings = data["data"]["rankings"]
        assert rankings[0]["score"] == 95.0
        assert rankings[0]["student_id"] == "20260001"
        assert rankings[0]["rank"] == 1

    def test_get_subject_ranking_by_class(self, client, auth_headers, sample_students, sample_grades):
        """测试班级单科排名"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get(
            "/api/v1/statistics/ranking/subject?subject=数学&exam_type=期中&class_name=2026级1班",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total_count"] == 3
        assert data["data"]["class_name"] == "2026级1班"

    def test_get_subject_ranking_asc(self, client, auth_headers, sample_students, sample_grades):
        """测试单科排名（升序）"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get(
            "/api/v1/statistics/ranking/subject?subject=数学&exam_type=期中&order=asc",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        rankings = data["data"]["rankings"]
        assert rankings[0]["score"] == 45.0

    def test_get_subject_ranking_with_limit(self, client, auth_headers, sample_students, sample_grades):
        """测试单科排名限制数量"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get(
            "/api/v1/statistics/ranking/subject?subject=数学&exam_type=期中&limit=3",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["rankings"]) == 3

    # ==================== 总分排名测试 ====================

    def test_get_total_ranking(self, client, auth_headers, sample_students, sample_grades):
        """测试总分排名"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get("/api/v1/statistics/ranking/total?exam_type=期中", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_count"] == 5

        rankings = data["data"]["rankings"]
        # 张三总分最高: 95+88 = 183
        assert rankings[0]["student_id"] == "20260001"
        assert rankings[0]["total_score"] == 183.0

    def test_get_total_ranking_by_class(self, client, auth_headers, sample_students, sample_grades):
        """测试班级总分排名"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get(
            "/api/v1/statistics/ranking/total?exam_type=期中&class_name=2026级1班",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total_count"] == 3
        assert data["data"]["class_name"] == "2026级1班"

    def test_get_total_ranking_with_subject_scores(self, client, auth_headers, sample_students, sample_grades):
        """测试总分排名包含各科成绩"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get("/api/v1/statistics/ranking/total?exam_type=期中", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        rankings = data["data"]["rankings"]

        # 检查第一个学生的各科成绩
        first_student = rankings[0]
        assert "数学" in first_student["subject_scores"]
        assert "语文" in first_student["subject_scores"]

    # ==================== 通用统计查询测试 ====================

    def test_get_statistics_default_metrics(self, client, auth_headers, sample_students, sample_grades):
        """测试通用统计查询（默认指标）"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get("/api/v1/statistics", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_students"] == 10
        assert "avg" in data["data"]["metrics"]
        assert "max" in data["data"]["metrics"]
        assert "min" in data["data"]["metrics"]
        assert "pass_rate" in data["data"]["metrics"]

    def test_get_statistics_custom_metrics(self, client, auth_headers, sample_students, sample_grades):
        """测试通用统计查询（自定义指标）"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get("/api/v1/statistics?metrics=avg,excellent_rate,median", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "avg" in data["data"]["metrics"]
        assert "excellent_rate" in data["data"]["metrics"]
        assert "median" in data["data"]["metrics"]

    def test_get_statistics_with_filters(self, client, auth_headers, sample_students, sample_grades):
        """测试带筛选条件的通用统计查询"""
        self._setup_test_data(client, sample_students, sample_grades, auth_headers)

        response = client.get(
            "/api/v1/statistics?class_name=2026级1班&subject=数学&metrics=avg,max",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total_students"] == 3
        assert data["data"]["metrics"]["avg"] == 75.0
        assert data["data"]["metrics"]["max"] == 95.0

    def test_get_statistics_no_data(self, client, auth_headers):
        """测试无数据时通用统计查询"""
        response = client.get("/api/v1/statistics", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_students"] == 0

    # ==================== 边界条件测试 ====================

    def test_report_no_data(self, client, auth_headers):
        """测试无数据时综合统计报告"""
        response = client.get("/api/v1/statistics/report", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["statistics"]["count"] == 0
        assert data["data"]["top_students"] == []

    def test_ranking_no_data(self, client, auth_headers):
        """测试无数据时排名查询"""
        response = client.get(
            "/api/v1/statistics/ranking/subject?subject=数学&exam_type=期中",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_count"] == 0
        assert data["data"]["rankings"] == []

    def test_total_ranking_no_data(self, client, auth_headers):
        """测试无数据时总分排名"""
        response = client.get(
            "/api/v1/statistics/ranking/total?exam_type=期中",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_count"] == 0
        assert data["data"]["rankings"] == []
