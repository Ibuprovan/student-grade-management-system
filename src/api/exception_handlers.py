"""
全局异常处理器

统一处理应用中的异常，返回标准格式的错误响应
"""

import logging
from typing import Union

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from src.core.exceptions import AppException

# 配置日志
logger = logging.getLogger(__name__)

# 错误码到 HTTP 状态码的映射
ERROR_CODE_TO_STATUS = {
    "NOT_FOUND": 404,
    "DUPLICATE": 409,
    "VALIDATION_ERROR": 422,
    "INVALID_FORMAT": 400,
    "INTERNAL_ERROR": 500,
}


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    处理自定义业务异常

    Args:
        request: FastAPI 请求对象
        exc: 业务异常实例

    Returns:
        JSONResponse: 标准格式的错误响应
    """
    status_code = ERROR_CODE_TO_STATUS.get(exc.code, 500)

    logger.warning(
        f"业务异常: [{exc.code}] {exc.message} | "
        f"路径: {request.url.path} | 方法: {request.method}"
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    处理请求参数验证异常

    将 Pydantic 的验证错误转换为统一的错误响应格式

    Args:
        request: FastAPI 请求对象
        exc: 请求验证异常

    Returns:
        JSONResponse: 标准格式的错误响应
    """
    # 提取第一个错误信息
    errors = exc.errors()
    if errors:
        first_error = errors[0]
        # 构建友好的错误消息
        loc = " -> ".join(str(l) for l in first_error.get("loc", []))
        msg = first_error.get("msg", "参数验证失败")
        message = f"参数错误 ({loc}): {msg}"
    else:
        message = "请求参数验证失败"

    logger.warning(
        f"参数验证失败: {message} | "
        f"路径: {request.url.path} | 方法: {request.method}"
    )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": message,
            },
        },
    )


async def general_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    处理未捕获的异常

    作为最后的兜底处理器，捕获所有未被其他处理器处理的异常

    Args:
        request: FastAPI 请求对象
        exc: 异常实例

    Returns:
        JSONResponse: 标准格式的错误响应
    """
    logger.error(
        f"未处理的异常: {type(exc).__name__}: {str(exc)} | "
        f"路径: {request.url.path} | 方法: {request.method}",
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "服务器内部错误，请稍后重试",
            },
        },
    )
