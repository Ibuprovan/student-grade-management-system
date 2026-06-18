"""
初始化默认用户脚本

首次运行时创建默认管理员账户。
默认账户信息：
- 用户名: admin
- 密码: admin123
- 角色: admin

⚠️ 安全提醒：生产环境部署后请立即修改默认密码！

使用方式：
    python -m src.scripts.init_users
"""

import sys
import logging

from sqlalchemy.orm import Session

from src.core.database import SessionLocal, init_db
from src.core.security import hash_password
from src.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 默认用户配置
DEFAULT_USERS = [
    {
        "username": "admin",
        "password": "admin123",
        "role": "admin",
        "need_change_password": False,
    },
    {
        "username": "teacher",
        "password": "teacher123",
        "role": "teacher",
        "need_change_password": False,
    },
    {
        "username": "student",
        "password": "student123",
        "role": "student",
        "need_change_password": False,
    },
]


def init_users(db: Session) -> None:
    """
    初始化默认用户

    检查用户是否已存在，不存在则创建。

    Args:
        db: 数据库会话
    """
    for user_data in DEFAULT_USERS:
        # 检查用户是否已存在
        existing_user = db.query(User).filter(
            User.username == user_data["username"]
        ).first()

        if existing_user:
            logger.info(f"用户 '{user_data['username']}' 已存在，跳过创建")
            continue

        # 创建新用户
        new_user = User(
            username=user_data["username"],
            hashed_password=hash_password(user_data["password"]),
            role=user_data["role"],
            is_active=True,
            need_change_password=user_data.get("need_change_password", False),
        )
        db.add(new_user)
        logger.info(f"创建用户: {user_data['username']} (角色: {user_data['role']})")

    db.commit()
    logger.info("默认用户初始化完成")


def main():
    """主函数"""
    logger.info("初始化数据库...")
    init_db()

    logger.info("初始化默认用户...")
    db = SessionLocal()
    try:
        init_users(db)
    finally:
        db.close()

    logger.info("=" * 50)
    logger.info("默认用户创建完成！")
    logger.info("")
    logger.info("默认账户信息：")
    logger.info("  管理员 - 用户名: admin, 密码: admin123")
    logger.info("  教师   - 用户名: teacher, 密码: teacher123")
    logger.info("  学生   - 用户名: student, 密码: student123")
    logger.info("")
    logger.info("班主任账号请在管理员端手动添加")
    logger.info("")
    logger.info("⚠️  安全提醒：生产环境部署后请立即修改默认密码！")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
