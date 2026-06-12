"""
批量导入 API 路由

提供学生信息批量导入相关的 API 接口。
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional

from src.core.database import get_db
from src.core.exceptions import ValidationException
from src.services.import_service import ImportService
from src.services.audit_service import AuditService
from src.schemas.import_schema import (
    ImportResponse,
    ImportResult,
    ImportErrorDetail,
    PreviewResponse,
    PreviewResult,
    PreviewStudent,
    TemplateFormat
)
from src.api.auth import get_current_user
from src.models.user import User

router = APIRouter(prefix="/import", tags=["批量导入"])


@router.post("/students", response_model=ImportResponse, summary="批量导入学生")
async def import_students(
    file: UploadFile = File(..., description="学生信息文件（.xlsx 或 .csv）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    从 Excel/CSV 文件批量导入学生信息
    
    - **file**: 上传的文件，支持 .xlsx 和 .csv 格式
    - 文件大小限制：10MB
    - 单次导入上限：1000条记录
    
    **文件格式要求：**
    - 必须包含以下列：学号、姓名、性别、班级、入学年份
    - 学号：8位数字（YYYY + 4位序号）
    - 姓名：2-20个字符
    - 性别：男 或 女
    - 班级：2-20个字符
    - 入学年份：2000-2100之间的整数
    """
    # 验证文件类型
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    
    allowed_extensions = ['.xlsx', '.csv']
    file_ext = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件格式，请上传 {', '.join(allowed_extensions)} 文件"
        )
    
    # 验证文件大小（10MB）
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail="文件大小超过限制（最大 10MB）"
        )
    
    if len(file_content) == 0:
        raise HTTPException(status_code=400, detail="文件内容为空")
    
    try:
        import_service = ImportService(db)
        result = import_service.import_from_file(
            file_content=file_content,
            filename=file.filename,
            operator_id=current_user.id,
            operator_name=current_user.username
        )
        
        # 构造错误详情
        error_details = [
            ImportErrorDetail(
                row=err['row'],
                student_id=err.get('student_id'),
                field=err.get('field'),
                error=err['error'],
                value=err.get('value')
            )
            for err in result.get('errors', [])
        ]
        
        import_result = ImportResult(
            total_rows=result['total_rows'],
            success_count=result['success_count'],
            fail_count=result['fail_count'],
            errors=error_details
        )
        
        message = f"导入完成：成功 {result['success_count']} 条，失败 {result['fail_count']} 条"
        
        # 记录审计日志
        try:
            audit_service = AuditService(db)
            audit_service.log_operation(
                user_id=current_user.id,
                username=current_user.username,
                action="import",
                resource_type="student",
                resource_id=None,
                details={
                    "filename": file.filename,
                    "total_rows": result['total_rows'],
                    "success_count": result['success_count'],
                    "fail_count": result['fail_count']
                }
            )
        except Exception as e:
            # 审计日志记录失败不影响主业务
            pass
        
        return ImportResponse(
            success=True,
            data=import_result,
            message=message
        )
        
    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.post("/students/preview", response_model=PreviewResponse, summary="预览导入数据")
async def preview_import(
    file: UploadFile = File(..., description="学生信息文件（.xlsx 或 .csv）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    预览上传文件中的学生数据，不执行实际导入
    
    - **file**: 上传的文件，支持 .xlsx 和 .csv 格式
    - 返回文件中的数据预览和校验结果
    """
    # 验证文件类型
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    
    allowed_extensions = ['.xlsx', '.csv']
    file_ext = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件格式，请上传 {', '.join(allowed_extensions)} 文件"
        )
    
    # 验证文件大小（10MB）
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail="文件大小超过限制（最大 10MB）"
        )
    
    if len(file_content) == 0:
        raise HTTPException(status_code=400, detail="文件内容为空")
    
    try:
        import_service = ImportService(db)
        result = import_service.preview_file(
            file_content=file_content,
            filename=file.filename
        )
        
        # 构造预览数据
        preview_data = [
            PreviewStudent(
                row=item['row'],
                student_id=item['student_id'],
                name=item['name'],
                gender=item['gender'],
                class_name=item['class_name'],
                enrollment_year=item['enrollment_year'],
                status=item['status'],
                errors=item.get('errors')
            )
            for item in result.get('preview', [])
        ]
        
        # 构造错误详情
        error_details = [
            ImportErrorDetail(
                row=err['row'],
                student_id=err.get('student_id'),
                field=err.get('field'),
                error=err['error'],
                value=err.get('value')
            )
            for err in result.get('errors', [])
        ]
        
        preview_result = PreviewResult(
            total_rows=result['total_rows'],
            valid_rows=result['valid_rows'],
            invalid_rows=result['invalid_rows'],
            preview=preview_data,
            errors=error_details
        )
        
        return PreviewResponse(
            success=True,
            data=preview_result
        )
        
    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览失败: {str(e)}")


@router.get("/students/template", summary="下载导入模板")
async def download_template(
    format: TemplateFormat = Query(
        TemplateFormat.XLSX, 
        description="模板格式：xlsx 或 csv"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    下载学生信息导入模板
    
    - **format**: 模板格式，支持 xlsx 和 csv
    - 模板包含字段说明和示例数据
    """
    try:
        import_service = ImportService(db)
        template_content = import_service.generate_template(format=format)
        
        # 设置响应头
        if format == TemplateFormat.XLSX:
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = "student_import_template.xlsx"
        else:
            media_type = "text/csv; charset=utf-8"
            filename = "student_import_template.csv"
        
        return StreamingResponse(
            iter([template_content]),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模板生成失败: {str(e)}")
