# TASK-012: Dashboard 真实数据接入

> **创建日期：** 2026-06-07  
> **负责人：** frontend-dev  
> **优先级：** P0 (核心功能)  
> **状态：** DONE  
> **依赖：** TASK-011

---

## 1. 任务概述

### 1.1 任务描述

将 Dashboard 页面的硬编码模拟数据替换为真实 API 数据，展示系统的真实运行状态。

### 1.2 关联需求

| 需求编号 | 需求名称 | 来源文档 |
|---------|---------|---------|
| UX-003 | Dashboard 真实数据 | comprehensive-check-report.md |
| CODE-003 | Dashboard 硬编码数据 | comprehensive-check-report.md |

---

## 2. 详细任务清单

### 2.1 后端 API

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 1.1 | 创建 Dashboard 统计接口 | `src/api/routes/dashboard.py` | 返回学生总数、成绩记录数、平均分、及格率 | TODO |
| 1.2 | 创建 Dashboard Service | `src/services/dashboard_service.py` | 汇总统计数据 | TODO |

### 2.2 前端集成

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 2.1 | 创建 Dashboard API | `frontend/src/api/dashboard.ts` | 封装 Dashboard 统计接口 | TODO |
| 2.2 | 创建 Dashboard Store | `frontend/src/stores/dashboard.ts` | 管理 Dashboard 状态 | TODO |
| 2.3 | 修改 Dashboard 页面 | `frontend/src/views/dashboard/Dashboard.vue` | 调用真实 API，添加加载状态 | TODO |

---

## 3. 技术规范

### 3.1 Dashboard API 响应格式

```json
{
  "success": true,
  "data": {
    "total_students": 128,
    "total_grades": 1024,
    "average_score": 78.5,
    "pass_rate": 85.2,
    "recent_grades": [...],
    "class_distribution": [...]
  }
}
```

### 3.2 加载状态

- 统计卡片加载时显示骨架屏或 loading 状态
- 数据加载失败时显示重试按钮

---

## 4. 验收标准

| 验收项 | 验收标准 |
|-------|---------|
| 数据真实 | 统计数据来自真实数据库 |
| 加载状态 | 数据加载时有明确的加载指示 |
| 错误处理 | API 调用失败时有友好提示 |
| 自动刷新 | 页面加载时自动获取数据 |

---

## 5. 工作量估算

| 子任务 | 预估工时 |
|--------|---------|
| 后端 API | 1.5h |
| 前端集成 | 1.5h |
| 加载状态和错误处理 | 1h |
| **合计** | **4h** |

---

## 6. 输出物清单

- [ ] `src/api/routes/dashboard.py` - Dashboard 路由
- [ ] `src/services/dashboard_service.py` - Dashboard 服务
- [ ] `frontend/src/api/dashboard.ts` - Dashboard API
- [ ] `frontend/src/stores/dashboard.ts` - Dashboard Store
- [ ] `frontend/src/views/dashboard/Dashboard.vue` - 更新 Dashboard 页面

---

> **任务状态变更记录**
> 
> | 时间 | 状态变更 | 操作人 | 备注 |
> |------|---------|--------|------|
> | 2026-06-07 | - → TODO | PMO | 任务创建 |
