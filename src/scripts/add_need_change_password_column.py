"""
添加 need_change_password 列到 users 表

使用方式：
    python -m src.scripts.add_need_change_password_column
"""

import logging

from sqlalchemy import text
from src.core.database import SessionLocal, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_column():
    """添加 need_change_password 列到 users 表"""
    db = SessionLocal()
    try:
        # 检查列是否已存在
        result = db.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'need_change_password' in columns:
            logger.info("need_change_password 列已存在，跳过添加")
            return
        
        # 添加列
        db.execute(text("ALTER TABLE users ADD COLUMN need_change_password BOOLEAN NOT NULL DEFAULT 0"))
        db.commit()
        logger.info("成功添加 need_change_password 列到 users 表")
        
    except Exception as e:
        db.rollback()
        logger.error(f"添加列失败: {e}")
        raise
    finally:
        db.close()


def main():
    """主函数"""
    logger.info("初始化数据库...")
    init_db()
    
    logger.info("添加 need_change_password 列...")
    add_column()
    
    logger.info("=" * 50)
    logger.info("列添加完成！")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
