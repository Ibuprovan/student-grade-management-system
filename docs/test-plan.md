# 登录功能测试计划（第二轮）

> **测试日期：** 2026-06-08  
> **测试工程师：** QA Agent  
> **测试类型：** 功能修复验证（第二轮）  
> **测试状态：** 已完成

---

## 1. 测试背景

用户反馈上一轮测试声称通过但登录仍然不工作。本轮测试必须：
- 启动后端和前端服务
- 通过 API 模拟完整浏览器登录流程
- 记录真实的测试结果
- 如实报告任何失败

---

## 2. 测试环境

| 组件 | 版本/配置 | 状态 |
|------|----------|------|
| Python | 3.x | ✅ 运行中 |
| FastAPI (后端) | uvicorn on port 8000 | ✅ 运行中 |
| Vue 3 + Vite (前端) | dev server on port 3000 | ✅ 运行中 |
| SQLite 数据库 | data/grades.db | ✅ 已初始化 |
| 默认用户 | admin/admin123, teacher/teacher123, student/student123 | ✅ 已创建 |

---

## 3. 测试矩阵

### 3.1 后端 API 测试

| 编号 | 测试用例 | 输入 | 预期结果 | 实际结果 | 状态 |
|------|---------|------|---------|---------|------|
| API-01 | 正确密码登录 | admin/admin123 | 200 + tokens | 200 + access_token + refresh_token | ✅ PASS |
| API-02 | 错误密码登录 | admin/wrongpassword | 401 | 401 Unauthorized | ✅ PASS |
| API-03 | 不存在用户 | nonexistent/admin123 | 401 | 401 Unauthorized | ✅ PASS |
| API-04 | 空请求体 | {} | 422 | 422 Validation Error | ✅ PASS |
| API-05 | 用户名过短 | ab/admin123 | 422 | 422 Validation Error | ✅ PASS |
| API-06 | 密码过短 | admin/12345 | 422 | 422 Validation Error | ✅ PASS |
| API-07 | 获取用户信息 | valid token | 200 + user info | 200 + user data | ✅ PASS |
| API-08 | 无 token 访问 | no auth header | 401/403 | 401 | ✅ PASS |
| API-09 | 无效 token | invalid_token | 401 | 401 | ✅ PASS |
| API-10 | Token 刷新 | valid refresh_token | 200 + new tokens | 200 + new tokens | ✅ PASS |

### 3.2 端到端流程测试

| 编号 | 测试用例 | 测试步骤 | 预期结果 | 实际结果 | 状态 |
|------|---------|---------|---------|---------|------|
| E2E-01 | 完整登录流程 | login → get tokens → get /me | 成功获取用户信息 | user_id=1, username=admin, role=admin | ✅ PASS |
| E2E-02 | 错误密码处理 | login with wrong password | 返回 401 + 错误消息 | 401 + "用户名或密码错误" | ✅ PASS |
| E2E-03 | 空表单提交 | login with empty fields | 返回 422 + 验证错误 | 422 + validation error | ✅ PASS |
| E2E-04 | Dashboard 访问 | login → access /dashboard/stats | 200 + 统计数据 | 200 + stats data | ✅ PASS |
| E2E-05 | 未认证访问保护路由 | access /dashboard/stats without token | 401 | 401 | ✅ PASS |
| E2E-06 | Token 自动刷新 | login → refresh token → get new tokens | 新 tokens 且与旧的不同 | tokens_are_different=True | ✅ PASS |
| E2E-07 | 登出流程 | login → logout | 200 + 成功消息 | 200 + "登出成功" | ✅ PASS |
| E2E-08 | 教师账号登录 | teacher/teacher123 | 200 + teacher role | role=teacher | ✅ PASS |
| E2E-09 | 学生账号登录 | student/student123 | 200 + student role | role=student | ✅ PASS |
| E2E-10 | CORS 配置 | OPTIONS request | 204 + CORS headers | 204 + correct headers | ✅ PASS |

### 3.3 前端代码审查

| 编号 | 审查项 | 审查内容 | 结果 |
|------|--------|---------|------|
| CODE-01 | Login.vue 表单验证 | username: required, min 3, max 50; password: required, min 6, max 128 | ✅ 正确 |
| CODE-02 | auth store login 函数 | 调用 API → 保存 tokens → 获取用户信息 → 返回 boolean | ✅ 正确 |
| CODE-03 | request.ts 拦截器 | 自动附加 token，处理 401，token 自动刷新 | ✅ 正确 |
| CODE-04 | router 守卫 | 检查认证状态，未登录跳转 /login | ✅ 正确 |
| CODE-05 | 错误处理 | catch 块提取 detail 字段显示错误消息 | ✅ 正确 |
| CODE-06 | Vite 代理配置 | /api → http://localhost:8000 | ✅ 正确 |
| CODE-07 | API base URL | /api/v1 (通过 VITE_API_BASE_URL 或默认值) | ✅ 正确 |

---

## 4. 测试结论

### 4.1 测试结果汇总

| 类别 | 总数 | 通过 | 失败 | 通过率 |
|------|------|------|------|--------|
| 后端 API 测试 | 10 | 10 | 0 | 100% |
| 端到端流程测试 | 10 | 10 | 0 | 100% |
| 前端代码审查 | 7 | 7 | 0 | 100% |
| **总计** | **27** | **27** | **0** | **100%** |

### 4.2 验收标准检查

| 验收标准 | 状态 | 说明 |
|---------|------|------|
| 正确密码登录 → 成功获取 tokens | ✅ 通过 | 返回 access_token + refresh_token |
| 错误密码登录 → 显示错误提示 | ✅ 通过 | 返回 401 + "用户名或密码错误" |
| 空表单提交 → 显示表单验证错误 | ✅ 通过 | 前端验证 + 后端 422 |
| Token 自动刷新 | ✅ 通过 | 新 tokens 与旧 tokens 不同 |
| 路由守卫保护 | ✅ 通过 | 未认证访问返回 401 |

### 4.3 最终判定

**✅ 测试通过 - 登录功能工作正常**

所有 27 项测试全部通过，登录功能在 API 层面和代码层面均工作正常。

---

## 5. 附录：测试脚本

### 5.1 后端 API 测试脚本
- 文件：`test_login_api.py`（10 个测试用例）

### 5.2 端到端测试脚本
- 文件：`test_e2e.py`（10 个测试用例）
