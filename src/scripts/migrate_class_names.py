"""
迁移脚本：将班级名称从 '三年X班' 格式改为 '2026级X班' 格式

运行方式：python -m src.scripts.migrate_class_names
"""

import sys
from src.core.database import SessionLocal, init_db
from src.models.student import Student
from src.models.class_teacher import ClassTeacher


# 中文数字 → 阿拉伯数字映射
CN_NUM_MAP = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
}


def convert_class_name(old_name: str, enrollment_year: int) -> str:
    """
    将 '三年一班' 转换为 '2026级1班'

    Args:
        old_name: 旧班级名称（如 "三年一班"）
        enrollment_year: 入学年份（如 2026）

    Returns:
        新班级名称（如 "2026级1班"）
    """
    import re
    # 提取 "年" 和 "班" 之间的部分
    match = re.search(r"年(.+?)班", old_name)
    if match:
        num_str = match.group(1)
        if num_str in CN_NUM_MAP:
            return f"{enrollment_year}级{CN_NUM_MAP[num_str]}班"
        elif num_str.isdigit():
            return f"{enrollment_year}级{num_str}班"
    # 如果格式不匹配，返回原名称
    return old_name


def migrate():
    """执行迁移"""
    init_db()
    db = SessionLocal()

    try:
        # 1. 迁移 students 表
        students = db.query(Student).all()
        student_mapping = {}  # old_name -> new_name

        for s in students:
            old_name = s.class_name
            if old_name not in student_mapping:
                new_name = convert_class_name(old_name, s.enrollment_year)
                student_mapping[old_name] = new_name

        print("=== 学生表班级名称迁移 ===")
        for old_name, new_name in student_mapping.items():
            count = db.query(Student).filter(Student.class_name == old_name).update(
                {"class_name": new_name},
                synchronize_session=False,
            )
            print(f"  {old_name} -> {new_name} ({count} 条记录)")

        # 2. 迁移 class_teachers 表（如果有记录）
        class_teachers = db.query(ClassTeacher).all()
        if class_teachers:
            print("\n=== 班主任表班级名称迁移 ===")
            for ct in class_teachers:
                old_name = ct.class_name
                if old_name in student_mapping:
                    new_name = student_mapping[old_name]
                    ct.class_name = new_name
                    print(f"  {old_name} -> {new_name}")

        db.commit()
        print("\n迁移完成！")

        # 验证
        print("\n=== 验证结果 ===")
        distinct_names = db.query(Student.class_name).distinct().all()
        print(f"当前班级名称: {[n[0] for n in distinct_names]}")

    except Exception as e:
        db.rollback()
        print(f"迁移失败: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
