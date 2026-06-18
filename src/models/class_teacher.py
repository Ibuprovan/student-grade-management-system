"""
班主任 ORM 模型

定义 class_teachers 表的 SQLAlchemy 模型，用于管理班主任与班级的对应关系。

规则：
- 每个班级最多一位班主任
- 班主任账号由管理员添加时自动创建（username = 入学年份 + 3位班级号，如 2026001）
- 初始密码 123456，首次登录需修改密码
"""

from datetime import datetime, timezone

from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class ClassTeacher(Base):
    """
    班主任模型

    对应数据库中的 class_teachers 表，存储班主任与班级的对应关系。

    Attributes:
        id: 主键
        user_id: 关联用户 ID（外键到 users 表）
        class_name: 班级名称（如 "2026级1班"）
        enrollment_year: 入学年份（如 2026）
        class_number: 班级序号（如 1、2、3）
        teacher_name: 班主任姓名
        created_at: 创建时间
    """

    __tablename__ = "class_teachers"
    __table_args__ = (
        UniqueConstraint("class_name", name="uq_class_teacher_class_name"),
        UniqueConstraint("user_id", name="uq_class_teacher_user_id"),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="主键 ID",
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        comment="关联用户 ID",
    )

    class_name: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        comment="班级名称（如 2026级1班）",
    )

    enrollment_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="入学年份（如 2026）",
    )

    class_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="班级序号（如 1、2、3）",
    )

    teacher_name: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="班主任姓名",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        comment="创建时间",
    )

    # 关系
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return (
            f"<ClassTeacher(id={self.id}, class_name='{self.class_name}', "
            f"teacher_name='{self.teacher_name}')>"
        )
