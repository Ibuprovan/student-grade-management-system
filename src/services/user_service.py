"""
用户管理业务逻辑 Service

实现用户管理的核心业务逻辑，包括：
- 用户列表查询（分页）
- 创建用户
- 更新用户信息
- 删除用户
- 重置用户密码
"""

from typing import List, Tuple, Optional

from sqlalchemy.orm import Session

from src.core.exceptions import (
    NotFoundException,
    DuplicateException,
    ValidationException,
)
from src.core.security import hash_password
from src.models.user import User
from src.repositories.user_repo import UserRepository
from src.schemas.user import UserCreate, UserUpdate


class UserService:
    """
    用户管理业务逻辑类

    职责：
    - 处理用户管理相关的业务逻辑
    - 协调 UserRepository 进行数据操作
    - 执行业务规则校验（用户名唯一性、防止自删除等）

    Attributes:
        repo: UserRepository 实例
    """

    def __init__(self, db: Session):
        """
        初始化 UserService

        Args:
            db: SQLAlchemy 数据库会话
        """
        self.repo = UserRepository(db)

    def get_user_list(
        self,
        page: int = 1,
        page_size: int = 20,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[User], int]:
        """
        获取用户列表（分页）

        Args:
            page: 页码（从 1 开始）
            page_size: 每页数量
            role: 按角色筛选（可选）
            is_active: 按启用状态筛选（可选）

        Returns:
            Tuple[List[User], int]: (用户列表, 总数)
        """
        skip = (page - 1) * page_size

        # 构建过滤条件
        filters = []
        if role is not None:
            filters.append(User.role == role)
        if is_active is not None:
            filters.append(User.is_active == is_active)

        users = self.repo.get_all(skip=skip, limit=page_size, filters=filters)
        total = self.repo.count(filters=filters)

        return users, total

    def get_user_by_id(self, user_id: int) -> User:
        """
        根据 ID 查询用户

        Args:
            user_id: 用户 ID

        Returns:
            User: 用户 ORM 对象

        Raises:
            NotFoundException: 用户不存在
        """
        user = self.repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("用户", str(user_id))
        return user

    def create_user(self, data: UserCreate) -> User:
        """
        创建用户

        Args:
            data: 用户创建请求数据

        Returns:
            User: 创建的用户 ORM 对象

        Raises:
            DuplicateException: 用户名已存在
        """
        # 检查用户名唯一性
        if self.repo.username_exists(data.username):
            raise DuplicateException("用户", "用户名", data.username)

        # 创建用户（密码哈希）
        user_data = {
            "username": data.username,
            "hashed_password": hash_password(data.password),
            "role": data.role,
            "is_active": data.is_active,
        }
        user = self.repo.create(user_data)
        return user

    def update_user(self, user_id: int, data: UserUpdate) -> User:
        """
        更新用户信息

        Args:
            user_id: 用户 ID
            data: 用户更新请求数据

        Returns:
            User: 更新后的用户 ORM 对象

        Raises:
            NotFoundException: 用户不存在
            DuplicateException: 用户名已被占用
        """
        # 检查用户是否存在
        user = self.repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("用户", str(user_id))

        # 获取需要更新的字段
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        if not update_data:
            return user

        # 检查用户名唯一性（如果要更新用户名）
        if "username" in update_data and update_data["username"] != user.username:
            if self.repo.username_exists(update_data["username"]):
                raise DuplicateException("用户", "用户名", update_data["username"])

        # 执行更新
        updated_user = self.repo.update(user_id, update_data)
        return updated_user

    def delete_user(self, user_id: int, current_user_id: int) -> bool:
        """
        删除用户

        Args:
            user_id: 要删除的用户 ID
            current_user_id: 当前操作用户 ID（防止自删除）

        Returns:
            bool: 删除成功返回 True

        Raises:
            NotFoundException: 用户不存在
            ValidationException: 不能删除自己
        """
        # 防止管理员删除自己
        if user_id == current_user_id:
            raise ValidationException("不能删除当前登录的用户")

        # 检查用户是否存在
        user = self.repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("用户", str(user_id))

        # 执行删除
        return self.repo.delete(user_id)

    def reset_password(self, user_id: int, new_password: str) -> User:
        """
        重置用户密码

        Args:
            user_id: 用户 ID
            new_password: 新密码

        Returns:
            User: 更新后的用户 ORM 对象

        Raises:
            NotFoundException: 用户不存在
        """
        # 检查用户是否存在
        user = self.repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("用户", str(user_id))

        # 更新密码
        updated_user = self.repo.update(
            user_id,
            {"hashed_password": hash_password(new_password)},
        )
        return updated_user
