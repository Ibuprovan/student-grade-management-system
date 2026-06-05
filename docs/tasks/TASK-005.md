# TASK-005: 前端项目初始化与基础架构

> **创建日期：** 2026-06-06  
> **负责人：** frontend-dev  
> **优先级：** P0 (核心功能)  
> **状态：** DONE

---

## 1. 任务概述

### 1.1 任务描述

初始化前端项目，搭建基于 Vue 3 + Element Plus + Vite 的基础架构，包括项目结构、路由配置、状态管理、API 封装、布局组件等基础设施，为后续页面开发提供标准化的开发环境。

### 1.2 业务背景

根据 PRD 的前端页面模块（F-FE）和架构文档的前端架构设计，前端项目需要采用 Vue 3 技术栈，配合 Element Plus UI 组件库、ECharts 图表库、Pinia 状态管理等，实现学生成绩管理系统的 Web 前端界面。

### 1.3 关联需求

| 需求编号 | 需求名称 | 来源文档 |
|---------|---------|---------|
| F-FE-001 | 学生信息管理页面 | prd.md |
| F-FE-002 | 成绩录入页面 | prd.md |
| F-FE-003 | 成绩查询页面 | prd.md |
| F-FE-004 | 统计分析页面 | prd.md |
| F-FE-005 | 响应式布局 | prd.md |

---

## 2. 详细任务清单

### 2.1 项目初始化

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 1.1 | 创建 Vue 3 项目 | rontend/ | 使用 Vite 创建 Vue 3 + TypeScript 项目 | DONE |
| 1.2 | 配置 package.json | rontend/package.json | 安装核心依赖：vue-router, pinia, axios, element-plus, echarts | DONE |
| 1.3 | 配置 Vite | rontend/vite.config.ts | 配置代理、别名、插件 | DONE |
| 1.4 | 配置 TypeScript | rontend/tsconfig.json | 配置路径别名、编译选项 | DONE |
| 1.5 | 配置 ESLint + Prettier | rontend/.eslintrc.cjs, rontend/.prettierrc | 代码规范配置 | DONE |

### 2.2 目录结构搭建

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 2.1 | 创建 src/api/ 目录 | rontend/src/api/ | API 接口封装目录 | DONE |
| 2.2 | 创建 src/assets/ 目录 | rontend/src/assets/ | 静态资源目录（images, styles） | DONE |
| 2.3 | 创建 src/components/ 目录 | rontend/src/components/ | 公共组件目录（layout, common, chart） | DONE |
| 2.4 | 创建 src/composables/ 目录 | rontend/src/composables/ | 组合式函数目录 | DONE |
| 2.5 | 创建 src/router/ 目录 | rontend/src/router/ | 路由配置目录 | DONE |
| 2.6 | 创建 src/stores/ 目录 | rontend/src/stores/ | 状态管理目录 | DONE |
| 2.7 | 创建 src/types/ 目录 | rontend/src/types/ | TypeScript 类型定义目录 | DONE |
| 2.8 | 创建 src/utils/ 目录 | rontend/src/utils/ | 工具函数目录 | DONE |
| 2.9 | 创建 src/views/ 目录 | rontend/src/views/ | 页面组件目录（student, grade, statistics, dashboard） | DONE |

### 2.3 核心配置文件

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 3.1 | 创建 Axios 实例配置 | rontend/src/api/index.ts | 配置 baseURL、超时、拦截器 | DONE |
| 3.2 | 创建路由配置 | rontend/src/router/index.ts | 配置路由表、路由守卫 | DONE |
| 3.3 | 创建应用入口 | rontend/src/main.ts | 初始化 Vue 应用、注册插件 | DONE |
| 3.4 | 创建根组件 | rontend/src/App.vue | 根组件，包含路由出口 | DONE |
| 3.5 | 创建 HTML 模板 | rontend/index.html | 入口 HTML 文件 | DONE |

### 2.4 布局组件开发

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 4.1 | 创建头部导航组件 | rontend/src/components/layout/AppHeader.vue | 顶部导航栏，包含 logo、用户信息 | DONE |
| 4.2 | 创建侧边栏组件 | rontend/src/components/layout/AppSidebar.vue | 左侧菜单导航 | DONE |
| 4.3 | 创建整体布局组件 | rontend/src/components/layout/AppLayout.vue | 主布局，组合 Header + Sidebar + Content | DONE |

### 2.5 通用组件开发

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 5.1 | 创建数据表格组件 | rontend/src/components/common/DataTable.vue | 基于 el-table 的通用表格组件 | DONE |
| 5.2 | 创建搜索表单组件 | rontend/src/components/common/SearchForm.vue | 通用搜索表单组件 | DONE |
| 5.3 | 创建分页组件 | rontend/src/components/common/Pagination.vue | 分页组件 | DONE |
| 5.4 | 创建确认对话框组件 | rontend/src/components/common/ConfirmDialog.vue | 确认操作对话框 | DONE |

