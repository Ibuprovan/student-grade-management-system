"""
教师任课分配数据访问层
"""

from typing import Optional, List

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from src.core.database import SessionLocal
from src.models.teacher_assignment import TeacherAssignment


class TeacherAssignmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> TeacherAssignment:
        obj = TeacherAssignment(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, assignment_id: int) -> bool:
        obj = self.db.get(TeacherAssignment, assignment_id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

    def get_by_id(self, assignment_id: int) -> Optional[TeacherAssignment]:
        return self.db.get(TeacherAssignment, assignment_id)

    def get_by_user_id(self, user_id: int) -> Optional[TeacherAssignment]:
        stmt = select(TeacherAssignment).where(TeacherAssignment.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_subject_class(self, subject: str, class_name: str) -> Optional[TeacherAssignment]:
        stmt = select(TeacherAssignment).where(
            and_(
                TeacherAssignment.subject == subject,
                TeacherAssignment.class_name == class_name,
            )
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all_ordered(self) -> List[TeacherAssignment]:
        stmt = select(TeacherAssignment).order_by(
            TeacherAssignment.subject, TeacherAssignment.class_name,
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_user(self, user_id: int) -> List[TeacherAssignment]:
        stmt = select(TeacherAssignment).where(
            TeacherAssignment.user_id == user_id,
        ).order_by(TeacherAssignment.class_name)
        return list(self.db.execute(stmt).scalars().all())
