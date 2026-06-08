"""
成绩数据验证 Schema

定义成绩相关的 Pydantic 模式，用于请求数据验证和响应数据序列化
"""

from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.core.constants import (
    SUBJECTS,
    EXAM_TYPES,
    SCORE_MIN,
    SCORE_MAX,
)


def _validate_score_precision(v: float) -> float:
    """
    验证分数精度和范围（公共验证函数）

    分数最多支持 1 位小数，且必须在 SCORE_MIN ~ SCORE_MAX 之间。
    此函数供 GradeBase、GradeBatchItem、GradeUpdate 共同复用，
    避免在多个 Schema 类中重复相同的验证逻辑。

    Args:
        v: 分数值

    Returns:
        float: 四舍五入到 1 位小数后的分数

    Raises:
        ValueError: 小数位数超过 1 位，或分数超出允许范围
    """
    # 检查小数位数
    score_str = str(v)
    if "." in score_str:
        decimal_places = len(score_str.split(".")[1])
        if decimal_places > 1:
            raise ValueError("分数最多支持1位小数")

    # 检查范围
    if v < SCORE_MIN or v > SCORE_MAX:
        raise ValueError(f"分数必须在{SCORE_MIN}-{SCORE_MAX}之间")

    return round(v, 1)


class GradeBase(BaseModel):
    """
    成绩基础模式

    包含成绩的基本字段定义和验证规则
    """

    student_id: str = Field(
        ...,
        min_length=8,
        max_length=8,
        description="学号",
        examples=["20260001"],
    )
    subject: str = Field(
        ...,
        description="科目",
        examples=["数学"],
    )
    score: float = Field(
        ...,
        ge=SCORE_MIN,
        le=SCORE_MAX,
        description="分数（0-100，支持1位小数）",
        examples=[95.5],
    )
    exam_type: str = Field(
        ...,
        description="考试类型",
        examples=["期中"],
    )
    exam_date: date = Field(
        ...,
        description="考试日期",
        examples=["2026-04-15"],
    )

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v: str) -> str:
        """
        验证科目名称

        Args:
            v: 科目名称

        Returns:
            str: 验证通过的科目名称

        Raises:
            ValueError: 科目不在允许列表中
        """
        if v not in SUBJECTS:
            raise ValueError(f"科目必须是以下之一：{', '.join(SUBJECTS)}")
        return v

    @field_validator("exam_type")
    @classmethod
    def validate_exam_type(cls, v: str) -> str:
        """
        验证考试类型

        Args:
            v: 考试类型

        Returns:
            str: 验证通过的考试类型

        Raises:
            ValueError: 考试类型不在允许列表中
        """
        if v not in EXAM_TYPES:
            raise ValueError(f"考试类型必须是以下之一：{', '.join(EXAM_TYPES)}")
        return v

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        """
        验证分数精度

        分数最多支持1位小数

        Args:
            v: 分数值

        Returns:
            float: 验证通过的分数

        Raises:
            ValueError: 分数小数位数超过1位
        """
        return _validate_score_precision(v)


class GradeCreate(GradeBase):
    """
    创建成绩请求模式

    用于 POST /api/v1/grades 接口的请求体验证
    """
    pass


class GradeBatchItem(BaseModel):
    """
    批量录入单项

    用于批量录入成绩时的单个学生分数
    """

    student_id: str = Field(
        ...,
        min_length=8,
        max_length=8,
        description="学号",
        examples=["20260001"],
    )
    score: float = Field(
        ...,
        ge=SCORE_MIN,
        le=SCORE_MAX,
        description="分数",
        examples=[95.5],
    )

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        """
        验证分数精度

        Args:
            v: 分数值

        Returns:
            float: 验证通过的分数

        Raises:
            ValueError: 分数小数位数超过1位
        """
        return _validate_score_precision(v)


class GradeBatchCreate(BaseModel):
    """
    批量创建成绩请求模式

    用于 POST /api/v1/grades/batch 接口的请求体验证
    批量录入时，所有成绩共享相同的科目、考试类型和考试日期
    """

    subject: str = Field(
        ...,
        description="科目（所有成绩同一科目）",
        examples=["数学"],
    )
    exam_type: str = Field(
        ...,
        description="考试类型",
        examples=["期中"],
    )
    exam_date: date = Field(
        ...,
        description="考试日期",
        examples=["2026-04-15"],
    )
    grades: List[GradeBatchItem] = Field(
        ...,
        min_length=1,
        description="成绩列表",
    )

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v: str) -> str:
        """验证科目名称"""
        if v not in SUBJECTS:
            raise ValueError(f"科目必须是以下之一：{', '.join(SUBJECTS)}")
        return v

    @field_validator("exam_type")
    @classmethod
    def validate_exam_type(cls, v: str) -> str:
        """验证考试类型"""
        if v not in EXAM_TYPES:
            raise ValueError(f"考试类型必须是以下之一：{', '.join(EXAM_TYPES)}")
        return v


class GradeUpdate(BaseModel):
    """
    更新成绩请求模式

    用于 PUT /api/v1/grades/{grade_id} 接口的请求体验证
    只能更新分数
    """

    score: float = Field(
        ...,
        ge=SCORE_MIN,
        le=SCORE_MAX,
        description="分数（0-100，支持1位小数）",
        examples=[92.0],
    )

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        """
        验证分数精度

        Args:
            v: 分数值

        Returns:
            float: 验证通过的分数

        Raises:
            ValueError: 分数小数位数超过1位
        """
        return _validate_score_precision(v)


class GradeResponse(GradeBase):
    """
    成绩响应模式

    用于 API 响应的数据序列化
    包含关联的学生信息（可选）
    """

    grade_id: int = Field(description="成绩ID")
    student_name: Optional[str] = Field(None, description="学生姓名")
    class_name: Optional[str] = Field(None, description="班级名称")
    created_at: datetime = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)  # 支持从 ORM 对象创建
