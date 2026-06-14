# TASK-019

## 基本信息

| 字段 | 值 |
|------|-----|
| ID | TASK-019 |
| 标题 | Supabase风格UI重设计 |
| 创建时间 | 2026-06-15 10:00 |
| 负责人 | frontend-dev |
| 优先级 | P0 |

## 状态流转

```
TODO → IN_PROGRESS → REVIEWS → TESTING → DONE
                     ↑            │
                (拒绝 ≤ 3 次)     ↓ (拒绝 > 3 次)
              修正后重试          BLOCKED (PMO仲裁)
```

**当前状态：** DONE

## 任务描述

### 需求背景
将学生成绩管理系统前端UI重新设计为Supabase风格，采用深色主题、翠绿色强调色，打造现代、简洁、代码优先的界面风格。

### 设计方向
参考Supabase的现代、简洁、代码优先的设计风格：
- **深色主题为主**：背景色接近黑色 (#0f0f23 或 #1a1a2e)
- **翠绿色强调色**：(#3ecf8e 或类似)
- **现代、简洁、代码优先**的设计风格

### 功能需求

#### 阶段1：设计系统定义
1. **定义设计令牌**
   - 颜色系统（主背景、卡片背景、强调色、文字颜色）
   - 字体系统（Geist Sans/Mono）
   - 间距系统（4px/8px/12px/16px/24px）
   - 圆角系统（8px/12px/16px）
   - 阴影和发光效果

2. **创建全局样式文件**
   - 更新 `global.scss` 为Supabase风格
   - 覆盖Element Plus默认样式变量
   - 定义通用工具类

#### 阶段2：组件重构
1. **布局组件重构**
   - `AppSidebar.vue`：深色背景，翠绿色选中状态
   - `AppHeader.vue`：深色背景，用户信息展示
   - `AppLayout.vue`：整体布局调整

2. **页面组件重构**
   - Dashboard页面：深色卡片，统计图表
   - 学生管理页面：深色表格，表单样式
   - 成绩管理页面：深色主题一致性
   - 统计分析页面：图表主题适配

3. **通用组件重构**
   - 按钮、输入框、卡片、表格等组件样式
   - 对话框、分页、标签等组件样式

#### 阶段3：测试验证
1. **视觉测试**
   - 所有页面显示正常
   - 颜色对比度符合WCAG标准
   - 响应式设计正常

2. **功能测试**
   - 交互效果正常（hover、click、focus）
   - 动画效果流畅
   - 主题切换正常（如果支持）

### 技术要求
- 使用SCSS变量定义设计令牌
- 覆盖Element Plus默认样式变量
- 保持现有功能不变
- 确保响应式设计
- 优化性能，避免不必要的重绘

### 修改文件清单

#### 样式文件
1. `frontend/src/assets/styles/global.scss` - 全局样式重写
2. `frontend/src/assets/styles/variables.scss` - 设计令牌变量（新建）
3. `frontend/src/assets/styles/element-override.scss` - Element Plus样式覆盖（新建）

#### 布局组件
1. `frontend/src/components/layout/AppSidebar.vue` - 侧边栏样式重构
2. `frontend/src/components/layout/AppHeader.vue` - 头部样式重构
3. `frontend/src/components/layout/AppLayout.vue` - 布局样式调整

#### 页面组件
1. `frontend/src/views/dashboard/Dashboard.vue` - Dashboard页面样式
2. `frontend/src/views/student/StudentList.vue` - 学生列表页面样式
3. `frontend/src/views/grade/GradeList.vue` - 成绩列表页面样式
4. `frontend/src/views/statistics/StatisticsOverview.vue` - 统计概览页面样式

## 验收标准

- [x] 深色主题实现完整，所有页面背景色正确
- [x] 翠绿色强调色应用一致，按钮、链接、选中状态等
- [x] 侧边栏深色背景，翠绿色选中状态
- [x] 卡片组件有微妙发光效果
- [x] 字体系统使用Geist Sans/Mono
- [x] 响应式设计正常，移动端可折叠侧边栏
- [x] 所有交互效果正常（hover、click、focus）
- [x] 动画效果流畅，无卡顿
- [x] 颜色对比度符合WCAG标准
- [x] 现有功能不受影响
- [x] 代码结构清晰，样式可维护

## 关联文档

- PRD: `docs/prd.md`
- 架构: `docs/architecture.md`
- 设计系统: `docs/design-system-supabase.md`
- API: `docs/api-spec.md`

## 变更记录

| 时间 | 操作人 | 状态变更 | 备注 |
|------|--------|----------|------|
| 2026-06-15 10:00 | PMO | TODO | 任务创建，需求分析 |
| 2026-06-15 10:05 | PMO | TODO | PRD更新，架构文档更新 |
| 2026-06-15 10:10 | PMO | TODO | 设计系统文档创建 |
| 2026-06-15 10:15 | PMO | IN_PROGRESS | 任务状态更新，开始开发 |
| 2026-06-15 10:20 | Frontend-dev | IN_PROGRESS | 设计系统变量文件创建 |
| 2026-06-15 10:25 | Frontend-dev | IN_PROGRESS | Element Plus样式覆盖创建 |
| 2026-06-15 10:30 | Frontend-dev | IN_PROGRESS | 全局样式文件更新 |
| 2026-06-15 10:35 | Frontend-dev | IN_PROGRESS | 布局组件样式更新 |
| 2026-06-15 10:40 | Frontend-dev | IN_PROGRESS | Dashboard页面样式更新 |
| 2026-06-15 10:45 | Frontend-dev | REVIEWS | 初步开发完成，提交审查 |
| 2026-06-15 11:00 | Reviewer | REVIEWS | 代码审查完成，有条件通过 |
| 2026-06-15 11:05 | PMO | TESTING | 审查通过，进入测试阶段 |
| 2026-06-15 12:00 | QA Engineer | TESTING | 测试执行完成，全部通过 |
| 2026-06-15 12:05 | PMO | DONE | 测试通过，任务完成 |