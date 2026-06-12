"""
批量导入 API 路由

提供学生信息和成绩批量导入相关的 API 接口。
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

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
    TemplateFormat,
    GradeImportResponse,
    GradeImportResult,
    GradeImportItem
)
from src.api.auth import get_current_user
from src.models.user import User

router = APIRouter(prefix="/api/v1/import", tags=["批量导入"])


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


# ==================== 成绩导入相关接口 ====================

@router.post("/grades", response_model=GradeImportResponse, summary="批量导入成绩")
async def import_grades(
    file: UploadFile = File(..., description="成绩信息文件（.xlsx 或 .csv）"),
    exam_type: str = Form(..., description="考试类型（期中、期末、月考、单元测试）"),
    exam_date: str = Form(..., description="考试日期（YYYY-MM-DD）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    从 Excel/CSV 文件批量导入成绩信息
    
    - **file**: 上传的文件，支持 .xlsx 和 .csv 格式
    - **exam_type**: 考试类型
    - **exam_date**: 考试日期
    - 文件大小限制：10MB
    - 单次导入上限：5000条记录
    
    **文件格式要求：**
    - 必须包含以下列：学号、科目、分数
    - 可选列：考试类型、考试日期（如文件中包含则优先使用文件中的值）
    - 学号：必须是已存在的学生
    - 科目：如数学、语文、英语等
    - 分数：0-100之间的数字
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
    
    # 验证考试类型
    valid_exam_types = ['期中', '期末', '月考', '单元测试']
    if exam_type not in valid_exam_types:
        raise HTTPException(
            status_code=400,
            detail=f"考试类型无效，有效值: {', '.join(valid_exam_types)}"
        )
    
    # 验证日期格式
    try:
        from datetime import datetime
        datetime.strptime(exam_date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，应为 YYYY-MM-DD")
    
    try:
        import_service = ImportService(db)
        result = import_service.import_grades_from_file(
            file_content=file_content,
            filename=file.filename,
            exam_type=exam_type,
            exam_date=exam_date,
            operator_id=current_user.id,
            operator_name=current_user.username
        )
        
        # 构造成功和失败项
        success_items = [
            GradeImportItem(
                row=item['row'],
                student_id=item['student_id'],
                name=item.get('name'),
                subject=item['subject'],
                score=item['score']
            )
            for item in result.get('success_items', [])
        ]
        
        failed_items = [
            GradeImportItem(
                row=item['row'],
                student_id=item['student_id'],
                name=item.get('name'),
                subject=item['subject'],
                score=item['score'],
                error=item.get('error')
            )
            for item in result.get('failed_items', [])
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
        
        import_result = GradeImportResult(
            total_rows=result['total_rows'],
            success_count=result['success_count'],
            fail_count=result['fail_count'],
            success_items=success_items,
            failed_items=failed_items,
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
                resource_type="grade",
                resource_id=None,
                details={
                    "filename": file.filename,
                    "exam_type": exam_type,
                    "exam_date": exam_date,
                    "total_rows": result['total_rows'],
                    "success_count": result['success_count'],
                    "fail_count": result['fail_count']
                }
            )
        except Exception:
            pass
        
        return GradeImportResponse(
            success=True,
            data=import_result,
            message=message
        )
        
    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.get("/grades/template", summary="下载成绩导入模板")
async def download_grade_template(
    format: TemplateFormat = Query(
        TemplateFormat.XLSX, 
        description="模板格式：xlsx 或 csv"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    下载成绩信息导入模板
    
    - **format**: 模板格式，支持 xlsx 和 csv
    - 模板包含字段说明和示例数据
    """
    try:
        import_service = ImportService(db)
        template_content = import_service.generate_grade_template(format=format)
        
        # 设置响应头
        if format == TemplateFormat.XLSX:
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = "grade_import_template.xlsx"
        else:
            media_type = "text/csv; charset=utf-8"
            filename = "grade_import_template.csv"
        
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
