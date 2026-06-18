"""
班主任管理 Schema
"""

from typing import Optional

from pydantic import BaseModel, Field


class ClassTeacherCreate(BaseModel):
    """创建班主任请求模型"""

    class_name: str = Field(
        ...,
        description="班级名称（必须与学生表中的班级名称一致）",
        examples=["2026级1班"],
    )
    enrollment_year: int = Field(
        ...,
        ge=2000,
        le=2100,
        description="入学年份（用于生成账号）",
        examples=[2026],
    )
    class_number: int = Field(
        ...,
        ge=1,
        le=99,
        description="班级序号（用于生成账号）",
        examples=[1],
    )
    teacher_name: str = Field(
        ...,
        min_length=2,
        max_length=20,
        description="班主任姓名",
        examples=["张老师"],
    )


class ClassTeacherResponse(BaseModel):
    """班主任响应模型"""

    id: int = Field(description="班主任记录 ID")
    class_name: str = Field(description="班级名称")
    enrollment_year: int = Field(description="入学年份")
    class_number: int = Field(description="班级序号")
    teacher_name: str = Field(description="班主任姓名")
    username: Optional[str] = Field(None, description="登录账号")
    user_id: Optional[int] = Field(None, description="关联用户 ID")
    created_at: Optional[str] = Field(None, description="创建时间")
