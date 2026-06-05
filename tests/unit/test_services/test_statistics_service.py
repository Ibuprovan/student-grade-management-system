"""
StatisticsService 单元测试

测试统计分析业务逻辑层的所有功能，包括：
- 平均分计算
- 最高分/最低分查询
- 及格率/优秀率计算
- 分数分布统计
- 综合统计报告
- 单科排名
- 总分排名
"""

from datetime import date

import pytest

from src.models.student import Student
from src.models.grade import Grade
from src.schemas.grade import GradeCreate
from src.schemas.student import StudentCreate
from src.services.grade_service import GradeService
from src.services.statistics_service import StatisticsService
from src.services.student_service import StudentService


class TestStatisticsService:
    """StatisticsService 测试类"""

    def _create_student(self, db_session, student_data: dict) -> Student:
        """辅助方法：创建学生"""
        service = StudentService(db_session)
        return service.create_student(StudentCreate(**student_data))

    def _create_grade(self, db_session, grade_data: dict) -> Grade:
        """辅助方法：创建成绩"""
        service = GradeService(db_session)
        return service.create_grade(GradeCreate(**grade_data))

    def _setup_test_data(self, db_session):
        """辅助方法：创建测试数据"""
        # 创建学生
        students = [
            {"student_id": "20260001", "name": "张三", "gender": "男", "class_name": "三年一班", "enrollment_year": 2026},
            {"student_id": "20260002", "name": "李四", "gender": "女", "class_name": "三年一班", "enrollment_year": 2026},
            {"student_id": "20260003", "name": "王五", "gender": "男", "class_name": "三年一班", "enrollment_year": 2026},
            {"student_id": "20260004", "name": "赵六", "gender": "女", "class_name": "三年二班", "enrollment_year": 2026},
            {"student_id": "20260005", "name": "钱七", "gender": "男", "class_name": "三年二班", "enrollment_year": 2026},
        ]
        for student_data in students:
            self._create_student(db_session, student_data)

        # 创建成绩
        grades = [
            {"student_id": "20260001", "subject": "数学", "score": 95.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)},
            {"student_id": "20260001", "subject": "语文", "score": 88.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)},
            {"student_id": "20260002", "subject": "数学", "score": 72.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)},
            {"student_id": "20260002", "subject": "语文", "score": 91.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)},
            {"student_id": "20260003", "subject": "数学", "score": 58.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)},
            {"student_id": "20260003", "subject": "语文", "score": 65.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)},
            {"student_id": "20260004", "subject": "数学", "score": 85.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)},
            {"student_id": "20260004", "subject": "语文", "score": 78.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)},
            {"student_id": "20260005", "subject": "数学", "score": 45.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)},
            {"student_id": "20260005", "subject": "语文", "score": 82.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)},
        ]
        for grade_data in grades:
            self._create_grade(db_session, grade_data)

    # ==================== 平均分测试 ====================

    def test_get_average_all(self, db_session):
        """测试计算所有成绩的平均分"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_average()

        assert result["count"] == 10
        # 总分: 95+88+72+91+58+65+85+78+45+82 = 759
        # 平均分: 759/10 = 75.9
        assert result["average"] == 75.9

    def test_get_average_by_class(self, db_session):
        """测试计算班级平均分"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_average(class_name="三年一班")

        assert result["count"] == 6
        # 三年一班总分: 95+88+72+91+58+65 = 469
        # 平均分: 469/6 ≈ 78.17
        assert result["average"] == 78.17

    def test_get_average_by_subject(self, db_session):
        """测试计算科目平均分"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_average(subject="数学")

        assert result["count"] == 5
        # 数学总分: 95+72+58+85+45 = 355
        # 平均分: 355/5 = 71.0
        assert result["average"] == 71.0

    def test_get_average_by_class_and_subject(self, db_session):
        """测试计算班级科目平均分"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_average(class_name="三年一班", subject="数学")

        assert result["count"] == 3
        # 三年一班数学: 95+72+58 = 225
        # 平均分: 225/3 = 75.0
        assert result["average"] == 75.0

    def test_get_average_empty(self, db_session):
        """测试无数据时计算平均分"""
        service = StatisticsService(db_session)

        result = service.get_average()

        assert result["count"] == 0
        assert result["average"] == 0.0

    # ==================== 最高分测试 ====================

    def test_get_max_score_all(self, db_session):
        """测试获取所有成绩的最高分"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_max_score()

        assert result["max_score"] == 95.0
        assert result["student_id"] == "20260001"
        assert result["student_name"] == "张三"

    def test_get_max_score_by_class(self, db_session):
        """测试获取班级最高分"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_max_score(class_name="三年二班")

        assert result["max_score"] == 85.0
        assert result["student_id"] == "20260004"

    def test_get_max_score_by_subject(self, db_session):
        """测试获取科目最高分"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_max_score(subject="语文")

        assert result["max_score"] == 91.0
        assert result["student_id"] == "20260002"

    def test_get_max_score_empty(self, db_session):
        """测试无数据时获取最高分"""
        service = StatisticsService(db_session)

        result = service.get_max_score()

        assert result["max_score"] == 0.0
        assert result["student_id"] is None

    # ==================== 最低分测试 ====================

    def test_get_min_score_all(self, db_session):
        """测试获取所有成绩的最低分"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_min_score()

        assert result["min_score"] == 45.0
        assert result["student_id"] == "20260005"

    def test_get_min_score_by_class(self, db_session):
        """测试获取班级最低分"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_min_score(class_name="三年一班")

        assert result["min_score"] == 58.0
        assert result["student_id"] == "20260003"

    def test_get_min_score_empty(self, db_session):
        """测试无数据时获取最低分"""
        service = StatisticsService(db_session)

        result = service.get_min_score()

        assert result["min_score"] == 0.0
        assert result["student_id"] is None

    # ==================== 及格率测试 ====================

    def test_get_pass_rate_all(self, db_session):
        """测试计算所有成绩的及格率"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_pass_rate()

        assert result["total_count"] == 10
        # 及格（>=60）: 95,88,72,91,65,85,78,82 = 8人
        assert result["passed_count"] == 8
        assert result["pass_rate"] == 80.0

    def test_get_pass_rate_by_class(self, db_session):
        """测试计算班级及格率"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_pass_rate(class_name="三年一班")

        assert result["total_count"] == 6
        # 三年一班: 95,88,72,91,58,65 -> 及格: 95,88,72,91,65 = 5人
        assert result["passed_count"] == 5
        assert result["pass_rate"] == round(5 / 6 * 100, 2)

    def test_get_pass_rate_by_subject(self, db_session):
        """测试计算科目及格率"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_pass_rate(subject="数学")

        assert result["total_count"] == 5
        # 数学: 95,72,58,85,45 -> 及格: 95,72,85 = 3人
        assert result["passed_count"] == 3
        assert result["pass_rate"] == 60.0

    def test_get_pass_rate_empty(self, db_session):
        """测试无数据时计算及格率"""
        service = StatisticsService(db_session)

        result = service.get_pass_rate()

        assert result["total_count"] == 0
        assert result["passed_count"] == 0
        assert result["pass_rate"] == 0.0

    # ==================== 优秀率测试 ====================

    def test_get_excellent_rate_all(self, db_session):
        """测试计算所有成绩的优秀率"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_excellent_rate()

        assert result["total_count"] == 10
        # 优秀（>=90）: 95,91 = 2人
        assert result["excellent_count"] == 2
        assert result["excellent_rate"] == 20.0

    def test_get_excellent_rate_by_class(self, db_session):
        """测试计算班级优秀率"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_excellent_rate(class_name="三年一班")

        assert result["total_count"] == 6
        # 三年一班: 95,88,72,91,58,65 -> 优秀: 95,91 = 2人
        assert result["excellent_count"] == 2
        assert result["excellent_rate"] == round(2 / 6 * 100, 2)

    def test_get_excellent_rate_empty(self, db_session):
        """测试无数据时计算优秀率"""
        service = StatisticsService(db_session)

        result = service.get_excellent_rate()

        assert result["total_count"] == 0
        assert result["excellent_count"] == 0
        assert result["excellent_rate"] == 0.0

    # ==================== 综合统计报告测试 ====================

    def test_get_report_all(self, db_session):
        """测试获取综合统计报告"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_report()

        assert result["statistics"]["count"] == 10
        assert result["statistics"]["average"] == 75.9
        assert result["statistics"]["max_score"] == 95.0
        assert result["statistics"]["min_score"] == 45.0
        assert result["statistics"]["pass_rate"] == 80.0
        assert result["statistics"]["excellent_rate"] == 20.0

        # 检查分数分布
        dist = result["statistics"]["score_distribution"]
        assert dist["0-59"] == 2  # 58, 45
        assert dist["60-69"] == 1  # 65
        assert dist["70-79"] == 2  # 72, 78
        assert dist["80-89"] == 3  # 88, 85, 82
        assert dist["90-100"] == 2  # 95, 91

    def test_get_report_by_class(self, db_session):
        """测试获取班级综合统计报告"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_report(class_name="三年一班")

        assert result["class_name"] == "三年一班"
        assert result["statistics"]["count"] == 6

    def test_get_report_top_students(self, db_session):
        """测试综合统计报告中的优秀学生"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_report(top_n=3)

        assert len(result["top_students"]) == 3
        # 按分数降序: 95, 91, 88
        assert result["top_students"][0]["score"] == 95.0
        assert result["top_students"][0]["student_id"] == "20260001"
        assert result["top_students"][1]["score"] == 91.0
        assert result["top_students"][1]["student_id"] == "20260002"

    def test_get_report_empty(self, db_session):
        """测试无数据时获取综合统计报告"""
        service = StatisticsService(db_session)

        result = service.get_report()

        assert result["statistics"]["count"] == 0
        assert result["statistics"]["average"] == 0.0
        assert result["top_students"] == []

    # ==================== 单科排名测试 ====================

    def test_get_subject_ranking_desc(self, db_session):
        """测试单科排名（降序）"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_subject_ranking(
            subject="数学",
            exam_type="期中",
            order="desc",
        )

        assert result["total_count"] == 5
        rankings = result["rankings"]

        # 验证排序正确（降序）
        assert rankings[0]["score"] == 95.0
        assert rankings[0]["student_id"] == "20260001"
        assert rankings[0]["rank"] == 1

        assert rankings[1]["score"] == 85.0
        assert rankings[1]["student_id"] == "20260004"
        assert rankings[1]["rank"] == 2

    def test_get_subject_ranking_asc(self, db_session):
        """测试单科排名（升序）"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_subject_ranking(
            subject="数学",
            exam_type="期中",
            order="asc",
        )

        rankings = result["rankings"]
        assert rankings[0]["score"] == 45.0
        assert rankings[0]["student_id"] == "20260005"

    def test_get_subject_ranking_by_class(self, db_session):
        """测试班级单科排名"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_subject_ranking(
            subject="数学",
            exam_type="期中",
            class_name="三年一班",
        )

        assert result["total_count"] == 3
        assert result["class_name"] == "三年一班"

    def test_get_subject_ranking_with_limit(self, db_session):
        """测试单科排名限制数量"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_subject_ranking(
            subject="数学",
            exam_type="期中",
            limit=2,
        )

        assert len(result["rankings"]) == 2

    def test_get_subject_ranking_empty(self, db_session):
        """测试无数据时单科排名"""
        service = StatisticsService(db_session)

        result = service.get_subject_ranking(
            subject="数学",
            exam_type="期中",
        )

        assert result["total_count"] == 0
        assert result["rankings"] == []

    def test_get_subject_ranking_tied_scores(self, db_session):
        """测试并列分数的排名"""
        # 创建学生
        self._create_student(db_session, {"student_id": "20260001", "name": "张三", "gender": "男", "class_name": "三年一班", "enrollment_year": 2026})
        self._create_student(db_session, {"student_id": "20260002", "name": "李四", "gender": "女", "class_name": "三年一班", "enrollment_year": 2026})
        self._create_student(db_session, {"student_id": "20260003", "name": "王五", "gender": "男", "class_name": "三年一班", "enrollment_year": 2026})

        # 创建相同分数的成绩
        self._create_grade(db_session, {"student_id": "20260001", "subject": "数学", "score": 90.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)})
        self._create_grade(db_session, {"student_id": "20260002", "subject": "数学", "score": 90.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)})
        self._create_grade(db_session, {"student_id": "20260003", "subject": "数学", "score": 80.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)})

        service = StatisticsService(db_session)
        result = service.get_subject_ranking(
            subject="数学",
            exam_type="期中",
        )

        rankings = result["rankings"]
        # 前两名并列第一
        assert rankings[0]["rank"] == 1
        assert rankings[1]["rank"] == 1
        assert rankings[2]["rank"] == 3

    # ==================== 总分排名测试 ====================

    def test_get_total_ranking_desc(self, db_session):
        """测试总分排名（降序）"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_total_ranking(
            exam_type="期中",
            order="desc",
        )

        assert result["total_count"] == 5
        rankings = result["rankings"]

        # 验证排序正确
        # 张三: 95+88 = 183
        # 李四: 72+91 = 163
        # 王五: 58+65 = 123
        # 赵六: 85+78 = 163
        # 钱七: 45+82 = 127

        assert rankings[0]["student_id"] == "20260001"
        assert rankings[0]["total_score"] == 183.0
        assert rankings[0]["rank"] == 1

    def test_get_total_ranking_by_class(self, db_session):
        """测试班级总分排名"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_total_ranking(
            exam_type="期中",
            class_name="三年一班",
        )

        assert result["total_count"] == 3
        assert result["class_name"] == "三年一班"

    def test_get_total_ranking_with_limit(self, db_session):
        """测试总分排名限制数量"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_total_ranking(
            exam_type="期中",
            limit=2,
        )

        assert len(result["rankings"]) == 2

    def test_get_total_ranking_empty(self, db_session):
        """测试无数据时总分排名"""
        service = StatisticsService(db_session)

        result = service.get_total_ranking(exam_type="期中")

        assert result["total_count"] == 0
        assert result["rankings"] == []

    def test_get_total_ranking_subject_scores(self, db_session):
        """测试总分排名包含各科成绩"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_total_ranking(exam_type="期中")

        # 检查第一个学生的各科成绩
        first_student = result["rankings"][0]
        assert "数学" in first_student["subject_scores"]
        assert "语文" in first_student["subject_scores"]

    # ==================== 通用统计指标测试 ====================

    def test_get_statistics_metrics_avg(self, db_session):
        """测试获取平均分指标"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_statistics_metrics(metrics=["avg"])

        assert "avg" in result["metrics"]
        assert result["metrics"]["avg"] == 75.9

    def test_get_statistics_metrics_multiple(self, db_session):
        """测试获取多个统计指标"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_statistics_metrics(metrics=["avg", "max", "min", "pass_rate"])

        assert "avg" in result["metrics"]
        assert "max" in result["metrics"]
        assert "min" in result["metrics"]
        assert "pass_rate" in result["metrics"]

    def test_get_statistics_metrics_median(self, db_session):
        """测试获取中位数指标"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_statistics_metrics(metrics=["median"])

        assert "median" in result["metrics"]
        # 10个成绩排序: 45,58,65,72,78,82,85,88,91,95
        # 中位数: (78+82)/2 = 80.0
        assert result["metrics"]["median"] == 80.0

    def test_get_statistics_metrics_std_dev(self, db_session):
        """测试获取标准差指标"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_statistics_metrics(metrics=["std_dev"])

        assert "std_dev" in result["metrics"]
        assert result["metrics"]["std_dev"] > 0

    def test_get_statistics_metrics_with_filters(self, db_session):
        """测试带筛选条件的统计指标"""
        self._setup_test_data(db_session)
        service = StatisticsService(db_session)

        result = service.get_statistics_metrics(
            class_name="三年一班",
            subject="数学",
            metrics=["avg", "max"],
        )

        assert result["total_students"] == 3
        assert result["metrics"]["avg"] == 75.0
        assert result["metrics"]["max"] == 95.0

    def test_get_statistics_metrics_empty(self, db_session):
        """测试无数据时获取统计指标"""
        service = StatisticsService(db_session)

        result = service.get_statistics_metrics()

        assert result["total_students"] == 0
        assert result["metrics"] == {}

    # ==================== 边界条件测试 ====================

    def test_all_students_pass(self, db_session):
        """测试所有学生都及格的情况"""
        # 创建学生
        self._create_student(db_session, {"student_id": "20260001", "name": "张三", "gender": "男", "class_name": "三年一班", "enrollment_year": 2026})
        self._create_student(db_session, {"student_id": "20260002", "name": "李四", "gender": "女", "class_name": "三年一班", "enrollment_year": 2026})

        # 所有成绩都及格
        self._create_grade(db_session, {"student_id": "20260001", "subject": "数学", "score": 90.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)})
        self._create_grade(db_session, {"student_id": "20260002", "subject": "数学", "score": 85.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)})

        service = StatisticsService(db_session)
        result = service.get_pass_rate()

        assert result["pass_rate"] == 100.0
        assert result["passed_count"] == 2

    def test_no_students_pass(self, db_session):
        """测试所有学生都不及格的情况"""
        # 创建学生
        self._create_student(db_session, {"student_id": "20260001", "name": "张三", "gender": "男", "class_name": "三年一班", "enrollment_year": 2026})
        self._create_student(db_session, {"student_id": "20260002", "name": "李四", "gender": "女", "class_name": "三年一班", "enrollment_year": 2026})

        # 所有成绩都不及格
        self._create_grade(db_session, {"student_id": "20260001", "subject": "数学", "score": 50.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)})
        self._create_grade(db_session, {"student_id": "20260002", "subject": "数学", "score": 45.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)})

        service = StatisticsService(db_session)
        result = service.get_pass_rate()

        assert result["pass_rate"] == 0.0
        assert result["passed_count"] == 0

    def test_all_students_excellent(self, db_session):
        """测试所有学生都优秀的情况"""
        # 创建学生
        self._create_student(db_session, {"student_id": "20260001", "name": "张三", "gender": "男", "class_name": "三年一班", "enrollment_year": 2026})
        self._create_student(db_session, {"student_id": "20260002", "name": "李四", "gender": "女", "class_name": "三年一班", "enrollment_year": 2026})

        # 所有成绩都优秀
        self._create_grade(db_session, {"student_id": "20260001", "subject": "数学", "score": 95.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)})
        self._create_grade(db_session, {"student_id": "20260002", "subject": "数学", "score": 98.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)})

        service = StatisticsService(db_session)
        result = service.get_excellent_rate()

        assert result["excellent_rate"] == 100.0
        assert result["excellent_count"] == 2

    def test_score_at_boundary_pass(self, db_session):
        """测试及格边界分数（60分）"""
        self._create_student(db_session, {"student_id": "20260001", "name": "张三", "gender": "男", "class_name": "三年一班", "enrollment_year": 2026})
        self._create_grade(db_session, {"student_id": "20260001", "subject": "数学", "score": 60.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)})

        service = StatisticsService(db_session)
        result = service.get_pass_rate()

        assert result["passed_count"] == 1
        assert result["pass_rate"] == 100.0

    def test_score_at_boundary_excellent(self, db_session):
        """测试优秀边界分数（90分）"""
        self._create_student(db_session, {"student_id": "20260001", "name": "张三", "gender": "男", "class_name": "三年一班", "enrollment_year": 2026})
        self._create_grade(db_session, {"student_id": "20260001", "subject": "数学", "score": 90.0, "exam_type": "期中", "exam_date": date(2026, 4, 15)})

        service = StatisticsService(db_session)
        result = service.get_excellent_rate()

        assert result["excellent_count"] == 1
        assert result["excellent_rate"] == 100.0
