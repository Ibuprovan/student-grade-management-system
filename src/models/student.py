"""
学生信息 ORM 模型

定义 students 表的 SQLAlchemy 模型，包含字段定义、索引和关系
"""

from datetime import datetime, timezone
from typing import List, TYPE_CHECKING

from sqlalchemy import String, Integer, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.grade import Grade
    from src.models.exam_total import StudentExamTotal


class Student(Base):
    """
    学生信息模型

    对应数据库中的 students 表，存储学生基本信息

    Attributes:
        student_id: 学号（主键），格式：YYYY + 4位序号（如：20260001）
        name: 学生姓名，2-20个字符
        gender: 性别，只能是"男"或"女"
        class_name: 班级名称，如"2026级1班"
        enrollment_year: 入学年份
        created_at: 记录创建时间
        updated_at: 记录最后更新时间
        grades: 关联的成绩记录列表（一对多关系）
    """

    __tablename__ = "students"

    # ==================== 字段定义 ====================

    # 主键：学号（格式：YYYY + 4位序号，如 20260001）
    student_id: Mapped[str] = mapped_column(
        String(8),
        primary_key=True,
        index=True,
        comment="学号",
    )

    # 姓名：2-20个字符
    name: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="姓名",
    )

    # 性别：男/女
    gender: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="性别",
    )

    # 班级：格式如 "2026级1班"
    class_name: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="班级",
    )

    # 入学年份
    enrollment_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="入学年份",
    )

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        comment="创建时间",
    )

    # 更新时间
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="更新时间",
    )

    # ==================== 关系定义 ====================

    # 一个学生有多条成绩记录（一对多关系）
    grades: Mapped[List["Grade"]] = relationship(
        "Grade",
        back_populates="student",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # 一个学生有多条总分记录（一对多关系）
    exam_totals: Mapped[List["StudentExamTotal"]] = relationship(
        "StudentExamTotal",
        back_populates="student",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ==================== 索引定义 ====================

    __table_args__ = (
        Index("idx_students_class_name", "class_name"),
        Index("idx_students_enrollment_year", "enrollment_year"),
    )

    # ==================== 方法定义 ====================

    def __repr__(self) -> str:
        """对象表示字符串"""
        return f"<Student(student_id='{self.student_id}', name='{self.name}')>"

    def __str__(self) -> str:
        """可读字符串表示"""
        return f"{self.name} ({self.student_id})"
