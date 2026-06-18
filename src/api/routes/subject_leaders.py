"""
学科教研组组长管理 API 路由（管理员权限）
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.auth import require_admin
from src.api.dependencies import get_db
from src.models.user import User
from src.schemas.subject_leader import SubjectLeaderCreate
from src.schemas.common import ApiResponse
from src.services.subject_leader_service import SubjectLeaderService

router = APIRouter(prefix="/api/v1/subject-leaders", tags=["学科组长管理"])


@router.get("/available-subjects")
def get_available_subjects(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin),
) -> ApiResponse:
    service = SubjectLeaderService(db)
    return ApiResponse(success=True, data=service.get_available_subjects())


@router.post("", status_code=status.HTTP_201_CREATED)
def create_subject_leader(
    data: SubjectLeaderCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin),
) -> ApiResponse:
    service = SubjectLeaderService(db)
    try:
        result = service.add_subject_leader(
            subject=data.subject,
            leader_name=data.leader_name,
        )
        return ApiResponse(
            success=True, data=result,
            message=f"组长添加成功，账号：{result['username']}，初始密码：123456",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{leader_id}")
def delete_subject_leader(
    leader_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin),
) -> ApiResponse:
    service = SubjectLeaderService(db)
    try:
        service.delete_subject_leader(leader_id)
        return ApiResponse(success=True, message="组长删除成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("")
def get_subject_leaders(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin),
) -> ApiResponse:
    service = SubjectLeaderService(db)
    return ApiResponse(success=True, data=service.get_all_leaders())
