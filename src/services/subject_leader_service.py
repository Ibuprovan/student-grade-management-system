"""
学科教研组组长业务逻辑 Service
"""

from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session

from src.core.security import hash_password
from src.models.subject_leader import SubjectLeader
from src.repositories.subject_leader_repo import SubjectLeaderRepository
from src.repositories.user_repo import UserRepository


# 科目英文名映射
SUBJECT_EN_MAP: Dict[str, str] = {
    "语文": "Chinese",
    "数学": "Math",
    "英语": "English",
    "物理": "Physics",
    "化学": "Chemistry",
    "生物": "Biology",
    "政治": "Politics",
    "历史": "History",
    "地理": "Geography",
}


class SubjectLeaderService:
    def __init__(self, db: Session):
        self.db = db
        self.leader_repo = SubjectLeaderRepository(db)
        self.user_repo = UserRepository(db)

    def get_available_subjects(self) -> List[Dict[str, Any]]:
        """返回尚未分配组长的科目列表"""
        from src.core.constants import SUBJECTS

        assigned = {sl.subject for sl in self.leader_repo.get_all_ordered()}
        result = []
        for subj in SUBJECTS:
            if subj not in assigned:
                result.append({
                    "subject": subj,
                    "subject_en": SUBJECT_EN_MAP.get(subj, subj),
                })
        return result

    def add_subject_leader(
        self, subject: str, leader_name: str
    ) -> Dict[str, Any]:
        subject_en = SUBJECT_EN_MAP.get(subject)
        if not subject_en:
            raise ValueError(f"未知科目: {subject}")

        existing = self.leader_repo.get_by_subject(subject)
        if existing:
            raise ValueError(f"科目 {subject} 已有组长: {existing.leader_name}")

        username = subject_en.lower()
        if self.user_repo.username_exists(username):
            raise ValueError(f"账号 {username} 已存在")

        user = self.user_repo.create({
            "username": username,
            "hashed_password": hash_password("123456"),
            "role": "subject_leader",
            "is_active": True,
            "need_change_password": True,
        })

        leader = self.leader_repo.create({
            "user_id": user.id,
            "subject": subject,
            "subject_en": subject_en,
            "leader_name": leader_name,
        })

        return {
            "id": leader.id,
            "subject": subject,
            "subject_en": subject_en,
            "leader_name": leader_name,
            "username": username,
            "user_id": user.id,
        }

    def delete_subject_leader(self, leader_id: int) -> bool:
        leader = self.leader_repo.get_by_id(leader_id)
        if not leader:
            raise ValueError("组长记录不存在")
        user_id = leader.user_id
        self.leader_repo.delete(leader_id)
        self.user_repo.delete(user_id)
        return True

    def get_all_leaders(self) -> List[Dict[str, Any]]:
        leaders = self.leader_repo.get_all_ordered()
        result = []
        for sl in leaders:
            user = self.user_repo.get_by_id(sl.user_id)
            result.append({
                "id": sl.id,
                "subject": sl.subject,
                "subject_en": sl.subject_en,
                "leader_name": sl.leader_name,
                "username": user.username if user else None,
                "user_id": sl.user_id,
                "created_at": sl.created_at.isoformat() if sl.created_at else None,
            })
        return result

    def get_leader_by_user_id(self, user_id: int) -> Optional[SubjectLeader]:
        return self.leader_repo.get_by_user_id(user_id)
