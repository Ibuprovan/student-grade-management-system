"""
学生信息 API 路由

提供学生管理的 RESTful 接口：
- POST   /api/v1/students          添加学生（需要认证）
- GET    /api/v1/students           学生列表（分页，需要认证）
- GET    /api/v1/students/search    搜索学生（需要认证）
- GET    /api/v1/students/classes   获取班级列表（需要认证）
- GET    /api/v1/students/{id}      查询单个学生（需要认证）
- PUT    /api/v1/students/{id}      修改学生（需要认证）
- DELETE /api/v1/students/{id}      删除学生（需要管理员权限）
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, Path, status

from src.api.dependencies import get_student_service
from src.api.auth import get_current_user, require_admin, require_teacher_or_admin
from src.core.config import settings
from src.core.utils import build_paginated_response
from src.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from src.schemas.batch import BatchDeleteRequest, BatchDeleteResponse
from src.schemas.common import ApiResponse, PaginatedResponse, SuccessResponse
from src.services.student_service import StudentService
from src.models.user import User

# 创建路由器
router = APIRouter(prefix="/api/v1/students", tags=["学生管理"])


@router.post(
    "",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary="添加学生",
    description="创建新的学生记录，学号必须唯一（需要教师权限）",
    responses={
        401: {"description": "未认证"},
        403: {"description": "权限不足"},
        409: {"description": "学号已存在"},
        422: {"description": "数据验证失败"},
    },
)
def create_student(
    data: StudentCreate,
    service: StudentService = Depends(get_student_service),
    current_user: User = Depends(require_teacher_or_admin),
) -> ApiResponse:
    """
    添加学生（需要教师权限）

    - **student_id**: 学号（8位数字，格式：YYYY + 4位序号）
    - **name**: 姓名（2-20个字符）
    - **gender**: 性别（男/女）
    - **class_name**: 班级名称
    - **enrollment_year**: 入学年份（2000-2100）
    """
    student = service.create_student(data)
    return ApiResponse(
        success=True,
        data=StudentResponse.model_validate(student),
        message="学生添加成功",
    )


@router.get(
    "",
    response_model=PaginatedResponse,
    summary="学生列表",
    description="获取学生列表，支持分页和按班级筛选（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def get_student_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
        description="每页数量",
    ),
    class_name: Optional[str] = Query(None, description="按班级筛选"),
    service: StudentService = Depends(get_student_service),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse:
    """
    获取学生列表（需要认证）

    - **page**: 页码（默认 1）
    - **page_size**: 每页数量（默认 20，最大 100）
    - **class_name**: 按班级筛选（可选）
    """
    # 限制每页最大数量
    page_size = min(page_size, settings.MAX_PAGE_SIZE)

    students, total = service.get_student_list(
        page=page,
        page_size=page_size,
        class_name=class_name,
    )

    return build_paginated_response(
        items=[StudentResponse.model_validate(s) for s in students],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/search",
    response_model=PaginatedResponse,
    summary="搜索学生",
    description="按学号或姓名关键词搜索学生（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def search_students(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    class_name: Optional[str] = Query(None, description="按班级筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: StudentService = Depends(get_student_service),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse:
    """
    搜索学生（需要认证）

    - **keyword**: 搜索关键词（匹配学号或姓名）
    - **class_name**: 按班级筛选（可选）
    - **page**: 页码
    - **page_size**: 每页数量
    """
    # 限制每页最大数量
    page_size = min(page_size, settings.MAX_PAGE_SIZE)

    students, total = service.search_students(
        keyword=keyword,
        class_name=class_name,
        page=page,
        page_size=page_size,
    )

    return build_paginated_response(
        items=[StudentResponse.model_validate(s) for s in students],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/classes",
    response_model=ApiResponse,
    summary="获取班级列表",
    description="获取所有去重的班级名称列表（需要认证）",
    responses={
        401: {"description": "未认证"},
    },
)
def get_classes(
    service: StudentService = Depends(get_student_service),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    获取班级列表（需要认证）

    返回系统中所有学生所属的去重班级名称列表，按名称排序。
    用于前端下拉框、筛选器等场景。
    """
    classes = service.get_all_classes()
    return ApiResponse(
        success=True,
        data=classes,
    )


@router.post(
    "/batch-delete",
    response_model=ApiResponse,
    summary="批量删除学生",
    description="批量删除学生记录及其所有成绩（需要管理员权限）",
    responses={
        401: {"description": "未认证"},
        403: {"description": "权限不足"},
        422: {"description": "数据验证失败"},
    },
)
def batch_delete_students(
    data: BatchDeleteRequest,
    service: StudentService = Depends(get_student_service),
    current_user: User = Depends(require_admin),
) -> ApiResponse:
    """
    批量删除学生（需要管理员权限）

    - **student_ids**: 学号数组
    - 删除学生会级联删除其所有成绩记录
    - 返回每条记录的删除结果
    """
    result = service.batch_delete_students(data.student_ids)
    return ApiResponse(
        success=True,
        data=BatchDeleteResponse(**result).model_dump(),
        message=f"批量删除完成：成功 {result['success_count']} 条，失败 {result['fail_count']} 条",
    )


@router.get(
    "/{student_id}",
    response_model=ApiResponse,
    summary="查询学生",
    description="根据学号查询学生详细信息（需要认证）",
    responses={
        401: {"description": "未认证"},
        404: {"description": "学生不存在"},
    },
)
def get_student(
    student_id: str = Path(..., description="学号"),
    service: StudentService = Depends(get_student_service),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    查询单个学生（需要认证）

    - **student_id**: 学号
    """
    student = service.get_student_by_id(student_id)
    return ApiResponse(
        success=True,
        data=StudentResponse.model_validate(student),
    )


@router.put(
    "/{student_id}",
    response_model=ApiResponse,
    summary="修改学生",
    description="更新学生信息，只更新提供的字段（需要教师权限）",
    responses={
        401: {"description": "未认证"},
        403: {"description": "权限不足"},
        404: {"description": "学生不存在"},
        422: {"description": "数据验证失败"},
    },
)
def update_student(
    data: StudentUpdate,
    student_id: str = Path(..., description="学号"),
    service: StudentService = Depends(get_student_service),
    current_user: User = Depends(require_teacher_or_admin),
) -> ApiResponse:
    """
    修改学生信息（需要教师权限）

    - **student_id**: 学号
    - 请求体中只提供需要更新的字段即可
    """
    student = service.update_student(student_id, data)
    return ApiResponse(
        success=True,
        data=StudentResponse.model_validate(student),
        message="学生信息更新成功",
    )


@router.delete(
    "/{student_id}",
    response_model=SuccessResponse,
    summary="删除学生",
    description="删除学生记录及其所有成绩（需要管理员权限）",
    responses={
        401: {"description": "未认证"},
        403: {"description": "权限不足"},
        404: {"description": "学生不存在"},
    },
)
def delete_student(
    student_id: str = Path(..., description="学号"),
    service: StudentService = Depends(get_student_service),
    current_user: User = Depends(require_admin),
) -> SuccessResponse:
    """
    删除学生（需要管理员权限）

    - **student_id**: 学号
    - 删除学生会级联删除其所有成绩记录
    """
    service.delete_student(student_id)
    return SuccessResponse(
        message=f"学生 '{student_id}' 删除成功",
    )
