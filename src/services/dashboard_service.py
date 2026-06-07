"""
仪表盘业务逻辑 Service

提供仪表盘页面所需的汇总统计数据，包括：
- 学生总数
- 成绩记录总数
- 平均分
- 及格率
"""

from typing import Dict, Any

from sqlalchemy import func, select, case
from sqlalchemy.orm import Session

from src.models.grade import Grade
from src.models.student import Student
from src.repositories.grade_repo import GradeRepository
from src.repositories.student_repo import StudentRepository


class DashboardService:
    """
    仪表盘业务逻辑类

    职责：
    - 汇总仪表盘页面所需的统计数据
    - 协调 StudentRepository 和 GradeRepository 进行数据查询
    - 计算平均分和及格率

    Attributes:
        student_repo: StudentRepository 实例
        grade_repo: GradeRepository 实例
        db: 数据库会话
    """

    # 常量定义
    PASS_SCORE = 60.0

    def __init__(self, db: Session):
        """
        初始化 DashboardService

        Args:
            db: SQLAlchemy 数据库会话
        """
        self.student_repo = StudentRepository(db)
        self.grade_repo = GradeRepository(db)
        self.db = db

    def get_student_count(self) -> int:
        """
        获取学生总数

        Returns:
            int: 学生总数
        """
        return self.student_repo.count()

    def get_grade_count(self) -> int:
        """
        获取成绩记录总数

        Returns:
            int: 成绩记录总数
        """
        return self.grade_repo.count()

    def get_average_score(self) -> float:
        """
        获取所有成绩的平均分

        Returns:
            float: 平均分（保留2位小数）
        """
        stmt = select(func.avg(Grade.score))
        result = self.db.execute(stmt)
        average = result.scalar()
        return round(float(average), 2) if average else 0.0

    def get_pass_rate(self) -> float:
        """
        获取及格率（>=60分）

        Returns:
            float: 及格率（百分比，保留2位小数）
        """
        stmt = select(
            func.count(Grade.grade_id).label("total_count"),
            func.sum(case((Grade.score >= self.PASS_SCORE, 1), else_=0)).label("passed_count"),
        )
        result = self.db.execute(stmt)
        row = result.one()

        total_count = row[0] if row[0] else 0
        passed_count = int(row[1]) if row[1] else 0

        if total_count == 0:
            return 0.0

        return round((passed_count / total_count) * 100, 2)

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        获取仪表盘汇总统计数据

        一次性获取所有仪表盘所需的统计数据，包括：
        - 学生总数
        - 成绩记录总数
        - 平均分
        - 及格率

        Returns:
            Dict[str, Any]: 包含统计数据的字典
        """
        return {
            "total_students": self.get_student_count(),
            "total_grades": self.get_grade_count(),
            "average_score": self.get_average_score(),
            "pass_rate": self.get_pass_rate(),
        }
