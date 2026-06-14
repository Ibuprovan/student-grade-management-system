# 学生成绩管理系统

基于 OpenCode 多 Agent 虚拟工程团队开发的全栈学生成绩管理系统。

## 项目概述

本项目是由 12 个 AI Agent 协作开发的全栈 Web 应用，展示了多 Agent 协同工作流程。项目已完成**第二代升级**，实现了完整的用户认证系统、UI美化、性能优化和安全增强。

## 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: SQLite
- **ORM**: SQLAlchemy 2.0
- **数据验证**: Pydantic 2.0
- **认证**: JWT (PyJWT)
- **密码加密**: bcrypt
- **速率限制**: slowapi

### 前端
- **框架**: Vue 3 + TypeScript
- **UI 组件库**: Element Plus
- **图表库**: ECharts
- **状态管理**: Pinia
- **HTTP 客户端**: Axios
- **构建工具**: Vite
- **权限指令**: v-permission
- **设计风格**: Supabase 深色主题

### 部署
- **容器化**: Docker + Docker Compose
- **Web 服务器**: Nginx
- **反向代理**: Nginx API 代理

## 项目结构

```
student-grade-management-system/
├── src/                          # 后端代码
│   ├── core/                     # 核心配置
│   │   ├── config.py             # 配置管理
│   │   ├── database.py           # 数据库连接
│   │   ├── security.py           # JWT 认证
│   │   ├── limiter.py            # 速率限制
│   │   └── exceptions.py         # 异常处理
│   ├── models/                   # 数据模型
│   ├── schemas/                  # 数据验证
│   ├── repositories/             # 数据访问层
│   ├── services/                 # 业务逻辑层
│   │   ├── student_service.py    # 学生服务
│   │   ├── grade_service.py      # 成绩服务
│   │   ├── statistics_service.py # 统计服务
│   │   ├── dashboard_service.py  # 仪表盘服务
│   │   └── import_service.py     # 批量导入服务
│   ├── api/                      # API 路由
│   │   ├── routes/               # 路由定义
│   │   │   ├── auth.py           # 认证路由
│   │   │   ├── students.py       # 学生路由
│   │   │   ├── grades.py         # 成绩路由
│   │   │   ├── statistics.py     # 统计路由
│   │   │   ├── dashboard.py      # 仪表盘路由
│   │   │   └── imports.py        # 批量导入路由
│   │   └── dependencies.py       # 依赖注入
│   ├── schemas/                  # 数据验证
│   │   └── import_schema.py      # 导入数据模式
│   ├── cli/                      # CLI 命令
│   └── main.py                   # 应用入口
├── frontend/                     # 前端代码
│   ├── src/
│   │   ├── api/                  # API 封装
│   │   │   ├── auth.ts           # 认证 API
│   │   │   ├── dashboard.ts      # 仪表盘 API
│   │   │   ├── import.ts         # 批量导入 API
│   │   │   └── ...               # 其他 API
│   │   ├── components/           # 组件
│   │   ├── composables/          # 组合式函数
│   │   ├── directives/           # 自定义指令
│   │   │   └── permission.ts     # 权限指令
│   │   ├── router/               # 路由
│   │   ├── stores/               # 状态管理
│   │   │   ├── auth.ts           # 认证状态
│   │   │   ├── dashboard.ts      # 仪表盘状态
│   │   │   └── ...               # 其他状态
│   │   ├── types/                # 类型定义
│   │   │   └── auth.ts           # 认证类型
│   │   ├── utils/                # 工具函数
│   │   └── views/                # 页面
│   │       ├── login/            # 登录页面
│   │       ├── dashboard/        # 仪表盘
│   │       ├── student/          # 学生管理
│   │       │   ├── StudentList.vue    # 学生列表
│   │       │   └── StudentImport.vue  # 批量导入
│   │       ├── grade/            # 成绩管理
│   │       ├── statistics/       # 统计分析
│   │       └── error/            # 错误页面
│   └── package.json
├── deployment/                   # 部署配置
│   ├── Dockerfile                # 后端 Docker 配置
│   ├── docker-compose.yml        # Docker Compose 配置
│   └── frontend/                 # 前端 Docker 配置
├── docs/                         # 文档
│   ├── prd.md                    # PRD 文档
│   ├── architecture.md           # 架构文档
│   ├── api-spec.md               # API 规范
│   ├── security-report.md        # 安全报告
│   ├── comprehensive-check-report.md # 全面检查报告
│   ├── project-plan.md           # 项目计划
│   ├── review-report.md          # 代码审查报告
│   └── tasks/                    # 任务文件
│       ├── TASK-010.md           # 登录页面任务
│       ├── TASK-011.md           # 路由守卫任务
│       ├── TASK-012.md           # Dashboard任务
│       ├── TASK-013.md           # UI美化任务
│       ├── TASK-014.md           # 性能优化任务
│       ├── TASK-015.md           # 用户信息任务
│       └── TASK-016.md           # 安全增强任务
├── reports/                      # 报告
│   ├── experiment-report.md      # 实验报告
│   ├── vulnerability-assessment.md # 漏洞评估
│   └── project-completion-summary.md # 项目完成总结
├── CHANGELOG/                    # 更新日志
│   ├── README.md                 # 更新日志索引
│   ├── V2.0.0-second-generation-upgrade.md # V2.0.0 更新记录
│   └── V2.0.1-login-fix.md       # V2.0.1 更新记录
├── tests/                        # 测试代码
├── data/                         # 数据文件
├── project-memory.md             # 项目记忆
├── .env.example                  # 环境变量配置模板
├── start.bat                     # Windows 一键启动脚本
├── restart-backend.bat           # 后端重启脚本（清理缓存）
├── start.ps1                     # PowerShell 启动脚本
├── requirements.txt              # Python 依赖
├── USER_GUIDE.md                 # 用户手册指南
└── LICENSE                       # MIT 许可证
```

