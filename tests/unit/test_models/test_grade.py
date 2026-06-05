"""
成绩模型单元测试

测试 Grade ORM 模型的基本功能
"""

import pytest
from datetime import date

from src.models.grade import Grade
from src.models.student import Student


class TestGradeModel:
    """Grade 模型测试类"""

    def test_create_grade(self, db_session, sample_student_data, sample_grade_data):
        """测试创建成绩记录"""
        # 先创建学生
        student = Student(**sample_student_data)
        db_session.add(student)
        db_session.commit()

        # 创建成绩
        grade = Grade(**sample_grade_data)
        db_session.add(grade)
        db_session.commit()

        # 验证记录已创建
        assert grade.grade_id is not None
        assert grade.student_id == "20260001"
        assert grade.subject == "数学"
        assert grade.score == 95.5
        assert grade.exam_type == "期中"
        assert grade.exam_date == date(2026, 4, 15)
        assert grade.created_at is not None

    def test_grade_repr(self, sample_grade_data):
        """测试成绩对象的字符串表示"""
        grade = Grade(**sample_grade_data)
        assert repr(grade) == "<Grade(student_id='20260001', subject='数学', score=95.5)>"
        assert str(grade) == "20260001 - 数学: 95.5"

    def test_grade_auto_increment_id(self, db_session, sample_student_data):
        """测试成绩ID自增"""
        # 创建学生
        student = Student(**sample_student_data)
        db_session.add(student)
        db_session.commit()

        # 创建多条成绩
        grade1 = Grade(
            student_id="20260001",
            subject="数学",
            score=95.5,
            exam_type="期中",
            exam_date=date(2026, 4, 15),
        )
        grade2 = Grade(
            student_id="20260001",
            subject="语文",
            score=88.0,
            exam_type="期中",
            exam_date=date(2026, 4, 15),
        )
        db_session.add_all([grade1, grade2])
        db_session.commit()

        # 验证ID自增
        assert grade1.grade_id == 1
        assert grade2.grade_id == 2

    def test_grade_unique_constraint(self, db_session, sample_student_data):
        """测试唯一约束（同一学生、科目、考试类型不能重复）"""
        from sqlalchemy.exc import IntegrityError

        # 创建学生
        student = Student(**sample_student_data)
        db_session.add(student)
        db_session.commit()

        # 创建第一条成绩
        grade1 = Grade(
            student_id="20260001",
            subject="数学",
            score=95.5,
            exam_type="期中",
            exam_date=date(2026, 4, 15),
        )
        db_session.add(grade1)
        db_session.commit()

        # 创建重复的成绩（相同学生、科目、考试类型）
        grade2 = Grade(
            student_id="20260001",
            subject="数学",
            score=90.0,
            exam_type="期中",
            exam_date=date(2026, 4, 20),
        )
        db_session.add(grade2)

        # 应该抛出完整性约束异常
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_grade_different_exam_types_allowed(self, db_session, sample_student_data):
        """测试不同考试类型可以共存"""
        # 创建学生
        student = Student(**sample_student_data)
        db_session.add(student)
        db_session.commit()

        # 同一学生、同一科目，不同考试类型
        grade1 = Grade(
            student_id="20260001",
            subject="数学",
            score=95.5,
            exam_type="期中",
            exam_date=date(2026, 4, 15),
        )
        grade2 = Grade(
            student_id="20260001",
            subject="数学",
            score=92.0,
            exam_type="期末",
            exam_date=date(2026, 6, 20),
        )
        db_session.add_all([grade1, grade2])
        db_session.commit()

        # 验证两条记录都存在
        assert grade1.grade_id is not None
        assert grade2.grade_id is not None

    def test_grade_student_relationship(self, db_session, sample_student_data, sample_grade_data):
        """测试成绩与学生的关系"""
        # 创建学生
        student = Student(**sample_student_data)
        db_session.add(student)
        db_session.commit()

        # 创建成绩
        grade = Grade(**sample_grade_data)
        db_session.add(grade)
        db_session.commit()

        # 验证关系
        assert grade.student is not None
        assert grade.student.student_id == "20260001"
        assert grade.student.name == "张三"

    def test_grade_foreign_key_constraint(self, db_session, sample_grade_data):
        """测试外键约束（不存在的学生无法录入成绩）"""
        from sqlalchemy.exc import IntegrityError

        # 不创建学生，直接创建成绩
        grade = Grade(**sample_grade_data)
        db_session.add(grade)

        # 应该抛出外键约束异常
        with pytest.raises(IntegrityError):
            db_session.commit()
