"""
用户管理 Schema

定义用户管理相关的 Pydantic 模型，用于管理员创建、更新、查询用户
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserCreate(BaseModel):
    """
    创建用户请求模型

    用于管理员创建新用户，所有字段必填。
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="用户名（唯一）",
        examples=["teacher01"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="密码",
        examples=["password123"],
    )
    role: str = Field(
        default="student",
        description="用户角色（admin / teacher / class_teacher / student）",
        examples=["teacher"],
    )
    is_active: bool = Field(
        default=True,
        description="账户是否启用",
    )

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """验证角色值"""
        allowed_roles = {"admin", "teacher", "class_teacher", "student"}
        if v not in allowed_roles:
            raise ValueError(f"角色必须是以下之一：{', '.join(allowed_roles)}")
        return v


class UserUpdate(BaseModel):
    """
    更新用户请求模型

    所有字段可选，只更新提供的字段。
    """

    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="用户名",
    )
    role: Optional[str] = Field(
        None,
        description="用户角色",
    )
    is_active: Optional[bool] = Field(
        None,
        description="账户是否启用",
    )

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: Optional[str]) -> Optional[str]:
        """验证角色值"""
        if v is not None:
            allowed_roles = {"admin", "teacher", "class_teacher", "student"}
            if v not in allowed_roles:
                raise ValueError(f"角色必须是以下之一：{', '.join(allowed_roles)}")
        return v


class UserPasswordReset(BaseModel):
    """
    重置密码请求模型

    管理员重置用户密码时使用。
    """

    new_password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="新密码",
        examples=["new_password123"],
    )


class UserResponse(BaseModel):
    """
    用户响应模型

    用于 API 响应的数据序列化，不包含密码字段。
    """

    id: int = Field(description="用户 ID")
    username: str = Field(description="用户名")
    role: str = Field(description="用户角色")
    is_active: bool = Field(description="账户是否启用")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    model_config = ConfigDict(from_attributes=True)
