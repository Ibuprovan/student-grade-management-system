"""
审计日志 API 路由

提供审计日志查询的 RESTful 接口（需要管理员权限）：
- GET /api/v1/audit-logs    获取审计日志列表
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies import get_db
from src.api.auth import require_admin
from src.core.config import settings
from src.core.utils import build_paginated_response
from src.schemas.audit_log import AuditLogResponse
from src.schemas.common import ApiResponse, PaginatedResponse
from src.services.audit_service import AuditService
from src.models.user import User
from sqlalchemy.orm import Session

# 创建路由器
router = APIRouter(prefix="/api/v1/audit-logs", tags=["审计日志"])


@router.get(
    "",
    response_model=PaginatedResponse,
    summary="获取审计日志列表",
    description="获取操作审计日志，支持分页和按条件筛选（需要管理员权限）",
    responses={
        401: {"description": "未认证"},
        403: {"description": "权限不足"},
    },
)
def get_audit_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: Optional[int] = Query(None, description="按用户 ID 筛选"),
    action: Optional[str] = Query(None, description="按操作类型筛选"),
    resource_type: Optional[str] = Query(None, description="按资源类型筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> PaginatedResponse:
    """
    获取审计日志列表（需要管理员权限）

    - **page**: 页码（默认 1）
    - **page_size**: 每页数量（默认 20，最大 100）
    - **user_id**: 按用户 ID 筛选（可选）
    - **action**: 按操作类型筛选（可选：create / update / delete / login / logout）
    - **resource_type**: 按资源类型筛选（可选：student / grade / user）
    """
    page_size = min(page_size, settings.MAX_PAGE_SIZE)

    service = AuditService(db)
    logs, total = service.get_audit_logs(
        page=page,
        page_size=page_size,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
    )

    return build_paginated_response(
        items=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        page=page,
        page_size=page_size,
    )
