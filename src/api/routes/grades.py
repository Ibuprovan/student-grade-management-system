"""
成绩管理 API 路由

提供成绩管理的 RESTful 接口：
- POST   /api/v1/grades                    录入单条成绩（需要教师权限）
- POST   /api/v1/grades/batch              批量录入成绩（需要教师权限）
- GET    /api/v1/grades/search              组合条件查询成绩（需要认证）
- GET    /api/v1/grades/export              导出成绩数据 CSV（需要教师权限）
- GET    /api/v1/grades/student/{student_id} 按学生查询成绩（需要认证）
- GET    /api/v1/grades/class/{class_name}  按班级查询成绩（需要认证）
- GET    /api/v1/grades/subject/{subject}   按科目查询成绩（需要认证）
- GET    /api/v1/grades/{grade_id}          查询单条成绩（需要认证）
- PUT    /api/v1/grades/{grade_id}          修改成绩（需要教师权限）
- DELETE /api/v1/grades/{grade_id}          删除成绩（需要管理员权限）
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query, Path, status
from fastapi.responses import StreamingResponse

from src.api.dependencies import get_grade_service
from src.api.auth import get_current_user, require_admin, require_teacher_or_admin
from src.core.config import settings
from src.core.utils import build_paginated_response
from src.schemas.grade import (
    GradeCreate,
    GradeUpdate,
    GradeBatchCreate,
    GradeResponse,
)
from src.schemas.common import ApiResponse, PaginatedResponse, SuccessResponse
from src.services.grade_service import GradeService
from src.models.grade import Grade
from src.models.user import User

# 创建路由器
router = APIRouter(prefix="/api/v1/grades", tags=["成绩管理"])


def _build_grade_response(grade: Grade) -> GradeResponse:
    """
    构建包含学生信息的成绩响应

    Args:
        grade: 成绩对象（已加载 student 关联）

    Returns:
        GradeResponse: 包含学生姓名和班级的成绩响应
    """
    grade_data = GradeResponse.model_validate(grade)
    if hasattr(grade, 'student') and grade.student:
        grade_data.student_name = grade.student.name
        grade_data.class_name = grade.student.class_name
    return grade_data


def _build_grade_responses(grades: List[Grade]) -> List[GradeResponse]:
    """
    批量构建包含学生信息的成绩响应

    Args:
        grades: 成绩列表

    Returns:
        List[GradeResponse]: 成绩响应列表
    """
    return [_build_grade_response(g) for g in grades]


@router.post(
    "",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary="录入单条成绩",
    description="录入单个学生的单科成绩（需要教师权限）",
    responses={
        401: {"description": "未认证"},
        403: {"description": "权限不足"},
        404: {"description": "学生不存在"},
        409: {"description": "成绩记录已存在"},
        422: {"description": "数据验证失败"},
    },
)
def create_grade(
    data: GradeCreate,
    service: GradeService = Depends(get_grade_service),
    current_user: User = Depends(require_teacher_or_admin),
) -> ApiResponse:
    """
    录入单条成绩（需要教师权限）

    - **student_id**: 学号（必须已存在于系统中）
    - **subject**: 科目（语文/数学/英语/物理/化学/生物/历史/地理/政治）
    - **score**: 分数（0-100，支持1位小数）
    - **exam_type**: 考试类型（期中/期末/月考/单元测试）
    - **exam_date**: 考试日期
    """
    grade = service.create_grade(data)
    return ApiResponse(
        success=True,
        data=_build_grade_response(grade),
        message="成绩录入成功",
    )


@router.post(
    "/batch",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary="批量录入成绩",
    description="批量录入多个学生的成绩（需要教师权限）",
    responses={
        401: {"description": "未认证"},
        403: {"description": "权限不足"},
        422: {"description": "数据验证失败"},
    },
)
def batch_create_grades(
    data: GradeBatchCreate,
    service: GradeService = Depends(get_grade_service),
    current_user: User = Depends(require_teacher_or_admin),
) -> ApiResponse:
    """
    批量录入成绩（需要教师权限）

    - **subject**: 科目（所有成绩同一科目）
    - **exam_type**: 考试类型
    - **exam_date**: 考试日期
    - **grades**: 成绩列表，每项包含 student_id 和 score
    """
    result = service.batch_create_grades(data)
    return ApiResponse(
        success=True,
        data=result,
        message=f"批量录入完成：成功 {result['success_count']} 条，失败 {result['fail_count']} 条",
    )


@router.get(
    "/search",
    response_model=PaginatedResponse,
    summary="组合条件查询成绩",
    description="支持按班级、科目、考试类型进行组合筛选查询（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def search_grades(
    class_name: Optional[str] = Query(None, description="按班级筛选"),
    subject: Optional[str] = Query(None, description="按科目筛选"),
    exam_type: Optional[str] = Query(None, description="按考试类型筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: GradeService = Depends(get_grade_service),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse:
    """
    组合条件查询成绩（需要认证）

    - **class_name**: 按班级筛选（可选）
    - **subject**: 按科目筛选（可选）
    - **exam_type**: 按考试类型筛选（可选）
    - **page**: 页码（默认 1）
    - **page_size**: 每页数量（默认 20，最大 100）
    """
    # 限制每页最大数量
    page_size = min(page_size, settings.MAX_PAGE_SIZE)

    grades, total = service.search_grades(
        class_name=class_name,
        subject=subject,
        exam_type=exam_type,
        page=page,
        page_size=page_size,
    )

    # 构建包含学生信息的响应
    grade_responses = _build_grade_responses(grades)

    return build_paginated_response(
        items=grade_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/export",
    summary="导出成绩数据",
    description="导出成绩数据为 CSV 文件（需要教师权限）",
    responses={
        401: {"description": "未认证"},
        403: {"description": "权限不足"},
    },
)
def export_grades(
    class_name: Optional[str] = Query(None, description="按班级筛选"),
    subject: Optional[str] = Query(None, description="按科目筛选"),
    exam_type: Optional[str] = Query(None, description="按考试类型筛选"),
    service: GradeService = Depends(get_grade_service),
    current_user: User = Depends(require_teacher_or_admin),
) -> StreamingResponse:
    """
    导出成绩数据为 CSV（需要教师权限）

    - **class_name**: 按班级筛选（可选）
    - **subject**: 按科目筛选（可选）
    - **exam_type**: 按考试类型筛选（可选）
    - 返回 CSV 格式文件，UTF-8 编码（带 BOM，兼容 Excel）
    - 包含学号、姓名、班级、科目、分数、考试类型、考试日期等字段
    """
    csv_content = service.export_grades_csv(
        class_name=class_name,
        subject=subject,
        exam_type=exam_type,
    )

    # 使用 StreamingResponse 返回文件
    # 添加 Content-Disposition 头，触发浏览器下载
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=grades_export.csv",
        },
    )


@router.get(
    "/student/{student_id}",
    response_model=ApiResponse,
    summary="按学生查询成绩",
    description="查询指定学生的所有科目成绩（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def get_grades_by_student(
    student_id: str = Path(..., description="学号"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: GradeService = Depends(get_grade_service),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    按学生查询成绩（需要认证）

    - **student_id**: 学号
    """
    skip = (page - 1) * page_size
    grades = service.get_grades_by_student(
        student_id=student_id,
        skip=skip,
        limit=page_size,
    )
    return ApiResponse(
        success=True,
        data=_build_grade_responses(grades),
    )


