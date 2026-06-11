# 代码审查报告：P0 + P1 改进

> **审查日期：** 2026-06-11  
> **审查人：** Code Reviewer Agent  
> **审查范围：** 前端改进 7 项 + 后端改进 5 项  
> **审查结论：** ❌ **不通过（REJECTED）**

---

## 一、审查结论

| 项目 | 结果 |
|------|------|
| **总体判定** | ❌ 不通过 |
| **阻塞问题** | 1 个（BLOCKER） |
| **高优先级问题** | 4 个 |
| **中优先级问题** | 3 个 |
| **低优先级问题** | 2 个 |
| **通过项** | 8 项 |

---

## 二、逐项审查结果

### 2.1 前端改进

#### ✅ FE-1: 移除调试日志（Login.vue、auth.ts、request.ts）

**结论：通过**

- `Login.vue`：无 `console.log` 调试语句
- `api/auth.ts`：无调试日志
- `utils/request.ts`：无调试日志
- `stores/auth.ts`：仅保留 `console.error` 用于错误处理（可接受）

#### ✅ FE-2: 密码修改功能（前端部分）

**结论：前端部分通过，但后端缺失导致整体失败**

前端实现完整：
- `api/auth.ts`：定义了 `changePassword()` 函数，调用 `POST /auth/change-password`
- `stores/auth.ts`：`changePassword()` 方法正确处理成功/失败
- `AppHeader.vue`：密码修改对话框完整，含密码强度指示器

⚠️ **但后端缺少对应接口**（详见 BE-5）

#### ✅ FE-3: 学生查看成绩页面（MyGrades.vue）

**结论：通过（有 1 个中等问题）**

- 路由 `/my-grades` 已注册，角色限制为 `['student']` ✓
- 侧边栏 `AppSidebar.vue` 正确使用 `v-if="authStore.isStudent"` 控制可见性 ✓
- 页面包含概览卡片、趋势图、成绩明细表格 ✓
- 支持按考试类型筛选 ✓

⚠️ **中等问题**：`MyGrades.vue` 第 148 行假设 `username === student_id`：
```typescript
const studentId = computed(() => authStore.user?.username || '')
```
如果管理员创建的用户名不是学号（如 `teacher01`），此逻辑将失败。

#### ✅ FE-4: 搜索防抖自动搜索（StudentList.vue、GradeList.vue）

**结论：通过**

- `useCommon.ts` 提供了 `useDebounce` 组合式函数
- `StudentList.vue`：学号/姓名输入框使用 `watch` + `debouncedSearch`（300ms）✓
- `GradeList.vue`：关键字输入框使用 `watch` + `debouncedSearch`（300ms）✓
- 班级等下拉框变化时立即搜索 ✓

#### ✅ FE-5: 导出全部筛选结果（StudentList.vue）

**结论：通过（有 1 个低等问题）**

- `handleExport()` 函数正确获取筛选条件下的所有数据
- CSV 格式正确，含 BOM 头（支持中文 Excel 打开）
- `escapeCSVField()` 处理了逗号、双引号、换行符等特殊字符
- 文件名含日期戳

⚠️ **低等问题**：使用 `page_size: '10000'` 硬编码获取全部数据，建议使用专用导出 API。

#### ✅ FE-6: 登录页隐藏默认密码（Login.vue）

**结论：通过**

- 默认账号提示默认隐藏（`showDefaultAccount = ref(false)`）
- 用户需主动点击"查看默认账号"按钮才会显示
- 使用 `v-if/v-else` 切换显示状态

#### ✅ FE-7: 密码强度校验（validation.ts、AppHeader.vue）

**结论：通过**

- `validation.ts`：`validatePasswordStrength` 要求 8+ 位、大写、小写、数字
- `AppHeader.vue`：密码修改对话框使用相同的强度校验规则
- 密码强度指示器（弱/中/强）视觉反馈完整
- 确认密码一致性校验正确

---

### 2.2 后端改进

#### ✅ BE-1: JWT 密钥检查（config.py、main.py）

**结论：通过**

- `config.py`：`JWT_SECRET_KEY` 配置项有默认值和文档说明
- `main.py`：`lifespan` 函数中检测生产环境是否使用默认密钥
- 检测到默认密钥时抛出 `RuntimeError`，阻止应用启动 ✓
- 日志消息清晰，包含密钥生成命令 ✓

#### ✅ BE-2: 用户管理 API（users.py、user_service.py、user schemas）

**结论：通过**

- CRUD 接口完整：列表、创建、查询、更新、删除、重置密码
- 权限控制：所有接口使用 `require_admin` 依赖 ✓
- 业务逻辑：
  - 用户名唯一性校验 ✓
  - 防止管理员删除自己 ✓
  - 密码 bcrypt 哈希 ✓
