"""
班主任专用 API 路由

提供班主任角色的专属接口（需要班主任或管理员权限）：
班主任仅可查看自己班级的数据，管理员可查看所有班级数据。

- GET /api/v1/class-teacher/dashboard      班级仪表盘统计
- GET /api/v1/class-teacher/students        班级学生列表
- GET /api/v1/class-teacher/grades          班级成绩列表
- GET /api/v1/class-teacher/statistics/overview  班级统计概览
- GET /api/v1/class-teacher/statistics/subject   班级科目统计
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, case, and_
from sqlalchemy.orm import Session

from src.api.auth import require_class_teacher_or_admin
from src.api.dependencies import get_db
from src.core.constants import (
    PASS_SCORE,
    EXCELLENT_SCORE,
    MAIN_SUBJECTS,
    MAIN_SUBJECT_PASS,
    MAIN_SUBJECT_EXCELLENT,
    TOTAL_PASS_SCORE,
    TOTAL_EXCELLENT_SCORE,
)
from src.models.class_teacher import ClassTeacher
from src.models.exam_total import StudentExamTotal
from src.models.grade import Grade
from src.models.student import Student
from src.models.user import User
from src.repositories.class_teacher_repo import ClassTeacherRepository
from src.repositories.grade_repo import GradeRepository
from src.repositories.student_repo import StudentRepository
from src.schemas.common import ApiResponse

router = APIRouter(prefix="/api/v1/class-teacher", tags=["班主任专用"])


def _get_class_name_for_teacher(
    current_user: User,
    db: Session,
    class_name_param: Optional[str] = None,
) -> str:
    """获取班主任对应的班级名称，管理员可指定班级"""
    if current_user.role == "admin":
        if not class_name_param:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="管理员需指定 class_name 参数",
            )
        return class_name_param

    repo = ClassTeacherRepository(db)
    ct = repo.get_by_user_id(current_user.id)
    if not ct:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到您负责的班级",
        )
    return ct.class_name


# ==================== 仪表盘 ====================


@router.get("/dashboard", response_model=ApiResponse)
def get_class_dashboard(
    class_name: Optional[str] = Query(None, description="班级名称（管理员必填）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_class_teacher_or_admin),
) -> ApiResponse:
    """获取班级仪表盘统计数据"""
    cn = _get_class_name_for_teacher(current_user, db, class_name)

    student_repo = StudentRepository(db)

    student_count = student_repo.count(filters=[Student.class_name == cn])

    # 成绩记录数：通过 student_id 关联 Student 表按班级过滤
    grade_count_stmt = (
        select(func.count())
        .select_from(Grade)
        .join(Student, Grade.student_id == Student.student_id)
        .where(Student.class_name == cn)
    )
    grade_count = db.execute(grade_count_stmt).scalar() or 0

    # 班级平均分（单科平均分的平均值）
    avg_stmt = (
        select(func.avg(Grade.score))
        .join(Student, Grade.student_id == Student.student_id)
        .where(Student.class_name == cn)
    )
    avg_result = db.execute(avg_stmt).scalar()
    average_score = round(float(avg_result), 2) if avg_result else 0.0

    # 及格率和优秀率
    rate_stmt = (
        select(
            func.count(Grade.grade_id).label("total"),
            func.sum(case((Grade.score >= PASS_SCORE, 1), else_=0)).label("passed"),
            func.sum(case((Grade.score >= EXCELLENT_SCORE, 1), else_=0)).label("excellent"),
        )
        .join(Student, Grade.student_id == Student.student_id)
        .where(Student.class_name == cn)
    )
    row = db.execute(rate_stmt).one()
    total = row[0] or 0
    passed = int(row[1]) if row[1] else 0
    excellent = int(row[2]) if row[2] else 0

    pass_rate = round((passed / total) * 100, 2) if total > 0 else 0.0
    excellent_rate = round((excellent / total) * 100, 2) if total > 0 else 0.0

    return ApiResponse(
        success=True,
        data={
            "class_name": cn,
            "total_students": student_count,
            "total_grades": grade_count,
            "average_score": average_score,
            "pass_rate": pass_rate,
            "excellent_rate": excellent_rate,
        },
    )


# ==================== 学生列表 ====================


@router.get("/students", response_model=ApiResponse)
def get_class_students(
    class_name: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_class_teacher_or_admin),
) -> ApiResponse:
    """获取班级学生列表（只读）"""
    cn = _get_class_name_for_teacher(current_user, db, class_name)

    student_repo = StudentRepository(db)
    skip = (page - 1) * page_size

    students = student_repo.get_all(
        skip=skip,
        limit=page_size,
        filters=[Student.class_name == cn],
    )
    total = student_repo.count(filters=[Student.class_name == cn])

    items = []
    for s in students:
        items.append({
            "student_id": s.student_id,
            "name": s.name,
            "gender": s.gender,
            "class_name": s.class_name,
            "enrollment_year": s.enrollment_year,
        })

    return ApiResponse(
        success=True,
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        },
    )


# ==================== 成绩列表 ====================


@router.get("/grades", response_model=ApiResponse)
def get_class_grades(
    class_name: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    exam_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_class_teacher_or_admin),
) -> ApiResponse:
    """获取班级成绩列表（只读）"""
    cn = _get_class_name_for_teacher(current_user, db, class_name)

    # 通过 student_id 关联 Student 表按班级过滤
    base_filters = [Student.class_name == cn]
    if subject:
        base_filters.append(Grade.subject == subject)
    if exam_type:
        base_filters.append(Grade.exam_type == exam_type)

    skip = (page - 1) * page_size

    # 查询总数
    count_stmt = (
        select(func.count())
        .select_from(Grade)
        .join(Student, Grade.student_id == Student.student_id)
        .where(and_(*base_filters))
    )
    total = db.execute(count_stmt).scalar() or 0

    # 查询数据
    stmt = (
        select(Grade, Student.name.label("student_name"))
        .join(Student, Grade.student_id == Student.student_id)
        .where(and_(*base_filters))
        .offset(skip)
        .limit(page_size)
    )
    rows = db.execute(stmt).all()

    items = []
    for g, student_name in rows:
        items.append({
            "grade_id": g.grade_id,
            "student_id": g.student_id,
            "student_name": student_name,
            "subject": g.subject,
            "score": float(g.score),
            "exam_type": g.exam_type,
            "exam_date": g.exam_date.isoformat() if g.exam_date else None,
            "class_name": cn,
        })

    return ApiResponse(
        success=True,
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        },
    )


# ==================== 总分成绩列表 ====================


@router.get("/grades/total", response_model=ApiResponse)
def get_class_grades_total(
    class_name: Optional[str] = Query(None),
    exam_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_class_teacher_or_admin),
) -> ApiResponse:
    """获取班级总分成绩列表（每人一行，各科成绩展开为列）"""
    cn = _get_class_name_for_teacher(current_user, db, class_name)

    # 查询该班级所有成绩，按学生+考试类型+考试日期分组
    stmt = (
        select(
            Grade.student_id,
            Student.name.label("student_name"),
            Grade.exam_type,
            Grade.exam_date,
            Grade.subject,
            Grade.score,
        )
        .join(Student, Grade.student_id == Student.student_id)
        .where(Student.class_name == cn)
    )
    if exam_type:
        stmt = stmt.where(Grade.exam_type == exam_type)
    stmt = stmt.order_by(Grade.student_id, Grade.exam_type, Grade.exam_date, Grade.subject)

    rows = db.execute(stmt).all()

    # 按 student_id + exam_type + exam_date 分组
    from collections import defaultdict
    groups: dict[tuple, dict] = {}
    subjects_set: list[str] = []

    for student_id, student_name, etype, edate, subject, score in rows:
        key = (student_id, etype, edate)
        if key not in groups:
            groups[key] = {
                "student_id": student_id,
                "student_name": student_name,
                "exam_type": etype,
                "exam_date": edate.isoformat() if edate else None,
                "subjects": {},
                "total_score": 0.0,
            }
        groups[key]["subjects"][subject] = float(score)
        groups[key]["total_score"] += float(score)
        if subject not in subjects_set:
            subjects_set.append(subject)

    # 按标准科目顺序排序
    from src.core.constants import SUBJECTS as SUBJECT_ORDER
    subject_order_map = {s: i for i, s in enumerate(SUBJECT_ORDER)}
    ordered_subjects = sorted(subjects_set, key=lambda s: subject_order_map.get(s, 999))

    # 构建分页
    all_items = list(groups.values())
    all_items.sort(key=lambda x: (-x["total_score"], x["student_id"]))
    total = len(all_items)
    skip = (page - 1) * page_size
    page_items = all_items[skip: skip + page_size]

    # 构建返回数据
    items = []
    for item in page_items:
        row = {
            "student_id": item["student_id"],
            "student_name": item["student_name"],
            "exam_type": item["exam_type"],
            "exam_date": item["exam_date"],
            "total_score": round(item["total_score"], 1),
        }
        for subj in ordered_subjects:
            row[subj] = item["subjects"].get(subj)
        items.append(row)

    return ApiResponse(
        success=True,
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "subjects": ordered_subjects,
        },
    )


# ==================== 统计概览 ====================


@router.get("/statistics/overview", response_model=ApiResponse)
def get_class_statistics_overview(
    class_name: Optional[str] = Query(None),
    exam_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_class_teacher_or_admin),
) -> ApiResponse:
    """获取班级统计概览"""
    cn = _get_class_name_for_teacher(current_user, db, class_name)

    student_count = db.execute(
        select(func.count()).select_from(Student).where(Student.class_name == cn)
    ).scalar() or 0

    grade_count = db.execute(
        select(func.count())
        .select_from(Grade)
        .join(Student, Grade.student_id == Student.student_id)
        .where(Student.class_name == cn)
    ).scalar() or 0

    avg_stmt = (
        select(func.avg(Grade.score))
        .join(Student, Grade.student_id == Student.student_id)
        .where(Student.class_name == cn)
    )
    if exam_type:
        avg_stmt = avg_stmt.where(Grade.exam_type == exam_type)
    avg_result = db.execute(avg_stmt).scalar()
    average_score = round(float(avg_result), 2) if avg_result else 0.0

    rate_stmt = (
        select(
            func.count(Grade.grade_id).label("total"),
            func.sum(case((Grade.score >= PASS_SCORE, 1), else_=0)).label("passed"),
            func.sum(case((Grade.score >= EXCELLENT_SCORE, 1), else_=0)).label("excellent"),
        )
        .join(Student, Grade.student_id == Student.student_id)
        .where(Student.class_name == cn)
    )
    if exam_type:
        rate_stmt = rate_stmt.where(Grade.exam_type == exam_type)
    row = db.execute(rate_stmt).one()
    total = row[0] or 0
    passed = int(row[1]) if row[1] else 0
    excellent = int(row[2]) if row[2] else 0
    pass_rate = round((passed / total) * 100, 2) if total > 0 else 0.0
    excellent_rate = round((excellent / total) * 100, 2) if total > 0 else 0.0

    total_stmt = (
        select(
            func.count().label("total"),
            func.sum(case((StudentExamTotal.total_score >= TOTAL_PASS_SCORE, 1), else_=0)).label("passed"),
            func.sum(case((StudentExamTotal.total_score >= TOTAL_EXCELLENT_SCORE, 1), else_=0)).label("excellent"),
            func.avg(StudentExamTotal.total_score).label("avg_total"),
            func.max(StudentExamTotal.total_score).label("max_total"),
        )
        .join(Student, StudentExamTotal.student_id == Student.student_id)
        .where(Student.class_name == cn)
    )
    if exam_type:
        total_stmt = total_stmt.where(StudentExamTotal.exam_type == exam_type)
    total_row = db.execute(total_stmt).one()

    total_exam_count = total_row[0] or 0
    total_pass = int(total_row[1]) if total_row[1] else 0
    total_excellent = int(total_row[2]) if total_row[2] else 0
    total_pass_rate = round((total_pass / total_exam_count) * 100, 2) if total_exam_count > 0 else 0.0
    total_excellent_rate = round((total_excellent / total_exam_count) * 100, 2) if total_exam_count > 0 else 0.0
    avg_total = round(float(total_row[3]), 1) if total_row[3] else 0.0
    max_total = round(float(total_row[4]), 1) if total_row[4] else 0.0

    dist_stmt = (
        select(StudentExamTotal.total_score)
        .join(Student, StudentExamTotal.student_id == Student.student_id)
        .where(Student.class_name == cn)
    )
    if exam_type:
        dist_stmt = dist_stmt.where(StudentExamTotal.exam_type == exam_type)
    scores = [float(r[0]) for r in db.execute(dist_stmt).all()]
    total_distribution = {}
    if scores:
        bins = [(0, 449), (450, 549), (550, 629), (630, 674), (675, 800)]
        labels = ["0-449", "450-549", "550-629", "630-674", "675-800"]
        for i, (lo, hi) in enumerate(bins):
            total_distribution[labels[i]] = sum(1 for s in scores if lo <= s <= hi)

    exam_type_stmt = (
        select(StudentExamTotal.exam_type, func.count().label("cnt"))
        .join(Student, StudentExamTotal.student_id == Student.student_id)
        .where(Student.class_name == cn)
        .group_by(StudentExamTotal.exam_type)
    )
    exam_types = [{"type": r[0], "count": r[1]} for r in db.execute(exam_type_stmt).all()]

    trend_stmt = (
        select(
            StudentExamTotal.exam_type,
            func.avg(StudentExamTotal.total_score).label("avg"),
            func.max(StudentExamTotal.total_score).label("max"),
        )
        .join(Student, StudentExamTotal.student_id == Student.student_id)
        .where(Student.class_name == cn)
        .group_by(StudentExamTotal.exam_type)
        .order_by(StudentExamTotal.exam_type)
    )
    trend = [{"exam_type": r[0], "avg_total": round(float(r[1]), 1) if r[1] else 0, "max_total": round(float(r[2]), 1) if r[2] else 0} for r in db.execute(trend_stmt).all()]

    subj_stmt = (
        select(Grade.subject, func.avg(Grade.score).label("avg"))
        .join(Student, Grade.student_id == Student.student_id)
        .where(Student.class_name == cn)
    )
    if exam_type:
        subj_stmt = subj_stmt.where(Grade.exam_type == exam_type)
    subj_stmt = subj_stmt.group_by(Grade.subject)
    subject_averages = [{"subject": r[0], "average": round(float(r[1]), 1) if r[1] else 0} for r in db.execute(subj_stmt).all()]

    radar_data = []
    for sa in subject_averages:
        subj = sa["subject"]
        is_major = subj in MAIN_SUBJECTS
        pass_th = MAIN_SUBJECT_PASS if is_major else PASS_SCORE
        exc_th = MAIN_SUBJECT_EXCELLENT if is_major else EXCELLENT_SCORE

        subj_rate_stmt = (
            select(
                func.count().label("total"),
                func.sum(case((Grade.score >= pass_th, 1), else_=0)).label("passed"),
                func.sum(case((Grade.score >= exc_th, 1), else_=0)).label("excellent"),
            )
            .join(Student, Grade.student_id == Student.student_id)
            .where(Student.class_name == cn, Grade.subject == subj)
        )
        if exam_type:
            subj_rate_stmt = subj_rate_stmt.where(Grade.exam_type == exam_type)
        sr = db.execute(subj_rate_stmt).one()
        st = sr[0] or 0
        sp = int(sr[1]) if sr[1] else 0
        se = int(sr[2]) if sr[2] else 0
        radar_data.append({
            "subject": subj,
            "average": sa["average"],
            "pass_rate": round((sp / st) * 100, 1) if st > 0 else 0,
            "excellent_rate": round((se / st) * 100, 1) if st > 0 else 0,
        })

    ranking_stmt = (
        select(
            StudentExamTotal.student_id,
            Student.name.label("student_name"),
            StudentExamTotal.total_score,
        )
        .join(Student, StudentExamTotal.student_id == Student.student_id)
        .where(Student.class_name == cn)
    )
    if exam_type:
        ranking_stmt = ranking_stmt.where(StudentExamTotal.exam_type == exam_type)
    ranking_stmt = ranking_stmt.order_by(StudentExamTotal.total_score.desc()).limit(10)
    top10_total = [{"rank": i + 1, "student_id": r[0], "student_name": r[1], "total_score": round(float(r[2]), 1)} for i, r in enumerate(db.execute(ranking_stmt).all())]

    subj_ranking_data = []
    for subj_info in subject_averages:
        subj = subj_info["subject"]
        sr_stmt = (
            select(Grade.student_id, Student.name.label("student_name"), Grade.score)
            .join(Student, Grade.student_id == Student.student_id)
            .where(Student.class_name == cn, Grade.subject == subj)
        )
        if exam_type:
            sr_stmt = sr_stmt.where(Grade.exam_type == exam_type)
        sr_stmt = sr_stmt.order_by(Grade.score.desc()).limit(10)
        top_list = [{"rank": i + 1, "student_id": r[0], "student_name": r[1], "score": round(float(r[2]), 1)} for i, r in enumerate(db.execute(sr_stmt).all())]
        subj_ranking_data.append({"subject": subj, "top10": top_list})

    return ApiResponse(
        success=True,
        data={
            "class_name": cn,
            "exam_type": exam_type,
            "student_count": student_count,
            "grade_count": grade_count,
            "average_score": average_score,
            "pass_rate": pass_rate,
            "excellent_rate": excellent_rate,
            "exam_count": total_exam_count,
            "avg_total_score": avg_total,
            "max_total_score": max_total,
            "total_pass_rate": total_pass_rate,
            "total_excellent_rate": total_excellent_rate,
            "total_distribution": total_distribution,
            "exam_types": exam_types,
            "total_trend": trend,
            "subject_averages": subject_averages,
            "subject_radar": radar_data,
            "top10_total": top10_total,
            "top10_subjects": subj_ranking_data,
        },
    )


# ==================== 科目统计 ====================


@router.get("/statistics/subject", response_model=ApiResponse)
def get_class_subject_statistics(
    class_name: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    exam_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_class_teacher_or_admin),
) -> ApiResponse:
    """获取班级科目统计信息（只读）"""
    cn = _get_class_name_for_teacher(current_user, db, class_name)

    from src.services.statistics_service import StatisticsService
    service = StatisticsService(db)
    result = service.get_batch_subject_statistics(
        class_name=cn,
        exam_type=exam_type,
    )

    return ApiResponse(success=True, data=result)
