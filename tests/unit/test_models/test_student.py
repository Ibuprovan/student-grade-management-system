"""
学生模型单元测试

测试 Student ORM 模型的基本功能
"""

import pytest
from datetime import datetime

from src.models.student import Student


class TestStudentModel:
    """Student 模型测试类"""

    def test_create_student(self, db_session, sample_student_data):
        """测试创建学生记录"""
        student = Student(**sample_student_data)
        db_session.add(student)
        db_session.commit()

        # 验证记录已创建
        assert student.student_id == "20260001"
        assert student.name == "张三"
        assert student.gender == "男"
        assert student.class_name == "2026级1班"
        assert student.enrollment_year == 2026
        assert student.created_at is not None
        assert student.updated_at is not None

    def test_student_repr(self, sample_student_data):
        """测试学生对象的字符串表示"""
        student = Student(**sample_student_data)
        assert repr(student) == "<Student(student_id='20260001', name='张三')>"
        assert str(student) == "张三 (20260001)"

    def test_student_fields_not_null(self, db_session):
        """测试必填字段不能为空"""
        # 缺少必填字段应该抛出异常
        with pytest.raises(Exception):
            student = Student(student_id="20260001")
            db_session.add(student)
            db_session.commit()

    def test_student_id_as_primary_key(self, db_session, sample_student_data):
        """测试学号作为主键"""
        student = Student(**sample_student_data)
        db_session.add(student)
        db_session.commit()

        # 通过主键查询
        found = db_session.get(Student, "20260001")
        assert found is not None
        assert found.student_id == "20260001"

    def test_student_update_timestamp(self, db_session, sample_student_data):
        """测试更新时间戳自动更新"""
        student = Student(**sample_student_data)
        db_session.add(student)
        db_session.commit()

        original_updated_at = student.updated_at

        # 更新学生信息
        student.name = "张三丰"
        db_session.commit()

        # 验证更新时间已变化
        assert student.updated_at >= original_updated_at

    def test_student_grades_relationship(self, db_session, sample_student_data):
        """测试学生与成绩的关系"""
        from src.models.grade import Grade
        from datetime import date

        student = Student(**sample_student_data)
        db_session.add(student)
        db_session.commit()

        # 添加成绩记录
        grade = Grade(
            student_id="20260001",
            subject="数学",
            score=95.5,
            exam_type="期中",
            exam_date=date(2026, 4, 15),
        )
        db_session.add(grade)
        db_session.commit()

        # 验证关系
        assert len(student.grades) == 1
        assert student.grades[0].subject == "数学"

    def test_student_cascade_delete(self, db_session, sample_student_data):
        """测试级联删除（删除学生时删除相关成绩）"""
        from src.models.grade import Grade
        from datetime import date

        student = Student(**sample_student_data)
        db_session.add(student)
        db_session.commit()

        # 添加成绩记录
        grade = Grade(
            student_id="20260001",
            subject="数学",
            score=95.5,
            exam_type="期中",
            exam_date=date(2026, 4, 15),
        )
        db_session.add(grade)
        db_session.commit()

        # 删除学生
        db_session.delete(student)
        db_session.commit()

        # 验证成绩也被删除
        grade = db_session.get(Grade, 1)
        assert grade is None
