# Bug 修复验证测试计划

> **测试日期：** 2026-06-08  
> **测试工程师：** QA Agent  
> **测试类型：** 全面 Bug 修复验证（第三轮）  
> **测试状态：** 进行中

---

## 1. 测试背景

本轮修复了 13 个问题（8 个前端 + 5 个后端），需全面验证修复效果。测试覆盖范围包括：
- 后端单元测试（models / repositories / services）
- 后端集成测试（auth / students / grades / statistics API）
- 前端构建检查
- Pydantic 弃用警告消除验证
- 特定修复场景的手动验证

---

## 2. 测试环境

| 组件 | 版本/配置 | 状态 |
|------|----------|------|
| Python | 3.12.4 | ✅ 可用 |
| pytest | 9.0.3 | ✅ 已安装 |
| pytest-cov | 7.1.0 | ✅ 已安装 |
| FastAPI | >=0.100.0 | ✅ 已安装 |
| SQLAlchemy | >=2.0.0 | ✅ 已安装 |
| Pydantic | >=2.0.0 | ✅ 已安装 |
| Vue 3 | ^3.3.0 | ✅ 已安装 |
| TypeScript | 5.9.3 | ✅ 已安装 |
| vue-tsc | ^1.8.0 | ⚠️ 版本不兼容 |
| Vite | ^4.4.0 | ✅ 已安装 |

---

## 3. 测试矩阵设计

### 3.1 后端单元测试矩阵（119 个用例）

| 测试模块 | 测试类 | 测试内容 | 用例数 |
|---------|--------|---------|-------|
| test_models | TestGradeModel | 成绩模型 CRUD、约束、关系 | 7 |
| test_models | TestStudentModel | 学生模型 CRUD、约束、关系 | 7 |
| test_repositories | TestStudentRepository | 学生仓库 CRUD、查询、搜索 | 11 |
| test_repositories | TestGradeRepository | 成绩仓库 CRUD、查询、批量操作 | 8 |
| test_services | TestGradeService | 成绩业务逻辑（录入、查询、修改、删除、边界值） | 20 |
| test_services | TestStatisticsService | 统计服务（平均分、最高/低分、及格率、排名等） | 40 |
| test_services | TestStudentService | 学生业务逻辑（CRUD、搜索、分页、唯一性校验） | 20 |

### 3.2 后端集成测试矩阵（98 个用例）

| 测试模块 | 测试类 | 测试内容 | 用例数 |
|---------|--------|---------|-------|
| test_auth | TestLoginAPI | 登录正常流、异常流、边界值 | 12 |
| test_auth | TestTokenRefreshAPI | Token 刷新正常流、异常流 | 4 |
| test_auth | TestGetCurrentUserAPI | 获取用户信息正常流、异常流 | 5 |
| test_auth | TestLogoutAPI | 登出正常流、异常流 | 2 |
| test_auth | TestLoginResponseFormat | 响应格式、Token 内容验证 | 3 |
| test_auth | TestAuthEdgeCases | SQL 注入、特殊字符、Unicode | 5 |
| test_students | TestStudentAPI | 学生 CRUD、搜索、分页、筛选 | 16 |
| test_grades | TestGradeAPI | 成绩 CRUD、批量录入、组合查询 | 23 |
| test_statistics | TestStatisticsAPI | 统计 API、排名、报告 | 28 |

### 3.3 特定修复场景验证矩阵

| 编号 | 测试场景 | 测试步骤 | 预期结果 | 关联修复 |
|------|---------|---------|---------|---------|
| V-01 | 登录功能 | 输入正确密码登录 | 成功跳转 Dashboard | 前端修复 #1 |
| V-02 | 登出功能 | 点击退出登录 | Token 被吊销，跳转登录页 | 前端修复 #2 |
| V-03 | 登出后 Token 失效 | 登出后用旧 Token 访问 API | 返回 401 | 后端修复 #1 |
| V-04 | 学生删除失败 | 删除不存在的学生 | 显示错误提示 | 前端修复 #3 |
| V-05 | 成绩表单验证 | 不填写必填字段提交 | 显示表单验证错误 | 前端修复 #4 |
| V-06 | CSV 导出 | 导出含逗号/引号的数据 | CSV 格式正确 | 前端修复 #5 |
| V-07 | Pydantic 弃用警告 | 运行 pytest 检查警告 | 无 PydanticDeprecated 输出 | 后端修复 #2 |

### 3.4 前端构建检查

| 编号 | 测试场景 | 测试命令 | 预期结果 |
|------|---------|---------|---------|
| FE-01 | vue-tsc 类型检查 | `npm run build` | 无类型错误 |
| FE-02 | Vite 生产构建 | `npx vite build` | 成功输出 dist 目录 |

### 3.5 安全与质量门禁

| 门禁项 | 标准 | 测试方法 |
|-------|------|---------|
| 单元测试通过率 | 100% | `pytest tests/unit/ -v` |
| 集成测试通过率 | 100% | `pytest tests/integration/ -v` |
| 代码覆盖率 | >= 80% | `pytest --cov=src` |
| Pydantic 弃用 | 0 个警告 | `pytest 2>&1 \| findstr PydanticDeprecated` |
| 前端构建 | 成功 | `npm run build` |
| DBA 审查 | 无未备案 DDL | 检查源码中 CREATE/ALTER TABLE |

---

## 4. DBA 优先权审查

| 审查项 | 结果 |
|-------|------|
| 源码中 CREATE TABLE | 未发现 |
| 源码中 ALTER TABLE | 未发现 |
| docs/database.md 备案 | 文件不存在（无需备案） |

**结论：** 无未备案的数据库结构变更，DBA 审查通过。

---

## 5. 负向惩罚机制检查

| 检查项 | 状态 | 说明 |
|-------|------|------|
| try-catch 块断言 | ✅ 通过 | test_auth.py 包含过期 Token、禁用账户等异常路径测试 |
| HTTP 非 200 断言 | ✅ 通过 | 测试覆盖 401、403、404、409、422 等状态码 |
| 错误处理测试 | ✅ 通过 | 包含 SQL 注入、特殊字符、空值等边界测试 |

---

> **文档状态：** 待执行测试并填写报告
