"""
班主任数据访问 Repository
"""

from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.class_teacher import ClassTeacher
from src.repositories.base import BaseRepository


class ClassTeacherRepository(BaseRepository[ClassTeacher]):
    """班主任数据访问类"""

    def __init__(self, db: Session):
        super().__init__(ClassTeacher, db)

    def get_by_class_name(self, class_name: str) -> Optional[ClassTeacher]:
        """根据班级名称查询班主任"""
        stmt = select(ClassTeacher).where(ClassTeacher.class_name == class_name)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_user_id(self, user_id: int) -> Optional[ClassTeacher]:
        """根据用户 ID 查询班主任"""
        stmt = select(ClassTeacher).where(ClassTeacher.user_id == user_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_enrollment_year_and_number(
        self, enrollment_year: int, class_number: int
    ) -> Optional[ClassTeacher]:
        """根据入学年份和班级序号查询班主任"""
        stmt = select(ClassTeacher).where(
            ClassTeacher.enrollment_year == enrollment_year,
            ClassTeacher.class_number == class_number,
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_all_ordered(self) -> List[ClassTeacher]:
        """获取所有班主任（按入学年份和班级序号排序）"""
        stmt = select(ClassTeacher).order_by(
            ClassTeacher.enrollment_year.desc(),
            ClassTeacher.class_number.asc(),
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
