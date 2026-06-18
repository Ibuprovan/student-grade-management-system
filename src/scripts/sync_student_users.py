"""
同步学生用户账号脚本

为已有的学生记录创建对应的登录账号。
用户名为学号，初始密码为 123456。

使用方式：
    python -m src.scripts.sync_student_users
"""

import sys
import logging

from sqlalchemy.orm import Session

from src.core.database import SessionLocal, init_db
from src.core.security import hash_password
from src.models.user import User
from src.models.student import Student

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sync_student_users(db: Session) -> None:
    """
    同步学生用户账号

    为所有没有对应用户账号的学生创建登录账号。

    Args:
        db: 数据库会话
    """
    # 获取所有学生
    students = db.query(Student).all()
    logger.info(f"找到 {len(students)} 名学生")

    # 获取所有学生角色的用户
    existing_users = db.query(User).filter(User.role == "student").all()
    existing_usernames = {user.username for user in existing_users}
    logger.info(f"找到 {len(existing_users)} 个学生用户账号")

    # 为没有账号的学生创建用户
    created_count = 0
    skipped_count = 0

    for student in students:
        if student.student_id in existing_usernames:
            logger.debug(f"学生 {student.student_id} ({student.name}) 已有账号，跳过")
            skipped_count += 1
            continue

        # 创建用户账号
        new_user = User(
            username=student.student_id,
            hashed_password=hash_password("123456"),
            role="student",
            is_active=True,
            need_change_password=True,
        )
        db.add(new_user)
        created_count += 1
        logger.info(f"为学生 {student.student_id} ({student.name}) 创建账号")

    # 提交事务
    try:
        db.commit()
        logger.info(f"同步完成：创建 {created_count} 个账号，跳过 {skipped_count} 个已有账号")
    except Exception as e:
        db.rollback()
        logger.error(f"同步失败: {e}")
        raise


def main():
    """主函数"""
    logger.info("初始化数据库...")
    init_db()

    logger.info("同步学生用户账号...")
    db = SessionLocal()
    try:
        sync_student_users(db)
    finally:
        db.close()

    logger.info("=" * 50)
    logger.info("学生用户账号同步完成！")
    logger.info("")
    logger.info("所有学生的登录信息：")
    logger.info("  用户名：学号（如：20260001）")
    logger.info("  初始密码：123456")
    logger.info("")
    logger.info("⚠️  安全提醒：请提醒学生登录后尽快修改密码！")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