- Schema 验证：
  - 用户名 3-50 字符 ✓
  - 角色枚举校验（admin/teacher/student）✓
  - 响应模型不包含密码字段 ✓

#### ✅ BE-3: 操作审计日志（audit_log model、audit_service.py、audit_logs.py）

**结论：通过（有 1 个高等问题）**

- `AuditLog` 模型字段完整：user_id、username、action、resource_type、resource_id、details、ip_address
- 索引设计合理：user_id、action、resource_type、created_at ✓
- `AuditService.log()` 记录失败不影响业务流程 ✓
- 查询接口支持分页和多维度筛选 ✓
- 权限控制：`require_admin` ✓

⚠️ **高等问题**：`AuditLogRepository` 定义在 `audit_service.py` 中而非 `repositories/` 目录，违反分层架构。

#### ⚠️ BE-4: 批量删除接口（students.py、student_service.py）

**结论：通过（有 1 个高等问题）**

- API 路由 `POST /api/v1/students/batch-delete` ✓
- 权限控制：`require_admin` ✓
- Schema 验证：`BatchDeleteRequest` 要求 `student_ids` 非空 ✓
- 响应格式：返回每条记录的删除结果 ✓

⚠️ **高等问题**：`batch_delete_students` 方法的文档声称"使用事务确保数据一致性：要么全部删除成功，要么全部回滚"，但实际实现是逐条删除，未使用显式事务。如果中途失败，部分学生已被删除。

#### ❌ BE-5: Token 过期检查（auth.py）

**结论：通过**

- `POST /api/v1/auth/check-token` 端点已实现 ✓
- 计算剩余时间，返回 `expiring_soon` 标志（30 分钟阈值）✓
- 返回 `expires_at` 和 `remaining_minutes` ✓

---

## 三、阻塞问题（BLOCKER）

### ❌ BUG-001: 后端缺少 `POST /api/v1/auth/change-password` 接口

**严重程度：** 🔴 BLOCKER  
**影响范围：** 密码修改功能完全不可用  
**涉及文件：**
- 前端：`frontend/src/api/auth.ts` 第 59-63 行
- 前端：`frontend/src/stores/auth.ts` 第 285-299 行
- 前端：`frontend/src/components/layout/AppHeader.vue` 第 337-358 行
- 后端：`src/api/routes/auth.py`（**缺失**）

**问题描述：**

前端 `auth.ts` 定义了密码修改 API：
```typescript
export function changePassword(oldPassword: string, newPassword: string): Promise<AuthApiResponse<void>> {
  return post<AuthApiResponse<void>>(`${BASE_URL}/change-password`, {
    old_password: oldPassword,
    new_password: newPassword,
  })
}
```

但后端 `src/api/routes/auth.py` 中**没有** `/change-password` 端点。用户点击"修改密码"后将收到 404 错误。

**修复方案：**

在 `src/api/routes/auth.py` 中添加：

```python
@router.post(
    "/change-password",
    response_model=SuccessResponse,
    summary="修改密码",
    description="当前用户修改自己的密码",
)
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository),
) -> SuccessResponse:
    # 验证旧密码
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误",
        )
    # 更新密码
    user_repo.update(current_user.id, {
        "hashed_password": hash_password(data.new_password)
    })
    return SuccessResponse(message="密码修改成功")
```

同时在 `src/schemas/auth.py` 中添加 `ChangePasswordRequest` Schema。

---

## 四、高优先级问题

### ⚠️ HI-001: 前后端密码强度校验不一致

**严重程度：** 🟠 高  
**涉及文件：**
- 前端：`frontend/src/utils/validation.ts` 第 185-211 行
- 后端：`src/schemas/user.py` 第 27-33 行

**问题描述：**

| 校验项 | 前端 | 后端 |
|--------|------|------|
| 最小长度 | 8 位 | 6 位 |
| 大写字母 | ✅ 必须 | ❌ 不检查 |
| 小写字母 | ✅ 必须 | ❌ 不检查 |
| 数字 | ✅ 必须 | ❌ 不检查 |

攻击者可绕过前端，直接调用 API 创建弱密码用户。

**修复方案：**

在后端 Schema 中添加密码强度验证器，与前端保持一致。

### ⚠️ HI-002: 批量删除未使用显式事务

**严重程度：** 🟠 高  
**涉及文件：** `src/services/student_service.py` 第 234-284 行

**问题描述：**

`batch_delete_students` 方法逐条删除学生，如果中途异常，部分学生已被删除但返回失败。

**修复方案：**

使用 SQLAlchemy 的 `begin_nested()` 或在 Repository 层统一管理事务。

### ⚠️ HI-003: AuditLogRepository 架构违规