### 2.6 工具函数开发

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 6.1 | 创建请求工具 | rontend/src/utils/request.ts | 封装 Axios 请求方法 | DONE |
| 6.2 | 创建格式化工具 | rontend/src/utils/format.ts | 日期、数字等格式化函数 | DONE |
| 6.3 | 创建验证工具 | rontend/src/utils/validation.ts | 表单验证规则 | DONE |

### 2.7 TypeScript 类型定义

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 7.1 | 创建学生类型定义 | rontend/src/types/student.ts | Student, StudentCreate, StudentUpdate 等类型 | DONE |
| 7.2 | 创建成绩类型定义 | rontend/src/types/grade.ts | Grade, GradeCreate, GradeBatchCreate 等类型 | DONE |
| 7.3 | 创建统计类型定义 | rontend/src/types/statistics.ts | StatisticsQuery, StatisticsResponse 等类型 | DONE |

---

## 3. 技术规范

### 3.1 技术栈

| 类别 | 技术选择 | 版本要求 | 说明 |
|------|---------|---------|------|
| 前端框架 | Vue 3 | 3.3+ | 组合式 API |
| UI 组件库 | Element Plus | 2.4+ | 按需导入 |
| 图表库 | ECharts | 5.4+ | 数据可视化 |
| 状态管理 | Pinia | 2.1+ | Vue 3 官方推荐 |
| HTTP 客户端 | Axios | 1.4+ | 请求拦截器 |
| 构建工具 | Vite | 4.4+ | 快速冷启动 |
| 路由管理 | Vue Router | 4.2+ | 嵌套路由 |
| 代码规范 | ESLint + Prettier | ESLint 8.44+ / Prettier 3.0+ | 代码格式化 |
| 测试框架 | Vitest | 0.34+ | 单元测试 |

### 3.2 目录结构规范

`
frontend/
├── public/                    # 静态资源
│   ├── favicon.ico           # 网站图标
│   └── index.html            # HTML入口模板
├── src/
│   ├── api/                  # API接口封装
│   │   ├── index.ts          # Axios实例配置
│   │   ├── student.ts        # 学生相关API
│   │   ├── grade.ts          # 成绩相关API
│   │   └── statistics.ts     # 统计相关API
│   ├── assets/               # 静态资源
│   │   ├── images/           # 图片资源
│   │   └── styles/           # 全局样式
│   ├── components/           # 公共组件
│   │   ├── layout/           # 布局组件
│   │   ├── common/           # 通用组件
│   │   └── chart/            # 图表组件
│   ├── composables/          # 组合式函数
│   ├── router/               # 路由配置
│   ├── stores/               # 状态管理
│   ├── types/                # TypeScript类型定义
│   ├── utils/                # 工具函数
│   ├── views/                # 页面组件
│   ├── App.vue               # 根组件
│   └── main.ts               # 应用入口
├── package.json              # 依赖配置
├── vite.config.ts            # Vite配置
├── tsconfig.json             # TypeScript配置
├── .eslintrc.cjs             # ESLint配置
└── .prettierrc               # Prettier配置
`

### 3.3 路由配置规范

`	ypescript
// 路由结构
/                           # 重定向到 /dashboard
/dashboard                  # 仪表盘
/student                    # 学生管理
  /student/list             # 学生列表
  /student/add              # 添加学生
  /student/edit/:id         # 编辑学生
  /student/detail/:id       # 学生详情
/grade                      # 成绩管理
  /grade/list               # 成绩列表
  /grade/input              # 成绩录入
  /grade/import             # 成绩导入
/statistics                 # 统计分析
  /statistics/overview      # 统计概览
  /statistics/class         # 班级统计
  /statistics/subject       # 科目统计
`

### 3.4 API 接口规范

| 规范项 | 说明 | 示例 |
|--------|------|------|
| 基础路径 | 所有 API 以 /api/v1 为前缀 | /api/v1/students |
| 请求方法 | 遵循 RESTful 规范 | GET, POST, PUT, DELETE |
| 响应格式 | 统一 JSON 格式 | { success: true, data: {}, error: null } |
| 分页参数 | 使用 page 和 page_size | ?page=1&page_size=20 |
| 错误处理 | HTTP 状态码 + 业务错误码 | 404 + STUDENT_NOT_FOUND |

---

## 4. 验收标准

### 4.1 功能验收

| 验收项 | 验收标准 | 测试方法 |
|-------|---------|---------|
| 项目启动 | 
pm run dev 成功启动开发服务器 | 手动测试 |
| 路由导航 | 所有路由可正常访问，页面切换流畅 | 手动测试 |
| 布局组件 | Header、Sidebar、Layout 组件正常显示 | 手动测试 |
| 通用组件 | DataTable、SearchForm、Pagination 组件可复用 | 组件测试 |
| API 封装 | Axios 实例配置正确，拦截器生效 | 单元测试 |
| 状态管理 | Pinia Store 可正常创建和使用 | 单元测试 |
| TypeScript | 类型定义完整，无类型错误 | 编译检查 |
| 代码规范 | ESLint + Prettier 检查通过 | 命令行检查 |

