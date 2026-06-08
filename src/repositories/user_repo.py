"""
用户数据访问 Repository

提供用户相关的数据库操作，包括按用户名查询、按 ID 查询等。
收归 auth 模块中散落的直接数据库查询逻辑。
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.user import User
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    用户数据访问类

    继承 BaseRepository，提供用户特有的查询方法。
    将 auth.py 路由和认证依赖中散落的 db.query(User) 调用
    统一收归到此 Repository 中，保持数据访问层的一致性。

    Attributes:
        model: User 模型类
        db: 数据库会话
    """

    def __init__(self, db: Session):
        """
        初始化用户 Repository

        Args:
            db: 数据库会话
        """
        super().__init__(User, db)

    def get_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名查询用户

        Args:
            username: 用户名

        Returns:
            Optional[User]: 用户实例，不存在则返回 None
        """
        stmt = select(User).where(User.username == username)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_active_by_id(self, user_id: int) -> Optional[User]:
        """
        根据 ID 查询启用状态的用户

        用于 Token 认证流程：仅返回 is_active=True 的用户，
        已禁用的用户不会被返回（调用方需自行判断 None）。

        Args:
            user_id: 用户 ID

        Returns:
            Optional[User]: 启用状态的用户实例，不存在或已禁用则返回 None
        """
        stmt = select(User).where(
            User.id == user_id,
            User.is_active == True,  # noqa: E712
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def username_exists(self, username: str) -> bool:
        """
        检查用户名是否已存在

        Args:
            username: 用户名

        Returns:
            bool: 存在返回 True，否则返回 False
        """
        return self.get_by_username(username) is not None
