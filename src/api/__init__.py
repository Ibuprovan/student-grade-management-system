"""
API 表现层模块

包含 FastAPI 路由和依赖注入配置
"""

from src.api.routes.students import router as students_router

__all__ = ["students_router"]
