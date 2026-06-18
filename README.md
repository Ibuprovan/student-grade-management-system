# 学生成绩管理系统

> 基于 OpenCode 多 Agent 虚拟工程团队开发的全栈学生成绩管理系统

<div align="center">

![Vue 3](https://img.shields.io/badge/Vue-3-42b883?style=flat-square&logo=vue.js)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi)
![TypeScript](https://img.shields.io/badge/TypeScript-3178c6?style=flat-square&logo=typescript)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-d71f00?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**[在线演示](http://localhost:5173)** · **[用户手册](USER_GUIDE.md)** · **[更新日志](CHANGELOG/)** · **[API 文档](http://localhost:8000/docs)**

</div>

---

## 项目简介

学生成绩管理系统是一个现代化的全栈 Web 应用，支持**管理员**、**班主任**、**学科组长**、**教师**、**学生**五级角色体系，提供学生管理、成绩管理、统计分析、权限控制等功能。

**核心特性**：RBAC 五级角色 · 班主任/学科组长专属空间 · ECharts 数据可视化 · JWT 双令牌认证 · Excel/CSV 批量导入 · 统一账号管理

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 + TypeScript | Composition API |
| UI 组件 | Element Plus | 企业级组件库 |
| 图表 | ECharts 5 | 数据可视化 |
| 状态管理 | Pinia | Vue 3 官方状态管理 |
| 后端 | FastAPI | 高性能 Python 框架 |
| 数据库 | SQLite + SQLAlchemy 2.0 | 轻量级 ORM |
| 认证 | JWT (PyJWT) | 无状态认证 |

---

## 快速开始

```bash
# 克隆、安装、启动
git clone https://github.com/Ibuprovan/student-grade-management-system.git
cd student-grade-management-system
cp .env.example .env

# 一键启动（Windows）
start.bat

# 或手动启动：
pip install -r requirements.txt
python -m src.scripts.init_users
uvicorn src.main:app --reload

cd frontend
npm install
npm run dev
```

### 默认账户

- 管理员：`admin` / `admin123`

> 班主任、学科组长账号由管理员在管理端手动添加，初始密码 `123456`（首次登录强制改密）。学生账号由系统根据学生信息自动生成。

---

## 项目结构

```
src/              # 后端：routes / core / models / schemas / services / scripts
frontend/src/     # 前端：views / api / stores / router / types / components
CHANGELOG/        # 版本更新日志
docs/             # 开发文档
USER_GUIDE.md     # 保姆级用户手册 ← 详细操作说明请阅读此文件
```

---

## 相关链接

- **用户手册** → [`USER_GUIDE.md`](USER_GUIDE.md)（各角色操作详解）
- **更新日志** → [`CHANGELOG/`](CHANGELOG/)
- **API 文档** → 启动后端后访问 `http://localhost:8000/docs`（Swagger UI）或 `http://localhost:8000/redoc`（ReDoc）

---

## 开源协议

[MIT License](LICENSE)

<div align="center">

**[回到顶部](#学生成绩管理系统)**

</div>
