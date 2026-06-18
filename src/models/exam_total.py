"""
学生考试总分 ORM 模型

定义 student_exam_totals 表，存储每个学生每次考试的总分
"""

from datetime import datetime, date, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    Integer,
    Float,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.student import Student


class StudentExamTotal(Base):
    """
    学生考试总分模型

    存储每个学生在每次考试中的总分（所有科目分数之和）

    Attributes:
        id: 主键
        student_id: 学号（外键）
        exam_type: 考试类型（期中、期末、月考、单元测试）
        exam_date: 考试日期
        total_score: 总分
        created_at: 创建时间
        updated_at: 更新时间

    唯一约束：同一学生、同一考试类型、同一考试日期只能有一条总分记录
    """

    __tablename__ = "student_exam_totals"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主键",
    )

    student_id: Mapped[str] = mapped_column(
        String(8),
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="学号",
    )

    exam_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="考试类型",
    )

    exam_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="考试日期",
    )

    total_score: Mapped[float] = mapped_column(
        Numeric(5, 1),
        nullable=False,
        comment="总分",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        comment="创建时间",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="更新时间",
    )

    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="exam_totals",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "exam_type",
            "exam_date",
            name="uq_student_exam_total",
        ),
        Index("idx_exam_totals_student", "student_id"),
        Index("idx_exam_totals_exam_type", "exam_type"),
        Index("idx_exam_totals_exam_date", "exam_date"),
    )

    def __repr__(self) -> str:
        return f"<StudentExamTotal(student_id='{self.student_id}', exam_type='{self.exam_type}', total={self.total_score})>"
