# AGENTS.md

## 项目概览

全栈学生成绩管理系统，FastAPI + Vue 3 + SQLite。五级角色：admin / teacher / class_teacher / subject_leader / student。

## 快速命令

```bash
# 一键启动（Windows）
start.bat

# 后端手动启动
pip install -r requirements.txt
python -m src.scripts.init_users
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 前端手动启动
cd frontend
npm install
npm run dev          # http://localhost:3000

# 测试
pytest tests/        # 后端测试

# 前端检查
npm run type-check   # TypeScript 类型检查
npm run lint         # ESLint
npm run build        # 构建
```

> `npm run dev` 默认端口 3000（非 5173）。`start.bat` 用 5173。

## 架构要点

- **后端正向依赖链**: routes → services → repositories → models (SQLAlchemy ORM)
- **API 基础路径**: `/api/v1`（硬编码在各 router 的 `prefix` 参数中）
- **前端代理**: Vite 将 `/api` 代理到 `http://localhost:8000`
- **数据库**: SQLite `data/grades.db`，引擎配置在 `src/core/database.py`，启用外键约束
- **认证**: JWT 双令牌（access 30min + refresh 7天），拦截器自动刷新
- **Token 存储**: 前端 localStorage，后端 `HTTPBearer`

## 角色与权限

| 角色 | 后端守卫 | 侧边栏 |
|------|----------|--------|
| admin | `require_admin` | 完整管理菜单 |
| teacher | `require_teacher_or_admin` | 同 admin 但无管理项 |
| class_teacher | `require_class_teacher_or_admin` | 专属只读页面 |
| subject_leader | `require_subject_leader_or_admin` | 专属只读页面 |
| student | — | 仅「我的成绩」 |

守卫定义在 `src/api/auth.py`。路由守卫在 `frontend/src/router/index.ts`。

## 后端路由文件

所有路由注册在 `src/main.py:app.include_router(...)`。每个文件对应一个 `prefix`：

| 文件 | prefix | 权限 |
|------|--------|------|
| `routes/students.py` | `/students` | teacher/admin |
| `routes/grades.py` | `/grades` | teacher/admin |
| `routes/statistics.py` | `/statistics` | 已登录 |
| `routes/class_teacher_scoped.py` | `/class-teacher` | class_teacher/admin |
| `routes/subject_leader_scoped.py` | `/subject-leader` | subject_leader/admin |
| `routes/teacher_scoped.py` | `/teacher` | teacher/admin |
| `routes/class_teachers.py` | `/class-teachers` | admin |
| `routes/subject_leaders.py` | `/subject-leaders` | admin |
| `routes/teacher_assignments.py` | `/teacher-assignments` | admin |
| `routes/accounts.py` | `/accounts` | admin |
| `routes/auth.py` | `/auth` | 公开 |
| `routes/dashboard.py` | `/dashboard` | admin |
| `routes/users.py` | `/users` | admin |
| `routes/imports.py` | `/import` | teacher/admin |

## 常量

定义在 `src/core/constants.py`：
- `SUBJECTS`: 9 科，顺序固定（语数英物化生政史地）
- `EXAM_TYPES`: 期中/期末/月考/单元测试
- `MAIN_SUBJECTS`: 语文/数学/英语（满分 150）
- 其他科目满分 100
- `SUBJECT_EN_MAP`: 科目 → 英文名映射

## 账号规则

- 管理员: `admin` / `admin123`
- 班主任: `{入学年份}{班级编号}`（如 `2026001`）
- 学科组长: 学科英文名小写（如 `chinese`）
- 教师: `{SubjectEn}{入学年份}{班级编号}`（如 `Chinese2026001`）
- 学生: 学号（8位数字）
- 初始密码: 一律 `123456`，班主任/学科组长/教师首次登录强制改密

## 统计注意事项

- 所有统计接口在 `exam_type` 未指定时自动取最新考试类型（`_get_latest_exam_type()`）
- 科目排序始终按 `SUBJECTS` 常量顺序

## 关键陷阱

1. 前端 `unplugin-auto-import` 自动导入 Vue API（ref/computed 等无需 import），但 TypeScript 可能报 `TS2305`，运行时会正常工作。
2. 后端 `MAX_PAGE_SIZE` 默认 100（`src/core/config.py`），前端传太大返回 422。
3. `StudentDetail.vue` 成绩汇总用 `/statistics/student/{id}`，成绩列表用 `/grades/search?student_id=...`。
4. Element Plus 弹窗(dialog) 有时需 `append-to-body` + `:teleported="false"` + `destroy-on-close` 避免渲染问题。
5. `require_*` 守卫不能用于 `get_current_user` 替代 — 前者不含用户注入，后者不做角色检查。
