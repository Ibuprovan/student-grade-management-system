"""
API 路由模块

包含所有 FastAPI 路由定义
"""

from src.api.routes.students import router as students_router
from src.api.routes.grades import router as grades_router
from src.api.routes.statistics import router as statistics_router
from src.api.routes.auth import router as auth_router
from src.api.routes.dashboard import router as dashboard_router
from src.api.routes.users import router as users_router
from src.api.routes.audit_logs import router as audit_logs_router
from src.api.routes.imports import router as imports_router
from src.api.routes.class_teachers import router as class_teachers_router
from src.api.routes.class_teacher_scoped import router as class_teacher_scoped_router
from src.api.routes.subject_leaders import router as subject_leaders_router
from src.api.routes.subject_leader_scoped import router as subject_leader_scoped_router
from src.api.routes.accounts import router as accounts_router
from src.api.routes.teacher_assignments import router as teacher_assignments_router
from src.api.routes.teacher_scoped import router as teacher_scoped_router

__all__ = [
    "students_router",
    "grades_router",
    "statistics_router",
    "auth_router",
    "dashboard_router",
    "users_router",
    "audit_logs_router",
    "imports_router",
    "class_teachers_router",
    "class_teacher_scoped_router",
    "subject_leaders_router",
    "subject_leader_scoped_router",
    "accounts_router",
    "teacher_assignments_router",
    "teacher_scoped_router",
]
