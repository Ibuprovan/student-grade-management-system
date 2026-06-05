"""
pytest 配置文件

提供测试用的数据库会话和 fixtures
"""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from src.core.database import Base
from src.models import Student, Grade


@pytest.fixture(scope="function")
def db_engine():
    """
    创建测试用的数据库引擎

    使用内存数据库，每次测试后自动清理
    """
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )

    # 启用 SQLite 外键约束（与生产环境保持一致）
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    创建测试用的数据库会话

    每次测试使用独立的事务，测试后自动回滚
    """
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_student_data():
    """示例学生数据"""
    return {
        "student_id": "20260001",
        "name": "张三",
        "gender": "男",
        "class_name": "三年一班",
        "enrollment_year": 2026,
    }


@pytest.fixture
def sample_grade_data():
    """示例成绩数据"""
    from datetime import date
    return {
        "student_id": "20260001",
        "subject": "数学",
        "score": 95.5,
        "exam_type": "期中",
        "exam_date": date(2026, 4, 15),
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
def sample_grades():
    """多个示例成绩数据"""
    from datetime import date
    return [
        {
            "student_id": "20260001",
            "subject": "数学",
            "score": 95.5,
            "exam_type": "期中",
            "exam_date": date(2026, 4, 15),
        },
        {
            "student_id": "20260001",
            "subject": "语文",
            "score": 88.0,
            "exam_type": "期中",
            "exam_date": date(2026, 4, 15),
        },
        {
            "student_id": "20260002",
            "subject": "数学",
            "score": 72.5,
            "exam_type": "期中",
            "exam_date": date(2026, 4, 15),
        },
    ]
