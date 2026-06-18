"""
教师任课分配业务逻辑 Service
"""

import re
from typing import Dict, Any, List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.core.security import hash_password
from src.core.constants import SUBJECTS
from src.models.teacher_assignment import TeacherAssignment
from src.models.student import Student
from src.repositories.teacher_assignment_repo import TeacherAssignmentRepository
from src.repositories.user_repo import UserRepository
from src.services.subject_leader_service import SUBJECT_EN_MAP


def parse_class_name(class_name: str) -> tuple:
    match = re.match(r"(\d{4})级(\d+)班", class_name)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 0


class TeacherAssignmentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TeacherAssignmentRepository(db)
        self.user_repo = UserRepository(db)

    def get_available_combinations(self) -> List[Dict[str, Any]]:
        """返回所有尚未分配教师的 (科目, 班级) 组合"""
        stmt = (
            select(Student.class_name, func.min(Student.enrollment_year).label("ey"))
            .group_by(Student.class_name)
            .order_by(Student.class_name)
        )
        class_rows = self.db.execute(stmt).all()

        assigned = {
            (t.subject, t.class_name)
            for t in self.repo.get_all_ordered()
        }

        result = []
        for class_name, enrollment_year in class_rows:
            _, class_number = parse_class_name(class_name)
            for subj in SUBJECTS:
                if (subj, class_name) not in assigned:
                    result.append({
                        "subject": subj,
                        "subject_en": SUBJECT_EN_MAP.get(subj, subj),
                        "class_name": class_name,
                        "enrollment_year": enrollment_year,
                        "class_number": class_number,
                    })
        return result

    @staticmethod
    def generate_username(subject_en: str, enrollment_year: int, class_number: int) -> str:
        """生成教师账号：{SubjectEn}{EnrollmentYear}{ClassNumber:03d}"""
        return f"{subject_en}{enrollment_year}{class_number:03d}"

    def add_assignment(
        self,
        subject: str,
        class_name: str,
        teacher_name: str,
    ) -> Dict[str, Any]:
        subject_en = SUBJECT_EN_MAP.get(subject)
        if not subject_en:
            raise ValueError(f"未知科目: {subject}")

        existing = self.repo.get_by_subject_class(subject, class_name)
        if existing:
            raise ValueError(
                f"{subject} 在 {class_name} 已有教师：{existing.teacher_name}"
            )

        enrollment_year, class_number = parse_class_name(class_name)
        username = self.generate_username(subject_en, enrollment_year, class_number)

        if self.user_repo.username_exists(username):
            raise ValueError(f"账号 {username} 已存在")

        user = self.user_repo.create({
            "username": username,
            "hashed_password": hash_password("123456"),
            "role": "teacher",
            "is_active": True,
            "need_change_password": True,
        })

        assignment = self.repo.create({
            "user_id": user.id,
            "subject": subject,
            "subject_en": subject_en,
            "class_name": class_name,
            "teacher_name": teacher_name,
        })

        return {
            "id": assignment.id,
            "subject": subject,
            "subject_en": subject_en,
            "class_name": class_name,
            "teacher_name": teacher_name,
            "username": username,
            "user_id": user.id,
        }

    def delete_assignment(self, assignment_id: int) -> bool:
        assignment = self.repo.get_by_id(assignment_id)
        if not assignment:
            raise ValueError("记录不存在")
        user_id = assignment.user_id
        self.repo.delete(assignment_id)
        self.user_repo.delete(user_id)
        return True

    def get_all_assignments(self) -> List[Dict[str, Any]]:
        assignments = self.repo.get_all_ordered()
        result = []
        for a in assignments:
            user = self.user_repo.get_by_id(a.user_id)
            result.append({
                "id": a.id,
                "subject": a.subject,
                "subject_en": a.subject_en,
                "class_name": a.class_name,
                "teacher_name": a.teacher_name,
                "username": user.username if user else None,
                "user_id": a.user_id,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            })
        return result

    def get_assignment_by_user_id(self, user_id: int) -> List[TeacherAssignment]:
        return self.repo.get_by_user(user_id)
