"""
生成匿名测试数据

为开发和演示环境生成测试数据，所有学生姓名为匿名化生成，
不包含真实个人信息。

用法：
    python -m src.scripts.seed_demo_data
"""

import logging
import random
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from src.core.database import SessionLocal, init_db
from src.core.security import hash_password
from src.core.constants import SUBJECTS, SUBJECT_EN_MAP
from src.models.user import User
from src.models.student import Student
from src.models.grade import Grade
from src.models.class_teacher import ClassTeacher
from src.models.subject_leader import SubjectLeader
from src.models.teacher_assignment import TeacherAssignment
from src.models.exam_total import StudentExamTotal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NUM_CLASSES = 5
STUDENTS_PER_CLASS = 20

SURNAMES = [
    "张", "李", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴",
    "徐", "孙", "马", "胡", "朱", "郭", "何", "罗", "高", "林",
]
GIVEN_M = ["伟", "强", "磊", "军", "勇", "杰", "涛", "明", "超", "辉"]
GIVEN_F = ["娜", "芳", "秀英", "敏", "静", "丽", "娟", "霞", "玲", "燕"]

TEACHER_FIRST = ["张", "李", "王", "刘", "陈", "杨", "赵"]
TEACHER_LAST = ["老师"]


def _random_name() -> str:
    surname = random.choice(SURNAMES)
    given = random.choice(GIVEN_M + GIVEN_F)
    return surname + given


def _random_gender() -> str:
    return random.choice(["男", "女"])


def _random_score(subject: str) -> float:
    if subject in ("语文", "数学", "英语"):
        max_score = 150.0
    else:
        max_score = 100.0
    score = random.gauss(max_score * 0.65, max_score * 0.15)
    score = max(0, min(max_score, score))
    return round(score, 1)


def seed_demo_data(db: Session) -> None:
    # 检查是否已有数据
    existing = db.query(User).filter(User.role != "admin").count()
    if existing > 0:
        logger.info("数据库已有非管理员用户（%d 个），跳过 seeding", existing)
        return

    now = datetime.now(timezone.utc)
    exam_types = ["期中", "期末"]
    exam_dates = [date(2026, 4, 15), date(2026, 6, 28)]

    # ── Students & Users ──
    logger.info("创建学生和用户账号...")
    students = []
    for class_no in range(1, NUM_CLASSES + 1):
        class_name = f"2026级{class_no}班"
        for seq in range(1, STUDENTS_PER_CLASS + 1):
            sid = f"2026{class_no:02d}{seq:02d}"
            name = _random_name()
            gender = _random_gender()
            student = Student(
                student_id=sid,
                name=name,
                gender=gender,
                class_name=class_name,
                enrollment_year=2026,
                created_at=now,
                updated_at=now,
            )
            db.add(student)
            students.append(student)
            user = User(
                username=sid,
                hashed_password=hash_password("123456"),
                role="student",
                is_active=True,
                need_change_password=False,
                created_at=now,
                updated_at=now,
            )
            db.add(user)
    db.flush()

    # ── Grades & Exam Totals ──
    logger.info("生成成绩记录...")
    for exam_type, exam_date in zip(exam_types, exam_dates):
        for student in students:
            total = 0.0
            for subject in SUBJECTS:
                score = _random_score(subject)
                total += score
                grade = Grade(
                    student_id=student.student_id,
                    subject=subject,
                    score=score,
                    exam_type=exam_type,
                    exam_date=exam_date,
                    created_at=now,
                    updated_at=now,
                )
                db.add(grade)
            total = round(total, 1)
            et = StudentExamTotal(
                student_id=student.student_id,
                exam_type=exam_type,
                exam_date=exam_date,
                total_score=total,
                created_at=now,
                updated_at=now,
            )
            db.add(et)
    db.flush()

    # ── Class Teachers ──
    logger.info("创建班主任账号...")
    for class_no in range(1, NUM_CLASSES + 1):
        username = f"2026{class_no:03d}"
        teacher_name = f"{random.choice(TEACHER_FIRST)}{random.choice(TEACHER_LAST)}"
        user = User(
            username=username,
            hashed_password=hash_password("123456"),
            role="class_teacher",
            is_active=True,
            need_change_password=True,
            created_at=now,
            updated_at=now,
        )
        db.add(user)
        db.flush()
        ct = ClassTeacher(
            user_id=user.id,
            class_name=f"2026级{class_no}班",
            enrollment_year=2026,
            class_number=class_no,
            teacher_name=teacher_name,
            created_at=now,
        )
        db.add(ct)
    db.flush()

    # ── Subject Leaders ──
    logger.info("创建学科组长账号...")
    subjects_for_leaders = ["语文", "数学", "英语", "物理", "化学", "生物"]
    for subject in subjects_for_leaders:
        subject_en = SUBJECT_EN_MAP[subject]
        user = User(
            username=subject_en.lower(),
            hashed_password=hash_password("123456"),
            role="subject_leader",
            is_active=True,
            need_change_password=True,
            created_at=now,
            updated_at=now,
        )
        db.add(user)
        db.flush()
        sl = SubjectLeader(
            user_id=user.id,
            subject=subject,
            subject_en=subject_en,
            leader_name=f"{random.choice(TEACHER_FIRST)}{random.choice(TEACHER_LAST)}",
            created_at=now,
        )
        db.add(sl)
    db.flush()

    # ── Teacher Assignment ──
    logger.info("创建教师任课分配...")
    user = User(
        username="Chinese2026001",
        hashed_password=hash_password("123456"),
        role="teacher",
        is_active=True,
        need_change_password=True,
        created_at=now,
        updated_at=now,
    )
    db.add(user)
    db.flush()
    ta = TeacherAssignment(
        user_id=user.id,
        subject="语文",
        subject_en="Chinese",
        class_name="2026级1班",
        teacher_name=f"{random.choice(TEACHER_FIRST)}老师",
        created_at=now,
    )
    db.add(ta)

    db.commit()
    logger.info("=" * 50)
    logger.info("测试数据生成完成！")
    logger.info("  班级: %d 个", NUM_CLASSES)
    logger.info("  学生: %d 人", len(students))
    logger.info("  成绩: %d 条", len(students) * len(SUBJECTS) * len(exam_types))
    logger.info("  班主任: %d 人", NUM_CLASSES)
    logger.info("  学科组长: %d 人", len(subjects_for_leaders))
    logger.info("  教师: 1 人")
    logger.info("=" * 50)
    logger.info("所有用户初始密码: 123456")
    logger.info("新增非管理员用户首次登录需修改密码")


def main():
    init_db()
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
