"""
学生考试总分数据访问层

提供 StudentExamTotal 模型的 CRUD 操作和查询方法
"""

from typing import Optional, List
from datetime import date

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from src.models.exam_total import StudentExamTotal
from src.repositories.base import BaseRepository


class ExamTotalRepository(BaseRepository[StudentExamTotal]):
    """
    学生考试总分仓库类

    提供总分记录的增删改查操作
    """

    def __init__(self, db: Session):
        super().__init__(db, StudentExamTotal)

    def get_unique(
        self,
        student_id: str,
        exam_type: str,
        exam_date: date,
    ) -> Optional[StudentExamTotal]:
        """
        获取唯一的总分记录（按学生+考试类型+考试日期）

        Args:
            student_id: 学号
            exam_type: 考试类型
            exam_date: 考试日期

        Returns:
            Optional[StudentExamTotal]: 总分记录，不存在返回 None
        """
        stmt = select(StudentExamTotal).where(
            and_(
                StudentExamTotal.student_id == student_id,
                StudentExamTotal.exam_type == exam_type,
                StudentExamTotal.exam_date == exam_date,
            )
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def upsert(
        self,
        student_id: str,
        exam_type: str,
        exam_date: date,
        total_score: float,
    ) -> StudentExamTotal:
        """
        插入或更新总分记录

        Args:
            student_id: 学号
            exam_type: 考试类型
            exam_date: 考试日期
            total_score: 总分

        Returns:
            StudentExamTotal: 创建或更新的记录
        """
        existing = self.get_unique(student_id, exam_type, exam_date)
        if existing:
            existing.total_score = total_score
            self.db.flush()
            return existing
        else:
            record = StudentExamTotal(
                student_id=student_id,
                exam_type=exam_type,
                exam_date=exam_date,
                total_score=total_score,
            )
            self.db.add(record)
            self.db.flush()
            return record

    def get_by_exam_type(
        self,
        exam_type: str,
        class_name: Optional[str] = None,
    ) -> List[StudentExamTotal]:
        """
        按考试类型查询总分记录

        Args:
            exam_type: 考试类型
            class_name: 班级名称（可选）

        Returns:
            List[StudentExamTotal]: 总分记录列表
        """
        from src.models.student import Student

        stmt = (
            select(StudentExamTotal)
            .join(Student, StudentExamTotal.student_id == Student.student_id)
            .where(StudentExamTotal.exam_type == exam_type)
        )
        if class_name:
            stmt = stmt.where(Student.class_name == class_name)

        return list(self.db.execute(stmt).scalars().all())

    def get_by_student(
        self,
        student_id: str,
        exam_type: Optional[str] = None,
    ) -> List[StudentExamTotal]:
        """
        按学生查询总分记录

        Args:
            student_id: 学号
            exam_type: 考试类型（可选）

        Returns:
            List[StudentExamTotal]: 总分记录列表
        """
        stmt = select(StudentExamTotal).where(
            StudentExamTotal.student_id == student_id
        )
        if exam_type:
            stmt = stmt.where(StudentExamTotal.exam_type == exam_type)

        return list(self.db.execute(stmt).scalars().all())
