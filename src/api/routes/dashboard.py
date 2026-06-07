"""
仪表盘 API 路由

提供仪表盘页面的 RESTful 接口（需要认证）：
- GET /api/v1/dashboard/stats  获取仪表盘统计数据
"""

from fastapi import APIRouter, Depends

from src.api.dependencies import get_db
from src.api.auth import get_current_user
from src.schemas.common import ApiResponse
from src.services.dashboard_service import DashboardService
from src.models.user import User
from sqlalchemy.orm import Session

# 创建路由器
router = APIRouter(prefix="/api/v1/dashboard", tags=["仪表盘"])


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    """
    获取 DashboardService 实例的依赖注入函数

    Args:
        db: 数据库会话（由 get_db 依赖注入）

    Returns:
        DashboardService: 仪表盘业务逻辑服务实例
    """
    return DashboardService(db)


@router.get(
    "/stats",
    response_model=ApiResponse,
    summary="获取仪表盘统计数据",
    description="获取仪表盘页面所需的汇总统计数据，包括学生总数、成绩记录总数、平均分和及格率（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def get_dashboard_stats(
    service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    获取仪表盘统计数据（需要认证）

    返回数据：
    - **total_students**: 学生总数
    - **total_grades**: 成绩记录总数
    - **average_score**: 平均分
    - **pass_rate**: 及格率（百分比）
    """
    result = service.get_dashboard_stats()
    return ApiResponse(
        success=True,
        data=result,
    )
