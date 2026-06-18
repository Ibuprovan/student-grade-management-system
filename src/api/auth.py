"""
认证依赖模块

提供 FastAPI 的认证依赖注入，包括：
- get_current_user: 从 JWT Token 中获取当前用户
- require_admin: 要求管理员权限
- require_authenticated: 要求已登录用户

使用方式：
    @router.get("/protected")
    def protected_endpoint(user: User = Depends(get_current_user)):
        return {"user": user.username}
"""

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.core.security import jwt_service
from src.models.user import User
from src.repositories.user_repo import UserRepository
from src.api.dependencies import get_user_repository

logger = logging.getLogger(__name__)

# HTTP Bearer 认证方案
# 自动从请求头 Authorization: Bearer <token> 中提取 Token
security = HTTPBearer(
    auto_error=True,  # 未提供 Token 时自动返回 401
    description="JWT 认证 Token",
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    """
    获取当前认证用户

    从请求头中提取 JWT Token，验证其有效性，并返回对应的用户对象。

    验证流程：
    1. 从 Authorization 头提取 Bearer Token
    2. 验证 Token 签名和有效期
    3. 检查 Token 是否在黑名单中
    4. 验证 Token 类型为 access
    5. 从数据库查询用户
    6. 检查用户是否启用

    Args:
        credentials: HTTP Bearer 认证凭据（自动注入）
        user_repo: 用户数据访问 Repository（自动注入）

    Returns:
        User: 当前认证的用户对象

    Raises:
        HTTPException 401: Token 无效、已过期、已被吊销或用户不存在
    """
    token = credentials.credentials

    try:
        # 验证 Token（签名 + 有效期 + 黑名单）
        payload = jwt_service.verify_token(token)

        # 确保是 Access Token
        if payload.type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的 Token 类型，请使用 Access Token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 从数据库查询用户（通过 Repository）
        user = user_repo.get_active_by_id(int(payload.sub))

        if user is None:
            logger.warning(f"Token 中的用户不存在或已被禁用: user_id={payload.sub}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except ValueError as e:
        # Token 验证失败（过期、无效、已吊销）
        logger.warning(f"Token 验证失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    要求管理员权限

    验证当前用户是否具有管理员角色。

    Args:
        current_user: 当前认证用户（由 get_current_user 注入）

    Returns:
        User: 验证通过的管理员用户

    Raises:
        HTTPException 403: 用户不是管理员
    """
    if current_user.role != "admin":
        logger.warning(
            f"权限不足: user_id={current_user.id}, "
            f"role={current_user.role}, required=admin"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足：需要管理员权限",
        )
    return current_user


async def require_teacher_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    要求教师或管理员权限

    验证当前用户是否具有教师或管理员角色。

    Args:
        current_user: 当前认证用户（由 get_current_user 注入）

    Returns:
        User: 验证通过的用户

    Raises:
        HTTPException 403: 用户权限不足
    """
    if current_user.role not in ("admin", "teacher"):
        logger.warning(
            f"权限不足: user_id={current_user.id}, "
            f"role={current_user.role}, required=admin|teacher"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足：需要教师或管理员权限",
        )
    return current_user


async def require_class_teacher_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    要求班主任或管理员权限

    班主任和管理员均可访问，班主任仅可访问自己班级的数据。
    """
    if current_user.role not in ("admin", "class_teacher"):
        logger.warning(
            f"权限不足: user_id={current_user.id}, "
            f"role={current_user.role}, required=admin|class_teacher"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足：需要班主任或管理员权限",
        )
    return current_user


async def require_subject_leader_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role not in ("admin", "subject_leader"):
        logger.warning(
            f"权限不足: user_id={current_user.id}, "
            f"role={current_user.role}, required=admin|subject_leader"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足：需要学科组长或管理员权限",
        )
    return current_user
