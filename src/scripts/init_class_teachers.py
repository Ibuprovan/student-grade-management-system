"""
初始化班主任脚本

为所有班级创建班主任账号。
"""

import sys
import logging

from sqlalchemy.orm import Session

from src.core.database import SessionLocal, init_db
from src.services.class_teacher_service import ClassTeacherService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_class_teachers(db: Session) -> None:
    """
    初始化班主任账号

    为所有有学生的班级创建班主任账号。
    账号格式：{入学年份}{班级号3位}，如 2026001
    初始密码：123456
    """
    service = ClassTeacherService(db)

    # 查询已有学生的班级
    from src.models.student import Student
    from sqlalchemy import select, func

    stmt = (
        select(
            Student.class_name,
            func.min(Student.enrollment_year).label("enrollment_year"),
        )
        .group_by(Student.class_name)
        .order_by(Student.class_name)
    )
    rows = db.execute(stmt).all()

    if not rows:
        logger.warning("数据库中没有学生数据，无法创建班主任")
        return

    created = 0
    for class_name, enrollment_year in rows:
        # 解析班级号
        year, class_number = service.parse_class_name(class_name)
        if year == 0:
            logger.warning(f"无法解析班级名称: {class_name}，跳过")
            continue

        # 检查是否已有班主任
        existing = service.class_teacher_repo.get_by_class_name(class_name)
        if existing:
            logger.info(f"班级 {class_name} 已有班主任: {existing.teacher_name}，跳过")
            continue

        # 检查用户名是否已存在
        username = service.generate_username(year, class_number)
        if service.user_repo.username_exists(username):
            logger.info(f"账号 {username} 已存在，跳过")
            continue

        try:
            result = service.add_class_teacher(
                class_name=class_name,
                enrollment_year=year,
                class_number=class_number,
                teacher_name=f"班主任{class_number}",
            )
            created += 1
            logger.info(
                f"创建班主任: {class_name} -> "
                f"username={result['username']}, "
                f"password=123456"
            )
        except Exception as e:
            logger.error(f"创建班主任失败 ({class_name}): {e}")

    db.commit()
    logger.info(f"班主任初始化完成，共创建 {created} 个账号")


def main():
    """主函数"""
    logger.info("初始化班主任账号...")
    init_db()

    db = SessionLocal()
    try:
        init_class_teachers(db)
    finally:
        db.close()

    logger.info("=" * 50)
    logger.info("班主任账号信息：")
    logger.info("  2026级1班 -> 用户名: 2026001, 密码: 123456")
    logger.info("  2026级2班 -> 用户名: 2026002, 密码: 123456")
    logger.info("  2026级3班 -> 用户名: 2026003, 密码: 123456")
    logger.info("  2026级4班 -> 用户名: 2026004, 密码: 123456")
    logger.info("  2026级5班 -> 用户名: 2026005, 密码: 123456")
    logger.info("")
    logger.info("⚠️  首次登录后请尽快修改密码！")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
