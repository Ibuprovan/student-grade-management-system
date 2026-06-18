"""
班主任业务逻辑 Service

提供班主任管理的核心业务逻辑，包括：
- 添加班主任（自动创建账号）
- 删除班主任（自动删除账号）
- 查询班主任列表
- 查询可分配的班级列表
"""

import re
from typing import Dict, Any, List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.core.security import hash_password
from src.models.class_teacher import ClassTeacher
from src.models.student import Student
from src.repositories.class_teacher_repo import ClassTeacherRepository
from src.repositories.user_repo import UserRepository


class ClassTeacherService:
    """班主任业务逻辑类"""

    def __init__(self, db: Session):
        self.db = db
        self.class_teacher_repo = ClassTeacherRepository(db)
        self.user_repo = UserRepository(db)

    @staticmethod
    def parse_class_name(class_name: str) -> tuple:
        """
        从班级名称中解析入学年份和班级序号

        班级名称格式：2026级1班 → (2026, 1)

        Returns:
            (enrollment_year, class_number) 或 (0, 0) 解析失败
        """
        match = re.match(r"(\d{4})级(\d+)班", class_name)
        if match:
            return int(match.group(1)), int(match.group(2))
        return 0, 0

    def get_available_classes(self) -> List[Dict[str, Any]]:
        """
        获取可分配的班级列表（从学生表中去重查询）

        返回所有有学生的班级，以及每个班级的入学年份和班级序号。
        已有班主任的班级不返回。
        """
        stmt = (
            select(
                Student.class_name,
                func.min(Student.enrollment_year).label("enrollment_year"),
                func.count().label("student_count"),
            )
            .group_by(Student.class_name)
            .order_by(Student.class_name)
        )
        rows = self.db.execute(stmt).all()

        # 已有班主任的班级
        assigned = {
            ct.class_name
            for ct in self.class_teacher_repo.get_all_ordered()
        }

        result = []
        for class_name, enrollment_year, student_count in rows:
            if class_name in assigned:
                continue
            _, class_number = self.parse_class_name(class_name)
            result.append({
                "class_name": class_name,
                "enrollment_year": enrollment_year,
                "class_number": class_number,
                "student_count": student_count,
            })

        return result

    @staticmethod
    def generate_username(enrollment_year: int, class_number: int) -> str:
        """
        生成班主任账号

        规则：入学年份 + 3位班级号
        例：2026级1班 → 2026001
        """
        return f"{enrollment_year}{class_number:03d}"

    def add_class_teacher(
        self,
        class_name: str,
        enrollment_year: int,
        class_number: int,
        teacher_name: str,
    ) -> Dict[str, Any]:
        """
        添加班主任并自动创建账号

        Args:
            class_name: 班级名称（如 "2026级1班"）
            enrollment_year: 入学年份
            class_number: 班级序号
            teacher_name: 班主任姓名
        """
        existing = self.class_teacher_repo.get_by_class_name(class_name)
        if existing:
            raise ValueError(f"班级 {class_name} 已有班主任：{existing.teacher_name}")

        username = self.generate_username(enrollment_year, class_number)

        if self.user_repo.username_exists(username):
            raise ValueError(f"账号 {username} 已存在")

        user = self.user_repo.create({
            "username": username,
            "hashed_password": hash_password("123456"),
            "role": "class_teacher",
            "is_active": True,
            "need_change_password": True,
        })

        class_teacher = self.class_teacher_repo.create({
            "user_id": user.id,
            "class_name": class_name,
            "enrollment_year": enrollment_year,
            "class_number": class_number,
            "teacher_name": teacher_name,
        })

        return {
            "id": class_teacher.id,
            "class_name": class_name,
            "enrollment_year": enrollment_year,
            "class_number": class_number,
            "teacher_name": teacher_name,
            "username": username,
            "user_id": user.id,
        }

    def delete_class_teacher(self, class_teacher_id: int) -> bool:
        """删除班主任并同时删除其用户账号"""
        class_teacher = self.class_teacher_repo.get_by_id(class_teacher_id)
        if not class_teacher:
            raise ValueError("班主任记录不存在")

        user_id = class_teacher.user_id
        self.class_teacher_repo.delete(class_teacher_id)
        self.user_repo.delete(user_id)
        return True

    def get_all_class_teachers(self) -> List[Dict[str, Any]]:
        """获取所有班主任列表"""
        teachers = self.class_teacher_repo.get_all_ordered()
        result = []
        for ct in teachers:
            user = self.user_repo.get_by_id(ct.user_id)
            result.append({
                "id": ct.id,
                "class_name": ct.class_name,
                "enrollment_year": ct.enrollment_year,
                "class_number": ct.class_number,
                "teacher_name": ct.teacher_name,
                "username": user.username if user else None,
                "user_id": ct.user_id,
                "created_at": ct.created_at.isoformat() if ct.created_at else None,
            })
        return result

    def get_class_teacher_by_user_id(self, user_id: int) -> Optional[ClassTeacher]:
        """根据用户 ID 获取班主任信息"""
        return self.class_teacher_repo.get_by_user_id(user_id)
