"""
重新生成学生考试总分脚本

从 Grade 表聚合计算每个学生每次考试的总分，
写入 StudentExamTotal 表。
"""

import sys
import logging
from datetime import date

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.core.database import SessionLocal, init_db
from src.models.grade import Grade
from src.models.student import Student
from src.models.exam_total import StudentExamTotal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def regenerate_exam_totals(db: Session) -> None:
    """
    从 Grade 表聚合生成 StudentExamTotal 记录

    按 student_id + exam_type + exam_date 分组，计算总分
    """
    # 查询所有成绩记录，按学生+考试类型+考试日期分组
    stmt = (
        select(
            Grade.student_id,
            Grade.exam_type,
            Grade.exam_date,
            func.sum(Grade.score).label("total_score"),
        )
        .group_by(Grade.student_id, Grade.exam_type, Grade.exam_date)
    )
    rows = db.execute(stmt).all()

    if not rows:
        logger.warning("没有找到成绩记录，无法生成总分")
        return

    created = 0
    updated = 0
    for student_id, exam_type, exam_date, total_score in rows:
        total_score = round(float(total_score), 1)

        # 检查是否已存在
        existing = db.query(StudentExamTotal).filter(
            StudentExamTotal.student_id == student_id,
            StudentExamTotal.exam_type == exam_type,
            StudentExamTotal.exam_date == exam_date,
        ).first()

        if existing:
            existing.total_score = total_score
            updated += 1
        else:
            record = StudentExamTotal(
                student_id=student_id,
                exam_type=exam_type,
                exam_date=exam_date,
                total_score=total_score,
            )
            db.add(record)
            created += 1

    db.commit()
    logger.info(f"总分记录生成完成: 新增 {created}, 更新 {updated}")


def main():
    """主函数"""
    logger.info("重新生成学生考试总分...")
    init_db()

    db = SessionLocal()
    try:
        regenerate_exam_totals(db)
    finally:
        db.close()

    logger.info("完成!")


if __name__ == "__main__":
    main()
