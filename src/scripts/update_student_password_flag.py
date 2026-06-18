"""
更新学生用户密码修改标志脚本

为所有学生用户设置 need_change_password 为 True。

使用方式：
    python -m src.scripts.update_student_password_flag
"""

import sys
import logging

from sqlalchemy.orm import Session

from src.core.database import SessionLocal, init_db
from src.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_student_password_flag(db: Session) -> None:
    """
    更新学生用户密码修改标志

    为所有学生用户设置 need_change_password 为 True。

    Args:
        db: 数据库会话
    """
    # 获取所有学生角色的用户
    students = db.query(User).filter(User.role == "student").all()
    logger.info(f"找到 {len(students)} 名学生用户")

    updated_count = 0
    for student in students:
        if not student.need_change_password:
            student.need_change_password = True
            updated_count += 1
            logger.info(f"更新学生 {student.username} 的密码修改标志")

    # 提交事务
    try:
        db.commit()
        logger.info(f"更新完成：更新 {updated_count} 名学生的密码修改标志")
    except Exception as e:
        db.rollback()
        logger.error(f"更新失败: {e}")
        raise


def main():
    """主函数"""
    logger.info("初始化数据库...")
    init_db()

    logger.info("更新学生用户密码修改标志...")
    db = SessionLocal()
    try:
        update_student_password_flag(db)
    finally:
        db.close()

    logger.info("=" * 50)
    logger.info("学生用户密码修改标志更新完成！")
    logger.info("")
    logger.info("所有学生首次登录时将被要求修改密码。")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
