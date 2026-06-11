"""
学生业务逻辑 Service

实现学生信息管理的核心业务逻辑，包括：
- 学生增删改查（CRUD）
- 学号唯一性校验
- 分页查询与搜索
"""

from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy.orm import Session

from src.core.exceptions import (
    StudentNotFoundException,
    DuplicateException,
    ValidationException,
)
from src.models.student import Student
from src.repositories.student_repo import StudentRepository
from src.schemas.student import StudentCreate, StudentUpdate


class StudentService:
    """
    学生业务逻辑类

    职责：
    - 处理学生相关的业务逻辑
    - 协调 Repository 层进行数据操作
    - 执行业务规则校验（如学号唯一性）

    Attributes:
        repo: StudentRepository 实例
    """

    def __init__(self, db: Session):
        """
        初始化 StudentService

        Args:
            db: SQLAlchemy 数据库会话
        """
        self.repo = StudentRepository(db)

    def create_student(self, data: StudentCreate) -> Student:
        """
        创建学生

        业务流程：
        1. 检查学号是否已存在
        2. 不存在则创建学生记录
        3. 返回创建的学生对象

        Args:
            data: 学生创建请求数据（已通过 Pydantic 验证）

        Returns:
            Student: 创建的学生 ORM 对象

        Raises:
            DuplicateException: 学号已存在
        """
        # 检查学号唯一性
        if self.repo.student_id_exists(data.student_id):
            raise DuplicateException("学生", "学号", data.student_id)

        # 创建学生记录
        student_data = data.model_dump()
        student = self.repo.create(student_data)
        return student

    def get_student_by_id(self, student_id: str) -> Student:
        """
        根据学号查询学生

        Args:
            student_id: 学号

        Returns:
            Student: 学生 ORM 对象

        Raises:
            StudentNotFoundException: 学生不存在
        """
        student = self.repo.get_by_student_id(student_id)
        if student is None:
            raise StudentNotFoundException(student_id)
        return student

    def get_student_list(
        self,
        page: int = 1,
        page_size: int = 20,
        class_name: Optional[str] = None,
    ) -> Tuple[List[Student], int]:
        """
        获取学生列表（分页）

        Args:
            page: 页码（从 1 开始）
            page_size: 每页数量
            class_name: 班级筛选（可选）

        Returns:
            Tuple[List[Student], int]: (学生列表, 总数)
        """
        # 计算偏移量
        skip = (page - 1) * page_size

        # 构建过滤条件
        filters = []
        if class_name:
            filters.append(Student.class_name == class_name)

        # 查询数据
        students = self.repo.get_all(skip=skip, limit=page_size, filters=filters)
        total = self.repo.count(filters=filters)

        return students, total

    def update_student(self, student_id: str, data: StudentUpdate) -> Student:
        """
        更新学生信息

        Args:
            student_id: 学号
            data: 学生更新请求数据（仅包含需要更新的字段）

        Returns:
            Student: 更新后的学生 ORM 对象

        Raises:
            StudentNotFoundException: 学生不存在
        """
        # 检查学生是否存在
        student = self.repo.get_by_student_id(student_id)
        if student is None:
            raise StudentNotFoundException(student_id)

        # 获取需要更新的字段（排除 None 值）
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        if not update_data:
            # 没有需要更新的字段，直接返回
            return student

        # 执行更新
        updated_student = self.repo.update(student.student_id, update_data)
        return updated_student

    def delete_student(self, student_id: str) -> bool:
        """
        删除学生

        删除学生时会级联删除其所有成绩记录（通过 ORM 的 cascade 配置）

        Args:
            student_id: 学号

        Returns:
            bool: 删除成功返回 True

        Raises:
            StudentNotFoundException: 学生不存在
        """
        # 检查学生是否存在
        student = self.repo.get_by_student_id(student_id)
        if student is None:
            raise StudentNotFoundException(student_id)

        # 执行删除
        return self.repo.delete(student.student_id)

    def search_students(
        self,
        keyword: str,
        class_name: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Student], int]:
        """
        搜索学生

        支持按学号或姓名模糊搜索，可选按班级筛选。
        使用数据库层面的 LIMIT/OFFSET 分页，避免将所有记录加载到内存。

        Args:
            keyword: 搜索关键词（匹配学号或姓名）
            class_name: 班级筛选（可选）
            page: 页码（从 1 开始）
            page_size: 每页数量

        Returns:
            Tuple[List[Student], int]: (学生列表, 总数)
        """
        skip = (page - 1) * page_size

        # 直接在数据库层面进行分页和筛选，避免内存分页
        students = self.repo.search(
            keyword=keyword,
            class_name=class_name,
            skip=skip,
            limit=page_size,
        )
        total = self.repo.count_search(keyword=keyword, class_name=class_name)

        return students, total

    def student_exists(self, student_id: str) -> bool:
        """
        检查学生是否存在

        Args:
            student_id: 学号

        Returns:
            bool: 存在返回 True，否则返回 False
        """
        return self.repo.student_id_exists(student_id)

    def get_all_classes(self) -> List[str]:
        """
        获取所有去重的班级名称列表

        通过 Repository 调用数据库 DISTINCT 查询，在数据库层面完成去重，
        避免将所有学生记录加载到内存后再去重。

        Returns:
            List[str]: 去重后的班级名称列表（已排序）
        """
        return self.repo.get_all_classes()

    def batch_delete_students(self, student_ids: List[str]) -> Dict[str, Any]:
        """
        批量删除学生

        使用显式事务确保数据一致性：要么全部删除成功，要么全部回滚。
        通过 SQLAlchemy 的 begin() 上下文管理器管理事务边界，
        避免 BaseRepository.delete() 中的逐条 commit 导致部分成功的情况。

        Args:
            student_ids: 要删除的学号列表

        Returns:
            Dict[str, Any]: 批量删除结果，包含 total, success_count, fail_count, results

        Raises:
            Exception: 事务内发生任何异常时自动回滚并重新抛出
        """
        results = []
        success_count = 0
        fail_count = 0

        # 先做存在性校验（只读，不涉及事务）
        students_map = {}
        for student_id in student_ids:
            student = self.repo.get_by_student_id(student_id)
            if student is None:
                results.append({
                    "student_id": student_id,
                    "status": "fail",
                    "error": f"学生 '{student_id}' 不存在",
                })
                fail_count += 1
            else:
                students_map[student_id] = student

        # 如果所有学生都不存在，直接返回
        if not students_map:
            return {
                "total": len(student_ids),
                "success_count": success_count,
                "fail_count": fail_count,
                "results": results,
            }

        # 使用显式事务批量删除
        try:
            with self.repo.db.begin():
                for student_id, student in students_map.items():
                    self.repo.db.delete(student)
                    results.append({
                        "student_id": student_id,
                        "status": "success",
                    })
                    success_count += 1
        except Exception as e:
            # 事务自动回滚（由 begin() 上下文管理器处理）
            # 将已标记为 success 的记录改为 fail
            for r in results:
                if r["status"] == "success":
                    r["status"] = "fail"
                    r["error"] = f"事务回滚: {e}"
            fail_count = len(student_ids) - fail_count
            success_count = 0
            raise

        return {
            "total": len(student_ids),
            "success_count": success_count,
            "fail_count": fail_count,
            "results": results,
        }
