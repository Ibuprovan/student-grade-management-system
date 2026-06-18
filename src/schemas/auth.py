"""
认证相关 Schema

定义登录请求、Token 响应、修改密码等认证相关的数据模型
"""

import re

from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    """
    登录请求模型

    Attributes:
        username: 用户名
        password: 密码
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="用户名",
        examples=["admin"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="密码",
        examples=["your_password"],
    )


class TokenResponse(BaseModel):
    """
    Token 响应模型

    登录成功后返回的 Token 信息。

    Attributes:
        access_token: 访问令牌（用于 API 认证）
        refresh_token: 刷新令牌（用于获取新的 access_token）
        token_type: Token 类型（固定为 bearer）
        expires_in: Access Token 有效期（秒）
    """

    access_token: str = Field(description="访问令牌")
    refresh_token: str = Field(description="刷新令牌")
    token_type: str = Field(default="bearer", description="Token 类型")
    expires_in: int = Field(description="Access Token 有效期（秒）")


class RefreshRequest(BaseModel):
    """
    刷新 Token 请求模型

    Attributes:
        refresh_token: 刷新令牌
    """

    refresh_token: str = Field(
        ...,
        description="刷新令牌",
    )


class UserInfo(BaseModel):
    """
    用户信息模型

    用于认证后返回当前用户信息。

    Attributes:
        id: 用户 ID
        username: 用户名
        role: 用户角色
        is_active: 账户是否启用
        need_change_password: 是否需要修改密码
    """

    id: int = Field(description="用户 ID")
    username: str = Field(description="用户名")
    role: str = Field(description="用户角色")
    is_active: bool = Field(description="账户是否启用")
    need_change_password: bool = Field(default=False, description="是否需要修改密码")


class ChangePasswordRequest(BaseModel):
    """
    修改密码请求模型

    Attributes:
        old_password: 当前密码（用于验证身份）
        new_password: 新密码（需满足强度要求）

    密码强度要求：
        - 至少 8 个字符
        - 包含至少一个大写字母
        - 包含至少一个小写字母
        - 包含至少一个数字
    """

    old_password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="当前密码",
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="新密码（至少8位，包含大小写字母和数字）",
    )

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        验证新密码强度

        要求：
        - 至少 8 个字符
        - 包含至少一个大写字母 [A-Z]
        - 包含至少一个小写字母 [a-z]
        - 包含至少一个数字 [0-9]

        Raises:
            ValueError: 密码不满足强度要求时抛出
        """
        if len(v) < 8:
            raise ValueError("密码长度至少为 8 个字符")
        if not re.search(r"[A-Z]", v):
            raise ValueError("密码必须包含至少一个大写字母")
        if not re.search(r"[a-z]", v):
            raise ValueError("密码必须包含至少一个小写字母")
        if not re.search(r"\d", v):
            raise ValueError("密码必须包含至少一个数字")
        return v
