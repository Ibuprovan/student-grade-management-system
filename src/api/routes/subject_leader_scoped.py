"""
学科教研组组长专用 API 路由（只读）
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, case, and_
from sqlalchemy.orm import Session

from src.api.auth import require_subject_leader_or_admin
from src.api.dependencies import get_db
from src.core.constants import (
    MAIN_SUBJECTS, MAIN_SUBJECT_PASS, MAIN_SUBJECT_EXCELLENT,
    PASS_SCORE, EXCELLENT_SCORE,
)
from src.models.grade import Grade
from src.models.student import Student
from src.models.user import User
from src.repositories.subject_leader_repo import SubjectLeaderRepository
from src.schemas.common import ApiResponse

router = APIRouter(prefix="/api/v1/subject-leader", tags=["学科组长专用"])


def _get_subject_for_leader(
    current_user: User, db: Session, subject_param: Optional[str] = None,
) -> str:
    if current_user.role == "admin":
        if not subject_param:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="管理员需指定 subject 参数",
            )
        return subject_param
    leader = SubjectLeaderRepository(db).get_by_user_id(current_user.id)
    if not leader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到您负责的学科",
        )
    return leader.subject


@router.get("/dashboard")
def get_subject_dashboard(
    subject: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_subject_leader_or_admin),
) -> ApiResponse:
    subj = _get_subject_for_leader(current_user, db, subject)
    is_major = subj in MAIN_SUBJECTS
    pass_th = MAIN_SUBJECT_PASS if is_major else PASS_SCORE
    exc_th = MAIN_SUBJECT_EXCELLENT if is_major else EXCELLENT_SCORE

    student_count = db.execute(
        select(func.count()).select_from(Student)
    ).scalar() or 0

    grade_count = db.execute(
        select(func.count()).select_from(Grade).where(Grade.subject == subj)
    ).scalar() or 0

    avg_result = db.execute(
        select(func.avg(Grade.score)).where(Grade.subject == subj)
    ).scalar()
    average_score = round(float(avg_result), 2) if avg_result else 0.0

    row = db.execute(select(
        func.count(Grade.grade_id),
        func.sum(case((Grade.score >= pass_th, 1), else_=0)),
        func.sum(case((Grade.score >= exc_th, 1), else_=0)),
    ).where(Grade.subject == subj)).one()
    total = row[0] or 0
    passed = int(row[1]) if row[1] else 0
    excellent = int(row[2]) if row[2] else 0
    pass_rate = round((passed / total) * 100, 2) if total > 0 else 0.0
    excellent_rate = round((excellent / total) * 100, 2) if total > 0 else 0.0

    return ApiResponse(success=True, data={
        "subject": subj,
        "total_students": student_count,
        "total_grades": grade_count,
        "average_score": average_score,
        "pass_rate": pass_rate,
        "excellent_rate": excellent_rate,
    })


@router.get("/grades")
def get_subject_grades(
    subject: Optional[str] = Query(None),
    class_name: Optional[str] = Query(None),
    exam_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_subject_leader_or_admin),
) -> ApiResponse:
    subj = _get_subject_for_leader(current_user, db, subject)

    filters = [Grade.subject == subj]
    if class_name:
        filters.append(Student.class_name == class_name)
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


@router.get("/statistics")
def get_subject_statistics(
    subject: Optional[str] = Query(None),
    class_name: Optional[str] = Query(None),
    exam_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_subject_leader_or_admin),
) -> ApiResponse:
    subj = _get_subject_for_leader(current_user, db, subject)
    is_major = subj in MAIN_SUBJECTS
    pass_th = MAIN_SUBJECT_PASS if is_major else PASS_SCORE
    exc_th = MAIN_SUBJECT_EXCELLENT if is_major else EXCELLENT_SCORE

    base_filters = [Grade.subject == subj]
    if class_name:
        base_filters.append(Student.class_name == class_name)
    if exam_type:
        base_filters.append(Grade.exam_type == exam_type)

    grade_count = db.execute(
        select(func.count()).select_from(Grade)
        .join(Student, Grade.student_id == Student.student_id)
        .where(and_(*base_filters))
    ).scalar() or 0

    row = db.execute(select(
        func.count(Grade.grade_id),
        func.avg(Grade.score),
        func.max(Grade.score),
        func.min(Grade.score),
        func.sum(case((Grade.score >= pass_th, 1), else_=0)),
        func.sum(case((Grade.score >= exc_th, 1), else_=0)),
    ).join(Student, Grade.student_id == Student.student_id)
      .where(and_(*base_filters))).one()

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
        select(Grade.score).join(Student, Grade.student_id == Student.student_id)
        .where(and_(*base_filters))
    ).all()]
    distribution = {k: 0 for k in dist_keys}
    for s in scores:
        for i, t in enumerate(thresholds):
            if s < t:
                distribution[dist_keys[i]] += 1
                break

    # 各班级对比
    class_filters = [Grade.subject == subj]
    if exam_type:
        class_filters.append(Grade.exam_type == exam_type)

    class_rows = db.execute(
        select(
            Student.class_name,
            func.avg(Grade.score).label("avg"),
            func.max(Grade.score).label("max"),
            func.min(Grade.score).label("min"),
            func.count(Grade.grade_id).label("cnt"),
            func.sum(case((Grade.score >= pass_th, 1), else_=0)).label("passed"),
            func.sum(case((Grade.score >= exc_th, 1), else_=0)).label("excellent"),
        )
        .join(Student, Grade.student_id == Student.student_id)
        .where(and_(*class_filters))
        .group_by(Student.class_name)
        .order_by(Student.class_name)
    ).all()

    class_comparison = [{
        "class_name": cn,
        "average": round(float(avg), 1) if avg else 0,
        "max_score": round(float(mx), 1) if mx else 0,
        "min_score": round(float(mn), 1) if mn else 0,
        "student_count": cnt,
        "pass_rate": round((int(p) / cnt) * 100, 1) if cnt else 0,
        "excellent_rate": round((int(e) / cnt) * 100, 1) if cnt else 0,
    } for cn, avg, mx, mn, cnt, p, e in class_rows]

    # 排名前十
    top_rows = db.execute(
        select(Grade.student_id, Student.name, Student.class_name, Grade.score)
        .join(Student, Grade.student_id == Student.student_id)
        .where(and_(*base_filters))
        .order_by(Grade.score.desc())
        .limit(10)
    ).all()
    top10 = [
        {"rank": i + 1, "student_id": r[0], "student_name": r[1],
         "class_name": r[2], "score": round(float(r[3]), 1)}
        for i, r in enumerate(top_rows)
    ]

    return ApiResponse(success=True, data={
        "subject": subj,
        "grade_count": grade_count,
        "average_score": average,
        "max_score": max_score,
        "min_score": min_score,
        "pass_rate": pass_rate,
        "excellent_rate": excellent_rate,
        "distribution": distribution,
        "class_comparison": class_comparison,
        "top10": top10,
    })
