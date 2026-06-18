"""
教师任课分配 Pydantic 验证模型
"""

from pydantic import BaseModel, Field


class TeacherAssignmentCreate(BaseModel):
    subject: str = Field(..., min_length=1, max_length=10, description="科目中文名")
    class_name: str = Field(..., min_length=1, max_length=20, description="班级名称")
    teacher_name: str = Field(..., min_length=1, max_length=20, description="教师姓名")
