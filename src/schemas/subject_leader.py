"""
学科教研组组长 Pydantic 模式
"""

from typing import Optional
from pydantic import BaseModel, Field


class SubjectLeaderCreate(BaseModel):
    subject: str = Field(..., description="科目名称", examples=["语文"])
    leader_name: str = Field(..., min_length=2, max_length=20, description="组长姓名")


class SubjectLeaderOut(BaseModel):
    id: int
    subject: str
    subject_en: str
    leader_name: str
    username: Optional[str] = None
    user_id: Optional[int] = None
    created_at: Optional[str] = None
