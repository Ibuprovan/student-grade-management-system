"""
核心配置模块

包含应用配置、数据库连接、常量定义和自定义异常
"""

from src.core.config import settings
from src.core.database import Base, get_db, init_db
from src.core.constants import SUBJECTS, EXAM_TYPES, GENDERS, SCORE_MIN, SCORE_MAX
from src.core.exceptions import (
    AppException,
    NotFoundException,
    DuplicateException,
    ValidationException,
    StudentNotFoundException,
    DuplicateGradeException,
    ScoreOutOfRangeException,
)

__all__ = [
    "settings",
    "Base",
    "get_db",
    "init_db",
    "SUBJECTS",
    "EXAM_TYPES",
    "GENDERS",
    "SCORE_MIN",
    "SCORE_MAX",
    "AppException",
    "NotFoundException",
    "DuplicateException",
    "ValidationException",
    "StudentNotFoundException",
    "DuplicateGradeException",
    "ScoreOutOfRangeException",
]
