"""
统计分析业务逻辑 Service

实现成绩统计分析的核心业务逻辑，包括：
- 平均分、最高分、最低分统计
- 及格率、优秀率统计
- 分数分布统计
- 单科排名、总分排名
- 综合统计报告
"""

import statistics
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy import func, and_, select, case
from sqlalchemy.orm import Session

from src.core.constants import PASS_SCORE, EXCELLENT_SCORE, TOTAL_PASS_SCORE, TOTAL_EXCELLENT_SCORE, MAIN_SUBJECTS, MAIN_SUBJECT_PASS, MAIN_SUBJECT_EXCELLENT
from src.models.grade import Grade
from src.models.student import Student
from src.models.exam_total import StudentExamTotal
from src.repositories.grade_repo import GradeRepository
from src.repositories.student_repo import StudentRepository


class StatisticsService:
    """
    统计分析业务逻辑类

    职责：
    - 处理成绩统计分析的业务逻辑
    - 协调 GradeRepository 进行数据查询和聚合
    - 执行统计指标计算（平均分、及格率、排名等）

    Attributes:
        grade_repo: GradeRepository 实例
        student_repo: StudentRepository 实例
        db: 数据库会话
    """

    def __init__(self, db: Session):
        """
        初始化 StatisticsService

        Args:
            db: SQLAlchemy 数据库会话
        """
        self.grade_repo = GradeRepository(db)
        self.student_repo = StudentRepository(db)
        self.db = db

    def _build_filters(
        self,
        class_name: Optional[str] = None,
        subject: Optional[str] = None,
        exam_type: Optional[str] = None,
    ) -> List:
        """
        构建查询过滤条件

        Args:
            class_name: 班级名称（可选）
            subject: 科目名称（可选）
            exam_type: 考试类型（可选）

        Returns:
            List: 过滤条件列表
        """
        filters = []
        if class_name:
            filters.append(Student.class_name == class_name)
        if subject:
            filters.append(Grade.subject == subject)
        if exam_type:
            filters.append(Grade.exam_type == exam_type)
        return filters

    def _get_scores(
        self,
        class_name: Optional[str] = None,
        subject: Optional[str] = None,
        exam_type: Optional[str] = None,
    ) -> List[Tuple[float, str, str]]:
        """
        获取符合条件的成绩列表

        Args:
            class_name: 班级名称（可选）
            subject: 科目名称（可选）
            exam_type: 考试类型（可选）

        Returns:
            List[Tuple[float, str, str]]: (分数, 学号, 学生姓名) 列表
        """
        stmt = (
            select(Grade.score, Grade.student_id, Student.name)
            .join(Student, Grade.student_id == Student.student_id)
        )

        filters = self._build_filters(class_name, subject, exam_type)
        for f in filters:
            stmt = stmt.where(f)

        result = self.db.execute(stmt)
        return [(row[0], row[1], row[2]) for row in result.all()]

    def get_average(
        self,
        class_name: Optional[str] = None,
        subject: Optional[str] = None,
        exam_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        计算平均分

        Args:
            class_name: 班级名称（可选）
            subject: 科目名称（可选）
            exam_type: 考试类型（可选）

        Returns:
            Dict[str, Any]: 包含平均分和统计信息的字典
        """
        score_data = self._get_scores(class_name, subject, exam_type)

        if not score_data:
            return {
                "average": 0.0,
                "count": 0,
                "subject": subject,
                "exam_type": exam_type,
                "class_name": class_name,
            }

        scores = [s[0] for s in score_data]
        average = round(sum(scores) / len(scores), 2)

        return {
            "average": average,
            "count": len(scores),
            "subject": subject,
            "exam_type": exam_type,
            "class_name": class_name,
        }

    def get_max_score(
        self,
        class_name: Optional[str] = None,
        subject: Optional[str] = None,
        exam_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        获取最高分

        Args:
            class_name: 班级名称（可选）
            subject: 科目名称（可选）
            exam_type: 考试类型（可选）

        Returns:
            Dict[str, Any]: 包含最高分和学生信息的字典
        """
        score_data = self._get_scores(class_name, subject, exam_type)

        if not score_data:
            return {
                "max_score": 0.0,
                "student_id": None,
                "student_name": None,
                "subject": subject,
                "exam_type": exam_type,
                "class_name": class_name,
            }

        # 找到最高分及其学生信息
        max_item = max(score_data, key=lambda x: x[0])

        return {
            "max_score": max_item[0],
            "student_id": max_item[1],
            "student_name": max_item[2],
            "subject": subject,
            "exam_type": exam_type,
            "class_name": class_name,
        }

    def get_min_score(
        self,
        class_name: Optional[str] = None,
        subject: Optional[str] = None,
        exam_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        获取最低分

        Args:
            class_name: 班级名称（可选）
            subject: 科目名称（可选）
            exam_type: 考试类型（可选）

        Returns:
            Dict[str, Any]: 包含最低分和学生信息的字典
        """
        score_data = self._get_scores(class_name, subject, exam_type)

        if not score_data:
            return {
                "min_score": 0.0,
                "student_id": None,
                "student_name": None,
                "subject": subject,
                "exam_type": exam_type,
                "class_name": class_name,
            }

        # 找到最低分及其学生信息
        min_item = min(score_data, key=lambda x: x[0])

        return {
            "min_score": min_item[0],
            "student_id": min_item[1],
            "student_name": min_item[2],
            "subject": subject,
            "exam_type": exam_type,
            "class_name": class_name,
        }

    def get_pass_rate(
        self,
        class_name: Optional[str] = None,
        subject: Optional[str] = None,
        exam_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        计算及格率（>=60分）

        Args:
            class_name: 班级名称（可选）
            subject: 科目名称（可选）
            exam_type: 考试类型（可选）

        Returns:
            Dict[str, Any]: 包含及格率和统计信息的字典
        """
        score_data = self._get_scores(class_name, subject, exam_type)

        if not score_data:
            return {
                "pass_rate": 0.0,
                "passed_count": 0,
                "total_count": 0,
                "subject": subject,
                "exam_type": exam_type,
                "class_name": class_name,
            }

        scores = [s[0] for s in score_data]
        passed_count = sum(1 for s in scores if s >= PASS_SCORE)
        pass_rate = round((passed_count / len(scores)) * 100, 2)

        return {
            "pass_rate": pass_rate,
            "passed_count": passed_count,
            "total_count": len(scores),
            "subject": subject,
            "exam_type": exam_type,
            "class_name": class_name,
        }

    def get_excellent_rate(
        self,
        class_name: Optional[str] = None,
        subject: Optional[str] = None,
        exam_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        计算优秀率（>=90分）

        Args:
            class_name: 班级名称（可选）
            subject: 科目名称（可选）
            exam_type: 考试类型（可选）

        Returns:
            Dict[str, Any]: 包含优秀率和统计信息的字典
        """
        score_data = self._get_scores(class_name, subject, exam_type)

        if not score_data:
            return {
                "excellent_rate": 0.0,
                "excellent_count": 0,
                "total_count": 0,
                "subject": subject,
                "exam_type": exam_type,
                "class_name": class_name,
            }

        scores = [s[0] for s in score_data]
        excellent_count = sum(1 for s in scores if s >= EXCELLENT_SCORE)
        excellent_rate = round((excellent_count / len(scores)) * 100, 2)

        return {
            "excellent_rate": excellent_rate,
            "excellent_count": excellent_count,
            "total_count": len(scores),
            "subject": subject,
            "exam_type": exam_type,
            "class_name": class_name,
        }

    def _calculate_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """
        计算分数分布

        Args:
            scores: 分数列表

        Returns:
            Dict[str, int]: 分数分布字典
        """
        distribution = {
            "0-59": 0,
            "60-69": 0,
            "70-79": 0,
            "80-89": 0,
            "90-100": 0,
        }

        for score in scores:
            if score < 60:
                distribution["0-59"] += 1
            elif score < 70:
                distribution["60-69"] += 1
            elif score < 80:
                distribution["70-79"] += 1
            elif score < 90:
                distribution["80-89"] += 1
            else:
                distribution["90-100"] += 1

        return distribution

    def get_report(
        self,
        class_name: Optional[str] = None,
        subject: Optional[str] = None,
        exam_type: Optional[str] = None,
        top_n: int = 5,
    ) -> Dict[str, Any]:
        """
        获取综合统计报告

        包含：平均分、最高分、最低分、及格率、优秀率、分数分布、优秀学生

        Args:
            class_name: 班级名称（可选）
            subject: 科目名称（可选）
            exam_type: 考试类型（可选）
            top_n: 优秀学生数量（默认5）

        Returns:
            Dict[str, Any]: 综合统计报告
        """
        score_data = self._get_scores(class_name, subject, exam_type)

        if not score_data:
            return {
                "class_name": class_name,
                "subject": subject,
                "exam_type": exam_type,
                "statistics": {
                    "count": 0,
                    "average": 0.0,
                    "max_score": 0.0,
                    "min_score": 0.0,
                    "pass_rate": 0.0,
                    "excellent_rate": 0.0,
                    "score_distribution": self._calculate_score_distribution([]),
                },
                "top_students": [],
            }

        scores = [s[0] for s in score_data]
        count = len(scores)
        average = round(sum(scores) / count, 2)
        max_score = max(scores)
        min_score = min(scores)
        passed_count = sum(1 for s in scores if s >= PASS_SCORE)
        excellent_count = sum(1 for s in scores if s >= EXCELLENT_SCORE)
        pass_rate = round((passed_count / count) * 100, 2)
        excellent_rate = round((excellent_count / count) * 100, 2)
        score_distribution = self._calculate_score_distribution(scores)

        # 获取优秀学生（按分数降序）
        sorted_data = sorted(score_data, key=lambda x: x[0], reverse=True)
        top_students = [
            {"student_id": item[1], "name": item[2], "score": item[0]}
            for item in sorted_data[:top_n]
        ]

        return {
            "class_name": class_name,
            "subject": subject,
            "exam_type": exam_type,
            "statistics": {
                "count": count,
                "average": average,
                "max_score": max_score,
                "min_score": min_score,
                "pass_rate": pass_rate,
                "excellent_rate": excellent_rate,
                "score_distribution": score_distribution,
            },
            "top_students": top_students,
        }

    def get_total_score_report(
        self,
        class_name: Optional[str] = None,
        exam_type: Optional[str] = None,
        top_n: int = 10,
    ) -> Dict[str, Any]:
        """
        获取总分统计报告

        优先从 StudentExamTotal 表查询，若无数据则从各科成绩聚合计算

        Args:
            class_name: 班级名称（可选）
            exam_type: 考试类型（可选）
            top_n: 优秀学生数量（默认10）

        Returns:
            Dict[str, Any]: 总分统计报告
        """
        # 优先从总分表查询
        rows = self._query_total_from_exam_total(class_name, exam_type)

        # 若总分表无数据，从各科成绩聚合计算
        if not rows:
            rows = self._query_total_from_grades(class_name, exam_type)

        if not rows:
            return {
                "class_name": class_name,
                "exam_type": exam_type,
                "statistics": {
                    "count": 0,
                    "student_count": 0,
                    "average": 0.0,
                    "max_score": 0.0,
                    "min_score": 0.0,
                    "pass_rate": 0.0,
                    "excellent_rate": 0.0,
                    "score_distribution": {},
                },
                "top_students": [],
            }

        # 解析数据：每行 = (total_score, student_id, student_name, subject_count)
        # StudentExamTotal 查询没有 subject_count，补默认值
        score_list = []
        for row in rows:
            total = float(row[0])
            sid = row[1]
            name = row[2]
            score_list.append((total, sid, name))

        scores = [s[0] for s in score_list]
        count = len(scores)
        average = round(sum(scores) / count, 2)
        max_score = max(scores)
        min_score = min(scores)

        # 满分 750：语文150 + 数学150 + 英语150 + 3门选修各100
        MAX_TOTAL = 750
        PASS_THRESHOLD = MAX_TOTAL * 0.6   # 450
        EXCELLENT_THRESHOLD = MAX_TOTAL * 0.9  # 675

        passed_count = sum(1 for s in scores if s >= PASS_THRESHOLD)
        excellent_count = sum(1 for s in scores if s >= EXCELLENT_THRESHOLD)
        pass_rate = round((passed_count / count) * 100, 2)
        excellent_rate = round((excellent_count / count) * 100, 2)

        # 动态分数分布：按实际数据范围分 5 段
        if max_score == min_score:
            distribution = {f"{round(min_score)}": count}
        else:
            step = (max_score - min_score) / 5
            distribution = {}
            for i in range(5):
                low = round(min_score + step * i, 1)
                high = round(min_score + step * (i + 1), 1)
                if i == 4:
                    label = f"{round(low)}-{round(max_score)}"
                else:
                    label = f"{round(low)}-{round(high)}"
                distribution[label] = 0

            for s in scores:
                idx = min(int((s - min_score) / step), 4)
                keys = list(distribution.keys())
                distribution[keys[idx]] += 1

        # 优秀学生
        sorted_list = sorted(score_list, key=lambda x: x[0], reverse=True)
        top_students = [
            {"student_id": item[1], "name": item[2], "score": round(item[0], 1)}
            for item in sorted_list[:top_n]
        ]

        return {
            "class_name": class_name,
            "exam_type": exam_type,
            "statistics": {
                "count": count,
                "student_count": count,
                "average": average,
                "max_score": max_score,
                "min_score": min_score,
                "pass_rate": pass_rate,
                "excellent_rate": excellent_rate,
                "score_distribution": distribution,
            },
            "top_students": top_students,
        }

    def _query_total_from_exam_total(
        self, class_name: Optional[str], exam_type: Optional[str]
    ) -> list:
        """从 StudentExamTotal 表查询总分"""
        stmt = (
            select(
                StudentExamTotal.total_score,
                StudentExamTotal.student_id,
                Student.name.label("student_name"),
            )
            .join(Student, StudentExamTotal.student_id == Student.student_id)
        )
        if exam_type:
            stmt = stmt.where(StudentExamTotal.exam_type == exam_type)
        if class_name:
            stmt = stmt.where(Student.class_name == class_name)
        return list(self.db.execute(stmt).all())

    def _query_total_from_grades(
        self, class_name: Optional[str], exam_type: Optional[str]
    ) -> list:
        """从各科成绩聚合计算总分，同时返回科目数"""
        stmt = (
            select(
                func.sum(Grade.score).label("total_score"),
                Grade.student_id,
                Student.name.label("student_name"),
                func.count(Grade.grade_id).label("subject_count"),
            )
            .join(Student, Grade.student_id == Student.student_id)
            .group_by(Grade.student_id, Student.name)
        )
        if exam_type:
            stmt = stmt.where(Grade.exam_type == exam_type)
        if class_name:
            stmt = stmt.where(Student.class_name == class_name)
        return list(self.db.execute(stmt).all())

    def get_subject_ranking(
        self,
        subject: str,
        exam_type: str,
        class_name: Optional[str] = None,
        order: str = "desc",
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        获取单科排名

        Args:
            subject: 科目名称（必填）
            exam_type: 考试类型（必填）
            class_name: 班级名称（可选，不填则为年级排名）
            order: 排序方式（asc/desc，默认 desc）
            limit: 返回数量限制（可选）

        Returns:
            Dict[str, Any]: 排名结果
        """
        # 构建查询
        stmt = (
            select(
                Grade.score,
                Grade.student_id,
                Student.name.label("student_name"),
                Student.class_name,
            )
            .join(Student, Grade.student_id == Student.student_id)
            .where(
                and_(
                    Grade.subject == subject,
                    Grade.exam_type == exam_type,
                )
            )
        )

        if class_name:
            stmt = stmt.where(Student.class_name == class_name)

        # 排序：默认按分数降序，分数相同时按学号升序
        if order == "desc":
            stmt = stmt.order_by(Grade.score.desc(), Grade.student_id.asc())
        else:
            stmt = stmt.order_by(Grade.score.asc(), Grade.student_id.asc())

        if limit:
            stmt = stmt.limit(limit)

        result = self.db.execute(stmt)
        rows = result.all()

        # 构建排名列表
        rankings = []
        current_rank = 0
        prev_score = None

        for i, row in enumerate(rows):
            # 处理并列排名
            if row[0] != prev_score:
                current_rank = i + 1
            prev_score = row[0]

            rankings.append({
                "rank": current_rank,
                "student_id": row[1],
                "student_name": row[2],
                "score": row[0],
            })

        return {
            "subject": subject,
            "exam_type": exam_type,
            "class_name": class_name,
            "total_count": len(rows),
            "rankings": rankings,
        }

    def get_total_ranking(
        self,
        exam_type: str,
        class_name: Optional[str] = None,
        order: str = "desc",
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        获取总分排名

        计算每个学生在指定考试类型下的所有科目总分，然后进行排名

        Args:
            exam_type: 考试类型（必填）
            class_name: 班级名称（可选，不填则为年级排名）
            order: 排序方式（asc/desc，默认 desc）
            limit: 返回数量限制（可选）

        Returns:
            Dict[str, Any]: 总分排名结果
        """
        # 查询每个学生的各科成绩
        stmt = (
            select(
                Grade.student_id,
                Student.name.label("student_name"),
                Grade.subject,
                Grade.score,
            )
            .join(Student, Grade.student_id == Student.student_id)
            .where(Grade.exam_type == exam_type)
        )

        if class_name:
            stmt = stmt.where(Student.class_name == class_name)

        result = self.db.execute(stmt)
        rows = result.all()

        # 按学生聚合各科成绩
        student_scores: Dict[str, Dict] = {}
        for row in rows:
            student_id = row[0]
            if student_id not in student_scores:
                student_scores[student_id] = {
                    "student_id": student_id,
                    "student_name": row[1],
                    "total_score": 0.0,
                    "subject_scores": {},
                }
            student_scores[student_id]["total_score"] += float(row[3])
            student_scores[student_id]["subject_scores"][row[2]] = float(row[3])

        # 转换为列表并排序
        ranking_list = list(student_scores.values())

        if order == "desc":
            ranking_list.sort(
                key=lambda x: (-x["total_score"], x["student_id"])
            )
        else:
            ranking_list.sort(
                key=lambda x: (x["total_score"], x["student_id"])
            )

        if limit:
            ranking_list = ranking_list[:limit]

        # 添加排名
        rankings = []
        current_rank = 0
        prev_total = None

        for i, item in enumerate(ranking_list):
            if item["total_score"] != prev_total:
                current_rank = i + 1
            prev_total = item["total_score"]

            rankings.append({
                "rank": current_rank,
                "student_id": item["student_id"],
                "student_name": item["student_name"],
                "total_score": round(item["total_score"], 1),
                "subject_scores": item["subject_scores"],
            })

        return {
            "exam_type": exam_type,
            "class_name": class_name,
            "total_count": len(ranking_list),
            "rankings": rankings,
        }

    def get_batch_class_statistics(
        self,
        exam_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        批量获取所有班级的统计数据

        及格率/优秀率按学生总分计算（满分750）：
        - 及格：总分 >= 450（60%）
        - 优秀：总分 >= 675（90%）

        Args:
            exam_type: 考试类型（可选）

        Returns:
            Dict[str, Any]: 包含所有班级统计数据的字典
        """
        # 查询每个学生的总分（按班级分组）
        total_stmt = (
            select(
                Student.class_name,
                Grade.student_id,
                func.sum(Grade.score).label("total_score"),
            )
            .join(Student, Grade.student_id == Student.student_id)
            .group_by(Student.class_name, Grade.student_id)
        )
        if exam_type:
            total_stmt = total_stmt.where(Grade.exam_type == exam_type)

        total_result = self.db.execute(total_stmt)
        total_rows = total_result.all()

        # 按班级聚合
        class_data: Dict[str, list] = {}
        for row in total_rows:
            class_name = row[0]
            total_score = float(row[2])
            if class_name not in class_data:
                class_data[class_name] = []
            class_data[class_name].append(total_score)

        # 构建结果（所有指标基于总分）
        classes = []
        for class_name, total_scores in class_data.items():
            student_count = len(total_scores)
            average = round(sum(total_scores) / student_count, 2) if student_count > 0 else 0.0
            max_score = round(max(total_scores), 1) if total_scores else 0.0
            min_score = round(min(total_scores), 1) if total_scores else 0.0

            passed_count = sum(1 for s in total_scores if s >= TOTAL_PASS_SCORE)
            excellent_count = sum(1 for s in total_scores if s >= TOTAL_EXCELLENT_SCORE)
            pass_rate = round((passed_count / student_count) * 100, 2) if student_count > 0 else 0.0
            excellent_rate = round((excellent_count / student_count) * 100, 2) if student_count > 0 else 0.0

            classes.append({
                "class_name": class_name,
                "student_count": student_count,
                "average_score": average,
                "max_score": max_score,
                "min_score": min_score,
                "pass_rate": pass_rate,
                "excellent_rate": excellent_rate,
            })

        return {"classes": classes}

    def get_batch_subject_statistics(
        self,
        class_name: Optional[str] = None,
        exam_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        批量获取所有科目的统计数据

        及格率/优秀率按科目满分计算：
        - 语文/数学/英语：满分150，及格>=90，优秀>=135
        - 其他科目：满分100，及格>=60，优秀>=90

        Args:
            class_name: 班级名称（可选）
            exam_type: 考试类型（可选）

        Returns:
            Dict[str, Any]: 包含所有科目统计数据的字典
        """
        # 查询每个科目每个学生的成绩
        student_stmt = (
            select(
                Grade.subject,
                Grade.student_id,
                Grade.score,
            )
            .join(Student, Grade.student_id == Student.student_id)
        )
        if class_name:
            student_stmt = student_stmt.where(Student.class_name == class_name)
        if exam_type:
            student_stmt = student_stmt.where(Grade.exam_type == exam_type)

        student_result = self.db.execute(student_stmt)
        student_rows = student_result.all()

        # 按科目聚合
        subject_data: Dict[str, Dict] = {}
        for row in student_rows:
            subject = row[0]
            score = float(row[2])
            if subject not in subject_data:
                subject_data[subject] = {"scores": []}
            subject_data[subject]["scores"].append(score)

        subjects = []
        for subject, data in sorted(subject_data.items()):
            scores = data["scores"]
            total_count = len(scores)
            average = round(sum(scores) / total_count, 2) if total_count > 0 else 0.0
            max_score = max(scores) if scores else 0.0
            min_score = min(scores) if scores else 0.0

            # 根据科目确定及格/优秀线
            if subject in MAIN_SUBJECTS:
                pass_threshold = MAIN_SUBJECT_PASS    # 90
                excellent_threshold = MAIN_SUBJECT_EXCELLENT  # 135
            else:
                pass_threshold = PASS_SCORE           # 60
                excellent_threshold = EXCELLENT_SCORE  # 90

            passed_count = sum(1 for s in scores if s >= pass_threshold)
            excellent_count = sum(1 for s in scores if s >= excellent_threshold)
            pass_rate = round((passed_count / total_count) * 100, 2) if total_count > 0 else 0.0
            excellent_rate = round((excellent_count / total_count) * 100, 2) if total_count > 0 else 0.0

            # 分数分布（按科目满分分5段）
            if subject in MAIN_SUBJECTS:
                dist_keys = ["0-89", "90-104", "105-119", "120-134", "135-150"]
                thresholds = [90, 105, 120, 135, 151]
            else:
                dist_keys = ["0-59", "60-69", "70-79", "80-89", "90-100"]
                thresholds = [60, 70, 80, 90, 101]

            distribution = {k: 0 for k in dist_keys}
            for s in scores:
                for i, t in enumerate(thresholds):
                    if s < t:
                        distribution[dist_keys[i]] += 1
                        break

            subjects.append({
                "subject": subject,
                "student_count": total_count,
                "average_score": average,
                "max_score": max_score,
                "min_score": min_score,
                "pass_rate": pass_rate,
                "excellent_rate": excellent_rate,
                "score_distribution": distribution,
            })

        return {"subjects": subjects}

    def get_statistics_metrics(
        self,
        class_name: Optional[str] = None,
        subject: Optional[str] = None,
        exam_type: Optional[str] = None,
        metrics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        获取指定的统计指标

        Args:
            class_name: 班级名称（可选）
            subject: 科目名称（可选）
            exam_type: 考试类型（可选）
            metrics: 需要计算的指标列表（可选，默认全部）

        Returns:
            Dict[str, Any]: 统计指标结果
        """
        if metrics is None:
            metrics = ["avg", "max", "min", "pass_rate"]

        score_data = self._get_scores(class_name, subject, exam_type)

        if not score_data:
            return {
                "query": {
                    "class_name": class_name,
                    "subject": subject,
                    "exam_type": exam_type,
                },
                "total_students": 0,
                "metrics": {},
            }

        scores = [s[0] for s in score_data]
        count = len(scores)
        result_metrics = {}

        for metric in metrics:
            if metric == "avg":
                result_metrics["avg"] = round(sum(scores) / count, 2)
            elif metric == "max":
                result_metrics["max"] = max(scores)
            elif metric == "min":
                result_metrics["min"] = min(scores)
            elif metric == "pass_rate":
                passed = sum(1 for s in scores if s >= PASS_SCORE)
                result_metrics["pass_rate"] = round((passed / count) * 100, 2)
            elif metric == "excellent_rate":
                excellent = sum(1 for s in scores if s >= EXCELLENT_SCORE)
                result_metrics["excellent_rate"] = round((excellent / count) * 100, 2)
            elif metric == "median":
                result_metrics["median"] = round(statistics.median(scores), 2)
            elif metric == "std_dev":
                if count > 1:
                    result_metrics["std_dev"] = round(statistics.stdev(scores), 2)
                else:
                    result_metrics["std_dev"] = 0.0

        return {
            "query": {
                "class_name": class_name,
                "subject": subject,
                "exam_type": exam_type,
            },
            "total_students": count,
            "metrics": result_metrics,
        }
