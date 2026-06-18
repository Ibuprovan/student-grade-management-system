"""
用户认证 ORM 模型

定义 users 表的 SQLAlchemy 模型，用于系统认证与授权。

角色说明：
- admin: 管理员，拥有所有权限
- teacher: 教师，可以管理学生和成绩
- student: 学生，仅可查看自己的成绩
"""

from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class User(Base):
    """
    用户认证模型

    对应数据库中的 users 表，存储用户认证信息。

    Attributes:
        id: 用户 ID（自增主键）
        username: 用户名（唯一）
        hashed_password: bcrypt 哈希后的密码
        role: 用户角色（admin / teacher / student）
        is_active: 账户是否启用
        created_at: 记录创建时间
        updated_at: 记录最后更新时间
    """

    __tablename__ = "users"

    # ==================== 字段定义 ====================

    # 主键：用户 ID（自增）
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="用户 ID",
    )

    # 用户名：唯一，用于登录
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="用户名",
    )

    # 密码：bcrypt 哈希存储，禁止明文
    hashed_password: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        comment="哈希密码",
    )

    # 角色：admin / teacher / student
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="student",
        comment="用户角色",
    )

    # 账户是否启用（可用于禁用账户而不删除）
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="账户是否启用",
    )

    # 是否需要修改密码（首次登录时为 True）
    need_change_password: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否需要修改密码",
    )

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        comment="创建时间",
    )

    # 更新时间
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="更新时间",
    )

    # ==================== 方法定义 ====================

    def __repr__(self) -> str:
        """对象表示字符串"""
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"

    def __str__(self) -> str:
        """可读字符串表示"""
        return f"{self.username} ({self.role})"
