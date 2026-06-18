"""
班主任管理 API 路由

提供班主任管理的 RESTful 接口（需要管理员权限）：
- GET    /api/v1/class-teachers/available-classes  获取可分配的班级列表
- POST   /api/v1/class-teachers                    添加班主任（自动创建账号）
- DELETE /api/v1/class-teachers/{id}                删除班主任（自动删除账号）
- GET    /api/v1/class-teachers                     获取所有班主任列表
"""

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.auth import require_admin
from src.api.dependencies import get_db
from src.models.user import User
from src.schemas.class_teacher import ClassTeacherCreate
from src.schemas.common import ApiResponse
from src.services.class_teacher_service import ClassTeacherService
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/class-teachers", tags=["班主任管理"])


@router.get(
    "/available-classes",
    response_model=ApiResponse,
    summary="获取可分配的班级列表",
    description="从学生表中查询所有有学生但尚未分配班主任的班级（需要管理员权限）",
)
def get_available_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> ApiResponse:
    service = ClassTeacherService(db)
    classes = service.get_available_classes()
    return ApiResponse(success=True, data=classes)


@router.post(
    "",
    response_model=ApiResponse,
    summary="添加班主任",
    description="添加班主任并自动创建登录账号（需要管理员权限）",
    status_code=status.HTTP_201_CREATED,
)
def create_class_teacher(
    data: ClassTeacherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> ApiResponse:
    service = ClassTeacherService(db)
    try:
        result = service.add_class_teacher(
            class_name=data.class_name,
            enrollment_year=data.enrollment_year,
            class_number=data.class_number,
            teacher_name=data.teacher_name,
        )
        return ApiResponse(
            success=True,
            data=result,
            message=f"班主任添加成功，账号：{result['username']}，初始密码：123456",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{class_teacher_id}",
    response_model=ApiResponse,
    summary="删除班主任",
    description="删除班主任并同时删除其登录账号（需要管理员权限）",
)
def delete_class_teacher(
    class_teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> ApiResponse:
    service = ClassTeacherService(db)
    try:
        service.delete_class_teacher(class_teacher_id)
        return ApiResponse(
            success=True,
            message="班主任删除成功",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "",
    response_model=ApiResponse,
    summary="获取班主任列表",
    description="获取所有班主任列表（需要管理员权限）",
)
def get_class_teachers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> ApiResponse:
    service = ClassTeacherService(db)
    teachers = service.get_all_class_teachers()
    return ApiResponse(
        success=True,
        data=teachers,
    )
