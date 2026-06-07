# TASK-010: 前端登录页面与认证流程

> **创建日期：** 2026-06-07  
> **负责人：** frontend-dev  
> **优先级：** P0 (核心功能)  
> **状态：** TODO

---

## 1. 任务概述

### 1.1 任务描述

实现前端完整的用户认证流程，包括登录页面、Token 管理、认证状态持久化，是系统可用的前提条件。

### 1.2 业务背景

后端已实现完整的 JWT 认证机制（Access Token + Refresh Token），但前端缺少：
- 登录页面
- Token 存储和管理
- 认证状态持久化
- Axios 请求拦截器自动附加 Token

### 1.3 关联需求

| 需求编号 | 需求名称 | 来源文档 |
|---------|---------|---------|
| F-SEC-001 | 用户认证 | comprehensive-check-report.md |
| UX-001 | 登录页面 | comprehensive-check-report.md |

---

## 2. 详细任务清单

### 2.1 认证状态管理

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 1.1 | 创建 auth store | `frontend/src/stores/auth.ts` | 管理 Token、用户信息、登录状态 | ✅ DONE |
| 1.2 | 定义认证类型 | `frontend/src/types/auth.ts` | LoginRequest、TokenResponse、UserInfo 类型 | ✅ DONE |

### 2.2 登录页面

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 2.1 | 创建登录页面 | `frontend/src/views/login/Login.vue` | 用户名/密码登录表单，表单验证 | ✅ DONE |
| 2.2 | 添加登录路由 | `frontend/src/router/index.ts` | 添加 `/login` 路由，不在布局内 | ✅ DONE |

### 2.3 API 集成

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 3.1 | 创建认证 API | `frontend/src/api/auth.ts` | login、refresh、logout、getMe 接口封装 | ✅ DONE |
| 3.2 | 修改 Axios 拦截器 | `frontend/src/utils/request.ts` | 自动附加 Token、处理 401 自动刷新 | ✅ DONE |

### 2.4 认证流程集成

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 4.1 | 修改路由守卫 | `frontend/src/router/index.ts` | 检查 Token，未登录跳转登录页 | ✅ DONE |
| 4.2 | 修改 App.vue | `frontend/src/App.vue` | 根据登录状态切换布局 | ✅ DONE |

---

## 3. 技术规范

### 3.1 登录页面设计

- 使用 Element Plus 的 el-form 组件
- 表单字段：用户名、密码
- 支持 Enter 键提交
- 登录成功后跳转到 Dashboard
- 登录失败显示友好错误提示

### 3.2 Token 管理策略

```
登录成功 → 存储 access_token + refresh_token 到 localStorage
请求拦截 → 自动附加 Authorization: Bearer <token>
401 响应 → 尝试 refresh_token 刷新
刷新失败 → 清除 Token，跳转登录页
```

### 3.3 路由守卫规则

```
公开路由（/login）→ 无需认证
受保护路由 → 检查 Token
  - Token 有效 → 放行
  - Token 过期 → 尝试刷新
  - 无 Token → 跳转登录页
```

---

## 4. 验收标准

### 4.1 功能验收

| 验收项 | 验收标准 | 测试方法 |
|-------|---------|---------|
| 登录功能 | 输入正确用户名密码能成功登录 | 手动测试 |
| Token 存储 | 登录后 Token 正确存储在 localStorage | 浏览器开发者工具 |
| 路由守卫 | 未登录时访问受保护页面自动跳转登录页 | 手动测试 |
| 自动附加 Token | API 请求自动携带 Authorization 头 | 网络面板 |
| Token 刷新 | Access Token 过期时自动使用 Refresh Token 刷新 | 手动测试 |
| 退出登录 | 点击退出后清除 Token 并跳转登录页 | 手动测试 |

### 4.2 代码质量验收

| 验收项 | 验收标准 |
|-------|---------|
| TypeScript | 所有类型定义完整 |
| 错误处理 | 登录失败、Token 刷新失败有友好提示 |
| 代码规范 | ESLint + Prettier 通过 |

---

## 5. 依赖关系

### 5.1 前置依赖

无（后端认证 API 已就绪）

### 5.2 后续依赖

| 任务编号 | 任务名称 | 依赖说明 |
|---------|---------|---------|
| TASK-011 | 路由守卫与 Token 管理 | 依赖本任务的 auth store |
| TASK-012 | Dashboard 真实数据接入 | 依赖本任务的认证状态 |
| TASK-015 | AppHeader 用户信息与退出功能 | 依赖本任务的 auth store |

---

## 6. 工作量估算

| 子任务 | 预估工时 | 备注 |
|--------|---------|------|
| 认证状态管理 | 2h | auth store + types |
| 登录页面 | 2h | UI + 表单验证 |
| API 集成 | 2h | auth API + 拦截器 |
| 认证流程集成 | 2h | 路由守卫 + App 改造 |
| **合计** | **8h** | |

---

## 7. 输出物清单

- [x] `frontend/src/types/auth.ts` - 认证类型定义
- [x] `frontend/src/api/auth.ts` - 认证 API 封装
- [x] `frontend/src/stores/auth.ts` - 认证状态管理
- [x] `frontend/src/views/login/Login.vue` - 登录页面
- [x] `frontend/src/router/index.ts` - 更新路由配置
- [x] `frontend/src/utils/request.ts` - 更新 Axios 拦截器
- [x] `frontend/src/App.vue` - 更新根组件

---

> **任务状态变更记录**
> 
> | 时间 | 状态变更 | 操作人 | 备注 |
> |------|---------|--------|------|
> | 2026-06-07 | - → TODO | PMO | 任务创建 |
> | 2026-06-07 | TODO → IN_PROGRESS | frontend-dev | 开始执行 |
> | 2026-06-07 | IN_PROGRESS → REVIEWS | frontend-dev | 开发完成，提交审查 |
> | 2026-06-07 | REVIEWS → TESTING | PMO | 审查通过，进入测试 |
> | 2026-06-07 | TESTING → DONE | PMO | 测试通过，任务完成 |
