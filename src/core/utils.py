"""
通用工具函数模块

提供项目中可复用的辅助函数，减少路由层的重复代码
"""

import math
from typing import Any, List

from src.schemas.common import PaginatedResponse


def build_paginated_response(
    items: List[Any],
    total: int,
    page: int,
    page_size: int,
) -> PaginatedResponse:
    """
    构建标准化的分页响应

    统一处理分页逻辑（总页数计算、响应结构组装），
    避免在各路由中重复编写相同的分页响应构建代码。

    Args:
        items: 当前页的数据列表（应已序列化为响应 Schema）
        total: 满足条件的记录总数
        page: 当前页码（从 1 开始）
        page_size: 每页数量

    Returns:
        PaginatedResponse: 标准化的分页响应对象
    """
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse(
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    )
