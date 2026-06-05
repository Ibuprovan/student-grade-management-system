"""
数据库连接模块

提供 SQLAlchemy 引擎、会话工厂和数据库初始化功能
"""

from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

from src.core.config import settings


class Base(DeclarativeBase):
    """
    SQLAlchemy 声明式基类

    所有 ORM 模型都应继承此类
    """
    pass


# 创建 SQLAlchemy 引擎
# 对于 SQLite，需要设置 check_same_thread=False 以允许多线程访问
engine = create_engine(
    settings.get_sync_database_url(),
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# SQLite 特殊配置：启用外键约束
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    SQLite 连接时启用外键约束支持

    Args:
        dbapi_connection: 数据库连接
        connection_record: 连接记录
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话的依赖注入函数

    用于 FastAPI 的 Depends 注入，确保会话在请求结束后正确关闭

    Yields:
        Session: SQLAlchemy 数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    初始化数据库

    创建所有已注册的表结构。如果表已存在，则跳过。
    """
    # 确保数据库目录存在
    db_path = settings.database_path
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # 导入所有模型以确保它们被注册到 Base.metadata
    import src.models  # noqa: F401

    # 创建所有表
    Base.metadata.create_all(bind=engine)


def drop_all_tables() -> None:
    """
    删除所有表（仅用于测试）

    警告：此操作会删除所有数据！
    """
    import src.models  # noqa: F401
    Base.metadata.drop_all(bind=engine)
