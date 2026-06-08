"""
认证 API 路由

提供用户认证相关的 RESTful 接口：
- POST /api/v1/auth/login          用户登录
- POST /api/v1/auth/refresh        刷新 Token
- POST /api/v1/auth/logout         用户登出（吊销 Token）
- GET  /api/v1/auth/me             获取当前用户信息
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import jwt_service, hash_password, verify_password
from src.core.config import settings
from src.models.user import User
from src.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    UserInfo,
)
from src.schemas.common import ApiResponse, SuccessResponse
from src.api.auth import get_current_user, security

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/v1/auth", tags=["认证管理"])


@router.post(
    "/login",
    response_model=ApiResponse,
    summary="用户登录",
    description="使用用户名和密码登录，获取 JWT Token",
    responses={
        401: {"description": "用户名或密码错误"},
        403: {"description": "账户已被禁用"},
    },
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
) -> ApiResponse:
    """
    用户登录

    - **username**: 用户名
    - **password**: 密码

    返回 Access Token 和 Refresh Token。
    """
    # 查询用户
    user = db.query(User).filter(User.username == data.username).first()

    if user is None:
        logger.warning(f"登录失败：用户不存在 - {data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 验证密码
    if not verify_password(data.password, user.hashed_password):
        logger.warning(f"登录失败：密码错误 - user_id={user.id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 检查账户是否启用
    if not user.is_active:
        logger.warning(f"登录失败：账户已禁用 - user_id={user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用，请联系管理员",
        )

    # 生成 Token
    access_token = jwt_service.create_access_token(
        user_id=str(user.id),
        username=user.username,
        role=user.role,
    )
    refresh_token = jwt_service.create_refresh_token(
        user_id=str(user.id),
        username=user.username,
    )

    logger.info(f"用户登录成功: user_id={user.id}, username={user.username}")

    return ApiResponse(
        success=True,
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ).model_dump(),
        message="登录成功",
    )


@router.post(
    "/refresh",
    response_model=ApiResponse,
    summary="刷新 Token",
    description="使用 Refresh Token 获取新的 Access Token",
    responses={
        401: {"description": "Refresh Token 无效或已过期"},
    },
)
def refresh_token(
    data: RefreshRequest,
    db: Session = Depends(get_db),
) -> ApiResponse:
    """
    刷新 Token

    - **refresh_token**: 刷新令牌

    返回新的 Access Token 和 Refresh Token。
    """
    try:
        # 验证 Refresh Token
        payload = jwt_service.verify_token(data.refresh_token)

        if payload.type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的 Token 类型，请使用 Refresh Token",
            )

        # 查询用户
        user = db.query(User).filter(User.id == int(payload.sub)).first()

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用",
            )

        # 生成新的 Token 对
        new_access_token = jwt_service.create_access_token(
            user_id=str(user.id),
            username=user.username,
            role=user.role,
        )
        new_refresh_token = jwt_service.create_refresh_token(
            user_id=str(user.id),
            username=user.username,
        )

        # 吊销旧的 Refresh Token
        jwt_service.blacklist_token(payload.jti)

        logger.info(f"Token 刷新成功: user_id={user.id}")

        return ApiResponse(
            success=True,
            data=TokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            ).model_dump(),
            message="Token 刷新成功",
        )

    except ValueError as e:
        logger.warning(f"Refresh Token 验证失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/logout",
    response_model=SuccessResponse,
    summary="用户登出",
    description="吊销当前 Token，实现登出",
)
def logout(
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> SuccessResponse:
    """
    用户登出

    吊销当前 Access Token（通过黑名单机制）。

    1. 从请求头中提取原始 Token
    2. 解码 Token 获取 jti（唯一标识）
    3. 将 jti 加入黑名单，使该 Token 失效
    """
    # 解码当前 Access Token 获取 jti
    payload = jwt_service.decode_token(credentials.credentials)
    # 将 Token 加入黑名单（吊销）
    jwt_service.blacklist_token(payload.jti)

    logger.info(f"用户登出: user_id={current_user.id}, jti={payload.jti}")
    return SuccessResponse(message="登出成功")


@router.get(
    "/me",
    response_model=ApiResponse,
    summary="获取当前用户信息",
    description="获取当前已认证用户的详细信息",
)
def get_me(
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    获取当前用户信息

    返回当前已认证用户的基本信息。
    """
    return ApiResponse(
        success=True,
        data=UserInfo(
            id=current_user.id,
            username=current_user.username,
            role=current_user.role,
            is_active=current_user.is_active,
        ).model_dump(),
    )

