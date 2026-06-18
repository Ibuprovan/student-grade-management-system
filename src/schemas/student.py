"""
学生数据验证 Schema

定义学生相关的 Pydantic 模式，用于请求数据验证和响应数据序列化
"""

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.core.constants import (
    GENDERS,
    STUDENT_ID_PATTERN,
    NAME_MIN_LENGTH,
    NAME_MAX_LENGTH,
    CLASS_NAME_MIN_LENGTH,
    CLASS_NAME_MAX_LENGTH,
    ENROLLMENT_YEAR_MIN,
    ENROLLMENT_YEAR_MAX,
)


class StudentBase(BaseModel):
    """
    学生基础模式

    包含学生的基本字段定义和验证规则
    """

    student_id: str = Field(
        ...,
        min_length=8,
        max_length=8,
        description="学号（8位数字，格式：YYYY + 4位序号）",
        examples=["20260001"],
    )
    name: str = Field(
        ...,
        min_length=NAME_MIN_LENGTH,
        max_length=NAME_MAX_LENGTH,
        description="姓名",
        examples=["张三"],
    )
    gender: str = Field(
        ...,
        description="性别",
        examples=["男"],
    )
    class_name: str = Field(
        ...,
        min_length=CLASS_NAME_MIN_LENGTH,
        max_length=CLASS_NAME_MAX_LENGTH,
        description="班级",
        examples=["2026级1班"],
    )
    enrollment_year: int = Field(
        ...,
        ge=ENROLLMENT_YEAR_MIN,
        le=ENROLLMENT_YEAR_MAX,
        description="入学年份",
        examples=[2026],
    )

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, v: str) -> str:
        """
        验证学号格式

        学号必须是8位数字，格式为 YYYY + 4位序号（如：20260001）

        Args:
            v: 学号字符串

        Returns:
            str: 验证通过的学号

        Raises:
            ValueError: 学号格式不正确
        """
        if not re.match(STUDENT_ID_PATTERN, v):
            raise ValueError("学号格式错误，应为8位数字（如：20260001）")
        # 验证年份部分是否合理
        year = int(v[:4])
        if year < ENROLLMENT_YEAR_MIN or year > ENROLLMENT_YEAR_MAX:
            raise ValueError(f"学号年份部分应在{ENROLLMENT_YEAR_MIN}-{ENROLLMENT_YEAR_MAX}之间")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        """
        验证性别字段

        Args:
            v: 性别字符串

        Returns:
            str: 验证通过的性别

        Raises:
            ValueError: 性别值不在允许范围内
        """
        if v not in GENDERS:
            raise ValueError(f"性别只能是 {' 或 '.join(GENDERS)}")
        return v


class StudentCreate(StudentBase):
    """
    创建学生请求模式

    用于 POST /api/v1/students 接口的请求体验证
    """
    pass


class StudentUpdate(BaseModel):
    """
    更新学生请求模式

    用于 PUT /api/v1/students/{student_id} 接口的请求体验证
    所有字段都是可选的，只更新提供的字段
    """

    name: Optional[str] = Field(
        None,
        min_length=NAME_MIN_LENGTH,
        max_length=NAME_MAX_LENGTH,
        description="姓名",
    )
    gender: Optional[str] = Field(
        None,
        description="性别",
    )
    class_name: Optional[str] = Field(
        None,
        min_length=CLASS_NAME_MIN_LENGTH,
        max_length=CLASS_NAME_MAX_LENGTH,
        description="班级",
    )
    enrollment_year: Optional[int] = Field(
        None,
        ge=ENROLLMENT_YEAR_MIN,
        le=ENROLLMENT_YEAR_MAX,
        description="入学年份",
    )

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        """
        验证性别字段（允许为 None）

        Args:
            v: 性别字符串或 None

        Returns:
            Optional[str]: 验证通过的性别或 None

        Raises:
            ValueError: 性别值不在允许范围内
        """
        if v is not None and v not in GENDERS:
            raise ValueError(f"性别只能是 {' 或 '.join(GENDERS)}")
        return v


class StudentResponse(StudentBase):
    """
    学生响应模式

    用于 API 响应的数据序列化，包含创建和更新时间
    """

    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    model_config = ConfigDict(from_attributes=True)  # 支持从 ORM 对象创建