@router.get(
    "/class/{class_name}",
    response_model=PaginatedResponse,
    summary="按班级查询成绩",
    description="查询指定班级的学生成绩（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def get_grades_by_class(
    class_name: str = Path(..., description="班级名称"),
    subject: Optional[str] = Query(None, description="按科目筛选"),
    exam_type: Optional[str] = Query(None, description="按考试类型筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: GradeService = Depends(get_grade_service),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse:
    """
    按班级查询成绩（需要认证）

    - **class_name**: 班级名称
    - **subject**: 按科目筛选（可选）
    - **exam_type**: 按考试类型筛选（可选）
    """
    # 限制每页最大数量
    page_size = min(page_size, settings.MAX_PAGE_SIZE)
    skip = (page - 1) * page_size

    grades = service.get_grades_by_class(
        class_name=class_name,
        subject=subject,
        exam_type=exam_type,
        skip=skip,
        limit=page_size,
    )

    total = service.count_grades_by_class(
        class_name=class_name,
        subject=subject,
        exam_type=exam_type,
    )

    return build_paginated_response(
        items=_build_grade_responses(grades),
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/subject/{subject}",
    response_model=PaginatedResponse,
    summary="按科目查询成绩",
    description="查询指定科目的学生成绩（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def get_grades_by_subject(
    subject: str = Path(..., description="科目名称"),
    exam_type: Optional[str] = Query(None, description="按考试类型筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: GradeService = Depends(get_grade_service),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse:
    """
    按科目查询成绩（需要认证）

    - **subject**: 科目名称
    - **exam_type**: 按考试类型筛选（可选）
    """
    # 限制每页最大数量
    page_size = min(page_size, settings.MAX_PAGE_SIZE)
    skip = (page - 1) * page_size

    grades = service.get_grades_by_subject(
        subject=subject,
        exam_type=exam_type,
        skip=skip,
        limit=page_size,
    )

    total = service.count_grades_by_subject(
        subject=subject,
        exam_type=exam_type,
    )

    return build_paginated_response(
        items=_build_grade_responses(grades),
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{grade_id}",
    response_model=ApiResponse,
    summary="查询单条成绩",
    description="根据成绩ID查询成绩详细信息（需要认证）",
    responses={
        401: {"description": "未认证"},
        404: {"description": "成绩记录不存在"},
    },
)
def get_grade(
    grade_id: int = Path(..., description="成绩ID"),
    service: GradeService = Depends(get_grade_service),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    查询单条成绩（需要认证）

    - **grade_id**: 成绩ID
    """
    grade = service.get_grade_by_id(grade_id)
    return ApiResponse(
        success=True,
        data=_build_grade_response(grade),
    )


@router.put(
    "/{grade_id}",
    response_model=ApiResponse,
    summary="修改成绩",
    description="修改已录入的成绩分数（需要教师权限）",
    responses={
        401: {"description": "未认证"},
        403: {"description": "权限不足"},
        404: {"description": "成绩记录不存在"},
        422: {"description": "数据验证失败"},
    },
)
def update_grade(
    data: GradeUpdate,
    grade_id: int = Path(..., description="成绩ID"),
    service: GradeService = Depends(get_grade_service),
    current_user: User = Depends(require_teacher_or_admin),
) -> ApiResponse:
    """
    修改成绩（需要教师权限）

    - **grade_id**: 成绩ID
    - **score**: 新的分数（0-100，支持1位小数）
    """
    grade = service.update_grade(grade_id, data)
    return ApiResponse(
        success=True,
        data=_build_grade_response(grade),
        message="成绩更新成功",
    )


@router.delete(
    "/{grade_id}",
    response_model=SuccessResponse,
    summary="删除成绩",
    description="删除成绩记录（需要管理员权限）",
    responses={
        401: {"description": "未认证"},
        403: {"description": "权限不足"},
        404: {"description": "成绩记录不存在"},
    },
)
def delete_grade(
    grade_id: int = Path(..., description="成绩ID"),
    service: GradeService = Depends(get_grade_service),
    current_user: User = Depends(require_admin),
) -> SuccessResponse:
    """
    删除成绩（需要管理员权限）

    - **grade_id**: 成绩ID
    """
    service.delete_grade(grade_id)
    return SuccessResponse(
        message="成绩记录删除成功",
    )
