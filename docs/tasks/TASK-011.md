# TASK-011: 路由守卫与 Token 管理

> **创建日期：** 2026-06-07  
> **负责人：** frontend-dev  
> **优先级：** P0 (核心功能)  
> **状态：** DONE  
> **依赖：** TASK-010

---

## 1. 任务概述

### 1.1 任务描述

完善前端路由守卫机制，实现 Token 的自动刷新、过期处理、权限验证，确保系统的安全性。

### 1.2 关联需求

| 需求编号 | 需求名称 | 来源文档 |
|---------|---------|---------|
| SEC-002 | 前端路由守卫 | comprehensive-check-report.md |
| SEC-003 | Token 存储策略 | comprehensive-check-report.md |

---

## 2. 详细任务清单

### 2.1 路由守卫

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 1.1 | 实现全局前置守卫 | `frontend/src/router/index.ts` | 检查 Token 有效性，未登录跳转登录页 | TODO |
| 1.2 | 添加路由元信息 | `frontend/src/router/index.ts` | 标记哪些路由需要认证 | TODO |

### 2.2 Token 自动刷新

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 2.1 | Axios 响应拦截器 | `frontend/src/utils/request.ts` | 401 时自动尝试刷新 Token | TODO |
| 2.2 | Token 刷新队列 | `frontend/src/utils/request.ts` | 刷新期间其他请求排队等待 | TODO |

### 2.3 权限控制

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 3.1 | 角色权限指令 | `frontend/src/directives/permission.ts` | v-permission 指令控制元素显示 | TODO |
| 3.2 | 路由权限守卫 | `frontend/src/router/index.ts` | 根据用户角色限制可访问路由 | TODO |

---

## 3. 技术规范

### 3.1 路由守卫流程

```
beforeEach(to, from, next)
  ├─ to.meta.requiresAuth === false → next()
  ├─ 无 Token → next('/login')
  ├─ Token 有效 → next()
  ├─ Token 过期 → 尝试刷新
  │   ├─ 刷新成功 → next()
  │   └─ 刷新失败 → next('/login')
  └─ 检查角色权限
      ├─ 有权限 → next()
      └─ 无权限 → next('/403')
```

### 3.2 Token 刷新策略

- 使用 Refresh Token 获取新的 Access Token
- 刷新期间其他 401 请求排队等待
- 刷新完成后重试排队的请求
- 刷新失败则清除所有 Token 并跳转登录页

---

## 4. 验收标准

| 验收项 | 验收标准 |
|-------|---------|
| 路由保护 | 未登录时无法访问任何受保护页面 |
| Token 刷新 | Access Token 过期后自动刷新，用户无感知 |
| 刷新失败 | Refresh Token 也过期时跳转登录页 |
| 角色权限 | 学生角色无法访问管理功能 |
| 请求排队 | 刷新期间不会发送重复的刷新请求 |

---

## 5. 工作量估算

| 子任务 | 预估工时 |
|--------|---------|
| 路由守卫 | 1.5h |
| Token 自动刷新 | 1.5h |
| 权限控制 | 1h |
| **合计** | **4h** |

---

## 6. 输出物清单

- [ ] `frontend/src/router/index.ts` - 更新路由守卫
- [ ] `frontend/src/utils/request.ts` - 更新拦截器
- [ ] `frontend/src/directives/permission.ts` - 权限指令

---

> **任务状态变更记录**
> 
> | 时间 | 状态变更 | 操作人 | 备注 |
> |------|---------|--------|------|
> | 2026-06-07 | - → TODO | PMO | 任务创建 |
