"""
学科教研组组长 ORM 模型
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.user import User


class SubjectLeader(Base):
    __tablename__ = "subject_leaders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    subject: Mapped[str] = mapped_column(String(10), nullable=False, unique=True, index=True)
    subject_en: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    leader_name: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<SubjectLeader(subject='{self.subject}', leader='{self.leader_name}')>"
