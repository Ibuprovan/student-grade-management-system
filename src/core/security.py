"""
安全模块

提供 JWT Token 的创建、验证和密码哈希功能，包括：
- JWT Access Token / Refresh Token 生成
- JWT Token 解码与验证
- 密码哈希与校验（bcrypt）
- Token 黑名单机制（基于内存，生产环境建议使用 Redis）

安全设计参考：
- OWASP JWT Cheat Sheet
- 算法强制 HS256，防止 Algorithm Confusion 攻击
- Token 包含 jti（唯一标识），支持吊销
- Access Token 短有效期（默认 30 分钟）
"""

import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from src.core.config import settings

logger = logging.getLogger(__name__)

# ==================== 密码哈希 ====================

# 使用 bcrypt 进行密码哈希，OWASP 推荐的安全算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    对明文密码进行 bcrypt 哈希

    Args:
        password: 明文密码

    Returns:
        str: 哈希后的密码字符串
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码与哈希密码是否匹配

    Args:
        plain_password: 用户输入的明文密码
        hashed_password: 数据库中存储的哈希密码

    Returns:
        bool: 密码匹配返回 True，否则返回 False
    """
    return pwd_context.verify(plain_password, hashed_password)


# ==================== Token 数据模型 ====================


class TokenPayload(BaseModel):
    """
    JWT Token 载荷模型

    Attributes:
        sub: 用户 ID（Subject）
        username: 用户名
        role: 用户角色（admin / teacher / student）
        exp: 过期时间
        jti: Token 唯一标识（用于吊销）
        type: Token 类型（access / refresh）
    """

    sub: str
    username: str
    role: str
    exp: datetime
    jti: str
    type: str


class TokenResponse(BaseModel):
    """
    Token 响应模型

    Attributes:
        access_token: 访问令牌
        refresh_token: 刷新令牌
        token_type: Token 类型（固定为 bearer）
        expires_in: Access Token 有效期（秒）
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# ==================== JWT 服务 ====================


class JWTService:
    """
    JWT Token 服务

    提供 Token 的创建、解码和验证功能。

    安全特性：
    - 强制使用 HS256 算法，防止 Algorithm Confusion 攻击
    - 每个 Token 包含唯一的 jti，支持精确吊销
    - Access Token 短有效期，默认 30 分钟
    - Refresh Token 较长有效期，默认 7 天
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        """
        初始化 JWT 服务

        Args:
            secret_key: 签名密钥（应为强随机字符串，至少 256 位）
            algorithm: 签名算法（仅支持 HS256）
            access_token_expire_minutes: Access Token 有效期（分钟）
            refresh_token_expire_days: Refresh Token 有效期（天）
        """
        if algorithm != "HS256":
            raise ValueError("出于安全考虑，仅支持 HS256 算法")

        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

        # 内存黑名单（生产环境应使用 Redis）
        self._blacklist: set[str] = set()

    def create_access_token(
        self,
        user_id: str,
        username: str,
        role: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        创建 Access Token

        Args:
            user_id: 用户 ID
            username: 用户名
            role: 用户角色
            expires_delta: 自定义过期时间（可选）

        Returns:
            str: 编码后的 JWT Token 字符串
        """
        now = datetime.now(timezone.utc)
        expire = now + (expires_delta or timedelta(minutes=self.access_token_expire_minutes))

        payload = {
            "sub": user_id,
            "username": username,
            "role": role,
            "exp": expire,
            "iat": now,
            "jti": str(uuid.uuid4()),
            "type": "access",
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.debug(f"创建 Access Token: user_id={user_id}, jti={payload['jti']}")
        return token

    def create_refresh_token(self, user_id: str, username: str) -> str:
        """
        创建 Refresh Token

        Args:
            user_id: 用户 ID
            username: 用户名

        Returns:
            str: 编码后的 JWT Refresh Token 字符串
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=self.refresh_token_expire_days)

        payload = {
            "sub": user_id,
            "username": username,
            "role": "",  # Refresh Token 不携带角色信息
            "exp": expire,
            "iat": now,
            "jti": str(uuid.uuid4()),
            "type": "refresh",
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.debug(f"创建 Refresh Token: user_id={user_id}, jti={payload['jti']}")
        return token

    def decode_token(self, token: str) -> TokenPayload:
        """
        解码并验证 JWT Token

        验证项：
        - 签名有效性（防篡改）
        - 过期时间（防重放）
        - 算法一致性（防 Algorithm Confusion）

        Args:
            token: JWT Token 字符串

        Returns:
            TokenPayload: 解码后的 Token 载荷

        Raises:
            ValueError: Token 无效或已过期时抛出
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_aud": False,
                },
            )
            return TokenPayload(**payload)
        except jwt.ExpiredSignatureError:
            raise ValueError("Token 已过期")
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效 Token: {e}")
            raise ValueError("无效的 Token")

    def blacklist_token(self, jti: str) -> None:
        """
        将 Token 加入黑名单（吊销）

        Args:
            jti: Token 的唯一标识
        """
        self._blacklist.add(jti)
        logger.info(f"Token 已加入黑名单: jti={jti}")

    def is_blacklisted(self, jti: str) -> bool:
        """
        检查 Token 是否在黑名单中

        Args:
            jti: Token 的唯一标识

        Returns:
            bool: 在黑名单中返回 True
        """
        return jti in self._blacklist

    def verify_token(self, token: str) -> TokenPayload:
        """
        完整验证 Token（包含黑名单检查）

        Args:
            token: JWT Token 字符串

        Returns:
            TokenPayload: 验证通过的 Token 载荷

        Raises:
            ValueError: Token 无效、已过期或已被吊销
        """
        payload = self.decode_token(token)

        # 检查黑名单
        if self.is_blacklisted(payload.jti):
            raise ValueError("Token 已被吊销")

        return payload


# ==================== 全局实例 ====================

# 从配置创建全局 JWT 服务实例
jwt_service = JWTService(
    secret_key=settings.JWT_SECRET_KEY,
    algorithm="HS256",
    access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    refresh_token_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
)
