"""
GradeService 单元测试

测试成绩业务逻辑层的所有功能，包括：
- 单条成绩录入（含学生存在性、重复性校验）
- 批量成绩录入（部分失败不影响成功记录）
- 成绩查询（单条/按学生/按班级/按科目/组合查询）
- 成绩修改
- 成绩删除
"""

from datetime import date

import pytest

from src.core.exceptions import (
    StudentNotFoundException,
    DuplicateGradeException,
    NotFoundException,
)
from src.models.student import Student
from src.models.grade import Grade
from src.schemas.grade import (
    GradeCreate,
    GradeUpdate,
    GradeBatchCreate,
    GradeBatchItem,
)
from src.schemas.student import StudentCreate
from src.services.grade_service import GradeService
from src.services.student_service import StudentService


class TestGradeService:
    """GradeService 测试类"""

    def _create_student(self, db_session, student_data: dict) -> Student:
        """辅助方法：创建学生"""
        service = StudentService(db_session)
        return service.create_student(StudentCreate(**student_data))

    def _create_grade(self, db_session, grade_data: dict) -> Grade:
        """辅助方法：创建成绩"""
        service = GradeService(db_session)
        return service.create_grade(GradeCreate(**grade_data))

    # ==================== 单条成绩录入测试 ====================

    def test_create_grade_success(self, db_session, sample_student_data, sample_grade_data):
        """测试成功录入成绩"""
        # 先创建学生
        self._create_student(db_session, sample_student_data)

        # 录入成绩
        service = GradeService(db_session)
        data = GradeCreate(**sample_grade_data)
        grade = service.create_grade(data)

        assert grade.student_id == "20260001"
        assert grade.subject == "数学"
        assert grade.score == 95.5
        assert grade.exam_type == "期中"
        assert grade.exam_date == date(2026, 4, 15)

    def test_create_grade_student_not_found(self, db_session, sample_grade_data):
        """测试录入成绩时学生不存在"""
        service = GradeService(db_session)
        data = GradeCreate(**sample_grade_data)

        with pytest.raises(StudentNotFoundException) as exc_info:
            service.create_grade(data)

        assert "20260001" in str(exc_info.value)

    def test_create_grade_duplicate(self, db_session, sample_student_data, sample_grade_data):
        """测试录入重复成绩（同一学生+科目+考试类型）"""
        # 先创建学生
        self._create_student(db_session, sample_student_data)

        # 第一次录入成绩
        service = GradeService(db_session)
        data = GradeCreate(**sample_grade_data)
        service.create_grade(data)

        # 尝试重复录入
        with pytest.raises(DuplicateGradeException) as exc_info:
            service.create_grade(data)

        assert "20260001-数学-期中" in str(exc_info.value)

    def test_create_grade_different_exam_type(
        self, db_session, sample_student_data, sample_grade_data
    ):
        """测试同一学生同一科目不同考试类型可以录入"""
        # 先创建学生
        self._create_student(db_session, sample_student_data)

        service = GradeService(db_session)

        # 录入期中成绩
        data1 = GradeCreate(**sample_grade_data)
        grade1 = service.create_grade(data1)
        assert grade1.exam_type == "期中"

        # 录入期末成绩（不同考试类型）
        grade_data2 = sample_grade_data.copy()
        grade_data2["exam_type"] = "期末"
        data2 = GradeCreate(**grade_data2)
        grade2 = service.create_grade(data2)
        assert grade2.exam_type == "期末"

    # ==================== 批量成绩录入测试 ====================

    def test_batch_create_grades_success(
        self, db_session, sample_students, sample_grade_data
    ):
        """测试批量录入成绩成功"""
        # 先创建多个学生
        for student_data in sample_students:
            self._create_student(db_session, student_data)

        # 批量录入成绩
        service = GradeService(db_session)
        data = GradeBatchCreate(
            subject="数学",
            exam_type="期中",
            exam_date=date(2026, 4, 15),
            grades=[
                GradeBatchItem(student_id="20260001", score=95.5),
                GradeBatchItem(student_id="20260002", score=88.0),
                GradeBatchItem(student_id="20260003", score=72.5),
            ],
        )

        result = service.batch_create_grades(data)

        assert result["total"] == 3
        assert result["success_count"] == 3
        assert result["fail_count"] == 0
        assert len(result["results"]) == 3

        # 验证每条记录都有 grade_id
        for r in result["results"]:
            assert r["status"] == "success"
            assert "grade_id" in r

    def test_batch_create_grades_partial_failure(
        self, db_session, sample_students
    ):
        """测试批量录入成绩部分失败"""
        # 只创建部分学生
        self._create_student(db_session, sample_students[0])
        self._create_student(db_session, sample_students[1])
        # 不创建第三个学生

        service = GradeService(db_session)
        data = GradeBatchCreate(
            subject="数学",
            exam_type="期中",
            exam_date=date(2026, 4, 15),
            grades=[
                GradeBatchItem(student_id="20260001", score=95.5),
                GradeBatchItem(student_id="20260002", score=88.0),
                GradeBatchItem(student_id="20260003", score=72.5),  # 不存在的学生
            ],
        )

        result = service.batch_create_grades(data)

        assert result["total"] == 3
        assert result["success_count"] == 2
        assert result["fail_count"] == 1

        # 验证失败的记录
        failed = [r for r in result["results"] if r["status"] == "fail"]
        assert len(failed) == 1
        assert failed[0]["student_id"] == "20260003"
        assert "不存在" in failed[0]["error"]

    def test_batch_create_grades_with_duplicate(
        self, db_session, sample_students
    ):
        """测试批量录入成绩时包含重复记录"""
        # 创建所有学生
        for student_data in sample_students:
            self._create_student(db_session, student_data)

        service = GradeService(db_session)

        # 先录入一条成绩
        service.create_grade(GradeCreate(
            student_id="20260001",
            subject="数学",
            score=90.0,
            exam_type="期中",
            exam_date=date(2026, 4, 15),
        ))

        # 批量录入（包含已存在的记录）
        data = GradeBatchCreate(
            subject="数学",
            exam_type="期中",
            exam_date=date(2026, 4, 15),
            grades=[
                GradeBatchItem(student_id="20260001", score=95.5),  # 已存在
                GradeBatchItem(student_id="20260002", score=88.0),
                GradeBatchItem(student_id="20260003", score=72.5),
            ],
        )

        result = service.batch_create_grades(data)

        assert result["total"] == 3
        assert result["success_count"] == 2
        assert result["fail_count"] == 1

        # 验证失败的记录
        failed = [r for r in result["results"] if r["status"] == "fail"]
        assert failed[0]["student_id"] == "20260001"
        assert "已存在" in failed[0]["error"]

    # ==================== 成绩查询测试 ====================

    def test_get_grade_by_id(self, db_session, sample_student_data, sample_grade_data):
        """测试根据成绩ID查询成绩"""
        self._create_student(db_session, sample_student_data)

        service = GradeService(db_session)
        grade = service.create_grade(GradeCreate(**sample_grade_data))

        # 查询成绩
        found = service.get_grade_by_id(grade.grade_id)

        assert found is not None
        assert found.grade_id == grade.grade_id
        assert found.student_id == "20260001"
        assert found.subject == "数学"

    def test_get_grade_by_id_not_found(self, db_session):
        """测试查询不存在的成绩"""
        service = GradeService(db_session)

        with pytest.raises(NotFoundException):
            service.get_grade_by_id(99999)

    def test_get_grades_by_student(
        self, db_session, sample_student_data, sample_grades
    ):
        """测试按学生查询成绩"""
        self._create_student(db_session, sample_student_data)

        service = GradeService(db_session)

        # 录入多条成绩
        for grade_data in sample_grades:
            if grade_data["student_id"] == "20260001":
                service.create_grade(GradeCreate(**grade_data))

        # 查询该学生的成绩
        grades = service.get_grades_by_student("20260001")

        assert len(grades) == 2  # 数学和语文
        for grade in grades:
            assert grade.student_id == "20260001"

    def test_get_grades_by_class(
        self, db_session, sample_students, sample_grades
    ):
        """测试按班级查询成绩"""
        # 创建学生
        for student_data in sample_students:
            self._create_student(db_session, student_data)

        service = GradeService(db_session)

        # 录入成绩
        for grade_data in sample_grades:
            service.create_grade(GradeCreate(**grade_data))

        # 按班级查询
        grades = service.get_grades_by_class("三年一班")

        # 三年一班有 3 条成绩：20260001-数学, 20260001-语文, 20260002-数学
        assert len(grades) == 3
        for grade in grades:
            assert grade.student.class_name == "三年一班"

    def test_get_grades_by_class_with_subject_filter(
        self, db_session, sample_students, sample_grades
    ):
        """测试按班级和科目筛选查询成绩"""
        # 创建学生
        for student_data in sample_students:
            self._create_student(db_session, student_data)

        service = GradeService(db_session)

        # 录入成绩
        for grade_data in sample_grades:
            service.create_grade(GradeCreate(**grade_data))

        # 按班级和科目查询
        grades = service.get_grades_by_class("三年一班", subject="数学")

        assert len(grades) == 2  # 20260001-数学, 20260002-数学

    def test_get_grades_by_subject(
        self, db_session, sample_students, sample_grades
    ):
        """测试按科目查询成绩"""
        # 创建学生
        for student_data in sample_students:
            self._create_student(db_session, student_data)

        service = GradeService(db_session)

        # 录入成绩
        for grade_data in sample_grades:
            service.create_grade(GradeCreate(**grade_data))

        # 按科目查询
        grades = service.get_grades_by_subject("数学")

        assert len(grades) == 2  # 20260001-数学, 20260002-数学
        for grade in grades:
            assert grade.subject == "数学"

    def test_search_grades(
        self, db_session, sample_students, sample_grades
    ):
        """测试组合条件查询成绩"""
        # 创建学生
        for student_data in sample_students:
            self._create_student(db_session, student_data)

        service = GradeService(db_session)

        # 录入成绩
        for grade_data in sample_grades:
            service.create_grade(GradeCreate(**grade_data))

        # 组合查询
        grades, total = service.search_grades(
            class_name="三年一班",
            subject="数学",
        )

        assert total == 2
        assert len(grades) == 2

    def test_search_grades_pagination(
        self, db_session, sample_students, sample_grades
    ):
        """测试组合条件查询分页"""
        # 创建学生
        for student_data in sample_students:
            self._create_student(db_session, student_data)

        service = GradeService(db_session)

        # 录入成绩
        for grade_data in sample_grades:
            service.create_grade(GradeCreate(**grade_data))

        # 第一页
        grades, total = service.search_grades(
            subject="数学",
            page=1,
            page_size=1,
        )

        assert total == 2
        assert len(grades) == 1

        # 第二页
        grades, total = service.search_grades(
            subject="数学",
            page=2,
            page_size=1,
        )

        assert total == 2
        assert len(grades) == 1

    # ==================== 成绩修改测试 ====================

    def test_update_grade_success(
        self, db_session, sample_student_data, sample_grade_data
    ):
        """测试修改成绩成功"""
        self._create_student(db_session, sample_student_data)

        service = GradeService(db_session)
        grade = service.create_grade(GradeCreate(**sample_grade_data))

        # 修改成绩
        update_data = GradeUpdate(score=98.0)
        updated = service.update_grade(grade.grade_id, update_data)

        assert updated.score == 98.0
        assert updated.grade_id == grade.grade_id

    def test_update_grade_not_found(self, db_session):
        """测试修改不存在的成绩"""
        service = GradeService(db_session)

        update_data = GradeUpdate(score=98.0)
        with pytest.raises(NotFoundException):
            service.update_grade(99999, update_data)

    # ==================== 成绩删除测试 ====================

    def test_delete_grade_success(
        self, db_session, sample_student_data, sample_grade_data
    ):
        """测试删除成绩成功"""
        self._create_student(db_session, sample_student_data)

        service = GradeService(db_session)
        grade = service.create_grade(GradeCreate(**sample_grade_data))

        # 删除成绩
        result = service.delete_grade(grade.grade_id)
        assert result is True

        # 验证成绩已被删除
        with pytest.raises(NotFoundException):
            service.get_grade_by_id(grade.grade_id)

    def test_delete_grade_not_found(self, db_session):
        """测试删除不存在的成绩"""
        service = GradeService(db_session)

        with pytest.raises(NotFoundException):
            service.delete_grade(99999)

    # ==================== 边界条件测试 ====================

    def test_create_grade_score_boundary_min(
        self, db_session, sample_student_data
    ):
        """测试录入最低分数（0分）"""
        self._create_student(db_session, sample_student_data)

        service = GradeService(db_session)
        grade_data = {
            "student_id": "20260001",
            "subject": "数学",
            "score": 0.0,
            "exam_type": "期中",
            "exam_date": date(2026, 4, 15),
        }
        grade = service.create_grade(GradeCreate(**grade_data))

        assert grade.score == 0.0

    def test_create_grade_score_boundary_max(
        self, db_session, sample_student_data
    ):
        """测试录入最高分数（100分）"""
        self._create_student(db_session, sample_student_data)

        service = GradeService(db_session)
        grade_data = {
            "student_id": "20260001",
            "subject": "数学",
            "score": 100.0,
            "exam_type": "期中",
            "exam_date": date(2026, 4, 15),
        }
        grade = service.create_grade(GradeCreate(**grade_data))

        assert grade.score == 100.0

    def test_count_grades_by_class(
        self, db_session, sample_students, sample_grades
    ):
        """测试统计班级成绩数量"""
        # 创建学生
        for student_data in sample_students:
            self._create_student(db_session, student_data)

        service = GradeService(db_session)

        # 录入成绩
        for grade_data in sample_grades:
            service.create_grade(GradeCreate(**grade_data))

        # 统计班级成绩数量
        # 三年一班有 3 条成绩：20260001-数学, 20260001-语文, 20260002-数学
        count = service.count_grades_by_class("三年一班")

        assert count == 3

    def test_count_grades_by_subject(
        self, db_session, sample_students, sample_grades
    ):
        """测试统计科目成绩数量"""
        # 创建学生
        for student_data in sample_students:
            self._create_student(db_session, student_data)

        service = GradeService(db_session)

        # 录入成绩
        for grade_data in sample_grades:
            service.create_grade(GradeCreate(**grade_data))

        # 统计科目成绩数量
        count = service.count_grades_by_subject("数学")

        assert count == 2
