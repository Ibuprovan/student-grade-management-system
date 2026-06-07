"""
API 路由模块

包含所有 FastAPI 路由定义
"""

from src.api.routes.students import router as students_router
from src.api.routes.grades import router as grades_router
from src.api.routes.statistics import router as statistics_router
from src.api.routes.auth import router as auth_router
from src.api.routes.dashboard import router as dashboard_router

__all__ = ["students_router", "grades_router", "statistics_router", "auth_router", "dashboard_router"]
