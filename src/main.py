"""
应用入口模块

提供 FastAPI 应用的创建和配置，包括：
- 应用实例创建
- 路由注册
- 异常处理器注册
- 中间件配置（CORS、安全响应头）
- 生命周期事件
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import (
    students_router,
    grades_router,
    statistics_router,
    auth_router,
    dashboard_router,
    users_router,
    audit_logs_router,
    imports_router,
    class_teachers_router,
    class_teacher_scoped_router,
    subject_leaders_router,
    subject_leader_scoped_router,
    accounts_router,
)
from src.api.exception_handlers import (
    app_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from src.core.config import settings
from src.core.database import init_db
from src.core.exceptions import AppException

from fastapi.exceptions import RequestValidationError


# 配置日志
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    在应用启动时初始化数据库，在应用关闭时进行清理
    """
    # 启动时
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")

    # ==================== P0-4: JWT 密钥安全检查 ====================
    # 生产环境下检测是否使用了默认密钥，防止安全风险
    _DEFAULT_JWT_SECRET = "dev-secret-key-change-in-production-environment!"
    if settings.is_production and settings.JWT_SECRET_KEY == _DEFAULT_JWT_SECRET:
        logger.critical(
            "安全警告：生产环境正在使用默认 JWT 密钥！"
            "请立即通过环境变量 JWT_SECRET_KEY 设置强密钥。"
            "生成方式：python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )
        raise RuntimeError(
            "生产环境禁止使用默认 JWT 密钥，请通过环境变量 JWT_SECRET_KEY 设置强密钥"
        )

    init_db()
    logger.info("数据库初始化完成")

    yield

    # 关闭时
    logger.info("应用关闭")


def create_app() -> FastAPI:
    """
    创建 FastAPI 应用实例

    Returns:
        FastAPI: 配置好的应用实例
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="学生成绩管理系统 API",
        # 生产环境禁用 API 文档，避免暴露接口细节
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ==================== CORS 配置（安全修复） ====================
    # 限制允许的源，防止恶意网站发起跨域请求
    # 生产环境应通过环境变量 CORS_ORIGINS 配置实际域名
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,  # 限制来源
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],  # 限制 HTTP 方法
        allow_headers=["Content-Type", "Authorization"],  # 限制请求头
    )

    # ==================== 安全响应头中间件 ====================
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        """添加安全相关的 HTTP 响应头"""
        response = await call_next(request)
        # 防止 MIME 类型嗅探攻击
        response.headers["X-Content-Type-Options"] = "nosniff"
        # 防止点击劫持
        response.headers["X-Frame-Options"] = "DENY"
        # XSS 防护（兼容旧浏览器）
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # 严格传输安全（HTTPS 环境生效）
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # 内容安全策略
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        # 控制 Referer 头信息
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # 注册异常处理器
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # ==================== 注册路由 ====================
    # 认证路由（公开）
    app.include_router(auth_router)

    # 业务路由（写操作需要认证）
    app.include_router(students_router)
    app.include_router(grades_router)
    app.include_router(statistics_router)
    app.include_router(dashboard_router)
    app.include_router(imports_router)  # 批量导入路由

    # 管理路由（需要管理员权限）
    app.include_router(users_router)
    app.include_router(audit_logs_router)
    app.include_router(class_teachers_router)
    app.include_router(subject_leaders_router)
    app.include_router(accounts_router)

    # 班主任专用路由（班主任或管理员权限）
    app.include_router(class_teacher_scoped_router)

    # 学科组长专用路由（学科组长或管理员权限）
    app.include_router(subject_leader_scoped_router)

    # 健康检查端点（公开，用于监控）
    @app.get("/health", tags=["系统"])
    async def health_check():
        """健康检查"""
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }

    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        # 开发环境仅绑定 localhost，避免暴露到局域网
        host="127.0.0.1" if settings.DEBUG else "0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
