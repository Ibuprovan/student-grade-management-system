"""
账号管理 API 路由（管理员权限）

提供统一的账号管理接口：
- GET    /api/v1/accounts                    获取所有账号（支持按角色筛选）
- GET    /api/v1/accounts/students           学生账号列表
- GET    /api/v1/accounts/class-teachers     班主任账号列表
- GET    /api/v1/accounts/subject-leaders    学科组长账号列表
- POST   /api/v1/accounts/{user_id}/reset-password  重置密码
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.auth import require_admin
from src.api.dependencies import get_db
from src.core.security import hash_password
from src.models.class_teacher import ClassTeacher
from src.models.student import Student
from src.models.subject_leader import SubjectLeader
from src.models.user import User
from src.schemas.common import ApiResponse

router = APIRouter(prefix="/api/v1/accounts", tags=["账号管理"])


def _build_account(user: User, db: Session) -> dict:
    """构建账号信息，附带关联角色的详细信息"""
    account = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "is_active": user.is_active,
        "need_change_password": user.need_change_password,
        "detail": None,
    }

    if user.role == "student":
        student = db.execute(
            select(Student).where(Student.student_id == user.username)
        ).scalar_one_or_none()
        if student:
            account["detail"] = {
                "student_id": student.student_id,
                "name": student.name,
                "class_name": student.class_name,
                "gender": student.gender,
            }
    elif user.role == "class_teacher":
        ct = db.execute(
            select(ClassTeacher).where(ClassTeacher.user_id == user.id)
        ).scalar_one_or_none()
        if ct:
            account["detail"] = {
                "class_name": ct.class_name,
                "teacher_name": ct.teacher_name,
                "enrollment_year": ct.enrollment_year,
                "class_number": ct.class_number,
            }
    elif user.role == "subject_leader":
        sl = db.execute(
            select(SubjectLeader).where(SubjectLeader.user_id == user.id)
        ).scalar_one_or_none()
        if sl:
            account["detail"] = {
                "subject": sl.subject,
                "subject_en": sl.subject_en,
                "leader_name": sl.leader_name,
            }

    return account


@router.get("")
def list_accounts(
    role: str = Query(None, description="按角色筛选: student, class_teacher, subject_leader"),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin),
) -> ApiResponse:
    stmt = select(User)
    if role:
        stmt = stmt.where(User.role == role)
    stmt = stmt.order_by(User.role, User.username)
    users = list(db.execute(stmt).scalars().all())
    accounts = [_build_account(u, db) for u in users]
    return ApiResponse(success=True, data=accounts)


@router.get("/students")
def list_student_accounts(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin),
) -> ApiResponse:
    users = list(
        db.execute(select(User).where(User.role == "student").order_by(User.username))
        .scalars().all()
    )
    accounts = [_build_account(u, db) for u in users]
    return ApiResponse(success=True, data=accounts)


@router.get("/class-teachers")
def list_class_teacher_accounts(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin),
) -> ApiResponse:
    users = list(
        db.execute(select(User).where(User.role == "class_teacher").order_by(User.username))
        .scalars().all()
    )
    accounts = [_build_account(u, db) for u in users]
    return ApiResponse(success=True, data=accounts)


@router.get("/subject-leaders")
def list_subject_leader_accounts(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin),
) -> ApiResponse:
    users = list(
        db.execute(select(User).where(User.role == "subject_leader").order_by(User.username))
        .scalars().all()
    )
    accounts = [_build_account(u, db) for u in users]
    return ApiResponse(success=True, data=accounts)


@router.post("/{user_id}/reset-password")
def reset_password(
    user_id: int = Path(...),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin),
) -> ApiResponse:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    new_password = "123456"
    user.hashed_password = hash_password(new_password)
    user.need_change_password = True
    db.commit()
    return ApiResponse(
        success=True,
        message=f"用户 {user.username} 密码已重置为 {new_password}",
        data={"username": user.username, "new_password": new_password},
    )
