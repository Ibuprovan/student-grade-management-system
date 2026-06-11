"""
审计日志 Schema

定义审计日志相关的 Pydantic 模型，用于查询和响应
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AuditLogResponse(BaseModel):
    """
    审计日志响应模型

    用于 API 响应的数据序列化。
    """

    id: int = Field(description="日志 ID")
    user_id: int = Field(description="操作用户 ID")
    username: str = Field(description="操作用户名")
    action: str = Field(description="操作类型")
    resource_type: str = Field(description="资源类型")
    resource_id: Optional[str] = Field(None, description="资源标识符")
    details: Optional[str] = Field(None, description="操作详情（JSON）")
    ip_address: Optional[str] = Field(None, description="客户端 IP 地址")
    created_at: datetime = Field(description="操作时间")

    model_config = ConfigDict(from_attributes=True)
