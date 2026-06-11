# P0+P1 改进验证测试计划

> **测试日期：** 2026-06-11  
> **测试工程师：** QA Agent  
> **测试类型：** P0+P1 改进验证  
> **测试状态：** 已完成

---

## 1. 测试背景

本轮验证 P0+P1 改进项的实现效果，包括：
- 登录页默认密码处理
- 密码修改功能
- 学生查看成绩功能
- 搜索防抖优化
- 用户管理功能
- 批量删除功能

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
| Vite | ^5.4.0 | ✅ 已安装 |

---

## 3. 测试矩阵设计

### 3.1 后端测试矩阵（217 个用例）

| 测试模块 | 测试类 | 测试内容 | 用例数 |
|---------|--------|---------|-------|
| test_models | TestGradeModel | 成绩模型 CRUD、约束、关系 | 7 |
| test_models | TestStudentModel | 学生模型 CRUD、约束、关系 | 7 |
| test_repositories | TestStudentRepository | 学生仓库 CRUD、查询、搜索 | 11 |
| test_repositories | TestGradeRepository | 成绩仓库 CRUD、查询、批量操作 | 8 |
| test_services | TestGradeService | 成绩业务逻辑（录入、查询、修改、删除、边界值） | 20 |
| test_services | TestStatisticsService | 统计服务（平均分、最高/低分、及格率、排名等） | 40 |
| test_services | TestStudentService | 学生业务逻辑（CRUD、搜索、分页、唯一性校验） | 20 |
| test_auth | TestLoginAPI | 登录正常流、异常流、边界值 | 12 |
| test_auth | TestTokenRefreshAPI | Token 刷新正常流、异常流 | 4 |
| test_auth | TestGetCurrentUserAPI | 获取用户信息正常流、异常流 | 5 |
| test_auth | TestLogoutAPI | 登出正常流、异常流 | 2 |
| test_auth | TestLoginResponseFormat | 响应格式、Token 内容验证 | 3 |
| test_auth | TestAuthEdgeCases | SQL 注入、特殊字符、Unicode | 5 |
| test_students | TestStudentAPI | 学生 CRUD、搜索、分页、筛选 | 16 |
| test_grades | TestGradeAPI | 成绩 CRUD、批量录入、组合查询 | 23 |
| test_statistics | TestStatisticsAPI | 统计 API、排名、报告 | 28 |

### 3.2 P0+P1 功能验证矩阵

| 编号 | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|------|---------|---------|---------|---------|
| V-01 | 登录页默认密码 | 打开登录页 | 默认密码隐藏，有"查看默认账号"按钮 | 代码审查 |
| V-02 | 密码修改 | 登录后点击头像 → 修改密码 | 弹出密码修改对话框 | 代码审查 |
| V-03 | 学生查看成绩 | 用 student 账号登录 | 侧边栏显示"我的成绩"菜单 | 代码审查 |
| V-04 | 搜索防抖 | 在学生列表输入学号 | 300ms 后自动搜索 | 代码审查 |
| V-05 | 用户管理 | 用 admin 账号登录 | 侧边栏显示"用户管理"菜单 | 代码审查 |
| V-06 | 批量删除 | 选择多个学生删除 | 调用批量删除接口 | 代码审查 |

### 3.3 前端构建检查

| 编号 | 测试场景 | 测试命令 | 预期结果 |
|------|---------|---------|---------|
| FE-01 | Vite 生产构建 | `npx vite build` | 成功输出 dist 目录 |

### 3.4 安全与质量门禁

| 门禁项 | 标准 | 测试方法 |
|-------|------|---------|
| 单元测试通过率 | 100% | `pytest tests/unit/ -v` |
| 集成测试通过率 | 100% | `pytest tests/integration/ -v` |
| 前端构建 | 成功 | `npx vite build` |
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

> **文档状态：** 已完成（2026-06-11）  
> **测试结果：** ✅ 通过  
> **详细报告：** 见 [test-report.md](./test-report.md)
