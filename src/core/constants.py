"""
常量定义模块

定义系统中使用的枚举值和常量
"""

from typing import List

# ==================== 业务常量 ====================

# 科目列表
SUBJECTS: List[str] = [
    "语文",
    "数学",
    "英语",
    "物理",
    "化学",
    "生物",
    "历史",
    "地理",
    "政治",
]

# 考试类型
EXAM_TYPES: List[str] = [
    "期中",
    "期末",
    "月考",
    "单元测试",
]

# 性别选项
GENDERS: List[str] = [
    "男",
    "女",
]

# ==================== 数值范围常量 ====================

# 分数范围
SCORE_MIN: float = 0.0
SCORE_MAX: float = 100.0

# 及格分数线
PASS_SCORE: float = 60.0

# 优秀分数线
EXCELLENT_SCORE: float = 90.0

# ==================== 格式常量 ====================

# 学号正则表达式：4位年份 + 4位序号（如：20260001）
STUDENT_ID_PATTERN: str = r"^\d{4}\d{4}$"

# 学号长度
STUDENT_ID_LENGTH: int = 8

# 姓名长度范围
NAME_MIN_LENGTH: int = 2
NAME_MAX_LENGTH: int = 20

# 班级名称长度范围
CLASS_NAME_MIN_LENGTH: int = 2
CLASS_NAME_MAX_LENGTH: int = 20

# 入学年份范围
ENROLLMENT_YEAR_MIN: int = 2000
ENROLLMENT_YEAR_MAX: int = 2100

# ==================== 统计指标常量 ====================

class StatisticsMetric:
    """统计指标枚举"""
    AVG = "avg"              # 平均分
    MAX = "max"              # 最高分
    MIN = "min"              # 最低分
    PASS_RATE = "pass_rate"  # 及格率
    EXCELLENT_RATE = "excellent_rate"  # 优秀率
    MEDIAN = "median"        # 中位数
    STD_DEV = "std_dev"      # 标准差

    ALL_METRICS = [AVG, MAX, MIN, PASS_RATE, EXCELLENT_RATE, MEDIAN, STD_DEV]
