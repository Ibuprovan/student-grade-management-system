"""
自定义异常模块

定义业务异常层次结构，用于统一错误处理
"""


class AppException(Exception):
    """
    应用基础异常

    所有业务异常的基类，包含错误消息和错误码

    Attributes:
        message: 错误描述消息
        code: 错误码，用于前端识别错误类型
    """

    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class NotFoundException(AppException):
    """
    资源不存在异常

    当查询的资源不存在时抛出

    Args:
        resource: 资源类型名称（如"学生"、"成绩"）
        identifier: 资源标识符（如学号、成绩ID）
    """

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} '{identifier}' 不存在",
            code="NOT_FOUND",
        )


class DuplicateException(AppException):
    """
    重复数据异常

    当尝试创建已存在的记录时抛出

    Args:
        resource: 资源类型名称
        field: 重复的字段名
        value: 重复的值
    """

    def __init__(self, resource: str, field: str, value: str):
        super().__init__(
            message=f"{resource} 的 {field} '{value}' 已存在",
            code="DUPLICATE",
        )


class ValidationException(AppException):
    """
    数据验证异常

    当输入数据不符合业务规则时抛出

    Args:
        message: 验证失败的详细描述
    """

    def __init__(self, message: str):
        super().__init__(message=message, code="VALIDATION_ERROR")


# ==================== 具体业务异常 ====================

class StudentNotFoundException(NotFoundException):
    """
    学生不存在异常

    Args:
        student_id: 学号
    """

    def __init__(self, student_id: str):
        super().__init__("学生", student_id)


class DuplicateGradeException(DuplicateException):
    """
    成绩重复异常

    当同一学生、同一科目、同一考试类型的成绩已存在时抛出

    Args:
        student_id: 学号
        subject: 科目
        exam_type: 考试类型
    """

    def __init__(self, student_id: str, subject: str, exam_type: str):
        super().__init__(
            "成绩",
            "学生-科目-考试类型",
            f"{student_id}-{subject}-{exam_type}",
        )


class ScoreOutOfRangeException(ValidationException):
    """
    分数超出范围异常

    Args:
        score: 超出范围的分数值
    """

    def __init__(self, score: float):
        super().__init__(f"分数 {score} 超出范围（0-100）")


class InvalidStudentIdFormatException(ValidationException):
    """
    学号格式异常

    Args:
        student_id: 格式错误的学号
    """

    def __init__(self, student_id: str):
        super().__init__(f"学号 '{student_id}' 格式错误，应为8位数字（如：20260001）")
