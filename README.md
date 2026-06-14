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

学生成绩管理系统是一个现代化的全栈 Web 应用，采用 **Supabase 深色主题**设计风格，由 12 个 AI Agent 协作开发完成。

**核心特性**：
- 🎨 **Supabase 深色主题** - 专业级 UI 设计，翠绿色强调色
- 🔐 **JWT 双令牌认证** - Access Token + Refresh Token 安全机制
- 👥 **RBAC 权限控制** - 管理员/教师/学生三级角色权限
- 📊 **数据可视化** - ECharts 图表展示统计分析
- 📥 **批量导入** - Excel/CSV 文件一键导入学生和成绩

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | Vue 3 + TypeScript | 响应式框架 |
| **UI 组件** | Element Plus | 企业级组件库 |
| **图表** | ECharts | 数据可视化 |
| **状态管理** | Pinia | Vue 3 官方状态管理 |
| **后端** | FastAPI | 高性能 Python 框架 |
| **数据库** | SQLite + SQLAlchemy 2.0 | 轻量级 ORM |
| **认证** | JWT (PyJWT) | 无状态认证 |
| **设计风格** | Supabase Dark | 深色主题设计系统 |

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
| 教师 | `teacher` | `teacher123` | 学生和成绩管理 |
| 学生 | `student` | `student123` | 查看自己的成绩 |

> ⚠️ 生产环境请务必修改默认密码和 JWT 密钥

---

## 功能特性

### 📊 仪表盘
- 实时统计数据展示
- 学生数量、成绩记录、平均分、及格率
- ECharts 图表可视化

### 👥 学生管理
- 学生列表（分页、搜索、筛选）
- 添加/编辑/删除学生
- 批量导入（Excel/CSV）
- 数据导出

### 📝 成绩管理
- 成绩录入（单条/批量）
- 成绩列表（多维度筛选）
- 批量导入成绩
- 成绩导出

### 📈 统计分析
- 统计概览
- 班级统计
- 科目统计
- 数据可视化图表

### 🔐 权限管理
- 用户管理（管理员）
- 角色权限控制
- 操作审计日志

---

## 设计系统

本项目采用 **Supabase 深色主题**设计风格：

```scss
// 主色调
$bg-primary: #0f0f23;      // 深色背景
$bg-secondary: #1a1a2e;    // 次要背景
$bg-tertiary: #16213e;     // 三级背景
$accent: #3ecf8e;           // 翠绿色强调
$text-primary: #ffffff;     // 主要文字
$text-secondary: #6b7280;   // 次要文字
```

**设计特点**：
- 深色主题，减少视觉疲劳
- 翠绿色强调色，提升视觉层次
- 现代化卡片设计，圆角边框
- 平滑过渡动画
- 响应式布局，支持移动端

---

## 项目结构

```
student-grade-management-system/
├── src/                          # 后端代码
│   ├── api/                      # API 路由
│   │   └── routes/               # 路由定义
│   ├── core/                     # 核心配置
│   ├── models/                   # 数据模型
│   ├── schemas/                  # 数据验证
│   ├── repositories/             # 数据访问层
│   └── services/                 # 业务逻辑层
├── frontend/                     # 前端代码
│   ├── src/
│   │   ├── api/                  # API 封装
│   │   ├── assets/styles/        # 样式文件
│   │   ├── components/           # 组件
│   │   ├── stores/               # 状态管理
│   │   ├── views/                # 页面
│   │   └── router/               # 路由
│   └── package.json
├── docs/                         # 文档
├── tests/                        # 测试
├── .env.example                  # 环境变量模板
├── start.bat                     # 启动脚本
└── requirements.txt              # Python 依赖
```

---

## API 文档

启动后端服务后访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

### 主要端点

| 模块 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 认证 | POST | `/api/v1/auth/login` | 用户登录 |
| 学生 | GET | `/api/v1/students` | 学生列表 |
| 成绩 | GET | `/api/v1/grades/search` | 成绩查询 |
| 统计 | GET | `/api/v1/statistics/overview` | 统计概览 |
| 导入 | POST | `/api/v1/import/students` | 批量导入学生 |
| 导入 | POST | `/api/v1/import/grades` | 批量导入成绩 |

---

## 测试

```bash
# 后端测试
pytest tests/

# 前端测试
cd frontend
npm run test
```

**测试覆盖率**：>80%（核心功能）

---

## 部署

### Docker 部署

```bash
cd deployment
cp .env.example .env
make deploy
```

### 手动部署

参考 `docs/deployment.md` 获取详细部署指南。

---

## 更新日志

| 版本 | 日期 | 说明 |
|------|------|------|
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

- ✅ JWT 双令牌认证（Access + Refresh）
- ✅ RBAC 三级权限控制
- ✅ CORS 安全配置
- ✅ 安全响应头（X-Content-Type-Options, X-Frame-Options 等）
- ✅ 输入验证（Pydantic + 前端双重验证）
- ✅ SQL 注入防护（全 ORM 架构）
- ✅ 速率限制（登录接口 10次/分钟）
- ✅ 密码哈希（bcrypt）

---

## 许可证

[MIT License](LICENSE)

---

<div align="center">

**[⬆ 回到顶部](#学生成绩管理系统)**

</div>
