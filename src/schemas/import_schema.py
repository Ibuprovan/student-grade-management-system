"""
导入功能相关的 Pydantic 模式定义
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ImportStatus(str, Enum):
    """导入状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ImportErrorDetail(BaseModel):
    """导入错误详情"""
    row: int = Field(..., description="错误行号")
    student_id: Optional[str] = Field(None, description="学号")
    field: Optional[str] = Field(None, description="错误字段")
    error: str = Field(..., description="错误信息")
    value: Optional[str] = Field(None, description="错误值")


class ImportResult(BaseModel):
    """导入结果"""
    total_rows: int = Field(..., description="总行数")
    success_count: int = Field(..., description="成功数量")
    fail_count: int = Field(..., description="失败数量")
    errors: List[ImportErrorDetail] = Field(default_factory=list, description="错误详情列表")


class ImportResponse(BaseModel):
    """导入响应"""
    success: bool = Field(True, description="是否成功")
    data: ImportResult = Field(..., description="导入结果")
    message: str = Field(..., description="响应消息")


class PreviewStudent(BaseModel):
    """预览学生数据"""
    row: int = Field(..., description="行号")
    student_id: str = Field(..., description="学号")
    name: str = Field(..., description="姓名")
    gender: str = Field(..., description="性别")
    class_name: str = Field(..., description="班级")
    enrollment_year: int = Field(..., description="入学年份")
    status: str = Field(..., description="状态：valid/invalid")
    errors: Optional[List[str]] = Field(None, description="错误信息列表")


class PreviewResult(BaseModel):
    """预览结果"""
    total_rows: int = Field(..., description="总行数")
    valid_rows: int = Field(..., description="有效行数")
    invalid_rows: int = Field(..., description="无效行数")
    preview: List[PreviewStudent] = Field(default_factory=list, description="预览数据")
    errors: List[ImportErrorDetail] = Field(default_factory=list, description="错误详情列表")


class PreviewResponse(BaseModel):
    """预览响应"""
    success: bool = Field(True, description="是否成功")
    data: PreviewResult = Field(..., description="预览结果")
    message: Optional[str] = Field(None, description="响应消息")


class TemplateFormat(str, Enum):
    """模板格式枚举"""
    XLSX = "xlsx"
    CSV = "csv"


class ImportLogBase(BaseModel):
    """导入日志基础模式"""
    filename: str = Field(..., description="文件名")
    file_type: str = Field(..., description="文件类型")
    total_rows: int = Field(..., description="总行数")
    success_count: int = Field(0, description="成功数量")
    fail_count: int = Field(0, description="失败数量")
    status: ImportStatus = Field(ImportStatus.PENDING, description="导入状态")
    error_details: Optional[str] = Field(None, description="错误详情JSON")
    operator_id: Optional[int] = Field(None, description="操作用户ID")
    operator_name: Optional[str] = Field(None, description="操作用户名")


class ImportLogCreate(ImportLogBase):
    """创建导入日志请求"""
    pass


class ImportLogResponse(ImportLogBase):
    """导入日志响应"""
    id: int = Field(..., description="日志ID")
    created_at: str = Field(..., description="创建时间")
    completed_at: Optional[str] = Field(None, description="完成时间")

    class Config:
        from_attributes = True
