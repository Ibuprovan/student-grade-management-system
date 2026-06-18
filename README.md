# 学生成绩管理系统

> 基于 OpenCode 多 Agent 虚拟工程团队开发的全栈学生成绩管理系统

<div align="center">

![Vue 3](https://img.shields.io/badge/Vue-3-42b883?style=flat-square&logo=vue.js)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi)
![TypeScript](https://img.shields.io/badge/TypeScript-3178c6?style=flat-square&logo=typescript)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-d71f00?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**[在线演示](http://localhost:5173)** · **[API 文档](http://localhost:8000/docs)** · **[更新日志](CHANGELOG/)**

</div>

---

## 项目简介

学生成绩管理系统是一个现代化的全栈 Web 应用，采用**专业教育风格浅色主题**，由 12 个 AI Agent 协作开发完成。

**核心特性**：

- **专业教育 UI** - 浅色主题，专业蓝主色调，清晰现代
- **JWT 双令牌认证** - Access Token + Refresh Token 安全机制
- **RBAC 权限控制** - 管理员/班主任/教师/学生四级角色权限
- **班主任专属空间** - 只读查看本班学生、成绩与统计
- **数据可视化** - ECharts 图表（折线图、柱状图、饼图、雷达图）
- **批量导入** - Excel/CSV 文件一键导入学生和成绩
- **响应式布局** - 适配 1280px / 1440px / 1920px 多种分辨率

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | Vue 3 + TypeScript | Composition API |
| **UI 组件** | Element Plus | 企业级组件库 |
| **图表** | ECharts 5 | 数据可视化 |
| **状态管理** | Pinia | Vue 3 官方状态管理 |
| **后端** | FastAPI | 高性能 Python 框架 |
| **数据库** | SQLite + SQLAlchemy 2.0 | 轻量级 ORM |
| **认证** | JWT (PyJWT) | 无状态认证 |

---

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+
- npm 或 pnpm

### 安装与启动

```bash
# 1. 克隆项目
git clone https://github.com/Ibuprovan/student-grade-management-system.git
cd student-grade-management-system

# 2. 配置环境变量
cp .env.example .env

# 3. 一键启动（Windows）
start.bat

# 或手动启动：

# 后端
pip install -r requirements.txt
python -m src.scripts.init_users
uvicorn src.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

### 默认账户

| 角色 | 用户名 | 密码 | 权限 |
|------|--------|------|------|
| 管理员 | `admin` | `admin123` | 全部权限 |
| 班主任 | `2026001` | `123456` | 查看本班数据（只读），首次登录强制改密 |
| 教师 | `teacher` | `teacher123` | 学生和成绩管理 |
| 学生 | `student` | `student123` | 查看自己的成绩 |

> 生产环境请务必修改默认密码和 JWT 密钥

---

## 功能特性

### 仪表盘
- 实时统计卡片（学生总数、成绩记录、平均分、及格率）
- 快捷操作入口
- 功能概览

### 学生管理
- 学生列表（分页、搜索、筛选、排序）
- 添加/编辑/删除学生
- 批量导入（Excel/CSV）
- 数据导出

### 成绩管理
- 成绩录入（每人一次录入所有 9 科成绩，实时总分计算）
- 成绩列表（多维度筛选、排序、总分排名视图）
- 批量导入（每人一行模板：学号+姓名+9 科成绩+考试类型+日期）
- 成绩导出

### 班主任空间（Class Teacher）
- **专属仪表盘**：班级概况、学生/成绩统计卡片
- **本班学生列表**：仅展示本班学生，支持搜索/筛选/分页
- **本班成绩列表**：仅展示本班学生成绩，支持科目/日期筛选、总分排名
- **本班统计分析**：总分统计概览 + 单科分数分布（只读）
- **首次登录强制改密**：初始密码 `123456`，登录后需立即修改
- **自动账号创建**：管理员分配班主任时自动生成用户账号

### 统计分析
- **统计概览**：总分统计卡片、总分分布柱状图、科目趋势折线图、科目占比饼图、三维能力雷达图、总分排名表、可选科目单科排名
- **班级统计**：班级平均分对比、及格率/优秀率对比、按班级名称排序（2026级1班→2班→3班→4班→5班）、支持平均分/及格率/优秀率排序
- **科目统计**：科目对比柱状图、及格率/优秀率折线图、分数分布、三维能力雷达图（平均分+及格率+优秀率）
- 所有图表统一 360px 高度，卡片等宽等高

### 权限管理
- 用户管理（管理员）
- 班主任管理（管理员分配班级、自动创建账号）
- 四级角色权限控制：管理员 / 班主任 / 教师 / 学生
- 班主任只读权限，只能查看本班数据
- 操作审计日志

---

## 设计系统

采用**专业教育风格**浅色主题，专业蓝主色调：

```scss
// 主色调
$bg-primary: #f5f7fa;      // 主背景
$bg-secondary: #ffffff;     // 卡片背景
$accent-primary: #2563eb;   // 专业蓝
$text-primary: #1f2937;     // 主要文字
$text-secondary: #6b7280;   // 次要文字
$border-primary: #e5e7eb;   // 边框
```

**设计规范**：
- 图表容器统一 360px 高度，overflow hidden
- 表格占满卡片宽度，min-width 自适应列
- 同行卡片 flex 等高对齐
- 标题层级：h1=24px, h2=20px, h3=16px, h4=14px
- 行高 1.55，段落间距均匀
- 排序三角标、按钮对比度、z-index 层级均有规范

---

## 项目结构

```
student-grade-management-system/
├── src/                          # 后端代码
│   ├── api/routes/               # API 路由
│   │   ├── auth.py               # 认证（含首次登录改密）
│   │   ├── class_teachers.py     # 班主任管理（管理员 CRUD）
│   │   ├── class_teacher_scoped.py # 班主任数据查询（只读）
│   │   ├── students.py           # 学生管理
│   │   ├── grades.py             # 成绩管理
│   │   ├── statistics.py         # 统计分析
│   │   └── import_export.py      # 导入导出
│   ├── core/                     # 核心配置
│   ├── models/                   # 数据模型
│   │   ├── student.py
│   │   ├── grade.py
│   │   ├── user.py
│   │   └── class_teacher.py      # 班主任模型
│   ├── schemas/                  # 数据验证
│   ├── repositories/             # 数据访问层
│   ├── services/                 # 业务逻辑层
│   └── scripts/                  # 工具脚本
├── frontend/                     # 前端代码
│   └── src/
│       ├── api/                  # API 封装（含 classTeacher.ts）
│       ├── stores/               # Pinia 状态管理（含 auth：isClassTeacher）
│       ├── types/                # TypeScript 类型
│       ├── views/                # 页面
│       └── router/               # 路由
├── docs/                         # 文档
├── tests/                        # 测试
├── CHANGELOG/                    # 版本更新日志
├── .env.example                  # 环境变量模板
├── start.bat                     # 启动脚本
└── requirements.txt              # Python 依赖
```

---

## API 文档

启动后端服务后访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要端点

| 模块 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 认证 | POST | `/api/v1/auth/login` | 用户登录 |
| 学生 | GET | `/api/v1/students` | 学生列表 |
| 成绩 | GET | `/api/v1/grades/search` | 成绩查询 |
| 统计 | GET | `/api/v1/statistics` | 统计数据 |
| 统计 | GET | `/api/v1/statistics/batch/subjects` | 批量科目统计 |
| 统计 | GET | `/api/v1/statistics/batch/classes` | 批量班级统计 |
| 统计 | GET | `/api/v1/statistics/report` | 综合统计报告 |
| 导入 | POST | `/api/v1/import/students` | 批量导入学生 |
| 导入 | POST | `/api/v1/import/grades` | 批量导入成绩 |
| 班主任管理 | GET | `/api/v1/class-teachers` | 班主任列表（管理员） |
| 班主任管理 | POST | `/api/v1/class-teachers` | 新增班主任（管理员） |
| 班主任管理 | DELETE | `/api/v1/class-teachers/{id}` | 删除班主任（管理员） |
| 班主任管理 | GET | `/api/v1/class-teachers/available-classes` | 可分配班级列表 |
| 班主任数据 | GET | `/api/v1/class-teacher/dashboard` | 班级仪表盘 |
| 班主任数据 | GET | `/api/v1/class-teacher/students` | 本班学生列表 |
| 班主任数据 | GET | `/api/v1/class-teacher/grades` | 本班成绩列表 |
| 班主任数据 | GET | `/api/v1/class-teacher/statistics/overview` | 本班统计概览 |
| 班主任数据 | GET | `/api/v1/class-teacher/statistics/subject` | 本班科目统计 |

---

## 测试

```bash
# 后端测试
pytest tests/

# 前端构建验证
cd frontend
npm run build
```

---

## 更新日志

| 版本 | 日期 | 说明 |
|------|------|------|
| **V5.0.0** | **2026-06-19** | **新增班主任角色、班级名称统一为"2026级X班"、MyGrades 优化、分数分布修复** |
| V4.4.0 | 2026-06-18 | 成绩计算验证优化（150分满分、及格率/优秀率修复）、CSV导入增强、GradeList重构 |
| V4.3.0 | 2026-06-15 | 成绩录入/导入改造（每人一次录入所有科目）、统计概览重构、班级统计排序 |
| V4.2.0 | 2026-06-15 | 学生总分查看与分析功能（总分排名、各科汇总、三端同步） |
| V4.1.0 | 2026-06-15 | 布局修复与数据可视化优化（图表溢出、卡片对齐、分数分布数据、饼图重叠） |
| V4.0.0 | 2026-06-15 | 前端 UI 重设计为专业教育系统风格 |
| V3.0.0 | 2026-06-15 | 前端 UI 全面重构为 Supabase 深色主题 |
| V2.4.0 | 2026-06-15 | 安全与架构全面优化 |
| V2.3.0 | 2026-06-12 | 新增批量导入功能 |
| V2.0.0 | 2026-06-07 | 第二代全面升级 |

完整更新记录请查看 [CHANGELOG/](CHANGELOG/)

---

## 开发团队

本项目由 12 个 AI Agent 协作开发：

| Agent | 职责 |
|-------|------|
| PMO | 项目管理办公室 |
| PM | 产品经理 |
| Architect | 系统架构师 |
| Frontend Dev | 前端工程师 |
| Backend Dev | 后端工程师 |
| Reviewer | 代码审查员 |
| QA Engineer | 测试工程师 |
| DevOps | 交付工程师 |
| Security | 合规安全官 |
| Memory | 记忆中台 |
| Report | 报告生成器 |
| Cyber | 网安特化智能体 |

---

## 安全特性

- JWT 双令牌认证（Access + Refresh）
- RBAC 三级权限控制
- CORS 安全配置
- 安全响应头（X-Content-Type-Options, X-Frame-Options 等）
- 输入验证（Pydantic + 前端双重验证）
- SQL 注入防护（全 ORM 架构）
- 速率限制（登录接口 10次/分钟）
- 密码哈希（bcrypt）

---

## 许可证

[MIT License](LICENSE)

---

<div align="center">

**[回到顶部](#学生成绩管理系统)**

</div>
