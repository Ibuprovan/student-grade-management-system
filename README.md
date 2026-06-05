# 学生成绩管理系统

基于 OpenCode 多 Agent 虚拟工程团队开发的全栈学生成绩管理系统。

## 项目概述

本项目是由 12 个 AI Agent 协作开发的全栈 Web 应用，展示了多 Agent 协同工作流程。

## 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: SQLite
- **ORM**: SQLAlchemy 2.0
- **数据验证**: Pydantic 2.0
- **认证**: JWT (python-jose)
- **密码加密**: bcrypt

### 前端
- **框架**: Vue 3 + TypeScript
- **UI 组件库**: Element Plus
- **图表库**: ECharts
- **状态管理**: Pinia
- **HTTP 客户端**: Axios
- **构建工具**: Vite

### 部署
- **容器化**: Docker + Docker Compose
- **Web 服务器**: Nginx
- **反向代理**: Nginx API 代理

## 项目结构

```
student-grade-management-system/
├── src/                          # 后端代码
│   ├── core/                     # 核心配置
│   ├── models/                   # 数据模型
│   ├── schemas/                  # 数据验证
│   ├── repositories/             # 数据访问层
│   ├── services/                 # 业务逻辑层
│   ├── api/                      # API 路由
│   ├── cli/                      # CLI 命令
│   └── main.py                   # 应用入口
├── frontend/                     # 前端代码
│   ├── src/
│   │   ├── api/                  # API 封装
│   │   ├── components/           # 组件
│   │   ├── composables/          # 组合式函数
│   │   ├── router/               # 路由
│   │   ├── stores/               # 状态管理
│   │   ├── types/                # 类型定义
│   │   ├── utils/                # 工具函数
│   │   └── views/                # 页面
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
│   ├── research.md               # CVE 调研报告
│   └── tasks/                    # 任务文件
├── reports/                      # 报告
│   ├── experiment-report.md      # 实验报告
│   └── vulnerability-assessment.md # 漏洞评估
├── tests/                        # 测试代码
├── data/                         # 数据文件
├── project-memory.md             # 项目记忆
├── agents.md                     # 多 Agent 建设方案
└── opencode.json                 # OpenCode 配置
```

## 快速开始

### 后端启动

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

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 教师 | teacher | teacher123 |
| 学生 | student | student123 |

## API 文档

启动后端后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发团队

本项目由 12 个 AI Agent 协作开发：

| Agent | 职责 |
|-------|------|
| pm | 产品经理 |
| backend-dev | 后端工程师 |
| report | 报告生成器 |
| pmo | 项目管理办公室 |
| architect | 系统架构师 |
| reviewer | 代码审查员 |
| memory | 记忆中台 |
| frontend-dev | 前端工程师 |
| devops | 交付工程师 |
| security | 合规安全官 |
| cyber | 网安特化智能体 |
| research | 前沿调研员 |

## 安全特性

- JWT 认证机制
- RBAC 权限控制
- CORS 安全配置
- 安全响应头
- 输入验证（Pydantic + 前端）
- SQL 注入防护（ORM）
- XSS 防护（Vue 3 默认转义）

## 测试

```bash
# 运行后端测试
pytest tests/

# 运行前端测试
cd frontend
npm run test
```

## License

MIT
