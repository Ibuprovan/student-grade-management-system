"""
学科教研组组长数据访问 Repository
"""

from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.subject_leader import SubjectLeader
from src.repositories.base import BaseRepository


class SubjectLeaderRepository(BaseRepository[SubjectLeader]):
    def __init__(self, db: Session):
        super().__init__(SubjectLeader, db)

    def get_by_subject(self, subject: str) -> Optional[SubjectLeader]:
        stmt = select(SubjectLeader).where(SubjectLeader.subject == subject)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_user_id(self, user_id: int) -> Optional[SubjectLeader]:
        stmt = select(SubjectLeader).where(SubjectLeader.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all_ordered(self) -> List[SubjectLeader]:
        from src.core.constants import SUBJECTS
        order_map = {s: i for i, s in enumerate(SUBJECTS)}
        leaders = list(self.db.execute(select(SubjectLeader)).scalars().all())
        leaders.sort(key=lambda x: order_map.get(x.subject, 999))
        return leaders
