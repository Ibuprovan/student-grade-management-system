# TASK-018

## 基本信息

| 字段 | 值 |
|------|-----|
| ID | TASK-018 |
| 标题 | 修复学生账号权限显示和成绩查看问题 |
| 创建时间 | 2026-06-14 10:00 |
| 负责人 | backend-dev / frontend-dev |
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

### 问题背景

**问题1：学生账号侧边栏显示无权限菜单**
- 学生账号登录后，侧边栏显示了所有菜单（学生管理、成绩管理、统计分析等）
- 但学生角色只有部分权限（只能看统计概览、我的成绩）
- 点击无权限菜单后，侧边栏活跃状态会卡住

**问题2：学生账号无法查看自己的成绩**
- 学生账号登录后，进入"我的成绩"页面
- 由于认证问题，无法正确获取当前学生的学号
- 导致无法查询到该学生的成绩数据

### 根因分析

**问题1根因**：
- `AppSidebar.vue` 中的菜单项是硬编码的，没有根据用户角色进行过滤
- 虽然路由配置中有 `roles` 限制，但侧边栏菜单显示逻辑未与角色关联

**问题2根因**：
- `User` 模型与 `Student` 模型是分离的，没有直接关联字段
- `MyGrades.vue` 使用 `authStore.user?.username` 作为 `studentId`，但用户名 ≠ 学号
- 需要通过后端接口获取当前学生用户关联的学生信息

### 修复方案

**问题1修复**：
- 在 `AppSidebar.vue` 中根据用户角色过滤菜单项
- 学生角色只显示：仪表盘、统计分析（统计概览）、我的成绩
- 隐藏：学生管理、成绩管理、班级统计、科目统计

**问题2修复**：
- 后端：在 `auth.py` 添加 `/api/v1/auth/me/student-info` 接口
- 前端：在 `auth.ts` 添加对应的 API 调用
- 前端：修改 `MyGrades.vue` 使用正确的 `student_id`

## 修改文件清单

### 后端修改

1. **src/api/routes/auth.py**
   - 添加 `StudentRepository` 依赖导入
   - 添加 `get_student_repository` 依赖注入函数
   - 添加 `GET /api/v1/auth/me/student-info` 接口

### 前端修改

1. **frontend/src/components/layout/AppSidebar.vue**
   - 添加角色权限判断（`v-if="authStore.isAdmin || authStore.isTeacher"`）
   - 学生管理菜单：仅管理员和教师可见
   - 成绩管理菜单：仅管理员和教师可见
   - 统计分析子菜单：班级统计和科目统计仅管理员和教师可见
   - 统计概览：所有角色可见
   - 我的成绩：仅学生可见

2. **frontend/src/api/auth.ts**
   - 添加 `StudentInfo` 接口定义
   - 添加 `getCurrentStudentInfo()` API 函数

3. **frontend/src/views/student/MyGrades.vue**
   - 导入 `getCurrentStudentInfo` API
   - 添加 `studentInfoLoading` 状态
   - 添加 `fetchStudentInfo()` 函数获取学生信息
   - 修改 `fetchData()` 函数，先获取学生信息再查询成绩

## 验收标准

- [x] 学生账号登录后，侧边栏只显示有权限的菜单
- [x] 学生账号只能看到：仪表盘、统计概览、我的成绩
- [x] 学生账号点击"我的成绩"能正确显示成绩数据
- [x] 管理员和教师账号登录后，侧边栏显示所有菜单
- [x] 路由权限控制正常工作
- [x] 错误提示友好（如未找到学生信息）

## 关联文档

- PRD: `docs/prd.md`
- 架构: `docs/architecture.md`
- API: `docs/api-spec.md`
- 数据库: `docs/database.md`

## 变更记录

| 时间 | 操作人 | 状态变更 | 备注 |
|------|--------|----------|------|
| 2026-06-14 10:00 | PMO | TODO | 任务创建，问题分析 |
| 2026-06-14 10:05 | PMO | IN_PROGRESS | 开始并行修复 |
| 2026-06-14 10:10 | Frontend-dev | IN_PROGRESS | 修复侧边栏权限过滤 |
| 2026-06-14 10:15 | Backend-dev | IN_PROGRESS | 添加学生信息接口 |
| 2026-06-14 10:20 | Frontend-dev | IN_PROGRESS | 修改 MyGrades.vue 使用新接口 |
| 2026-06-14 10:25 | PMO | DONE | 修复完成 |
