"""
StudentService 单元测试

测试学生业务逻辑层的所有功能，包括：
- 学生创建（含学号唯一性校验）
- 学生查询（单个/列表）
- 学生更新
- 学生删除
- 学生搜索（含分页）
"""

import pytest
from unittest.mock import MagicMock, patch

from src.core.exceptions import (
    StudentNotFoundException,
    DuplicateException,
)
from src.models.student import Student
from src.schemas.student import StudentCreate, StudentUpdate
from src.services.student_service import StudentService


class TestStudentService:
    """StudentService 测试类"""

    def _create_mock_student(self, **kwargs) -> Student:
        """辅助方法：创建模拟学生对象"""
        defaults = {
            "student_id": "20260001",
            "name": "张三",
            "gender": "男",
            "class_name": "三年一班",
            "enrollment_year": 2026,
        }
        defaults.update(kwargs)
        student = MagicMock(spec=Student)
        for key, value in defaults.items():
            setattr(student, key, value)
        return student

    def test_create_student_success(self, db_session, sample_student_data):
        """测试成功创建学生"""
        service = StudentService(db_session)
        data = StudentCreate(**sample_student_data)

        student = service.create_student(data)

        assert student.student_id == "20260001"
        assert student.name == "张三"
        assert student.gender == "男"
        assert student.class_name == "三年一班"
        assert student.enrollment_year == 2026

    def test_create_student_duplicate_id(self, db_session, sample_student_data):
        """测试创建学生时学号重复"""
        service = StudentService(db_session)
        data = StudentCreate(**sample_student_data)

        # 先创建一个学生
        service.create_student(data)

        # 尝试创建相同学号的学生，应该抛出异常
        with pytest.raises(DuplicateException) as exc_info:
            service.create_student(data)

        assert "学号" in str(exc_info.value)
        assert "20260001" in str(exc_info.value)

    def test_get_student_by_id_success(self, db_session, sample_student_data):
        """测试根据学号查询学生成功"""
        service = StudentService(db_session)
        data = StudentCreate(**sample_student_data)

        # 先创建学生
        service.create_student(data)

        # 查询学生
        student = service.get_student_by_id("20260001")

        assert student is not None
        assert student.student_id == "20260001"
        assert student.name == "张三"

    def test_get_student_by_id_not_found(self, db_session):
        """测试查询不存在的学生"""
        service = StudentService(db_session)

        with pytest.raises(StudentNotFoundException) as exc_info:
            service.get_student_by_id("99999999")

        assert "99999999" in str(exc_info.value)

    def test_get_student_list(self, db_session, sample_students):
        """测试获取学生列表"""
        service = StudentService(db_session)

        # 创建多个学生
        for data in sample_students:
            service.create_student(StudentCreate(**data))

        # 获取列表
        students, total = service.get_student_list(page=1, page_size=10)

        assert len(students) == 3
        assert total == 3

    def test_get_student_list_with_class_filter(self, db_session, sample_students):
        """测试按班级筛选学生列表"""
        service = StudentService(db_session)

        # 创建多个学生
        for data in sample_students:
            service.create_student(StudentCreate(**data))

        # 按班级筛选
        students, total = service.get_student_list(
            page=1, page_size=10, class_name="三年一班"
        )

        assert len(students) == 2
        assert total == 2

    def test_get_student_list_pagination(self, db_session, sample_students):
        """测试学生列表分页"""
        service = StudentService(db_session)

        # 创建多个学生
        for data in sample_students:
            service.create_student(StudentCreate(**data))

        # 第一页
        students, total = service.get_student_list(page=1, page_size=2)
        assert len(students) == 2
        assert total == 3

        # 第二页
        students, total = service.get_student_list(page=2, page_size=2)
        assert len(students) == 1
        assert total == 3

    def test_update_student_success(self, db_session, sample_student_data):
        """测试更新学生信息成功"""
        service = StudentService(db_session)
        create_data = StudentCreate(**sample_student_data)
        service.create_student(create_data)

        # 更新学生信息
        update_data = StudentUpdate(name="张三丰")
        updated_student = service.update_student("20260001", update_data)

        assert updated_student.name == "张三丰"
        assert updated_student.student_id == "20260001"

    def test_update_student_not_found(self, db_session):
        """测试更新不存在的学生"""
        service = StudentService(db_session)

        update_data = StudentUpdate(name="张三丰")
        with pytest.raises(StudentNotFoundException):
            service.update_student("99999999", update_data)

    def test_update_student_no_changes(self, db_session, sample_student_data):
        """测试更新学生但没有实际更改"""
        service = StudentService(db_session)
        create_data = StudentCreate(**sample_student_data)
        service.create_student(create_data)

        # 空更新
        update_data = StudentUpdate()
        updated_student = service.update_student("20260001", update_data)

        assert updated_student.name == "张三"

    def test_delete_student_success(self, db_session, sample_student_data):
        """测试删除学生成功"""
        service = StudentService(db_session)
        data = StudentCreate(**sample_student_data)
        service.create_student(data)

        # 删除学生
        result = service.delete_student("20260001")
        assert result is True

        # 验证学生已被删除
        with pytest.raises(StudentNotFoundException):
            service.get_student_by_id("20260001")

    def test_delete_student_not_found(self, db_session):
        """测试删除不存在的学生"""
        service = StudentService(db_session)

        with pytest.raises(StudentNotFoundException):
            service.delete_student("99999999")

    def test_search_students_by_name(self, db_session, sample_students):
        """测试按姓名搜索学生"""
        service = StudentService(db_session)

        # 创建多个学生
        for data in sample_students:
            service.create_student(StudentCreate(**data))

        # 搜索
        students, total = service.search_students(keyword="张")

        assert len(students) == 1
        assert students[0].name == "张三"

    def test_search_students_by_student_id(self, db_session, sample_students):
        """测试按学号搜索学生"""
        service = StudentService(db_session)

        # 创建多个学生
        for data in sample_students:
            service.create_student(StudentCreate(**data))

        # 搜索
        students, total = service.search_students(keyword="20260001")

        assert len(students) == 1
        assert students[0].student_id == "20260001"

    def test_search_students_with_class_filter(self, db_session, sample_students):
        """测试搜索学生时按班级筛选"""
        service = StudentService(db_session)

        # 创建多个学生
        for data in sample_students:
            service.create_student(StudentCreate(**data))

        # 搜索并按班级筛选
        students, total = service.search_students(
            keyword="2026", class_name="三年一班"
        )

        assert len(students) == 2

    def test_search_students_no_results(self, db_session, sample_students):
        """测试搜索学生无结果"""
        service = StudentService(db_session)

        # 创建多个学生
        for data in sample_students:
            service.create_student(StudentCreate(**data))

        # 搜索不存在的关键词
        students, total = service.search_students(keyword="赵六")

        assert len(students) == 0

    def test_student_exists_true(self, db_session, sample_student_data):
        """测试检查学生存在"""
        service = StudentService(db_session)
        data = StudentCreate(**sample_student_data)
        service.create_student(data)

        assert service.student_exists("20260001") is True

    def test_student_exists_false(self, db_session):
        """测试检查学生不存在"""
        service = StudentService(db_session)

        assert service.student_exists("99999999") is False
