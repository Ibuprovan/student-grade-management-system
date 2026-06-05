"""
Repository 单元测试

测试 StudentRepository 和 GradeRepository 的功能
"""

import pytest
from datetime import date

from src.models.student import Student
from src.models.grade import Grade
from src.repositories.student_repo import StudentRepository
from src.repositories.grade_repo import GradeRepository


class TestStudentRepository:
    """StudentRepository 测试类"""

    def test_create_student(self, db_session, sample_student_data):
        """测试创建学生"""
        repo = StudentRepository(db_session)
        student = repo.create(sample_student_data)

        assert student.student_id == "20260001"
        assert student.name == "张三"

    def test_get_by_student_id(self, db_session, sample_student_data):
        """测试根据学号查询"""
        repo = StudentRepository(db_session)
        repo.create(sample_student_data)

        student = repo.get_by_student_id("20260001")
        assert student is not None
        assert student.name == "张三"

    def test_get_by_student_id_not_found(self, db_session):
        """测试查询不存在的学号"""
        repo = StudentRepository(db_session)

        student = repo.get_by_student_id("99999999")
        assert student is None

    def test_get_by_class(self, db_session, sample_students):
        """测试根据班级查询"""
        repo = StudentRepository(db_session)
        for data in sample_students:
            repo.create(data)

        students = repo.get_by_class("三年一班")
        assert len(students) == 2

    def test_count_by_class(self, db_session, sample_students):
        """测试统计班级学生数量"""
        repo = StudentRepository(db_session)
        for data in sample_students:
            repo.create(data)

        count = repo.count_by_class("三年一班")
        assert count == 2

    def test_search_by_name(self, db_session, sample_students):
        """测试按姓名搜索"""
        repo = StudentRepository(db_session)
        for data in sample_students:
            repo.create(data)

        results = repo.search("张")
        assert len(results) == 1
        assert results[0].name == "张三"

    def test_search_by_student_id(self, db_session, sample_students):
        """测试按学号搜索"""
        repo = StudentRepository(db_session)
        for data in sample_students:
            repo.create(data)

        results = repo.search("20260001")
        assert len(results) == 1
        assert results[0].student_id == "20260001"

    def test_get_all_classes(self, db_session, sample_students):
        """测试获取所有班级"""
        repo = StudentRepository(db_session)
        for data in sample_students:
            repo.create(data)

        classes = repo.get_all_classes()
        assert len(classes) == 2
        assert "三年一班" in classes
        assert "三年二班" in classes

    def test_student_id_exists(self, db_session, sample_student_data):
        """测试检查学号是否存在"""
        repo = StudentRepository(db_session)
        repo.create(sample_student_data)

        assert repo.student_id_exists("20260001") is True
        assert repo.student_id_exists("99999999") is False

    def test_update_student(self, db_session, sample_student_data):
        """测试更新学生信息"""
        repo = StudentRepository(db_session)
        repo.create(sample_student_data)

        updated = repo.update("20260001", {"name": "张三丰"})
        assert updated is not None
        assert updated.name == "张三丰"

    def test_delete_student(self, db_session, sample_student_data):
        """测试删除学生"""
        repo = StudentRepository(db_session)
        repo.create(sample_student_data)

        result = repo.delete("20260001")
        assert result is True

        student = repo.get_by_student_id("20260001")
        assert student is None


class TestGradeRepository:
    """GradeRepository 测试类"""

    def _create_student(self, db_session):
        """辅助方法：创建测试学生"""
        student = Student(
            student_id="20260001",
            name="张三",
            gender="男",
            class_name="三年一班",
            enrollment_year=2026,
        )
        db_session.add(student)
        db_session.commit()
        return student

    def test_create_grade(self, db_session, sample_grade_data):
        """测试创建成绩"""
        self._create_student(db_session)

        repo = GradeRepository(db_session)
        grade = repo.create(sample_grade_data)

        assert grade.grade_id is not None
        assert grade.student_id == "20260001"
        assert grade.score == 95.5

    def test_get_by_student(self, db_session):
        """测试根据学号查询成绩"""
        self._create_student(db_session)
        repo = GradeRepository(db_session)

        # 创建多条成绩
        repo.create({
            "student_id": "20260001",
            "subject": "数学",
            "score": 95.5,
            "exam_type": "期中",
            "exam_date": date(2026, 4, 15),
        })
        repo.create({
            "student_id": "20260001",
            "subject": "语文",
            "score": 88.0,
            "exam_type": "期中",
            "exam_date": date(2026, 4, 15),
        })

        grades = repo.get_by_student("20260001")
        assert len(grades) == 2

    def test_get_by_subject(self, db_session):
        """测试根据科目查询成绩"""
        self._create_student(db_session)
        repo = GradeRepository(db_session)

        repo.create({
            "student_id": "20260001",
            "subject": "数学",
            "score": 95.5,
            "exam_type": "期中",
            "exam_date": date(2026, 4, 15),
        })

        grades = repo.get_by_subject("数学")
        assert len(grades) == 1

    def test_get_unique_grade(self, db_session):
        """测试查询唯一成绩记录"""
        self._create_student(db_session)
        repo = GradeRepository(db_session)

        repo.create({
            "student_id": "20260001",
            "subject": "数学",
            "score": 95.5,
            "exam_type": "期中",
            "exam_date": date(2026, 4, 15),
        })

        grade = repo.get_unique_grade("20260001", "数学", "期中")
        assert grade is not None
        assert grade.score == 95.5

    def test_exists_unique_grade(self, db_session):
        """测试检查唯一成绩是否存在"""
        self._create_student(db_session)
        repo = GradeRepository(db_session)

        repo.create({
            "student_id": "20260001",
            "subject": "数学",
            "score": 95.5,
            "exam_type": "期中",
            "exam_date": date(2026, 4, 15),
        })

        assert repo.exists_unique_grade("20260001", "数学", "期中") is True
        assert repo.exists_unique_grade("20260001", "数学", "期末") is False

    def test_update_grade(self, db_session):
        """测试更新成绩"""
        self._create_student(db_session)
        repo = GradeRepository(db_session)

        grade = repo.create({
            "student_id": "20260001",
            "subject": "数学",
            "score": 95.5,
            "exam_type": "期中",
            "exam_date": date(2026, 4, 15),
        })

        updated = repo.update(grade.grade_id, {"score": 92.0})
        assert updated is not None
        assert updated.score == 92.0

    def test_delete_grade(self, db_session):
        """测试删除成绩"""
        self._create_student(db_session)
        repo = GradeRepository(db_session)

        grade = repo.create({
            "student_id": "20260001",
            "subject": "数学",
            "score": 95.5,
            "exam_type": "期中",
            "exam_date": date(2026, 4, 15),
        })

        result = repo.delete(grade.grade_id)
        assert result is True

    def test_bulk_create(self, db_session, sample_students, sample_grades):
        """测试批量创建成绩"""
        student_repo = StudentRepository(db_session)
        for data in sample_students:
            student_repo.create(data)

        grade_repo = GradeRepository(db_session)
        grades = grade_repo.bulk_create(sample_grades)

        assert len(grades) == 3
        for grade in grades:
            assert grade.grade_id is not None
