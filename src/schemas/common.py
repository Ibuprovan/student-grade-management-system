"""
通用响应 Schema

定义 API 通用的响应模式，包括成功响应、错误响应、分页响应等
"""

from typing import Optional, Any, List, Generic, TypeVar
from enum import Enum

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorCode(str, Enum):
    """错误码枚举"""

    NOT_FOUND = "NOT_FOUND"
    DUPLICATE = "DUPLICATE"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_FORMAT = "INVALID_FORMAT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ErrorDetail(BaseModel):
    """错误详情"""

    code: ErrorCode = Field(description="错误码")
    message: str = Field(description="错误描述")


class ApiResponse(BaseModel):
    """通用 API 响应"""

    success: bool = Field(description="请求是否成功")
    data: Optional[Any] = Field(None, description="响应数据")
    message: Optional[str] = Field(None, description="响应消息")
    error: Optional[ErrorDetail] = Field(None, description="错误详情")


class PaginatedData(BaseModel):
    """分页数据"""

    items: List[Any] = Field(description="数据列表")
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    total_pages: int = Field(description="总页数")


class PaginatedResponse(BaseModel):
    """分页响应"""

    success: bool = Field(True, description="请求是否成功")
    data: PaginatedData = Field(description="分页数据")


class SuccessResponse(BaseModel):
    """成功响应（无数据）"""

    success: bool = Field(True, description="请求是否成功")
    message: str = Field(description="响应消息")
