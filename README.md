# 学生成绩管理系统

> 基于 OpenCode 多 Agent 虚拟工程团队开发的全栈学生成绩管理系统

<div align="center">

![Vue 3](https://img.shields.io/badge/Vue-3-42b883?style=flat-square&logo=vue.js)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi)
![TypeScript](https://img.shields.io/badge/TypeScript-3178c6?style=flat-square&logo=typescript)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-d71f00?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**[用户手册](USER_GUIDE.md)** · **[更新日志](CHANGELOG/)** · **[API 文档](http://localhost:8000/docs)**

</div>

---

## 项目简介

全栈学生成绩管理系统，支持**管理员、教师、班主任、学科组长、学生**五级角色体系。

**核心功能：** 学生管理 · 成绩录入/导入 · ECharts 统计分析 · RBAC 权限控制 · Excel/CSV 批量导入导出 · 统一账号管理

---

## 快速开始

```bash
git clone https://github.com/Ibuprovan/student-grade-management-system.git
cd student-grade-management-system

# Windows 一键启动
start.bat
```

### 默认账户

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | `admin` | `admin123` |

> 班主任、学科组长、教师账号由管理员在后台手动添加，初始密码 `123456`（首次登录强制改密）。学生账号由系统根据学生信息自动生成。

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Element Plus + ECharts 5 |
| 状态管理 | Pinia |
| 后端 | FastAPI + SQLAlchemy 2.0 |
| 数据库 | SQLite |
| 认证 | JWT 双令牌 |

---

## 项目结构

```
src/              # 后端：routes / core / models / schemas / services / scripts
frontend/src/     # 前端：views / api / stores / router / types / components
CHANGELOG/        # 版本更新日志
USER_GUIDE.md     # 保姆级用户手册
```

---

## 相关链接

- **用户手册** → [`USER_GUIDE.md`](USER_GUIDE.md)（各角色操作详解）
- **更新日志** → [`CHANGELOG/`](CHANGELOG/)
- **API 文档** → `http://localhost:8000/docs`（Swagger UI）

---

## 开源协议

[MIT License](LICENSE)
