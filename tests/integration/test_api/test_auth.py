"""
认证 API 集成测试

测试认证相关的所有 API 端点，包括：
- POST /api/v1/auth/login          用户登录
- POST /api/v1/auth/refresh        刷新 Token
- POST /api/v1/auth/logout         用户登出
- GET  /api/v1/auth/me             获取当前用户信息

测试覆盖：
- 正常流：标准登录、Token 刷新、获取用户信息、登出
- 异常流：错误密码、错误用户名、无效 Token、禁用账户
- 边界值：空表单、字段过短、字段过长
"""

from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db
from src.core.security import hash_password
from src.core.exceptions import AppException
from src.api.exception_handlers import (
    app_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from src.models.user import User


@pytest.fixture(scope="function")
def test_engine():
    """创建测试数据库引擎

    使用 StaticPool 确保 in-memory SQLite 的所有连接共享同一个数据库实例。
    """
    engine = create_engine(
        "sqlite://",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # 启用 SQLite 外键约束
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # 导入所有模型以确保注册
    import src.models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    yield engine

    # 清理
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """创建测试数据库会话"""
    TestSessionLocal = sessionmaker(bind=test_engine)
    session = TestSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client(test_engine):
    """创建测试客户端"""
    TestSessionLocal = sessionmaker(bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # 创建不带 lifespan 的测试专用 FastAPI app
    @asynccontextmanager
    async def _noop_lifespan(app):
        yield

    test_app = FastAPI(title="Test App", lifespan=_noop_lifespan)

    # 注册异常处理器
    test_app.add_exception_handler(AppException, app_exception_handler)
    test_app.add_exception_handler(RequestValidationError, validation_exception_handler)
    test_app.add_exception_handler(Exception, general_exception_handler)

    # 注册认证路由
    from src.api.routes.auth import router as auth_router
    test_app.include_router(auth_router)

    # 覆盖数据库依赖
    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as c:
        yield c

    # 清理
    test_app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def seed_users(db_session):
    """创建测试用户数据

    每个测试前自动创建三个默认用户：admin、teacher、student。
    """
    users = [
        User(
            username="admin",
            hashed_password=hash_password("admin123"),
            role="admin",
            is_active=True,
        ),
        User(
            username="teacher",
            hashed_password=hash_password("teacher123"),
            role="teacher",
            is_active=True,
        ),
        User(
            username="student",
            hashed_password=hash_password("student123"),
            role="student",
            is_active=True,
        ),
        User(
            username="disabled_user",
            hashed_password=hash_password("password123"),
            role="student",
            is_active=False,
        ),
    ]
    db_session.add_all(users)
    db_session.commit()


class TestLoginAPI:
    """登录 API 测试类"""

    # ==================== 正常流测试 ====================

    def test_login_admin_success(self, client):
        """TC-01: 管理员正常登录

        验证：
        - 返回 200 状态码
        - success 为 True
        - 返回 access_token 和 refresh_token
        - token_type 为 bearer
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert data["data"]["expires_in"] > 0
        # Token 不为空字符串
        assert len(data["data"]["access_token"]) > 0
        assert len(data["data"]["refresh_token"]) > 0

    def test_login_teacher_success(self, client):
        """TC-13a: 教师角色登录

        验证：
        - 教师账户可以正常登录
        - 返回有效的 Token
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "teacher", "password": "teacher123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]

    def test_login_student_success(self, client):
        """TC-13b: 学生角色登录

        验证：
        - 学生账户可以正常登录
        - 返回有效的 Token
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "student", "password": "student123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]

    # ==================== 异常流测试 ====================

    def test_login_wrong_password(self, client):
        """TC-02: 错误密码登录

        验证：
        - 返回 401 状态码
        - 错误信息包含"用户名或密码错误"
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "用户名或密码错误" in data["detail"]

    def test_login_nonexistent_user(self, client):
        """TC-03: 不存在的用户名

        验证：
        - 返回 401 状态码
        - 错误信息包含"用户名或密码错误"（不泄露用户是否存在）
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "password123"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "用户名或密码错误" in data["detail"]

    def test_login_disabled_account(self, client):
        """TC-12: 禁用账户登录

        验证：
        - 返回 403 状态码
        - 错误信息包含"账户已被禁用"
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "disabled_user", "password": "password123"},
        )

        assert response.status_code == 403
        data = response.json()
        assert "账户已被禁用" in data["detail"]

    # ==================== 边界值测试 ====================

    def test_login_empty_body(self, client):
        """TC-04a: 空请求体

        验证：
        - 返回 422 状态码（验证失败）
        """
        response = client.post("/api/v1/auth/login", json={})

        assert response.status_code == 422

    def test_login_missing_password(self, client):
        """TC-04b: 缺少密码字段

        验证：
        - 返回 422 状态码（验证失败）
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin"},
        )

        assert response.status_code == 422

    def test_login_missing_username(self, client):
        """TC-04c: 缺少用户名字段

        验证：
        - 返回 422 状态码（验证失败）
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"password": "admin123"},
        )

        assert response.status_code == 422

    def test_login_username_too_short(self, client):
        """TC-05: 用户名过短（2字符）

        验证：
        - 返回 422 状态码
        - 用户名最小长度为 3
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "ab", "password": "admin123"},
        )

        assert response.status_code == 422

    def test_login_password_too_short(self, client):
        """TC-06: 密码过短（5字符）

        验证：
        - 返回 422 状态码
        - 密码最小长度为 6
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "12345"},
        )

        assert response.status_code == 422

    def test_login_empty_string_fields(self, client):
        """TC-04d: 空字符串字段

        验证：
        - 返回 422 状态码（字段不能为空）
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "", "password": ""},
        )

        assert response.status_code == 422


class TestTokenRefreshAPI:
    """Token 刷新 API 测试类"""

    def _get_tokens(self, client) -> dict:
        """辅助方法：获取登录后的 Token"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        return response.json()["data"]

    # ==================== 正常流测试 ====================

    def test_refresh_token_success(self, client):
        """TC-07: 正常刷新 Token

        验证：
        - 返回 200 状态码
        - 返回新的 access_token 和 refresh_token
        - 新 Token 与旧 Token 不同
        """
        # 先登录获取 Token
        tokens = self._get_tokens(client)

        # 使用 refresh_token 刷新
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        # 新 Token 应该与旧 Token 不同
        assert data["data"]["access_token"] != tokens["access_token"]
        assert data["data"]["refresh_token"] != tokens["refresh_token"]

    # ==================== 异常流测试 ====================

    def test_refresh_token_invalid(self, client):
        """TC-08a: 无效的 Refresh Token

        验证：
        - 返回 401 状态码
        """
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token-string"},
        )

        assert response.status_code == 401

    def test_refresh_token_empty(self, client):
        """TC-08b: 空 Refresh Token

        验证：
        - 返回 422 状态码（验证失败）
        """
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": ""},
        )

        # Pydantic 验证通过（非空字符串），但 Token 验证失败
        assert response.status_code in [401, 422]

    def test_refresh_token_reuse_old_token(self, client):
        """TC-08c: 重用已刷新的旧 Refresh Token

        验证：
        - 旧 Refresh Token 被吊销后无法再次使用
        - 返回 401 状态码
        """
        # 先登录获取 Token
        tokens = self._get_tokens(client)

        # 第一次刷新
        response1 = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert response1.status_code == 200

        # 尝试重用旧的 refresh_token（应该已被吊销）
        response2 = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert response2.status_code == 401


