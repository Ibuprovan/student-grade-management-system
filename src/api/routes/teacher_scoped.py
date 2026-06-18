"""
教师专用 API 路由（只读）

教师只能看到自己所带科目+班级的组合数据。
每位教师可能有多个 (subject, class) 组合。

- GET /api/v1/teacher/dashboard       教师仪表盘
- GET /api/v1/teacher/grades          教师成绩管理
- GET /api/v1/teacher/statistics       教师统计概览
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, case, and_
from sqlalchemy.orm import Session

from src.api.auth import require_teacher_or_admin
from src.api.dependencies import get_db
from src.core.constants import (
    MAIN_SUBJECTS, MAIN_SUBJECT_PASS, MAIN_SUBJECT_EXCELLENT,
    PASS_SCORE, EXCELLENT_SCORE, SUBJECTS,
)
from src.models.grade import Grade
from src.models.student import Student
from src.models.user import User
from src.repositories.teacher_assignment_repo import TeacherAssignmentRepository
from src.schemas.common import ApiResponse
from src.services.teacher_assignment_service import TeacherAssignmentService

router = APIRouter(prefix="/api/v1/teacher", tags=["教师专用"])


def _get_teacher_assignments(current_user: User, db: Session):
    """获取教师的所有任课组合"""
    repo = TeacherAssignmentRepository(db)
    assignments = repo.get_by_user(current_user.id)
    if not assignments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到您的任课信息",
        )
    return assignments


def _get_filters(current_user: User, db: Session, subject: Optional[str], class_name: Optional[str]):
    """
    返回 (assignments, filters_info)：
    - 如果是教师角色，根据其任课自动限制 subject+class
    - 如果是管理员，使用查询参数
    """
    if current_user.role == "admin":
        if not subject or not class_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="管理员需同时指定 subject 和 class_name 参数",
            )
        return [{"subject": subject, "class_name": class_name}]

    return _get_teacher_assignments(current_user, db)


# ==================== 仪表盘 ====================


@router.get("/dashboard")
def get_teacher_dashboard(
    subject: Optional[str] = Query(None),
    class_name: Optional[str] = Query(None),
    exam_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
) -> ApiResponse:
    assignments = _get_filters(current_user, db, subject, class_name)

    results = []
    for a in assignments:
        subj = a["subject"] if isinstance(a, dict) else a.subject
        cn = a["class_name"] if isinstance(a, dict) else a.class_name
        is_major = subj in MAIN_SUBJECTS
        pass_th = MAIN_SUBJECT_PASS if is_major else PASS_SCORE
        exc_th = MAIN_SUBJECT_EXCELLENT if is_major else EXCELLENT_SCORE

        base = [Student.class_name == cn, Grade.subject == subj]
        if exam_type:
            base.append(Grade.exam_type == exam_type)

        student_count = db.execute(
            select(func.count()).select_from(Student).where(Student.class_name == cn)
        ).scalar() or 0

        grade_count = db.execute(
            select(func.count()).select_from(Grade)
            .join(Student, Grade.student_id == Student.student_id)
            .where(and_(*base))
        ).scalar() or 0

        avg_result = db.execute(
            select(func.avg(Grade.score))
            .join(Student, Grade.student_id == Student.student_id)
            .where(and_(*base))
        ).scalar()
        average_score = round(float(avg_result), 2) if avg_result else 0.0

        row = db.execute(select(
            func.count(Grade.grade_id),
            func.sum(case((Grade.score >= pass_th, 1), else_=0)),
            func.sum(case((Grade.score >= exc_th, 1), else_=0)),
        ).join(Student, Grade.student_id == Student.student_id)
          .where(and_(*base))).one()
        total = row[0] or 0
        passed = int(row[1]) if row[1] else 0
        excellent = int(row[2]) if row[2] else 0
        pass_rate = round((passed / total) * 100, 2) if total > 0 else 0.0
        excellent_rate = round((excellent / total) * 100, 2) if total > 0 else 0.0

        results.append({
            "subject": subj,
            "class_name": cn,
            "student_count": student_count,
            "total_grades": grade_count,
            "average_score": average_score,
            "pass_rate": pass_rate,
            "excellent_rate": excellent_rate,
        })

    return ApiResponse(success=True, data=results)


# ==================== 成绩管理 ====================


@router.get("/grades")
def get_teacher_grades(
    subject: Optional[str] = Query(None),
    class_name: Optional[str] = Query(None),
    exam_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
) -> ApiResponse:
    assignments = _get_filters(current_user, db, subject, class_name)

    subj_filter = [a["subject"] if isinstance(a, dict) else a.subject for a in assignments]
    class_filter = [a["class_name"] if isinstance(a, dict) else a.class_name for a in assignments]

    filters = [
        Grade.subject.in_(subj_filter),
        Student.class_name.in_(class_filter),
    ]
    if exam_type:
        filters.append(Grade.exam_type == exam_type)
    if search:
        filters.append(
            (Student.student_id.contains(search)) | (Student.name.contains(search))
        )

    skip = (page - 1) * page_size
    total = db.execute(
        select(func.count()).select_from(Grade)
        .join(Student, Grade.student_id == Student.student_id)
        .where(and_(*filters))
    ).scalar() or 0

    rows = db.execute(
        select(Grade, Student.name, Student.class_name)
        .join(Student, Grade.student_id == Student.student_id)
        .where(and_(*filters))
        .order_by(Grade.exam_date.desc(), Student.student_id)
        .offset(skip).limit(page_size)
    ).all()

    items = [{
        "grade_id": g.grade_id,
        "student_id": g.student_id,
        "student_name": sn,
        "class_name": cn,
        "subject": g.subject,
        "score": float(g.score),
        "exam_type": g.exam_type,
        "exam_date": g.exam_date.isoformat() if g.exam_date else None,
    } for g, sn, cn in rows]

    return ApiResponse(success=True, data={
        "items": items, "total": total, "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    })


# ==================== 统计概览 ====================


@router.get("/statistics")
def get_teacher_statistics(
    subject: Optional[str] = Query(None),
    class_name: Optional[str] = Query(None),
    exam_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
) -> ApiResponse:
    assignments = _get_filters(current_user, db, subject, class_name)

    results = []
    for a in assignments:
        subj = a["subject"] if isinstance(a, dict) else a.subject
        cn = a["class_name"] if isinstance(a, dict) else a.class_name
        is_major = subj in MAIN_SUBJECTS
        pass_th = MAIN_SUBJECT_PASS if is_major else PASS_SCORE
        exc_th = MAIN_SUBJECT_EXCELLENT if is_major else EXCELLENT_SCORE

        base = [Student.class_name == cn, Grade.subject == subj]
        if exam_type:
            base.append(Grade.exam_type == exam_type)

        student_count = db.execute(
            select(func.count()).select_from(Student).where(Student.class_name == cn)
        ).scalar() or 0

        row = db.execute(select(
            func.count(Grade.grade_id),
            func.avg(Grade.score),
            func.max(Grade.score),
            func.min(Grade.score),
            func.sum(case((Grade.score >= pass_th, 1), else_=0)),
            func.sum(case((Grade.score >= exc_th, 1), else_=0)),
        ).join(Student, Grade.student_id == Student.student_id)
          .where(and_(*base))).one()

        total = row[0] or 0
        average = round(float(row[1]), 2) if row[1] else 0.0
        max_score = round(float(row[2]), 1) if row[2] else 0.0
        min_score = round(float(row[3]), 1) if row[3] else 0.0
        passed = int(row[4]) if row[4] else 0
        excellent = int(row[5]) if row[5] else 0
        pass_rate = round((passed / total) * 100, 2) if total > 0 else 0.0
        excellent_rate = round((excellent / total) * 100, 2) if total > 0 else 0.0

        # 分数分布
        if is_major:
            dist_keys = ["0-89", "90-104", "105-119", "120-134", "135-150"]
            thresholds = [90, 105, 120, 135, 151]
        else:
            dist_keys = ["0-59", "60-69", "70-79", "80-89", "90-100"]
            thresholds = [60, 70, 80, 90, 101]

        scores = [float(r[0]) for r in db.execute(
            select(Grade.score)
            .join(Student, Grade.student_id == Student.student_id)
            .where(and_(*base))
        ).all()]
        distribution = {k: 0 for k in dist_keys}
        for s in scores:
            for i, t in enumerate(thresholds):
                if s < t:
                    distribution[dist_keys[i]] += 1
                    break

        # 排名前十
        top_rows = db.execute(
            select(Grade.student_id, Student.name, Grade.score)
            .join(Student, Grade.student_id == Student.student_id)
            .where(and_(*base))
            .order_by(Grade.score.desc())
            .limit(10)
        ).all()
        top10 = [
            {"rank": i + 1, "student_id": r[0], "student_name": r[1],
             "score": round(float(r[2]), 1)}
            for i, r in enumerate(top_rows)
        ]

        # 参考人数（去重学生数）
        ref_count = db.execute(
            select(func.count(func.distinct(Grade.student_id)))
            .join(Student, Grade.student_id == Student.student_id)
            .where(and_(*base))
        ).scalar() or 0

        results.append({
            "subject": subj,
            "class_name": cn,
            "student_count": student_count,
            "grade_count": total,
            "reference_count": ref_count,
            "average_score": average,
            "max_score": max_score,
            "min_score": min_score,
            "pass_rate": pass_rate,
            "excellent_rate": excellent_rate,
            "distribution": distribution,
            "top10": top10,
        })

    return ApiResponse(success=True, data=results)
