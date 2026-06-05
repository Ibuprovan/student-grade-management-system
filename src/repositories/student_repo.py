"""
学生数据访问 Repository

提供学生相关的数据库操作，包括学号查询、班级查询等
"""

from typing import Optional, List

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from src.models.student import Student
from src.repositories.base import BaseRepository


class StudentRepository(BaseRepository[Student]):
    """
    学生数据访问类

    继承 BaseRepository，提供学生特有的查询方法

    Attributes:
        model: Student 模型类
        db: 数据库会话
    """

    def __init__(self, db: Session):
        """
        初始化学生 Repository

        Args:
            db: 数据库会话
        """
        super().__init__(Student, db)

    def get_by_student_id(self, student_id: str) -> Optional[Student]:
        """
        根据学号查询学生

        Args:
            student_id: 学号

        Returns:
            Optional[Student]: 学生实例，不存在则返回 None
        """
        stmt = select(Student).where(Student.student_id == student_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_class(
        self,
        class_name: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Student]:
        """
        根据班级查询学生列表

        Args:
            class_name: 班级名称
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            List[Student]: 学生列表
        """
        stmt = (
            select(Student)
            .where(Student.class_name == class_name)
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def count_by_class(self, class_name: str) -> int:
        """
        统计班级学生数量

        Args:
            class_name: 班级名称

        Returns:
            int: 班级学生数量
        """
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(Student)
            .where(Student.class_name == class_name)
        )
        result = self.db.execute(stmt)
        return result.scalar() or 0

    def search(
        self,
        keyword: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Student]:
        """
        搜索学生（按学号或姓名模糊匹配）

        Args:
            keyword: 搜索关键词
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            List[Student]: 匹配的学生列表
        """
        search_pattern = f"%{keyword}%"
        stmt = (
            select(Student)
            .where(
                or_(
                    Student.student_id.like(search_pattern),
                    Student.name.like(search_pattern),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_all_classes(self) -> List[str]:
        """
        获取所有班级名称列表

        Returns:
            List[str]: 去重后的班级名称列表
        """
        from sqlalchemy import distinct

        stmt = select(distinct(Student.class_name))
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def student_id_exists(self, student_id: str) -> bool:
        """
        检查学号是否已存在

        Args:
            student_id: 学号

        Returns:
            bool: 存在返回 True，否则返回 False
        """
        return self.get_by_student_id(student_id) is not None