class TestGetCurrentUserAPI:
    """获取当前用户信息 API 测试类"""

    def _get_auth_header(self, client) -> dict:
        """辅助方法：获取认证请求头"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        token = response.json()["data"]["access_token"]
        return {"Authorization": f"Bearer {token}"}

    # ==================== 正常流测试 ====================

    def test_get_current_user_success(self, client):
        """TC-09a: 获取当前用户信息

        验证：
        - 返回 200 状态码
        - 返回用户信息包含 id、username、role、is_active
        """
        headers = self._get_auth_header(client)

        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == "admin"
        assert data["data"]["role"] == "admin"
        assert data["data"]["is_active"] is True
        assert "id" in data["data"]

    def test_get_current_user_teacher(self, client):
        """TC-09b: 教师用户获取信息

        验证：
        - 教师角色返回正确的用户信息
        """
        # 教师登录
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "teacher", "password": "teacher123"},
        )
        token = response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["username"] == "teacher"
        assert data["data"]["role"] == "teacher"

    # ==================== 异常流测试 ====================

    def test_get_current_user_no_token(self, client):
        """TC-10a: 未认证访问

        验证：
        - 返回 401 状态码
        - 未提供 Token 时拒绝访问
        """
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client):
        """TC-10b: 无效 Token 访问

        验证：
        - 返回 401 状态码
        - 无效 Token 时拒绝访问
        """
        headers = {"Authorization": "Bearer invalid-token-string"}

        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 401

    def test_get_current_user_expired_token(self, client):
        """TC-10c: 过期 Token 访问

        验证：
        - 返回 401 状态码
        - 过期 Token 时拒绝访问
        """
        from datetime import timedelta
        from src.core.security import jwt_service

        # 创建一个已过期的 Token
        expired_token = jwt_service.create_access_token(
            user_id="1",
            username="admin",
            role="admin",
            expires_delta=timedelta(seconds=-1),  # 已过期
        )
        headers = {"Authorization": f"Bearer {expired_token}"}

        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 401


class TestLogoutAPI:
    """登出 API 测试类"""

    def _get_auth_header(self, client) -> dict:
        """辅助方法：获取认证请求头"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        token = response.json()["data"]["access_token"]
        return {"Authorization": f"Bearer {token}"}

    # ==================== 正常流测试 ====================

    def test_logout_success(self, client):
        """TC-11: 正常登出

        验证：
        - 返回 200 状态码
        - success 为 True
        - 返回登出成功消息
        """
        headers = self._get_auth_header(client)

        response = client.post("/api/v1/auth/logout", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "登出成功" in data["message"]

    # ==================== 异常流测试 ====================

    def test_logout_no_token(self, client):
        """TC-11b: 未认证时登出

        验证：
        - 返回 401 状态码
        """
        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 401


class TestLoginResponseFormat:
    """登录响应格式测试"""

    def test_login_response_has_all_fields(self, client):
        """验证登录响应包含所有必要字段

        检查点：
        - access_token 存在且非空
        - refresh_token 存在且非空
        - token_type 为 bearer
        - expires_in 为正整数
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
        )

        assert response.status_code == 200
        data = response.json()["data"]

        # 验证所有必要字段
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "expires_in" in data

        # 验证字段值
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
        assert isinstance(data["refresh_token"], str)
        assert len(data["refresh_token"]) > 0
        assert data["token_type"] == "bearer"
        assert isinstance(data["expires_in"], int)
        assert data["expires_in"] > 0

    def test_login_token_contains_user_info(self, client):
        """验证 Token 中包含正确的用户信息

        检查点：
        - Token 解码后包含正确的 username
        - Token 解码后包含正确的 role
        """
        from src.core.security import jwt_service

        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
        )

        token = response.json()["data"]["access_token"]

        # 解码 Token 验证内容
        payload = jwt_service.decode_token(token)
        assert payload.username == "admin"
        assert payload.role == "admin"
        assert payload.type == "access"

    def test_login_refresh_token_type(self, client):
        """验证 Refresh Token 的类型为 refresh

        检查点：
        - Refresh Token 的 type 字段为 refresh
        """
        from src.core.security import jwt_service

        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
        )

        token = response.json()["data"]["refresh_token"]

        # 解码 Refresh Token 验证类型
        payload = jwt_service.decode_token(token)
        assert payload.type == "refresh"


class TestAuthEdgeCases:
    """认证边界情况测试"""

    def test_login_sql_injection_attempt(self, client):
        """SQL 注入攻击测试

        验证：
        - SQL 注入不会导致认证绕过
        - 返回 401 状态码
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin' OR '1'='1", "password": "anything"},
        )

        assert response.status_code == 401

    def test_login_special_characters_in_password(self, client):
        """特殊字符密码测试

        验证：
        - 密码中的特殊字符不会导致错误
        - 返回 401（密码错误）
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "p@$$w0rd!#%^&*()"},
        )

        assert response.status_code == 401

    def test_login_unicode_username(self, client):
        """Unicode 用户名测试

        验证：
        - Unicode 用户名不会导致服务器错误
        - 返回 401（用户不存在）
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "管理员", "password": "password123"},
        )

        assert response.status_code == 401

    def test_login_whitespace_password(self, client):
        """空白密码测试

        验证：
        - 纯空白密码不会导致认证绕过
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "      "},
        )

        # 空白密码长度 >= 6，但密码不匹配
        assert response.status_code == 401

    def test_login_case_sensitive_username(self, client):
        """用户名大小写敏感测试

        验证：
        - 用户名区分大小写
        - 'Admin' 不等于 'admin'
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "Admin", "password": "admin123"},
        )

        assert response.status_code == 401