**严重程度：** 🟠 高  
**涉及文件：** `src/services/audit_service.py` 第 19-33 行

**问题描述：**

`AuditLogRepository` 定义在 Service 文件中，违反了 `docs/architecture.md` 规定的分层架构（Repository 层应在 `repositories/` 目录）。

**修复方案：**

将 `AuditLogRepository` 移至 `src/repositories/audit_log_repo.py`。

### ⚠️ HI-004: 缺少 `docs/database.md` 文档

**严重程度：** 🟠 高  

**问题描述：**

新增了 `users` 和 `audit_logs` 两张表，但项目中没有 `docs/database.md` 文件记录数据库表结构变更。根据 DBA 优先权审查规则，新增表结构应在文档中备案。

---

## 五、中优先级问题

### ⚠️ MED-001: MyGrades 假设 username === student_id

**严重程度：** 🟡 中  
**涉及文件：** `frontend/src/views/student/MyGrades.vue` 第 148 行

**问题描述：**
```typescript
const studentId = computed(() => authStore.user?.username || '')
```
假设用户名就是学号，但管理员可能创建非学号用户名。

**修复方案：**

后端 `/auth/me` 接口应返回关联的 `student_id`，或在 User 模型中添加 `student_id` 字段。

### ⚠️ MED-002: 前端类型安全问题

**严重程度：** 🟡 中  
**涉及文件：**
- `frontend/src/views/student/MyGrades.vue` 第 205、210 行
- `frontend/src/views/student/StudentList.vue` 第 445-446 行

**问题描述：**

多处使用 `(xxx as any)` 类型断言，绕过了 TypeScript 类型检查。

### ⚠️ MED-003: Export 硬编码 page_size

**严重程度：** 🟡 中  
**涉及文件：** `frontend/src/views/student/StudentList.vue` 第 434 行

**问题描述：**

`page_size: '10000'` 硬编码，如果数据量超过 10000 条将丢失数据。应使用后端导出 API（`GET /api/v1/export/students`）。

---

## 六、低优先级问题

### ℹ️ LOW-001: 前端 console.error/console.warn 残留

**严重程度：** 🟢 低  
**涉及文件：**
- `stores/auth.ts`：3 处 `console.error`
- `router/index.ts`：1 处 `console.error` + 1 处 `console.warn`
- `views/student/MyGrades.vue`：1 处 `console.error`

**说明：** 这些是错误处理日志，非调试日志，可接受。但建议统一使用 Logger 工具而非直接调用 console。

### ℹ️ LOW-002: 登录页默认凭据提示

**严重程度：** 🟢 低  
**涉及文件：** `frontend/src/views/login/Login.vue` 第 65-78 行

**说明：** 默认凭据需用户主动点击才显示（`showDefaultAccount` 默认 `false`），开发阶段可接受。生产环境建议完全移除或通过环境变量控制。

---

## 七、已通过的功能清单

| # | 功能 | 前端 | 后端 | 结论 |
|---|------|------|------|------|
| 1 | 移除调试日志 | ✅ | N/A | 通过 |
| 2 | JWT 密钥检查 | N/A | ✅ | 通过 |
| 3 | 用户管理 API | N/A | ✅ | 通过 |
| 4 | 操作审计日志 | N/A | ✅ | 通过（有小问题） |
| 5 | 批量删除接口 | N/A | ✅ | 通过（有小问题） |
| 6 | Token 过期检查 | N/A | ✅ | 通过 |
| 7 | 学生查看成绩页面 | ✅ | N/A | 通过 |
| 8 | 搜索防抖自动搜索 | ✅ | N/A | 通过 |
| 9 | 导出全部筛选结果 | ✅ | N/A | 通过 |
| 10 | 登录页隐藏默认密码 | ✅ | N/A | 通过 |
| 11 | 密码强度校验 | ✅ | ⚠️ | 前端通过，后端缺失 |
| 12 | 密码修改功能 | ✅ | ❌ | 后端接口缺失 |

---

## 八、修复优先级建议

| 优先级 | 问题编号 | 修复建议 |
|--------|---------|---------|
| **P0** | BUG-001 | 添加后端 `/auth/change-password` 端点 |
| **P1** | HI-001 | 后端添加密码强度校验 |
| **P1** | HI-004 | 创建 `docs/database.md` |
| **P2** | HI-002 | 批量删除使用显式事务 |
| **P2** | HI-003 | 移动 AuditLogRepository |
| **P3** | MED-001~003 | MyGrades 学生ID、类型安全、导出优化 |
| **P4** | LOW-001~002 | 日志工具化、生产环境配置 |

---

> **审查结束**  
> 请 backend-dev 优先修复 BUG-001（阻塞问题），然后重新提交审查。
