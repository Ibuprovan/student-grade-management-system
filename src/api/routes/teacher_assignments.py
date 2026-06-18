"""
教师任课分配管理 API 路由（管理员权限）
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.auth import require_admin
from src.api.dependencies import get_db
from src.models.user import User
from src.schemas.teacher_assignment import TeacherAssignmentCreate
from src.schemas.common import ApiResponse
from src.services.teacher_assignment_service import TeacherAssignmentService

router = APIRouter(prefix="/api/v1/teacher-assignments", tags=["教师任课管理"])


@router.get("/available")
def get_available_combinations(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin),
) -> ApiResponse:
    service = TeacherAssignmentService(db)
    return ApiResponse(success=True, data=service.get_available_combinations())


@router.post("", status_code=status.HTTP_201_CREATED)
def create_assignment(
    data: TeacherAssignmentCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin),
) -> ApiResponse:
    service = TeacherAssignmentService(db)
    try:
        result = service.add_assignment(
            subject=data.subject,
            class_name=data.class_name,
            teacher_name=data.teacher_name,
        )
        return ApiResponse(
            success=True, data=result,
            message=f"教师添加成功，账号：{result['username']}，初始密码：123456",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin),
) -> ApiResponse:
    service = TeacherAssignmentService(db)
    try:
        service.delete_assignment(assignment_id)
        return ApiResponse(success=True, message="教师删除成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("")
def get_assignments(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin),
) -> ApiResponse:
    service = TeacherAssignmentService(db)
    return ApiResponse(success=True, data=service.get_all_assignments())
