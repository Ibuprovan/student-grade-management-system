"""
操作审计日志 ORM 模型

定义 audit_logs 表的 SQLAlchemy 模型，用于记录系统中的关键操作。
"""

from datetime import datetime, timezone

from sqlalchemy import String, Integer, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class AuditLog(Base):
    """
    操作审计日志模型

    对应数据库中的 audit_logs 表，记录系统中所有关键操作。

    Attributes:
        id: 日志 ID（自增主键）
        user_id: 操作用户 ID
        username: 操作用户名（冗余存储，便于查询）
        action: 操作类型（create / update / delete / login / logout）
        resource_type: 资源类型（student / grade / user）
        resource_id: 资源标识符
        details: 操作详情（JSON 格式）
        ip_address: 客户端 IP 地址
        created_at: 操作时间
    """

    __tablename__ = "audit_logs"

    # ==================== 字段定义 ====================

    # 主键：日志 ID（自增）
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="日志 ID",
    )

    # 操作用户 ID
    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="操作用户 ID",
    )

    # 操作用户名（冗余存储，避免 JOIN 查询）
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="操作用户名",
    )

    # 操作类型
    action: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="操作类型",
    )

    # 资源类型
    resource_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="资源类型",
    )

    # 资源标识符
    resource_id: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        comment="资源标识符",
    )

    # 操作详情（JSON 字符串）
    details: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="操作详情",
    )

    # 客户端 IP 地址
    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=True,
        comment="客户端 IP 地址",
    )

    # 操作时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        comment="操作时间",
    )

    # ==================== 索引定义 ====================

    __table_args__ = (
        Index("idx_audit_logs_user_id", "user_id"),
        Index("idx_audit_logs_action", "action"),
        Index("idx_audit_logs_resource_type", "resource_type"),
        Index("idx_audit_logs_created_at", "created_at"),
    )

    # ==================== 方法定义 ====================

    def __repr__(self) -> str:
        """对象表示字符串"""
        return (
            f"<AuditLog(id={self.id}, user_id={self.user_id}, "
            f"action='{self.action}', resource_type='{self.resource_type}')>"
        )
