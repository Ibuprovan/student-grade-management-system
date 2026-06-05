"""
认证相关 Schema

定义登录请求、Token 响应等认证相关的数据模型
"""

from pydantic import BaseModel, Field


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
        examples=["admin123"],
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
    """

    id: int = Field(description="用户 ID")
    username: str = Field(description="用户名")
    role: str = Field(description="用户角色")
    is_active: bool = Field(description="账户是否启用")
