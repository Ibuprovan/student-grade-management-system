"""
批量操作 Schema

定义批量操作相关的 Pydantic 模型
"""

from typing import List

from pydantic import BaseModel, Field


class BatchDeleteRequest(BaseModel):
    """
    批量删除请求模型

    用于批量删除学生等场景。
    """

    student_ids: List[str] = Field(
        ...,
        min_length=1,
        description="学号列表",
        examples=[["20260001", "20260002"]],
    )


class BatchDeleteResponse(BaseModel):
    """
    批量删除响应模型

    返回批量删除的结果统计。
    """

    total: int = Field(description="请求删除的总数")
    success_count: int = Field(description="成功删除的数量")
    fail_count: int = Field(description="删除失败的数量")
    results: List[dict] = Field(description="每条记录的删除结果")
