"""
成绩信息 ORM 模型

定义 grades 表的 SQLAlchemy 模型，包含字段定义、外键、索引和唯一约束
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


class Grade(Base):
    """
    成绩信息模型

    对应数据库中的 grades 表，存储学生各科成绩

    Attributes:
        grade_id: 成绩ID（主键，自增）
        student_id: 学号（外键，关联 students 表）
        subject: 科目名称
        score: 分数，0-100，支持1位小数
        exam_type: 考试类型（期中、期末、月考、单元测试）
        exam_date: 考试日期
        created_at: 记录创建时间
        updated_at: 记录最后更新时间
        student: 关联的学生对象（多对一关系）

    唯一约束：
        同一学生、同一科目、同一考试类型只能有一条成绩记录
    """

    __tablename__ = "grades"

    # ==================== 字段定义 ====================

    # 主键：成绩ID（自增）
    grade_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="成绩ID",
    )

    # 外键：学号
    student_id: Mapped[str] = mapped_column(
        String(8),
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="学号",
    )

    # 科目：语文、数学、英语等
    subject: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="科目",
    )

    # 分数：0-100，支持1位小数
    score: Mapped[float] = mapped_column(
        Numeric(4, 1),
        nullable=False,
        comment="分数",
    )

    # 考试类型：期中、期末、月考、单元测试
    exam_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="考试类型",
    )

    # 考试日期
    exam_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="考试日期",
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

    # 成绩属于某个学生（多对一关系）
    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="grades",
        lazy="selectin",
    )

    # ==================== 约束和索引定义 ====================

    __table_args__ = (
        # 唯一约束：同一学生、同一科目、同一考试类型只能有一条记录
        UniqueConstraint(
            "student_id",
            "subject",
            "exam_type",
            name="uq_student_subject_exam",
        ),
        # 按学生ID查询的索引
        Index("idx_grades_student_id", "student_id"),
        # 按科目和考试类型查询的索引
        Index("idx_grades_subject_exam_type", "subject", "exam_type"),
        # 按考试日期查询的索引
        Index("idx_grades_exam_date", "exam_date"),
    )

    # ==================== 方法定义 ====================

    def __repr__(self) -> str:
        """对象表示字符串"""
        return (
            f"<Grade(student_id='{self.student_id}', "
            f"subject='{self.subject}', score={self.score})>"
        )

    def __str__(self) -> str:
        """可读字符串表示"""
        return f"{self.student_id} - {self.subject}: {self.score}"
