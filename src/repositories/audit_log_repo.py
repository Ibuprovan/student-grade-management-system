"""
审计日志数据访问 Repository

提供审计日志相关的数据库操作。
从 audit_service.py 中拆分而来，遵循 Repository 层架构规范。
"""

from sqlalchemy.orm import Session

from src.models.audit_log import AuditLog
from src.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """
    审计日志数据访问类

    继承 BaseRepository，提供审计日志特有的查询方法。
    目前主要使用 BaseRepository 提供的通用 CRUD 操作，
    后续可扩展如按时间范围查询、按操作类型统计等特有方法。

    Attributes:
        model: AuditLog 模型类
        db: 数据库会话
    """

    def __init__(self, db: Session):
        """
        初始化审计日志 Repository

        Args:
            db: 数据库会话
        """
        super().__init__(AuditLog, db)
