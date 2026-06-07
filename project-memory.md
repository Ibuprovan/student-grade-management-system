# Project Memory

## 系统拓扑

### 技术栈
- **后端框架**: FastAPI 0.100+
- **数据库**: SQLite 3.35+
- **ORM**: SQLAlchemy 2.0+
- **数据验证**: Pydantic 2.0+
- **CLI**: Typer 0.9+
- **测试框架**: pytest 7.0+
- **前端框架**: Vue 3.3+ / React 18.2+（二选一）
- **UI组件库**: Element Plus 2.4+ / Ant Design 5.x
- **图表库**: ECharts 5.4+ / Chart.js 4.x
- **状态管理**: Pinia 2.1+ / Redux Toolkit 1.9+
- **构建工具**: Vite 4.4+
- **前端测试**: Vitest 0.34+ / Jest 29.x

### 模块结构
```
src/
├── core/           # 核心配置（config, database, exceptions）
├── models/         # 数据模型（Student, Grade）
├── schemas/        # 数据验证（Pydantic模式）
├── repositories/   # 数据访问层（BaseRepository, StudentRepo, GradeRepo）
├── services/       # 业务逻辑层（StudentService, GradeService, StatisticsService）
├── api/            # API 路由（students, grades, statistics）
├── cli/            # CLI 命令（student_cmd, grade_cmd, statistics_cmd）
└── main.py         # 应用入口

frontend/
├── src/
│   ├── api/             # API接口封装
│   ├── components/      # 公共组件
│   ├── views/           # 页面组件
│   │   ├── student/     # 学生管理页面
│   │   ├── grade/       # 成绩管理页面
│   │   ├── statistics/  # 统计分析页面
│   │   └── dashboard/   # 仪表盘
│   ├── stores/          # 状态管理
│   └── router/          # 路由配置
├── package.json
└── vite.config.js
```

## 数据模型

### students 表
| 字段 | 类型 | 说明 |
|------|------|------|
| student_id | VARCHAR(8) | 学号（主键，格式：YYYY+4位序号） |
| name | VARCHAR(20) | 姓名 |
| gender | VARCHAR(2) | 性别（男/女） |
| class_name | VARCHAR(20) | 班级 |
| enrollment_year | INTEGER | 入学年份 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### grades 表
| 字段 | 类型 | 说明 |
|------|------|------|
| grade_id | INTEGER | 成绩ID（主键，自增） |
| student_id | VARCHAR(8) | 学号（外键） |
| subject | VARCHAR(10) | 科目 |
| score | FLOAT | 分数（0-100，支持1位小数） |
| exam_type | VARCHAR(10) | 考试类型 |
| exam_date | DATE | 考试日期 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

**约束设计：**
- students表：student_id（主键）、class_name（普通索引）
- grades表：grade_id（主键）、student_id（普通索引）、(student_id, subject, exam_type)（唯一复合索引）

## 决策索引

| TASK | 决策 | 原因 |
|------|------|------|
| TASK-001 | 使用 SQLAlchemy 2.0 新语法 | 类型安全性更好，支持 Mapped 类型注解 |
| TASK-001 | 使用 SQLite | 轻量级、零配置、满足 10,000 学生需求 |
| TASK-001 | 实现 Repository 模式 | 数据访问抽象，便于未来切换数据库 |
| TASK-002 | 使用 FastAPI | 高性能、自动文档、类型安全 |
| TASK-002 | 实现分层架构 | Service → Repository → DB，职责清晰 |
| TASK-002 | 学号格式验证 | 8位数字（YYYY+4位序号），确保唯一性 |
| TASK-003 | 支持批量录入 | 提高成绩录入效率，使用事务保证数据一致性 |
| TASK-003 | 唯一约束设计 | (student_id, subject, exam_type) 防止重复录入 |
| TASK-003 | 实现多维度查询 | 支持按学生、班级、科目、组合条件查询 |
| TASK-004 | 实现排名功能 | 满足教学评估需求，支持单科和总分排名 |
| TASK-004 | 统计指标设计 | 平均分、最高分、最低分、及格率、优秀率、中位数、标准差 |
| TASK-004 | 分数分布统计 | 5个分数段（0-59, 60-69, 70-79, 80-89, 90-100） |
| PRD-UPDATE | 添加前端页面需求 | 满足用户Web端访问需求，提升用户体验 |
| PRD-UPDATE | 响应式设计要求 | 支持移动端访问，扩大用户覆盖范围 |
| PRD-UPDATE | 前端技术栈选型 | Vue 3/React 18 + ECharts，成熟稳定生态 |

## API 接口统计

| 模块 | 接口数 | 说明 |
|------|--------|------|
| 学生管理 | 5 | CRUD + 搜索（POST/GET/PUT/DELETE） |
| 成绩管理 | 5 | CRUD + 批量录入（POST/GET/PUT/DELETE） |
| 统计分析 | 3 | 统计 + 排名 + 学生综合统计 |
| 数据导入导出 | 2 | CSV导入 + 导出 |
| 健康检查 | 1 | 服务状态 |
| **总计** | **16** | - |

**API基础路径：** `/api/v1`
**文档地址：** `/docs` (Swagger UI)、`/redoc` (ReDoc)

## 测试统计

| 类型 | 数量 | 状态 |
|------|------|------|
| 单元测试 | 95 | ✅ 全部通过 |
| 集成测试 | 91 | ✅ 全部通过 |
| **总计** | **186** | ✅ |

**测试覆盖率：** >80%（核心功能）
**测试框架：** pytest 7.0+
**测试命令：** `pytest tests/`

## 前端认证系统

### 认证架构
- **认证方式：** JWT (Access Token + Refresh Token)
- **Token 存储：** localStorage
- **Token 刷新：** 自动刷新队列机制

### 认证相关文件
| 文件 | 说明 |
|------|------|
| `frontend/src/types/auth.ts` | 认证类型定义 |
| `frontend/src/api/auth.ts` | 认证 API 封装 |
| `frontend/src/stores/auth.ts` | 认证状态管理 (Pinia) |
| `frontend/src/views/login/Login.vue` | 登录页面 |
| `frontend/src/router/index.ts` | 路由配置（含认证守卫） |
| `frontend/src/utils/request.ts` | Axios 拦截器（含 Token 刷新） |

### 认证流程
1. 用户访问受保护路由
2. 路由守卫检查认证状态
3. 未认证跳转登录页
4. 用户输入凭据登录
5. 登录成功存储 Token
6. 请求拦截器自动附加 Token
7. 401 响应自动刷新 Token
8. 刷新失败清除状态跳转登录页

### API 接口
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/auth/login` | POST | 用户登录 |
| `/api/v1/auth/refresh` | POST | 刷新 Token |
| `/api/v1/auth/logout` | POST | 用户登出 |
| `/api/v1/auth/me` | GET | 获取当前用户 |

## 决策索引（续）

| TASK | 决策 | 原因 |
|------|------|------|
| TASK-010 | 使用 JWT 认证 | 无状态、可扩展、前后端分离友好 |
| TASK-010 | Access + Refresh Token | 提升安全性，减少频繁登录 |
| TASK-010 | Token 刷新队列机制 | 避免并发请求重复刷新 |
| TASK-010 | localStorage 存储 | MVP 阶段简单实现，未来可升级 httpOnly Cookie |
| TASK-010 | 路由守卫 + Axios 拦截器 | 双重保障认证流程 |
