"""
审计日志业务逻辑 Service

提供审计日志的记录和查询功能，用于追踪系统中的关键操作。
"""

import json
import logging
from typing import Optional, List, Tuple

from sqlalchemy.orm import Session

from src.models.audit_log import AuditLog
from src.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class AuditLogRepository(BaseRepository[AuditLog]):
    """
    审计日志数据访问类

    继承 BaseRepository，提供审计日志特有的查询方法。
    """

    def __init__(self, db: Session):
        """
        初始化审计日志 Repository

        Args:
            db: 数据库会话
        """
        super().__init__(AuditLog, db)


class AuditService:
    """
    审计日志业务逻辑类

    职责：
    - 记录系统中的关键操作
    - 查询审计日志（分页、筛选）

    Attributes:
        repo: AuditLogRepository 实例
    """

    def __init__(self, db: Session):
        """
        初始化 AuditService

        Args:
            db: SQLAlchemy 数据库会话
        """
        self.repo = AuditLogRepository(db)

    def log(
        self,
        user_id: int,
        username: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """
        记录审计日志

        Args:
            user_id: 操作用户 ID
            username: 操作用户名
            action: 操作类型（create / update / delete / login / logout）
            resource_type: 资源类型（student / grade / user）
            resource_id: 资源标识符（可选）
            details: 操作详情字典（可选，会被序列化为 JSON）
            ip_address: 客户端 IP 地址（可选）

        Returns:
            AuditLog: 创建的审计日志记录
        """
        log_data = {
            "user_id": user_id,
            "username": username,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": json.dumps(details, ensure_ascii=False) if details else None,
            "ip_address": ip_address,
        }

        try:
            audit_log = self.repo.create(log_data)
            return audit_log
        except Exception as e:
            # 审计日志记录失败不应影响正常业务流程
            logger.error(f"审计日志记录失败: {e}")
            return None

    def get_audit_logs(
        self,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> Tuple[List[AuditLog], int]:
        """
        查询审计日志（分页）

        Args:
            page: 页码（从 1 开始）
            page_size: 每页数量
            user_id: 按用户 ID 筛选（可选）
            action: 按操作类型筛选（可选）
            resource_type: 按资源类型筛选（可选）

        Returns:
            Tuple[List[AuditLog], int]: (日志列表, 总数)
        """
        from sqlalchemy import select, func

        skip = (page - 1) * page_size

        # 构建过滤条件
        filters = []
        if user_id is not None:
            filters.append(AuditLog.user_id == user_id)
        if action is not None:
            filters.append(AuditLog.action == action)
        if resource_type is not None:
            filters.append(AuditLog.resource_type == resource_type)

        # 查询数据（按时间倒序）
        stmt = select(AuditLog)
        for f in filters:
            stmt = stmt.where(f)
        stmt = stmt.order_by(AuditLog.created_at.desc()).offset(skip).limit(page_size)

        result = self.repo.db.execute(stmt)
        logs = list(result.scalars().all())

        # 统计总数
        count_stmt = select(func.count()).select_from(AuditLog)
        for f in filters:
            count_stmt = count_stmt.where(f)
        total = self.repo.db.execute(count_stmt).scalar() or 0

        return logs, total
