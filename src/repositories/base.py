"""
基础 Repository 模块

提供通用的 CRUD 操作基类，所有具体的 Repository 都应继承此类
"""

from typing import Generic, TypeVar, Type, Optional, List, Any, Dict

from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import Session

from src.core.database import Base

# 定义泛型类型变量
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    基础 Repository 类

    提供通用的 CRUD 操作，子类可以继承并扩展特定的查询方法

    Type Parameters:
        ModelType: SQLAlchemy 模型类型

    Attributes:
        model: SQLAlchemy 模型类
        db: 数据库会话
    """

    def __init__(self, model: Type[ModelType], db: Session):
        """
        初始化 Repository

        Args:
            model: SQLAlchemy 模型类
            db: 数据库会话
        """
        self.model = model
        self.db = db

    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """
        创建记录

        Args:
            obj_in: 包含模型字段的字典

        Returns:
            ModelType: 创建的模型实例
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """
        根据主键查询记录

        Args:
            id: 主键值

        Returns:
            Optional[ModelType]: 查询到的模型实例，不存在则返回 None
        """
        return self.db.get(self.model, id)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[List[Any]] = None,
    ) -> List[ModelType]:
        """
        查询所有记录（支持分页和过滤）

        Args:
            skip: 跳过的记录数（偏移量）
            limit: 返回的最大记录数
            filters: SQLAlchemy 过滤条件列表

        Returns:
            List[ModelType]: 模型实例列表
        """
        stmt = select(self.model)

        if filters:
            for filter_condition in filters:
                stmt = stmt.where(filter_condition)

        stmt = stmt.offset(skip).limit(limit)
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def count(self, filters: Optional[List[Any]] = None) -> int:
        """
        统计记录数量

        Args:
            filters: SQLAlchemy 过滤条件列表

        Returns:
            int: 满足条件的记录数量
        """
        stmt = select(func.count()).select_from(self.model)

        if filters:
            for filter_condition in filters:
                stmt = stmt.where(filter_condition)

        result = self.db.execute(stmt)
        return result.scalar() or 0

    def update(self, id: Any, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """
        更新记录

        Args:
            id: 主键值
            obj_in: 包含要更新字段的字典

        Returns:
            Optional[ModelType]: 更新后的模型实例，不存在则返回 None
        """
        db_obj = self.get_by_id(id)
        if db_obj is None:
            return None

        for key, value in obj_in.items():
            if hasattr(db_obj, key) and value is not None:
                setattr(db_obj, key, value)

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: Any) -> bool:
        """
        删除记录

        Args:
            id: 主键值

        Returns:
            bool: 删除成功返回 True，记录不存在返回 False
        """
        db_obj = self.get_by_id(id)
        if db_obj is None:
            return False

        self.db.delete(db_obj)
        self.db.commit()
        return True

    def exists(self, id: Any) -> bool:
        """
        检查记录是否存在

        Args:
            id: 主键值

        Returns:
            bool: 存在返回 True，否则返回 False
        """
        return self.get_by_id(id) is not None

    def bulk_create(self, objs_in: List[Dict[str, Any]]) -> List[ModelType]:
        """
        批量创建记录

        Args:
            objs_in: 包含模型字段的字典列表

        Returns:
            List[ModelType]: 创建的模型实例列表
        """
        db_objs = [self.model(**obj_in) for obj_in in objs_in]
        self.db.add_all(db_objs)
        self.db.commit()

        for db_obj in db_objs:
            self.db.refresh(db_obj)

        return db_objs