### 4.2 性能验收

| 验收项 | 验收标准 | 测试方法 |
|-------|---------|---------|
| 首屏加载 | 首屏加载时间 < 2 秒 | Lighthouse 测试 |
| 热更新 | 修改代码后热更新 < 1 秒 | 开发体验 |
| 构建速度 | 生产构建时间 < 30 秒 | 构建测试 |

### 4.3 兼容性验收

| 验收项 | 验收标准 | 测试方法 |
|-------|---------|---------|
| 浏览器兼容 | Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ | CrossBrowserTesting |
| 响应式布局 | 支持 320px - 4K 分辨率 | 多设备测试 |

---

## 5. 依赖关系

### 5.1 前置依赖

| 任务编号 | 任务名称 | 依赖说明 |
|---------|---------|---------|
| 无 | - | 本任务为前端开发的第一步 |

### 5.2 后续依赖

| 任务编号 | 任务名称 | 依赖说明 |
|---------|---------|---------|
| TASK-006 | 学生信息管理前端页面 | 依赖本任务的基础架构 |
| TASK-007 | 成绩管理前端页面 | 依赖本任务的基础架构 |
| TASK-008 | 统计分析前端页面 | 依赖本任务的基础架构 |

---

## 6. 风险与注意事项

| 风险项 | 说明 | 应对措施 |
|-------|------|---------|
| 依赖版本冲突 | npm 依赖可能存在版本冲突 | 使用 pnpm 或锁定依赖版本 |
| TypeScript 配置 | TS 配置可能影响开发体验 | 参考 Vue 3 官方配置 |
| Element Plus 按需导入 | 按需导入配置复杂 | 使用 unplugin-vue-components 插件 |
| 跨域问题 | 开发环境可能遇到跨域 | 配置 Vite 代理 |

---

## 7. 工作量估算

| 子任务 | 预估工时 | 备注 |
|--------|---------|------|
| 项目初始化 | 1h | Vite 创建项目、安装依赖 |
| 目录结构搭建 | 0.5h | 创建目录、初始化文件 |
| 核心配置文件 | 2h | Axios、路由、入口文件 |
| 布局组件开发 | 3h | Header、Sidebar、Layout |
| 通用组件开发 | 4h | DataTable、SearchForm、Pagination、ConfirmDialog |
| 工具函数开发 | 2h | request、format、validation |
| TypeScript 类型定义 | 1.5h | student、grade、statistics 类型 |
| 测试与调试 | 2h | 功能测试、问题修复 |
| **合计** | **16h** | |

---

## 8. 输出物清单

- [x] rontend/ - 前端项目根目录
- [x] rontend/package.json - 依赖配置
- [x] rontend/vite.config.ts - Vite 配置
- [x] rontend/tsconfig.json - TypeScript 配置
- [x] rontend/.eslintrc.cjs - ESLint 配置
- [x] rontend/.prettierrc - Prettier 配置
- [x] rontend/src/api/index.ts - Axios 实例配置
- [x] rontend/src/router/index.ts - 路由配置
- [x] rontend/src/main.ts - 应用入口
- [x] rontend/src/App.vue - 根组件
- [x] rontend/src/components/layout/AppHeader.vue - 头部导航
- [x] rontend/src/components/layout/AppSidebar.vue - 侧边栏
- [x] rontend/src/components/layout/AppLayout.vue - 整体布局
- [x] rontend/src/components/common/DataTable.vue - 数据表格
- [x] rontend/src/components/common/SearchForm.vue - 搜索表单
- [x] rontend/src/components/common/Pagination.vue - 分页组件
- [x] rontend/src/components/common/ConfirmDialog.vue - 确认对话框
- [x] rontend/src/utils/request.ts - 请求工具
- [x] rontend/src/utils/format.ts - 格式化工具
- [x] rontend/src/utils/validation.ts - 验证工具
- [x] rontend/src/types/student.ts - 学生类型定义
- [x] rontend/src/types/grade.ts - 成绩类型定义
- [x] rontend/src/types/statistics.ts - 统计类型定义

---

## 9. 任务状态变更记录

| 时间 | 状态变更 | 操作人 | 备注 |
|------|---------|--------|------|
| 2026-06-06 | - → TODO | PMO | 任务创建 |
| 2026-06-06 | TODO → IN_PROGRESS | frontend-dev | 前端项目初始化完成 |
| 2026-06-06 | IN_PROGRESS → REVIEWS | frontend-dev | 第一次提交审查 |
| 2026-06-06 | REVIEWS → IN_PROGRESS | reviewer | 第一次拒绝：API端点不符、Element Plus全量导入、PaginatedResponse字段名错误 |
| 2026-06-06 | IN_PROGRESS → REVIEWS | frontend-dev | 第二次提交审查（已修复所有问题） |
| 2026-06-06 | REVIEWS → **DONE** | reviewer | ? 审查通过 |

---

> **任务完成**  
> 所有审查问题已修复，前端基础架构符合项目规范。  
> 可进入 TASK-006/007/008 的页面开发。
