"""
认证 API 路由

提供用户认证相关的 RESTful 接口：
- POST /api/v1/auth/login             用户登录
- POST /api/v1/auth/refresh           刷新 Token
- POST /api/v1/auth/logout            用户登出（吊销 Token）
- GET  /api/v1/auth/me                获取当前用户信息
- POST /api/v1/auth/change-password   修改密码
"""

import logging
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import jwt_service, hash_password, verify_password
from src.core.config import settings
from src.models.user import User
from src.repositories.user_repo import UserRepository
from src.repositories.student_repo import StudentRepository
from src.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    UserInfo,
    ChangePasswordRequest,
)
from src.schemas.common import ApiResponse, SuccessResponse
from src.api.auth import get_current_user, security, get_user_repository

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
    user_repo: UserRepository = Depends(get_user_repository),
) -> ApiResponse:
    """
    用户登录

    - **username**: 用户名
    - **password**: 密码

    返回 Access Token 和 Refresh Token。
    """
    # 查询用户（通过 Repository）
    user = user_repo.get_by_username(data.username)

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
    user_repo: UserRepository = Depends(get_user_repository),
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

        # 查询用户（通过 Repository，同时检查启用状态）
        user = user_repo.get_active_by_id(int(payload.sub))

        if user is None:
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


@router.post(
    "/change-password",
    response_model=ApiResponse,
    summary="修改密码",
    description="验证旧密码后修改为新密码，需要认证",
    responses={
        400: {"description": "旧密码错误"},
        401: {"description": "未认证"},
        422: {"description": "新密码强度不足"},
    },
)
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository),
) -> ApiResponse:
    """
    修改密码

    - **old_password**: 当前密码（用于身份验证）
    - **new_password**: 新密码（需满足强度要求：至少8位，包含大小写字母和数字）

    验证流程：
    1. 验证旧密码是否正确
    2. 验证新密码强度（由 Schema 层自动完成）
    3. 确保新密码与旧密码不同
    4. 哈希新密码并更新数据库
    """
    # 1. 验证旧密码
    if not verify_password(data.old_password, current_user.hashed_password):
        logger.warning(f"修改密码失败：旧密码错误 - user_id={current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码不正确",
        )

    # 2. 确保新密码与旧密码不同
    if data.old_password == data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与旧密码相同",
        )

    # 3. 哈希新密码并更新
    new_hashed_password = hash_password(data.new_password)
    user_repo.update(current_user.id, {"hashed_password": new_hashed_password})

    logger.info(f"用户密码修改成功: user_id={current_user.id}")

    return ApiResponse(
        success=True,
        message="密码修改成功",
    )


@router.post(
    "/check-token",
    response_model=ApiResponse,
    summary="检查 Token 状态",
    description="检查当前 Token 是否即将过期（30 分钟内）",
    responses={
        401: {"description": "未认证"},
    },
)
def check_token(
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> ApiResponse:
    """
    检查 Token 状态

    检查当前 Access Token 是否即将过期（30 分钟内），
    前端可根据返回的 `expiring_soon` 标志提前刷新 Token。
    """
    # 解码 Token 获取过期时间
    payload = jwt_service.decode_token(credentials.credentials)

    # 计算剩余时间
    now = datetime.now(timezone.utc)
    expires_at = payload.exp
    remaining = expires_at - now
    remaining_minutes = remaining.total_seconds() / 60

    # 判断是否即将过期（30 分钟内）
    expiring_soon = remaining_minutes <= 30

    return ApiResponse(
        success=True,
        data={
            "expiring_soon": expiring_soon,
            "expires_at": expires_at.isoformat(),
            "remaining_minutes": round(remaining_minutes, 1),
        },
    )


def get_student_repository(db: Session = Depends(get_db)) -> StudentRepository:
    """获取 StudentRepository 实例的依赖注入函数"""
    return StudentRepository(db)


@router.get(
    "/me/student-info",
    response_model=ApiResponse,
    summary="获取当前学生用户关联的学生信息",
    description="获取当前登录学生用户关联的学生基本信息（学号、姓名、班级等）",
    responses={
        401: {"description": "未认证"},
        403: {"description": "非学生角色"},
        404: {"description": "未找到关联的学生信息"},
    },
)
def get_current_student_info(
    current_user: User = Depends(get_current_user),
    student_repo: StudentRepository = Depends(get_student_repository),
) -> ApiResponse:
    """
    获取当前学生用户关联的学生信息

    仅学生角色可调用，通过用户名查找关联的学生记录。
    学生用户的用户名应与学号一致。
    """
    # 检查是否是学生角色
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="此接口仅限学生用户使用",
        )

    # 通过用户名（学号）查找学生
    student = student_repo.get_by_student_id(current_user.username)

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到关联的学生信息，请联系管理员",
        )

    return ApiResponse(
        success=True,
        data={
            "student_id": student.student_id,
            "name": student.name,
            "gender": student.gender,
            "class_name": student.class_name,
            "enrollment_year": student.enrollment_year,
        },
    )

