# TASK-013: UI 美化 - 温馨友好风格

> **创建日期：** 2026-06-07  
> **负责人：** frontend-dev  
> **优先级：** P1 (重要功能)  
> **状态：** DONE

---

## 1. 任务概述

### 1.1 任务描述

对系统 UI 进行全面美化，从 Element Plus 默认风格转变为温馨友好的教育系统风格。包括配色方案、侧边栏、卡片样式、字体排版等方面的优化。

### 1.2 设计目标

- **温馨友好**：使用暖色调、圆角设计、柔和阴影
- **现代简洁**：保持界面整洁，避免视觉噪音
- **教育系统风格**：适合学校环境，专业但不死板
- **良好可读性**：确保文字清晰，对比度适当

---

## 2. 详细任务清单

### 2.1 全局样式重构

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 1.1 | 更新 CSS 变量 | `frontend/src/assets/styles/global.scss` | 新的配色方案、圆角、阴影 | TODO |
| 1.2 | 更新 Element Plus 主题 | `frontend/src/main.ts` | 配置 Element Plus 主题色 | TODO |

### 2.2 侧边栏美化

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 2.1 | 重新设计侧边栏 | `frontend/src/components/layout/AppSidebar.vue` | 温馨配色、更好的交互效果 | TODO |

### 2.3 页面美化

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 3.1 | 登录页面美化 | `frontend/src/views/login/Login.vue` | 温馨的登录页面设计 | TODO |
| 3.2 | Dashboard 美化 | `frontend/src/views/dashboard/Dashboard.vue` | 统计卡片、快捷操作优化 | TODO |
| 3.3 | 列表页面美化 | `frontend/src/views/student/StudentList.vue` 等 | 表格、搜索区域优化 | TODO |
| 3.4 | 表单页面美化 | `frontend/src/views/student/StudentForm.vue` 等 | 表单卡片样式优化 | TODO |

### 2.4 组件美化

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 4.1 | 美化 DataTable | `frontend/src/components/common/DataTable.vue` | 表格样式优化 | TODO |
| 4.2 | 美化统计卡片 | Dashboard 和 StatisticsOverview | 卡片设计优化 | TODO |

---

## 3. 设计规范

### 3.1 配色方案

```scss
// 温馨友好配色方案
--primary-color: #5B8DEF;      // 柔和蓝（主色调）
--primary-light: #8BAAFF;      // 浅蓝
--primary-dark: #3A6DD9;       // 深蓝
--success-color: #52C41A;      // 清新绿
--warning-color: #FAAD14;      // 温暖橙
--danger-color: #FF4D4F;       // 柔和红
--bg-color: #F7F8FA;           // 浅灰背景
--sidebar-bg: #FFFFFF;         // 白色侧边栏
--sidebar-active: #EBF3FF;     // 浅蓝选中
--card-shadow: 0 2px 12px rgba(91, 141, 239, 0.08);  // 柔和阴影
--border-radius: 12px;         // 大圆角
```

### 3.2 侧边栏设计

- 白色背景替代深灰色
- 使用主色调作为选中状态
- Logo 区域使用渐变色
- 菜单项增加图标和文字的间距

### 3.3 卡片设计

- 更大的圆角（12px）
- 柔和的阴影效果
- Hover 时轻微上浮
- 统计卡片使用渐变色图标背景

---

## 4. 验收标准

| 验收项 | 验收标准 |
|-------|---------|
| 配色一致 | 所有页面使用统一的温馨配色方案 |
| 侧边栏 | 白色背景，选中状态清晰 |
| 卡片效果 | 圆角、阴影、hover 效果协调 |
| 响应式 | 移动端样式正常 |
| 可读性 | 文字对比度符合 WCAG 标准 |

---

## 5. 工作量估算

| 子任务 | 预估工时 |
|--------|---------|
| 全局样式重构 | 3h |
| 侧边栏美化 | 2h |
| 页面美化 | 8h |
| 组件美化 | 3h |
| **合计** | **16h** |

---

## 6. 输出物清单

- [ ] `frontend/src/assets/styles/global.scss` - 更新全局样式
- [ ] `frontend/src/main.ts` - 更新主题配置
- [ ] `frontend/src/components/layout/AppSidebar.vue` - 更新侧边栏
- [ ] `frontend/src/views/login/Login.vue` - 更新登录页面
- [ ] `frontend/src/views/dashboard/Dashboard.vue` - 更新 Dashboard
- [ ] 各列表和表单页面样式更新

---

> **任务状态变更记录**
> 
> | 时间 | 状态变更 | 操作人 | 备注 |
> |------|---------|--------|------|
> | 2026-06-07 | - → TODO | PMO | 任务创建 |
