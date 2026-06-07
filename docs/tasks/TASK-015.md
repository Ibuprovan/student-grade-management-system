# TASK-015: AppHeader 用户信息与退出功能

> **创建日期：** 2026-06-07  
> **负责人：** frontend-dev  
> **优先级：** P1 (重要功能)  
> **状态：** DONE  
> **依赖：** TASK-011

---

## 1. 任务概述

### 1.1 任务描述

修复 AppHeader 中的用户信息显示和退出登录功能，使其与认证系统集成。

### 1.2 关联需求

| 需求编号 | 需求名称 | 来源文档 |
|---------|---------|---------|
| CODE-004 | 用户信息硬编码 | comprehensive-check-report.md |
| CODE-005 | 退出登录未实现 | comprehensive-check-report.md |
| UX-002 | 退出登录无功能 | comprehensive-check-report.md |

---

## 2. 详细任务清单

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 1.1 | 获取用户信息 | `AppHeader.vue` | 从 auth store 获取真实用户名和角色 | TODO |
| 1.2 | 实现退出登录 | `AppHeader.vue` | 调用 logout API，清除 Token，跳转登录页 | TODO |
| 1.3 | 添加角色显示 | `AppHeader.vue` | 显示用户角色标签 | TODO |

---

## 3. 技术规范

### 3.1 用户信息显示

```vue
<span class="user-name">{{ authStore.user?.username || '未登录' }}</span>
<el-tag size="small">{{ roleLabel }}</el-tag>
```

### 3.2 退出登录

```typescript
async function handleLogout() {
  await ElMessageBox.confirm('确定要退出登录吗？', '提示')
  await authStore.logout()
  router.push('/login')
}
```

---

## 4. 验收标准

| 验收项 | 验收标准 |
|-------|---------|
| 用户名显示 | 显示当前登录用户的真实用户名 |
| 角色显示 | 显示用户角色（管理员/教师/学生） |
| 退出登录 | 点击退出后清除 Token 并跳转登录页 |

---

## 5. 工作量估算

| 子任务 | 预估工时 |
|--------|---------|
| 用户信息集成 | 1h |
| 退出登录功能 | 1h |
| 测试验证 | 1h |
| **合计** | **3h** |

---

> **任务状态变更记录**
> 
> | 时间 | 状态变更 | 操作人 | 备注 |
> |------|---------|--------|------|
> | 2026-06-07 | - → TODO | PMO | 任务创建 |
