"""
学生数据访问 Repository

提供学生相关的数据库操作，包括学号查询、班级查询、搜索等
"""

from typing import Optional, List

from sqlalchemy import select, func, distinct, or_
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
        class_name: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Student]:
        """
        搜索学生（按学号或姓名模糊匹配）

        支持在数据库层面进行分页和班级筛选，避免将所有记录加载到内存。

        Args:
            keyword: 搜索关键词（匹配学号或姓名）
            class_name: 班级筛选（可选）
            skip: 跳过的记录数（分页偏移量）
            limit: 返回的最大记录数

        Returns:
            List[Student]: 匹配的学生列表
        """
        stmt = self._build_search_stmt(keyword, class_name)
        stmt = stmt.offset(skip).limit(limit)
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def count_search(
        self,
        keyword: str,
        class_name: Optional[str] = None,
    ) -> int:
        """
        统计搜索结果总数

        与 search 方法使用相同的过滤条件，用于分页计算。
        通过数据库 COUNT 聚合函数实现，无需将记录加载到内存。

        Args:
            keyword: 搜索关键词（匹配学号或姓名）
            class_name: 班级筛选（可选）

        Returns:
            int: 满足条件的学生总数
        """
        search_pattern = f"%{keyword}%"
        stmt = (
            select(func.count())
            .select_from(Student)
            .where(
                or_(
                    Student.student_id.like(search_pattern),
                    Student.name.like(search_pattern),
                )
            )
        )
        if class_name:
            stmt = stmt.where(Student.class_name == class_name)

        result = self.db.execute(stmt)
        return result.scalar() or 0

    def _build_search_stmt(self, keyword: str, class_name: Optional[str] = None):
        """
        构建搜索查询语句（内部方法）

        将搜索条件构建逻辑抽取为内部方法，供 search 和 count_search 复用，
        避免重复编写过滤条件。

        Args:
            keyword: 搜索关键词
            class_name: 班级筛选（可选）

        Returns:
            SQLAlchemy Select 语句对象
        """
        search_pattern = f"%{keyword}%"
        stmt = select(Student).where(
            or_(
                Student.student_id.like(search_pattern),
                Student.name.like(search_pattern),
            )
        )
        if class_name:
            stmt = stmt.where(Student.class_name == class_name)
        return stmt

    def get_all_classes(self) -> List[str]:
        """
        获取所有去重的班级名称列表

        使用 SQL DISTINCT 从数据库层面去重，避免将所有记录加载到内存。
        返回结果按班级名称排序，确保接口返回顺序一致。

        Returns:
            List[str]: 去重后的班级名称列表（已排序）
        """
        stmt = (
            select(distinct(Student.class_name))
            .order_by(Student.class_name)
        )
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
