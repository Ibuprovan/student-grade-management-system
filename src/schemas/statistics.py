"""
统计分析 Schema

定义统计分析相关的 Pydantic 模式，用于请求/响应数据验证
"""

from enum import Enum
from typing import Optional, List, Dict

from pydantic import BaseModel, ConfigDict, Field


class StatisticsMetric(str, Enum):
    """统计指标枚举"""

    AVG = "avg"
    MAX = "max"
    MIN = "min"
    PASS_RATE = "pass_rate"
    EXCELLENT_RATE = "excellent_rate"
    MEDIAN = "median"
    STD_DEV = "std_dev"


class StatisticsQuery(BaseModel):
    """统计查询模式"""

    class_name: Optional[str] = Field(None, description="班级名称")
    subject: Optional[str] = Field(None, description="科目名称")
    exam_type: Optional[str] = Field(None, description="考试类型")
    metrics: List[StatisticsMetric] = Field(
        default=[
            StatisticsMetric.AVG,
            StatisticsMetric.MAX,
            StatisticsMetric.MIN,
            StatisticsMetric.PASS_RATE,
        ],
        description="需要计算的统计指标列表",
    )


class AverageResponse(BaseModel):
    """平均分统计响应"""

    average: float = Field(description="平均分")
    count: int = Field(description="参与统计的人数")
    subject: Optional[str] = Field(None, description="科目")
    exam_type: Optional[str] = Field(None, description="考试类型")
    class_name: Optional[str] = Field(None, description="班级")


class MaxScoreResponse(BaseModel):
    """最高分统计响应"""

    max_score: float = Field(description="最高分")
    student_id: Optional[str] = Field(None, description="最高分学生学号")
    student_name: Optional[str] = Field(None, description="最高分学生姓名")
    subject: Optional[str] = Field(None, description="科目")
    exam_type: Optional[str] = Field(None, description="考试类型")
    class_name: Optional[str] = Field(None, description="班级")


class MinScoreResponse(BaseModel):
    """最低分统计响应"""

    min_score: float = Field(description="最低分")
    student_id: Optional[str] = Field(None, description="最低分学生学号")
    student_name: Optional[str] = Field(None, description="最低分学生姓名")
    subject: Optional[str] = Field(None, description="科目")
    exam_type: Optional[str] = Field(None, description="考试类型")
    class_name: Optional[str] = Field(None, description="班级")


class PassRateResponse(BaseModel):
    """及格率统计响应"""

    pass_rate: float = Field(description="及格率（百分比）")
    passed_count: int = Field(description="及格人数")
    total_count: int = Field(description="总人数")
    subject: Optional[str] = Field(None, description="科目")
    exam_type: Optional[str] = Field(None, description="考试类型")
    class_name: Optional[str] = Field(None, description="班级")


class ExcellentRateResponse(BaseModel):
    """优秀率统计响应"""

    excellent_rate: float = Field(description="优秀率（百分比）")
    excellent_count: int = Field(description="优秀人数")
    total_count: int = Field(description="总人数")
    subject: Optional[str] = Field(None, description="科目")
    exam_type: Optional[str] = Field(None, description="考试类型")
    class_name: Optional[str] = Field(None, description="班级")


class ScoreDistribution(BaseModel):
    """分数分布"""

    range_0_59: int = Field(0, alias="0-59", description="0-59分人数")
    range_60_69: int = Field(0, alias="60-69", description="60-69分人数")
    range_70_79: int = Field(0, alias="70-79", description="70-79分人数")
    range_80_89: int = Field(0, alias="80-89", description="80-89分人数")
    range_90_100: int = Field(0, alias="90-100", description="90-100分人数")

    model_config = ConfigDict(populate_by_name=True)


class TopStudent(BaseModel):
    """优秀学生信息"""

    student_id: str = Field(description="学号")
    name: str = Field(description="姓名")
    score: float = Field(description="分数")


class StatisticsDetail(BaseModel):
    """统计详情"""

    count: int = Field(description="总人数")
    average: float = Field(description="平均分")
    max_score: float = Field(description="最高分")
    min_score: float = Field(description="最低分")
    pass_rate: float = Field(description="及格率")
    excellent_rate: float = Field(description="优秀率")
    score_distribution: Dict[str, int] = Field(description="分数分布")


class ReportResponse(BaseModel):
    """综合统计报告响应"""

    class_name: Optional[str] = Field(None, description="班级")
    subject: Optional[str] = Field(None, description="科目")
    exam_type: Optional[str] = Field(None, description="考试类型")
    statistics: StatisticsDetail = Field(description="统计数据")
    top_students: List[TopStudent] = Field(description="优秀学生列表")


class RankingItem(BaseModel):
    """排名项"""

    rank: int = Field(description="排名")
    student_id: str = Field(description="学号")
    student_name: str = Field(description="学生姓名")
    score: float = Field(description="分数")


class RankingResponse(BaseModel):
    """排名响应模式"""

    subject: Optional[str] = Field(None, description="科目")
    exam_type: Optional[str] = Field(None, description="考试类型")
    class_name: Optional[str] = Field(None, description="班级")
    total_count: int = Field(description="参与排名的总人数")
    rankings: List[RankingItem] = Field(description="排名列表")


class TotalRankingItem(BaseModel):
    """总分排名项"""

    rank: int = Field(description="排名")
    student_id: str = Field(description="学号")
    student_name: str = Field(description="学生姓名")
    total_score: float = Field(description="总分")
    subject_scores: Dict[str, float] = Field(description="各科成绩")


class TotalRankingResponse(BaseModel):
    """总分排名响应"""

    exam_type: Optional[str] = Field(None, description="考试类型")
    class_name: Optional[str] = Field(None, description="班级")
    total_count: int = Field(description="参与排名的总人数")
    rankings: List[TotalRankingItem] = Field(description="排名列表")


class StatisticsResponse(BaseModel):
    """通用统计响应"""

    query: Dict = Field(description="查询条件")
    total_students: int = Field(description="参与统计的学生数")
    metrics: Dict = Field(description="统计指标结果")
