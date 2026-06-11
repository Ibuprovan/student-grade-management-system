"""
用户管理 API 路由

提供用户管理的 RESTful 接口（需要管理员权限）：
- GET    /api/v1/users                获取用户列表
- POST   /api/v1/users                创建用户
- GET    /api/v1/users/{id}           查询单个用户
- PUT    /api/v1/users/{id}           更新用户
- DELETE /api/v1/users/{id}           删除用户
- PUT    /api/v1/users/{id}/password  重置用户密码
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, Path, status

from src.api.dependencies import get_user_service
from src.api.auth import require_admin
from src.core.config import settings
from src.core.utils import build_paginated_response
from src.schemas.user import (
    UserCreate,
    UserUpdate,
    UserPasswordReset,
    UserResponse,
)
from src.schemas.common import ApiResponse, PaginatedResponse, SuccessResponse
from src.services.user_service import UserService
from src.models.user import User

# 创建路由器
router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])


@router.get(
    "",
    response_model=PaginatedResponse,
    summary="获取用户列表",
    description="获取所有用户列表，支持分页和按角色筛选（需要管理员权限）",
    responses={
        401: {"description": "未认证"},
        403: {"description": "权限不足"},
    },
)
def get_user_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    role: Optional[str] = Query(None, description="按角色筛选"),
    is_active: Optional[bool] = Query(None, description="按启用状态筛选"),
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin),
) -> PaginatedResponse:
    """
    获取用户列表（需要管理员权限）

    - **page**: 页码（默认 1）
    - **page_size**: 每页数量（默认 20，最大 100）
    - **role**: 按角色筛选（可选：admin / teacher / student）
    - **is_active**: 按启用状态筛选（可选）
    """
    page_size = min(page_size, settings.MAX_PAGE_SIZE)

    users, total = service.get_user_list(
        page=page,
        page_size=page_size,
        role=role,
        is_active=is_active,
    )

    return build_paginated_response(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
    description="创建新用户（需要管理员权限）",
    responses={
        401: {"description": "未认证"},
        403: {"description": "权限不足"},
        409: {"description": "用户名已存在"},
        422: {"description": "数据验证失败"},
    },
)
def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin),
) -> ApiResponse:
    """
    创建用户（需要管理员权限）

    - **username**: 用户名（3-50 个字符，唯一）
    - **password**: 密码（6-128 个字符）
    - **role**: 角色（admin / teacher / student，默认 student）
    - **is_active**: 是否启用（默认 true）
    """
    user = service.create_user(data)
    return ApiResponse(
        success=True,
        data=UserResponse.model_validate(user),
        message="用户创建成功",
    )


@router.get(
    "/{user_id}",
    response_model=ApiResponse,
    summary="查询用户",
    description="根据 ID 查询用户详细信息（需要管理员权限）",
    responses={
        401: {"description": "未认证"},
        403: {"description": "权限不足"},
        404: {"description": "用户不存在"},
    },
)
def get_user(
    user_id: int = Path(..., description="用户 ID"),
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin),
) -> ApiResponse:
    """
    查询单个用户（需要管理员权限）

    - **user_id**: 用户 ID
    """
    user = service.get_user_by_id(user_id)
    return ApiResponse(
        success=True,
        data=UserResponse.model_validate(user),
    )


@router.put(
    "/{user_id}",
    response_model=ApiResponse,
    summary="更新用户",
    description="更新用户信息，只更新提供的字段（需要管理员权限）",
    responses={
        401: {"description": "未认证"},
        403: {"description": "权限不足"},
        404: {"description": "用户不存在"},
        409: {"description": "用户名已存在"},
        422: {"description": "数据验证失败"},
    },
)
def update_user(
    data: UserUpdate,
    user_id: int = Path(..., description="用户 ID"),
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin),
) -> ApiResponse:
    """
    更新用户信息（需要管理员权限）

    - **user_id**: 用户 ID
    - 请求体中只提供需要更新的字段即可
    """
    user = service.update_user(user_id, data)
    return ApiResponse(
        success=True,
        data=UserResponse.model_validate(user),
        message="用户信息更新成功",
    )


@router.delete(
    "/{user_id}",
    response_model=SuccessResponse,
    summary="删除用户",
    description="删除用户（需要管理员权限，不能删除自己）",
    responses={
        401: {"description": "未认证"},
        403: {"description": "权限不足"},
        404: {"description": "用户不存在"},
        422: {"description": "不能删除自己"},
    },
)
def delete_user(
    user_id: int = Path(..., description="用户 ID"),
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin),
) -> SuccessResponse:
    """
    删除用户（需要管理员权限）

    - **user_id**: 用户 ID
    - 不能删除当前登录的用户
    """
    service.delete_user(user_id, current_user.id)
    return SuccessResponse(
        message=f"用户 '{user_id}' 删除成功",
    )


@router.put(
    "/{user_id}/password",
    response_model=SuccessResponse,
    summary="重置用户密码",
    description="管理员重置用户密码（需要管理员权限）",
    responses={
        401: {"description": "未认证"},
        403: {"description": "权限不足"},
        404: {"description": "用户不存在"},
        422: {"description": "数据验证失败"},
    },
)
def reset_password(
    data: UserPasswordReset,
    user_id: int = Path(..., description="用户 ID"),
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin),
) -> SuccessResponse:
    """
    重置用户密码（需要管理员权限）

    - **user_id**: 用户 ID
    - **new_password**: 新密码（6-128 个字符）
    """
    service.reset_password(user_id, data.new_password)
    return SuccessResponse(
        message=f"用户 '{user_id}' 密码重置成功",
    )