## 快速开始

### 环境配置（首次运行必读）

在启动项目前，需要创建 `.env` 配置文件：

```bash
# 复制配置模板
cp .env.example .env
```

**关键配置说明**：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DEBUG` | `True` | 调试模式，开发环境设为 `True`，生产环境设为 `False` |
| `DATABASE_URL` | `sqlite:///./data/grades.db` | 数据库连接字符串 |
| `JWT_SECRET_KEY` | 默认值（仅开发环境可用） | JWT 签名密钥，生产环境必须更换 |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | CORS 允许的源 |

> **安全提示**：当 `DEBUG=False` 时，系统会强制要求设置自定义 `JWT_SECRET_KEY`，否则无法启动。生成方式：
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

### 一键启动（推荐）

**Windows 用户**：有两种启动方式：

#### 方式一：使用批处理文件（简单）
双击运行 `start.bat` 文件，系统将自动：
1. 检查并安装依赖
2. 初始化数据库
3. 启动后端和前端服务
4. 自动打开浏览器访问系统

> **遇到问题时**：如果更新代码后出现异常，双击 `restart-backend.bat` 可清理缓存并重启后端服务。

#### 方式二：使用 PowerShell 脚本（推荐，支持中文）
右键点击 `start.ps1` 文件，选择"使用 PowerShell 运行"，或者：
1. 打开 PowerShell
2. 运行命令：`.\start.ps1`

**注意**：如果遇到编码问题，请优先使用 PowerShell 脚本。

**其他系统用户**：请参考下方手动启动步骤。

### 手动启动

#### 后端启动

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python -m src.scripts.init_users

# 启动服务
uvicorn src.main:app --reload
```

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### Docker 部署

```bash
cd deployment

# 配置环境变量
cp .env.example .env

# 一键部署
make deploy
```

## 默认账户

| 角色 | 用户名 | 密码 | 权限说明 |
|------|--------|------|----------|
| 管理员 | admin | admin123 | 拥有所有功能权限 |
| 教师 | teacher | teacher123 | 可以管理学生和成绩 |
| 学生 | student | student123 | 只能查看自己的成绩 |

**访问地址**：http://localhost:5173

## API 文档

启动后端后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

### 主要 API 端点

| 模块 | 端点 | 说明 |
|------|------|------|
| 认证 | `POST /api/v1/auth/login` | 用户登录 |
| 学生 | `GET /api/v1/students` | 获取学生列表 |
| 学生 | `GET /api/v1/students/classes` | 获取班级列表 |
| 成绩 | `GET /api/v1/grades` | 获取成绩列表 |
| 统计 | `GET /api/v1/statistics/overview` | 统计概览 |
| 仪表盘 | `GET /api/v1/dashboard/stats` | 仪表盘数据 |

## 开发团队

本项目由 12 个 AI Agent 协作开发，第二代升级由以下团队完成：

| Agent | 职责 | 第二代贡献 |
|-------|------|-----------|
| pmo | 项目管理办公室 | 全面检查、任务创建、进度跟踪 |
| pm | 产品经理 | 需求分析、PRD 更新 |
| architect | 系统架构师 | 架构设计、技术方案 |
| frontend-dev | 前端工程师 | 登录页面、路由守卫、UI 美化、Dashboard |
| backend-dev | 后端工程师 | 性能优化、安全增强、Dashboard API |
| reviewer | 代码审查员 | 代码审查、质量检查 |
| qa-engineer | 测试工程师 | 单元测试、集成测试 |
| devops | 交付工程师 | 部署配置 |
| security | 合规安全官 | 安全审查 |
| memory | 记忆中台 | 项目记忆维护 |
| report | 报告生成器 | 实验报告、项目总结 |
| cyber | 网安特化智能体 | 漏洞评估 |
| research | 前沿调研员 | 技术调研 |

## 安全特性

- **JWT 认证机制**：Access Token + Refresh Token 双令牌
- **RBAC 权限控制**：admin/teacher/student 三级角色
- **CORS 安全配置**：限制来源和方法
- **安全响应头**：X-Content-Type-Options、X-Frame-Options、X-XSS-Protection 等
- **输入验证**：Pydantic + 前端双重验证
- **SQL 注入防护**：全 ORM 架构，无原生 SQL
- **XSS 防护**：Vue 3 默认转义，无 v-html 使用
- **速率限制**：登录接口 10次/分钟，防止暴力攻击
- **批量限制**：成绩批量创建最多 500 条，防止资源耗尽
- **密码哈希**：bcrypt 哈希存储，符合 OWASP 标准
- **权限指令**：v-permission 指令控制前端元素显示

## 测试

### 后端测试
```bash
# 运行所有测试
pytest tests/

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 查看测试覆盖率
pytest --cov=src tests/
```

### 前端测试
```bash
cd frontend

