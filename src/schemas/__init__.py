"""
数据验证模块

包含所有 Pydantic Schema 定义，用于请求/响应数据验证
"""

from src.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
)
from src.schemas.grade import (
    GradeCreate,
    GradeBatchCreate,
    GradeUpdate,
    GradeResponse,
)
from src.schemas.common import (
    ApiResponse,
    PaginatedResponse,
    SuccessResponse,
    ErrorCode,
    ErrorDetail,
)
from src.schemas.statistics import (
    StatisticsQuery,
    StatisticsResponse,
    AverageResponse,
    MaxScoreResponse,
    MinScoreResponse,
    PassRateResponse,
    ExcellentRateResponse,
    ReportResponse,
    RankingResponse,
    TotalRankingResponse,
    StatisticsMetric,
)
from src.schemas.user import (
    UserCreate,
    UserUpdate,
    UserPasswordReset,
    UserResponse,
)
from src.schemas.batch import (
    BatchDeleteRequest,
    BatchDeleteResponse,
)
from src.schemas.audit_log import AuditLogResponse

__all__ = [
    "StudentCreate",
    "StudentUpdate",
    "StudentResponse",
    "GradeCreate",
    "GradeBatchCreate",
    "GradeUpdate",
    "GradeResponse",
    "ApiResponse",
    "PaginatedResponse",
    "SuccessResponse",
    "ErrorCode",
    "ErrorDetail",
    "StatisticsQuery",
    "StatisticsResponse",
    "AverageResponse",
    "MaxScoreResponse",
    "MinScoreResponse",
    "PassRateResponse",
    "ExcellentRateResponse",
    "ReportResponse",
    "RankingResponse",
    "TotalRankingResponse",
    "StatisticsMetric",
    "UserCreate",
    "UserUpdate",
    "UserPasswordReset",
    "UserResponse",
    "BatchDeleteRequest",
    "BatchDeleteResponse",
    "AuditLogResponse",
]
