"""
教师任课分配 ORM 模型

每位教师负责一个科目的一个班级教学，账号规则：
用户名 = 学科英文名 + 班级编码（如 Chinese2026001, Math2026001, English2026003）
初始密码 123456，首次登录需修改密码
"""

from datetime import datetime, timezone

from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class TeacherAssignment(Base):
    __tablename__ = "teacher_assignments"
    __table_args__ = (
        UniqueConstraint("subject", "class_name", name="uq_teacher_subject_class"),
        UniqueConstraint("user_id", name="uq_teacher_assignment_user_id"),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, comment="主键 ID",
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True, comment="关联用户 ID",
    )
    subject: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="科目中文名（如 语文）",
    )
    subject_en: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="科目英文名（如 Chinese）",
    )
    class_name: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="班级名称（如 2026级1班）",
    )
    teacher_name: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="教师姓名",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), comment="创建时间",
    )

    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return (
            f"<TeacherAssignment(id={self.id}, subject='{self.subject}', "
            f"class_name='{self.class_name}', teacher_name='{self.teacher_name}')>"
        )
