"""
统计分析 API 路由

提供成绩统计分析的 RESTful 接口（所有接口需要认证）：
- GET /api/v1/statistics/average          平均分统计
- GET /api/v1/statistics/max              最高分统计
- GET /api/v1/statistics/min              最低分统计
- GET /api/v1/statistics/pass-rate        及格率统计
- GET /api/v1/statistics/excellent-rate   优秀率统计
- GET /api/v1/statistics/report           综合统计报告
- GET /api/v1/statistics/ranking/subject  单科排名
- GET /api/v1/statistics/ranking/total    总分排名
- GET /api/v1/statistics                  通用统计查询
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_statistics_service
from src.api.auth import get_current_user
from src.schemas.common import ApiResponse
from src.schemas.statistics import (
    AverageResponse,
    MaxScoreResponse,
    MinScoreResponse,
    PassRateResponse,
    ExcellentRateResponse,
    ReportResponse,
    RankingResponse,
    TotalRankingResponse,
    StatisticsResponse,
    StatisticsMetric,
)
from src.services.statistics_service import StatisticsService
from src.models.user import User

# 创建路由器
router = APIRouter(prefix="/api/v1/statistics", tags=["统计分析"])


@router.get(
    "/average",
    response_model=ApiResponse,
    summary="平均分统计",
    description="计算指定条件下的成绩平均分（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def get_average(
    class_name: Optional[str] = Query(None, description="班级名称（可选）"),
    subject: Optional[str] = Query(None, description="科目名称（可选）"),
    exam_type: Optional[str] = Query(None, description="考试类型（可选）"),
    service: StatisticsService = Depends(get_statistics_service),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    平均分统计（需要认证）

    - **class_name**: 班级名称（可选）
    - **subject**: 科目名称（可选）
    - **exam_type**: 考试类型（可选）
    """
    result = service.get_average(
        class_name=class_name,
        subject=subject,
        exam_type=exam_type,
    )
    return ApiResponse(
        success=True,
        data=AverageResponse(**result).model_dump(),
    )


