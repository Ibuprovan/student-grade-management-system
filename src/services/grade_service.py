"""
成绩业务逻辑 Service

实现成绩管理的核心业务逻辑，包括：
- 单条成绩录入（含学生存在性、重复性校验）
- 批量成绩录入（部分失败不影响成功的记录）
- 成绩修改
- 成绩删除
- 多维度成绩查询（按学生、班级、科目、组合条件）
- 成绩数据导出（CSV）
"""

import csv
import io
from datetime import date
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy.orm import Session

from src.core.exceptions import (
    StudentNotFoundException,
    DuplicateGradeException,
    ScoreOutOfRangeException,
    NotFoundException,
)
from src.models.grade import Grade
from src.models.student import Student
from src.models.exam_total import StudentExamTotal
from src.repositories.grade_repo import GradeRepository
from src.repositories.student_repo import StudentRepository
from src.repositories.exam_total_repo import ExamTotalRepository
from src.schemas.grade import (
    GradeCreate,
    GradeUpdate,
    GradeBatchCreate,
    GradeResponse,
)


class GradeService:
    """
    成绩业务逻辑类

    职责：
    - 处理成绩相关的业务逻辑
    - 协调 GradeRepository 和 StudentRepository 进行数据操作
    - 执行业务规则校验（学生存在性、成绩唯一性、分数范围）

    Attributes:
        grade_repo: GradeRepository 实例
        student_repo: StudentRepository 实例
    """

    def __init__(self, db: Session):
        """
        初始化 GradeService

        Args:
            db: SQLAlchemy 数据库会话
        """
        self.grade_repo = GradeRepository(db)
        self.student_repo = StudentRepository(db)
        self.exam_total_repo = ExamTotalRepository(db)
        self.db = db

    def create_grade(self, data: GradeCreate) -> Grade:
        """
        录入单条成绩

        业务流程：
        1. 检查学生是否存在
        2. 检查成绩记录是否已存在（学生+科目+考试类型）
        3. 验证分数范围（0-100）
        4. 创建成绩记录
        5. 返回创建的成绩对象

        Args:
            data: 成绩创建请求数据（已通过 Pydantic 验证）

        Returns:
            Grade: 创建的成绩 ORM 对象

        Raises:
            StudentNotFoundException: 学生不存在
            DuplicateGradeException: 成绩记录已存在（同一学生+科目+考试类型）
        """
        # 检查学生是否存在
        student = self.student_repo.get_by_student_id(data.student_id)
        if student is None:
            raise StudentNotFoundException(data.student_id)

        # 检查成绩是否已存在（唯一约束：学生+科目+考试类型）
        existing = self.grade_repo.get_unique_grade(
            data.student_id, data.subject, data.exam_type
        )
        if existing is not None:
            raise DuplicateGradeException(
                data.student_id, data.subject, data.exam_type
            )

        # 创建成绩记录
        grade_data = data.model_dump()
        grade = self.grade_repo.create(grade_data)
        return grade

    def save_exam_total(
        self,
        student_id: str,
        exam_type: str,
        exam_date: date,
        total_score: float,
    ) -> StudentExamTotal:
        """
        保存学生考试总分

        Args:
            student_id: 学号
            exam_type: 考试类型
            exam_date: 考试日期
            total_score: 总分

        Returns:
            StudentExamTotal: 保存的总分记录
        """
        return self.exam_total_repo.upsert(
            student_id=student_id,
            exam_type=exam_type,
            exam_date=exam_date,
            total_score=total_score,
        )

    def batch_create_grades(self, data: GradeBatchCreate) -> Dict[str, Any]:
        """
        批量录入成绩

        业务流程：
        1. 遍历每条成绩记录
        2. 对每条记录执行：检查学生存在性、检查重复、校验分数
        3. 统计成功/失败数量
        4. 批量插入成功的记录
        5. 返回批量处理结果

        Args:
            data: 批量创建成绩请求数据

        Returns:
            Dict[str, Any]: 批量处理结果，包含 total, success_count, fail_count, results
        """
        results = []
        success_grades = []

        for item in data.grades:
            try:
                # 检查学生是否存在
                student = self.student_repo.get_by_student_id(item.student_id)
                if student is None:
                    results.append({
                        "student_id": item.student_id,
                        "status": "fail",
                        "error": f"学生 '{item.student_id}' 不存在",
                    })
                    continue

                # 检查成绩是否已存在
                existing = self.grade_repo.get_unique_grade(
                    item.student_id, data.subject, data.exam_type
                )
                if existing is not None:
                    results.append({
                        "student_id": item.student_id,
                        "status": "fail",
                        "error": f"成绩已存在（{item.student_id}-{data.subject}-{data.exam_type}）",
                    })
                    continue

                # 准备成绩数据
                grade_data = {
                    "student_id": item.student_id,
                    "subject": data.subject,
                    "score": item.score,
                    "exam_type": data.exam_type,
                    "exam_date": data.exam_date,
                }
                success_grades.append(grade_data)
                results.append({
                    "student_id": item.student_id,
                    "status": "success",
                })

            except Exception as e:
                results.append({
                    "student_id": item.student_id,
                    "status": "fail",
                    "error": str(e),
                })

        # 批量插入成功的记录
        created_grades = []
        if success_grades:
            created_grades = self.grade_repo.bulk_create(success_grades)
            # 更新成功记录的 grade_id
            idx = 0
            for result in results:
                if result["status"] == "success" and idx < len(created_grades):
                    result["grade_id"] = created_grades[idx].grade_id
                    idx += 1

        success_count = sum(1 for r in results if r["status"] == "success")
        fail_count = sum(1 for r in results if r["status"] == "fail")

        return {
            "total": len(data.grades),
            "success_count": success_count,
            "fail_count": fail_count,
            "results": results,
        }

    def export_grades_csv(
        self,
        class_name: Optional[str] = None,
        subject: Optional[str] = None,
        exam_type: Optional[str] = None,
    ) -> str:
        """
        导出成绩数据为 CSV 格式

        支持按班级、科目、考试类型筛选，返回 CSV 格式的字符串。
        包含学生姓名和班级信息，便于数据分析。

        Args:
            class_name: 班级筛选（可选）
            subject: 科目筛选（可选）
            exam_type: 考试类型筛选（可选）

        Returns:
            str: CSV 格式的成绩数据字符串（UTF-8 BOM 编码，兼容 Excel）
        """
        # 构建过滤条件
        filters = []
        if class_name:
            filters.append(Student.class_name == class_name)
        if subject:
            filters.append(Grade.subject == subject)
        if exam_type:
            filters.append(Grade.exam_type == exam_type)

        # 查询成绩数据（包含学生信息）
        grades = self.grade_repo.get_grades_with_student_info(
            skip=0,
            limit=10000,  # 导出上限
            filters=filters if filters else None,
        )

        # 使用 StringIO 和 csv.writer 生成 CSV
        output = io.StringIO()
        # 写入 BOM 头，确保 Excel 正确识别 UTF-8 编码
        output.write('\ufeff')

        writer = csv.writer(output)
        # 写入表头
        writer.writerow([
            '学号', '姓名', '班级', '科目', '分数', '考试类型', '考试日期', '创建时间'
        ])

        # 写入数据行
        for grade in grades:
            student = grade.student
            writer.writerow([
                grade.student_id,
                student.name if student else '',
                student.class_name if student else '',
                grade.subject,
                grade.score,
                grade.exam_type,
                grade.exam_date.strftime('%Y-%m-%d') if grade.exam_date else '',
                grade.created_at.strftime('%Y-%m-%d %H:%M:%S') if grade.created_at else '',
            ])

        return output.getvalue()

    def get_grade_by_id(self, grade_id: int) -> Grade:
        """
        根据成绩ID查询成绩

        Args:
            grade_id: 成绩ID

        Returns:
            Grade: 成绩 ORM 对象

        Raises:
            NotFoundException: 成绩记录不存在
        """
        grade = self.grade_repo.get_by_id(grade_id)
        if grade is None:
            raise NotFoundException("成绩记录", str(grade_id))
        return grade

    def update_grade(self, grade_id: int, data: GradeUpdate) -> Grade:
        """
        修改成绩

        Args:
            grade_id: 成绩ID
            data: 成绩更新请求数据（只包含分数）

        Returns:
            Grade: 更新后的成绩 ORM 对象

        Raises:
            NotFoundException: 成绩记录不存在
        """
        # 检查成绩是否存在
        grade = self.grade_repo.get_by_id(grade_id)
        if grade is None:
            raise NotFoundException("成绩记录", str(grade_id))

        # 更新分数
        update_data = data.model_dump(exclude_unset=True)
        updated_grade = self.grade_repo.update(grade_id, update_data)
        return updated_grade

    def delete_grade(self, grade_id: int) -> bool:
        """
        删除成绩

        Args:
            grade_id: 成绩ID

        Returns:
            bool: 删除成功返回 True

        Raises:
            NotFoundException: 成绩记录不存在
        """
        # 检查成绩是否存在
        grade = self.grade_repo.get_by_id(grade_id)
        if grade is None:
            raise NotFoundException("成绩记录", str(grade_id))

        # 执行删除
        return self.grade_repo.delete(grade_id)

    def get_grades_by_student(
        self,
        student_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Grade]:
        """
        按学生查询成绩

        Args:
            student_id: 学号
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            List[Grade]: 该学生的所有成绩列表
        """
        return self.grade_repo.get_by_student(
            student_id=student_id,
            skip=skip,
            limit=limit,
        )

    def get_grades_by_class(
        self,
        class_name: str,
        subject: Optional[str] = None,
        exam_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Grade]:
        """
        按班级查询成绩

        Args:
            class_name: 班级名称
            subject: 科目筛选（可选）
            exam_type: 考试类型筛选（可选）
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            List[Grade]: 该班级的成绩列表
        """
        filters = [Student.class_name == class_name]

        if subject:
            filters.append(Grade.subject == subject)
        if exam_type:
            filters.append(Grade.exam_type == exam_type)

        return self.grade_repo.get_grades_with_student_info(
            skip=skip,
            limit=limit,
            filters=filters,
        )

    def count_grades_by_class(
        self,
        class_name: str,
        subject: Optional[str] = None,
        exam_type: Optional[str] = None,
    ) -> int:
        """
        统计班级成绩数量

        Args:
            class_name: 班级名称
            subject: 科目筛选（可选）
            exam_type: 考试类型筛选（可选）

        Returns:
            int: 成绩数量
        """
        filters = [Student.class_name == class_name]
        if subject:
            filters.append(Grade.subject == subject)
        if exam_type:
            filters.append(Grade.exam_type == exam_type)

        return self.grade_repo.count_with_student_filters(filters=filters)

    def get_grades_by_subject(
        self,
        subject: str,
        exam_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Grade]:
        """
        按科目查询成绩

        Args:
            subject: 科目名称
            exam_type: 考试类型筛选（可选）
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            List[Grade]: 该科目的成绩列表
        """
        filters = [Grade.subject == subject]
        if exam_type:
            filters.append(Grade.exam_type == exam_type)

        return self.grade_repo.get_grades_with_student_info(
            skip=skip,
            limit=limit,
            filters=filters,
        )

    def count_grades_by_subject(
        self,
        subject: str,
        exam_type: Optional[str] = None,
    ) -> int:
        """
        统计科目成绩数量

        Args:
            subject: 科目名称
            exam_type: 考试类型筛选（可选）

        Returns:
            int: 成绩数量
        """
        filters = [Grade.subject == subject]
        if exam_type:
            filters.append(Grade.exam_type == exam_type)
        return self.grade_repo.count(filters=filters)

    def search_grades(
        self,
        class_name: Optional[str] = None,
        subject: Optional[str] = None,
        exam_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Grade], int]:
        """
        组合条件查询成绩

        支持按班级、科目、考试类型进行组合筛选

        Args:
            class_name: 班级筛选（可选）
            subject: 科目筛选（可选）
            exam_type: 考试类型筛选（可选）
            page: 页码（从 1 开始）
            page_size: 每页数量

        Returns:
            Tuple[List[Grade], int]: (成绩列表, 总数)
        """
        skip = (page - 1) * page_size

        # 构建过滤条件
        filters = []
        if class_name:
            filters.append(Student.class_name == class_name)
        if subject:
            filters.append(Grade.subject == subject)
        if exam_type:
            filters.append(Grade.exam_type == exam_type)

        # 查询数据（包含学生信息）
        grades = self.grade_repo.get_grades_with_student_info(
            skip=skip,
            limit=page_size,
            filters=filters if filters else None,
        )

        # 统计总数（使用支持 Student 表过滤的计数方法）
        total = self.grade_repo.count_with_student_filters(
            filters=filters if filters else None
        )

        return grades, total