# 运行测试
npm run test

# 运行测试并查看覆盖率
npm run test:coverage
```

### 测试统计
- **后端单元测试**：119 项全部通过
- **前端构建**：成功，无 TypeScript 错误
- **测试覆盖率**：>80%（核心功能）

## 第二代升级特性

### 🎯 用户认证系统
- 完整的登录页面和认证流程
- JWT 双令牌机制（Access Token + Refresh Token）
- 路由守卫和权限控制
- Token 自动刷新机制

### 🎨 UI 美化 - 温馨友好风格
- 暖色调配色方案（青绿主色 #2A9D8F）
- 圆角设计（10-14px）和柔和阴影
- 教育系统风格，专业但不死板
- 响应式设计，支持移动端

### ⚡ 性能优化
- 搜索学生：数据库层面分页，性能提升
- 班级列表：独立接口，DISTINCT 查询
- Dashboard：真实 API 数据，非硬编码

### 🔒 安全增强
- 速率限制：登录接口 10次/分钟
- 批量限制：成绩批量创建最多 500 条
- 权限指令：v-permission 控制前端元素显示
- 安全响应头：完整的安全配置

### 📥 批量导入
- 支持 Excel/CSV 文件一键导入学生和成绩
- 数据预览与校验，显示有效/无效统计
- 导入模板下载，包含字段说明和示例
- 导入结果反馈：成功数、失败数、错误详情
- 事务处理，保证数据一致性
- CSV 文件自动处理 BOM 编码

### 📊 真实数据展示
- Dashboard 显示真实统计数据
- 用户信息显示真实用户名和角色
- 退出登录功能完整实现

## 项目统计

| 指标 | 数量 |
|------|------|
| 后端代码文件 | 65+ |
| 前端代码文件 | 95+ |
| 单元测试 | 133 项 |
| API 接口 | 22 个 |
| 文档文件 | 35+ |
| 总代码行数 | 18,500+ |

## 更新日志

| 版本 | 日期 | 类型 | 说明 |
|------|------|------|------|
| V3.0.0 | 2026-06-15 | 重大更新 | 前端UI全面重构为Supabase深色主题风格 |
| V2.4.0 | 2026-06-15 | 安全+架构优化 | 全面审查修复：安全漏洞、数据库索引、代码质量 |
| V2.3.3 | 2026-06-14 | Bug 修复 | 成绩列表全面修复：数据显示、导出功能、侧边栏状态 |
| V2.3.2 | 2026-06-14 | Bug 修复 | 修复学生账号侧边栏权限显示和成绩查看问题 |
| V2.3.1 | 2026-06-14 | Bug 修复 | 批量导入功能全面修复：成绩导入、FormData解析、结果显示 |
| V2.3.0 | 2026-06-12 | 功能更新 | 新增批量导入学生功能：Excel/CSV上传、数据校验、结果反馈 |
| V2.2.2 | 2026-06-12 | Bug 修复 + 配置优化 | 修复 JWT 密钥检查、新增环境配置模板、完善文档 |
| V2.2.1 | 2026-06-11 | Bug 修复 + 性能优化 | 审查修复、ECharts 按需引入、导入进度条、导出 API |
| V2.2.0 | 2026-06-11 | 功能更新 + 安全增强 | P0+P1 全面改进：安全、UX、新功能 |
| V2.1.4 | 2026-06-09 | UI/UX 优化 | 全面改进：空状态差异化、导航状态、按钮一致性、加载状态 |
| V2.1.3 | 2026-06-09 | UI 优化 | 精调图表布局、统一板块标题样式 |
| V2.1.2 | 2026-06-09 | Bug 修复 | 登录功能与统计页面修复：formRef、图标、API路由、空数据保护 |
| V2.1.1 | 2026-06-08 | 安全更新 | 升级前端依赖修复 npm 漏洞 |
| V2.1.0 | 2026-06-08 | 架构优化 | 消除代码重复、统一依赖管理、提升可维护性 |
| V2.0.2 | 2026-06-08 | Bug 修复 | 全面 Bug 修复：13 个问题 + 98 个集成测试修复 |
| V2.0.1 | 2026-06-08 | Bug 修复 | 修复登录按钮点击无响应问题 |
| V2.0.0 | 2026-06-07 | 重大更新 | 第二代全面升级：认证系统、UI美化、性能优化、安全增强 |

详细更新记录请查看 [CHANGELOG/](CHANGELOG/) 文件夹。

## License

MIT
