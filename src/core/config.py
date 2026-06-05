"""
应用配置模块

使用 Pydantic Settings 管理应用配置，支持环境变量和 .env 文件
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from pydantic import ConfigDict


class Settings(BaseSettings):
    """
    应用配置类

    所有配置项均可通过环境变量覆盖，优先级：
    环境变量 > .env 文件 > 默认值
    """

    # ==================== 应用配置 ====================
    APP_NAME: str = Field(default="学生成绩管理系统", description="应用名称")
    APP_VERSION: str = Field(default="1.0.0", description="应用版本")
    DEBUG: bool = Field(default=False, description="调试模式")

    # ==================== 数据库配置 ====================
    # 默认使用 SQLite，数据库文件存放在项目根目录的 data/ 文件夹下
    DATABASE_URL: str = Field(
        default="sqlite:///./data/grades.db",
        description="数据库连接字符串",
    )

    # SQLAlchemy 连接池配置
    DB_ECHO: bool = Field(default=False, description="是否打印 SQL 语句")
    DB_POOL_SIZE: int = Field(default=5, description="连接池大小")
    DB_MAX_OVERFLOW: int = Field(default=10, description="连接池最大溢出数")

    # ==================== 分页配置 ====================
    DEFAULT_PAGE_SIZE: int = Field(default=20, description="默认每页数量")
    MAX_PAGE_SIZE: int = Field(default=100, description="最大每页数量")

    # ==================== 安全配置 ====================
    # JWT 密钥（生产环境必须通过环境变量设置强密钥）
    # 生成方式：python -c "import secrets; print(secrets.token_urlsafe(32))"
    JWT_SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production-environment!",
        description="JWT 签名密钥（生产环境必须更换）",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access Token 有效期（分钟）",
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Refresh Token 有效期（天）",
    )

    # CORS 允许的源（生产环境应限制为实际域名）
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="CORS 允许的源（逗号分隔）",
    )

    # ==================== 路径配置 ====================
    # 项目根目录（自动推导）
    BASE_DIR: Path = Field(default=Path(__file__).resolve().parent.parent.parent)

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def database_path(self) -> Path:
        """获取数据库文件的绝对路径"""
        # 从 DATABASE_URL 中提取路径部分
        # sqlite:///./data/grades.db -> ./data/grades.db
        db_path_str = self.DATABASE_URL.replace("sqlite:///", "")
        db_path = Path(db_path_str)

        # 如果是相对路径，则相对于项目根目录
        if not db_path.is_absolute():
            db_path = self.BASE_DIR / db_path

        return db_path

    def get_sync_database_url(self) -> str:
        """
        获取同步数据库连接 URL

        Returns:
            str: 同步数据库连接字符串
        """
        return self.DATABASE_URL

    @property
    def cors_origins_list(self) -> list[str]:
        """
        获取 CORS 允许的源列表

        Returns:
            list[str]: 解析后的源列表
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


# 全局配置单例
settings = Settings()
