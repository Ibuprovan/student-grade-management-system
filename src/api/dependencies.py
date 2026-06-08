"""
依赖注入模块

提供 FastAPI 的依赖注入配置，包括：
- 数据库会话注入
- Service 实例注入
- Repository 实例注入
- 认证依赖注入（在 src.api.auth 中定义）
"""

from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.repositories.user_repo import UserRepository
from src.services.student_service import StudentService
from src.services.grade_service import GradeService
from src.services.statistics_service import StatisticsService
from src.services.dashboard_service import DashboardService


def get_student_service(db: Session = Depends(get_db)) -> StudentService:
    """
    获取 StudentService 实例的依赖注入函数

    每次请求创建一个新的 StudentService 实例，绑定到该请求的数据库会话

    Args:
        db: 数据库会话（由 get_db 依赖注入）

    Returns:
        StudentService: 学生业务逻辑服务实例
    """
    return StudentService(db)


def get_grade_service(db: Session = Depends(get_db)) -> GradeService:
    """
    获取 GradeService 实例的依赖注入函数

    每次请求创建一个新的 GradeService 实例，绑定到该请求的数据库会话

    Args:
        db: 数据库会话（由 get_db 依赖注入）

    Returns:
        GradeService: 成绩业务逻辑服务实例
    """
    return GradeService(db)


def get_statistics_service(db: Session = Depends(get_db)) -> StatisticsService:
    """
    获取 StatisticsService 实例的依赖注入函数

    每次请求创建一个新的 StatisticsService 实例，绑定到该请求的数据库会话

    Args:
        db: 数据库会话（由 get_db 依赖注入）

    Returns:
        StatisticsService: 统计分析业务逻辑服务实例
    """
    return StatisticsService(db)


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    """
    获取 DashboardService 实例的依赖注入函数

    每次请求创建一个新的 DashboardService 实例，绑定到该请求的数据库会话

    Args:
        db: 数据库会话（由 get_db 依赖注入）

    Returns:
        DashboardService: 仪表盘业务逻辑服务实例
    """
    return DashboardService(db)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """
    获取 UserRepository 实例的依赖注入函数

    每次请求创建一个新的 UserRepository 实例，绑定到该请求的数据库会话。
    供 auth 模块的认证流程使用，收归散落的直接数据库查询。

    Args:
        db: 数据库会话（由 get_db 依赖注入）

    Returns:
        UserRepository: 用户数据访问实例
    """
    return UserRepository(db)
