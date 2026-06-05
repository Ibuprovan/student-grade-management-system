"""
成绩数据访问 Repository

提供成绩相关的数据库操作，包括按学生、科目、考试类型查询等
"""

from typing import Optional, List

from sqlalchemy import select, and_
from sqlalchemy.orm import Session, joinedload

from src.models.grade import Grade
from src.models.student import Student
from src.repositories.base import BaseRepository


class GradeRepository(BaseRepository[Grade]):
    """
    成绩数据访问类

    继承 BaseRepository，提供成绩特有的查询方法

    Attributes:
        model: Grade 模型类
        db: 数据库会话
    """

    def __init__(self, db: Session):
        """
        初始化成绩 Repository

        Args:
            db: 数据库会话
        """
        super().__init__(Grade, db)

    def get_by_student(
        self,
        student_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Grade]:
        """
        根据学号查询该学生的所有成绩

        Args:
            student_id: 学号
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            List[Grade]: 成绩列表
        """
        stmt = (
            select(Grade)
            .where(Grade.student_id == student_id)
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_by_subject(
        self,
        subject: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Grade]:
        """
        根据科目查询成绩列表

        Args:
            subject: 科目名称
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            List[Grade]: 成绩列表
        """
        stmt = (
            select(Grade)
            .where(Grade.subject == subject)
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_by_student_and_subject(
        self,
        student_id: str,
        subject: str,
    ) -> List[Grade]:
        """
        根据学号和科目查询成绩

        Args:
            student_id: 学号
            subject: 科目名称

        Returns:
            List[Grade]: 成绩列表
        """
        stmt = select(Grade).where(
            and_(
                Grade.student_id == student_id,
                Grade.subject == subject,
            )
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_unique_grade(
        self,
        student_id: str,
        subject: str,
        exam_type: str,
    ) -> Optional[Grade]:
        """
        查询唯一成绩记录（同一学生、科目、考试类型）

        Args:
            student_id: 学号
            subject: 科目名称
            exam_type: 考试类型

        Returns:
            Optional[Grade]: 成绩实例，不存在则返回 None
        """
        stmt = select(Grade).where(
            and_(
                Grade.student_id == student_id,
                Grade.subject == subject,
                Grade.exam_type == exam_type,
            )
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def exists_unique_grade(
        self,
        student_id: str,
        subject: str,
        exam_type: str,
    ) -> bool:
        """
        检查唯一成绩记录是否存在

        Args:
            student_id: 学号
            subject: 科目名称
            exam_type: 考试类型

        Returns:
            bool: 存在返回 True，否则返回 False
        """
        return self.get_unique_grade(student_id, subject, exam_type) is not None

    def get_by_class_and_subject(
        self,
        class_name: str,
        subject: str,
        exam_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Grade]:
        """
        根据班级和科目查询成绩（带学生信息）

        Args:
            class_name: 班级名称
            subject: 科目名称
            exam_type: 考试类型（可选）
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            List[Grade]: 成绩列表（包含关联的学生信息）
        """
        stmt = (
            select(Grade)
            .join(Student)
            .where(
                and_(
                    Student.class_name == class_name,
                    Grade.subject == subject,
                )
            )
        )

        if exam_type:
            stmt = stmt.where(Grade.exam_type == exam_type)

        stmt = stmt.offset(skip).limit(limit)
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def count_by_class_and_subject(
        self,
        class_name: str,
        subject: str,
        exam_type: Optional[str] = None,
    ) -> int:
        """
        统计班级某科目的成绩数量

        Args:
            class_name: 班级名称
            subject: 科目名称
            exam_type: 考试类型（可选）

        Returns:
            int: 成绩数量
        """
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(Grade)
            .join(Student)
            .where(
                and_(
                    Student.class_name == class_name,
                    Grade.subject == subject,
                )
            )
        )

        if exam_type:
            stmt = stmt.where(Grade.exam_type == exam_type)

        result = self.db.execute(stmt)
        return result.scalar() or 0

    def get_grades_with_student_info(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[List] = None,
    ) -> List[Grade]:
        """
        查询成绩列表（包含学生信息）

        使用 joinedload 预加载学生信息，避免 N+1 查询问题。
        当过滤条件中包含 Student 模型的字段时，会自动添加 JOIN。

        Args:
            skip: 跳过的记录数
            limit: 返回的最大记录数
            filters: 额外的过滤条件

        Returns:
            List[Grade]: 成绩列表（包含关联的学生信息）
        """
        stmt = (
            select(Grade)
            .join(Student, Grade.student_id == Student.student_id)
            .options(joinedload(Grade.student))
            .offset(skip)
            .limit(limit)
        )

        if filters:
            for filter_condition in filters:
                stmt = stmt.where(filter_condition)

        result = self.db.execute(stmt)
        return list(result.scalars().unique().all())

    def count_with_student_filters(
        self,
        filters: Optional[List] = None,
    ) -> int:
        """
        统计成绩数量（支持关联 Student 表过滤）

        当过滤条件中包含 Student 模型的字段时，会自动添加 JOIN。

        Args:
            filters: 过滤条件列表

        Returns:
            int: 满足条件的成绩数量
        """
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(Grade)
            .join(Student, Grade.student_id == Student.student_id)
        )

        if filters:
            for filter_condition in filters:
                stmt = stmt.where(filter_condition)

        result = self.db.execute(stmt)
        return result.scalar() or 0