@router.get(
    "/max",
    response_model=ApiResponse,
    summary="最高分统计",
    description="查询指定条件下的最高分及学生信息（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def get_max_score(
    class_name: Optional[str] = Query(None, description="班级名称（可选）"),
    subject: Optional[str] = Query(None, description="科目名称（可选）"),
    exam_type: Optional[str] = Query(None, description="考试类型（可选）"),
    service: StatisticsService = Depends(get_statistics_service),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    最高分统计（需要认证）

    - **class_name**: 班级名称（可选）
    - **subject**: 科目名称（可选）
    - **exam_type**: 考试类型（可选）
    """
    result = service.get_max_score(
        class_name=class_name,
        subject=subject,
        exam_type=exam_type,
    )
    return ApiResponse(
        success=True,
        data=MaxScoreResponse(**result).model_dump(),
    )


@router.get(
    "/min",
    response_model=ApiResponse,
    summary="最低分统计",
    description="查询指定条件下的最低分及学生信息（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def get_min_score(
    class_name: Optional[str] = Query(None, description="班级名称（可选）"),
    subject: Optional[str] = Query(None, description="科目名称（可选）"),
    exam_type: Optional[str] = Query(None, description="考试类型（可选）"),
    service: StatisticsService = Depends(get_statistics_service),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    最低分统计（需要认证）

    - **class_name**: 班级名称（可选）
    - **subject**: 科目名称（可选）
    - **exam_type**: 考试类型（可选）
    """
    result = service.get_min_score(
        class_name=class_name,
        subject=subject,
        exam_type=exam_type,
    )
    return ApiResponse(
        success=True,
        data=MinScoreResponse(**result).model_dump(),
    )


@router.get(
    "/pass-rate",
    response_model=ApiResponse,
    summary="及格率统计",
    description="计算指定条件下的及格率（>=60分）（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def get_pass_rate(
    class_name: Optional[str] = Query(None, description="班级名称（可选）"),
    subject: Optional[str] = Query(None, description="科目名称（可选）"),
    exam_type: Optional[str] = Query(None, description="考试类型（可选）"),
    service: StatisticsService = Depends(get_statistics_service),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    及格率统计（需要认证）

    - **class_name**: 班级名称（可选）
    - **subject**: 科目名称（可选）
    - **exam_type**: 考试类型（可选）
    """
    result = service.get_pass_rate(
        class_name=class_name,
        subject=subject,
        exam_type=exam_type,
    )
    return ApiResponse(
        success=True,
        data=PassRateResponse(**result).model_dump(),
    )


@router.get(
    "/excellent-rate",
    response_model=ApiResponse,
    summary="优秀率统计",
    description="计算指定条件下的优秀率（>=90分）（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def get_excellent_rate(
    class_name: Optional[str] = Query(None, description="班级名称（可选）"),
    subject: Optional[str] = Query(None, description="科目名称（可选）"),
    exam_type: Optional[str] = Query(None, description="考试类型（可选）"),
    service: StatisticsService = Depends(get_statistics_service),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    优秀率统计（需要认证）

    - **class_name**: 班级名称（可选）
    - **subject**: 科目名称（可选）
    - **exam_type**: 考试类型（可选）
    """
    result = service.get_excellent_rate(
        class_name=class_name,
        subject=subject,
        exam_type=exam_type,
    )
    return ApiResponse(
        success=True,
        data=ExcellentRateResponse(**result).model_dump(),
    )


@router.get(
    "/report",
    response_model=ApiResponse,
    summary="综合统计报告",
    description="获取包含所有统计指标、分数分布和优秀学生的综合报告（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def get_report(
    class_name: Optional[str] = Query(None, description="班级名称（可选）"),
    subject: Optional[str] = Query(None, description="科目名称（可选）"),
    exam_type: Optional[str] = Query(None, description="考试类型（可选）"),
    top_n: int = Query(5, ge=1, le=50, description="优秀学生数量"),
    service: StatisticsService = Depends(get_statistics_service),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    综合统计报告（需要认证）

    - **class_name**: 班级名称（可选）
    - **subject**: 科目名称（可选）
    - **exam_type**: 考试类型（可选）
    - **top_n**: 优秀学生数量（默认5）
    """
    result = service.get_report(
        class_name=class_name,
        subject=subject,
        exam_type=exam_type,
        top_n=top_n,
    )
    return ApiResponse(
        success=True,
        data=ReportResponse(**result).model_dump(),
    )


@router.get(
    "/report/total",
    response_model=ApiResponse,
    summary="总分统计报告",
    description="获取基于学生总分的统计报告（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def get_total_score_report(
    class_name: Optional[str] = Query(None, description="班级名称（可选）"),
    exam_type: Optional[str] = Query(None, description="考试类型（可选）"),
    top_n: int = Query(10, ge=1, le=50, description="优秀学生数量"),
    service: StatisticsService = Depends(get_statistics_service),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    总分统计报告（需要认证）

    - **class_name**: 班级名称（可选）
    - **exam_type**: 考试类型（可选）
    - **top_n**: 优秀学生数量（默认10）
    """
    result = service.get_total_score_report(
        class_name=class_name,
        exam_type=exam_type,
        top_n=top_n,
    )
    return ApiResponse(
        success=True,
        data=result,
    )


@router.get(
    "/ranking/subject",
    response_model=ApiResponse,
    summary="单科排名",
    description="获取指定科目的成绩排名（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def get_subject_ranking(
    subject: str = Query(..., description="科目名称（必填）"),
    exam_type: str = Query(..., description="考试类型（必填）"),
    class_name: Optional[str] = Query(None, description="班级名称（可选，不填则为年级排名）"),
    order: str = Query("desc", description="排序方式（asc/desc）"),
    limit: Optional[int] = Query(None, ge=1, description="返回数量限制"),
    service: StatisticsService = Depends(get_statistics_service),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    单科排名（需要认证）

    - **subject**: 科目名称（必填）
    - **exam_type**: 考试类型（必填）
    - **class_name**: 班级名称（可选，不填则为年级排名）
    - **order**: 排序方式（asc升序/desc降序，默认desc）
    - **limit**: 返回数量限制（可选）
    """
    result = service.get_subject_ranking(
        subject=subject,
        exam_type=exam_type,
        class_name=class_name,
        order=order,
        limit=limit,
    )
    return ApiResponse(
        success=True,
        data=RankingResponse(**result).model_dump(),
    )


@router.get(
    "/ranking/total",
    response_model=ApiResponse,
    summary="总分排名",
    description="获取学生总分排名（所有科目分数之和）（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def get_total_ranking(
    exam_type: str = Query(..., description="考试类型（必填）"),
    class_name: Optional[str] = Query(None, description="班级名称（可选，不填则为年级排名）"),
    order: str = Query("desc", description="排序方式（asc/desc）"),
    limit: Optional[int] = Query(None, ge=1, description="返回数量限制"),
    service: StatisticsService = Depends(get_statistics_service),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    总分排名（需要认证）

    - **exam_type**: 考试类型（必填）
    - **class_name**: 班级名称（可选，不填则为年级排名）
    - **order**: 排序方式（asc升序/desc降序，默认desc）
    - **limit**: 返回数量限制（可选）
    """
    result = service.get_total_ranking(
        exam_type=exam_type,
        class_name=class_name,
        order=order,
        limit=limit,
    )
    return ApiResponse(
        success=True,
        data=TotalRankingResponse(**result).model_dump(),
    )


@router.get(
    "",
    response_model=ApiResponse,
    summary="通用统计查询",
    description="根据指定的指标列表获取统计数据（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def get_statistics(
    class_name: Optional[str] = Query(None, description="班级名称（可选）"),
    subject: Optional[str] = Query(None, description="科目名称（可选）"),
    exam_type: Optional[str] = Query(None, description="考试类型（可选）"),
    metrics: Optional[str] = Query(
        None,
        description="统计指标（逗号分隔，可选值：avg,max,min,pass_rate,excellent_rate,median,std_dev）",
    ),
    service: StatisticsService = Depends(get_statistics_service),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    通用统计查询（需要认证）

    - **class_name**: 班级名称（可选）
    - **subject**: 科目名称（可选）
    - **exam_type**: 考试类型（可选）
    - **metrics**: 统计指标（逗号分隔，默认：avg,max,min,pass_rate）
    """
    # 解析 metrics 参数
    metrics_list = None
    if metrics:
        metrics_list = [m.strip() for m in metrics.split(",")]

    result = service.get_statistics_metrics(
        class_name=class_name,
        subject=subject,
        exam_type=exam_type,
        metrics=metrics_list,
    )
    return ApiResponse(
        success=True,
        data=StatisticsResponse(**result).model_dump(),
    )


@router.get(
    "/batch/classes",
    response_model=ApiResponse,
    summary="批量班级统计",
    description="一次获取所有班级的统计数据（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def get_batch_class_statistics(
    exam_type: Optional[str] = Query(None, description="考试类型（可选）"),
    service: StatisticsService = Depends(get_statistics_service),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    批量获取所有班级的统计数据（需要认证）

    - **exam_type**: 考试类型（可选）
    """
    result = service.get_batch_class_statistics(exam_type=exam_type)
    return ApiResponse(
        success=True,
        data=result,
    )


@router.get(
    "/batch/subjects",
    response_model=ApiResponse,
    summary="批量科目统计",
    description="一次获取所有科目的统计数据（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def get_batch_subject_statistics(
    class_name: Optional[str] = Query(None, description="班级名称（可选）"),
    exam_type: Optional[str] = Query(None, description="考试类型（可选）"),
    service: StatisticsService = Depends(get_statistics_service),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    批量获取所有科目的统计数据（需要认证）

    - **class_name**: 班级名称（可选）
    - **exam_type**: 考试类型（可选）
    """
    result = service.get_batch_subject_statistics(
        class_name=class_name,
        exam_type=exam_type,
    )
    return ApiResponse(
        success=True,
        data=result,
    )
