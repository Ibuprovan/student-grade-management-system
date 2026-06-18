# TASK-001: 数据库模型实现

> **创建日期：** 2026-06-05  
> **负责人：** backend-dev  
> **优先级：** P0 (核心功能)  
> **状态：** DONE

---

## 1. 任务概述

### 1.1 任务描述

实现学生成绩管理系统的数据库模型层，包括 SQLAlchemy ORM 模型定义、数据库连接配置、以及基础 Repository 模式实现。

### 1.2 业务背景

根据架构文档，系统采用分层架构，数据模型层是整个系统的基础。需要实现：
- Student（学生）模型
- Grade（成绩）模型
- 数据库连接和初始化
- 基础 Repository 接口

### 1.3 关联需求

| 需求编号 | 需求名称 | 来源文档 |
|---------|---------|---------|
| F-STD-001 ~ F-STD-005 | 学生信息管理 | prd.md |
| F-GRD-001 ~ F-GRD-004 | 成绩录入管理 | prd.md |
| 4.1 ER 图设计 | 数据模型设计 | architecture.md |
| 4.2 SQLAlchemy 模型 | ORM 模型定义 | architecture.md |

---

## 2. 详细任务清单

### 2.1 核心配置层（core/）

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 1.1 | 创建数据库配置 | `src/core/config.py` | 应用配置、数据库路径、分页参数 | DONE |
| 1.2 | 创建数据库连接 | `src/core/database.py` | SQLAlchemy 引擎、会话工厂、Base 类 | DONE |
| 1.3 | 创建常量定义 | `src/core/constants.py` | 科目列表、考试类型、分数范围等枚举值 | DONE |
| 1.4 | 创建自定义异常 | `src/core/exceptions.py` | 业务异常层次结构 | DONE |

### 2.2 数据模型层（models/）

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 2.1 | 创建 Student 模型 | `src/models/student.py` | 学生表 ORM 模型，包含字段定义和关系 | DONE |
| 2.2 | 创建 Grade 模型 | `src/models/grade.py` | 成绩表 ORM 模型，包含外键和唯一约束 | DONE |
| 2.3 | 创建模型初始化 | `src/models/__init__.py` | 导出所有模型类 | DONE |

### 2.3 数据访问层（repositories/）

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 3.1 | 创建基础 Repository | `src/repositories/base.py` | 通用 CRUD 操作基类 | DONE |
| 3.2 | 创建 StudentRepository | `src/repositories/student_repo.py` | 学生数据访问，包含学号查询、班级查询 | DONE |
| 3.3 | 创建 GradeRepository | `src/repositories/grade_repo.py` | 成绩数据访问，包含按学生/科目查询 | DONE |

### 2.4 数据验证层（schemas/）

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 4.1 | 创建 Student Schema | `src/schemas/student.py` | Pydantic 模式：StudentCreate, StudentUpdate, StudentResponse | DONE |
| 4.2 | 创建 Grade Schema | `src/schemas/grade.py` | Pydantic 模式：GradeCreate, GradeBatchCreate, GradeResponse | DONE |

---

## 3. 技术规范

### 3.1 数据库表结构

#### students 表

```sql
CREATE TABLE students (
    student_id VARCHAR(8) PRIMARY KEY,      -- 学号（如：20260001）
    name VARCHAR(20) NOT NULL,              -- 姓名
    gender VARCHAR(2) NOT NULL,             -- 性别（男/女）
    class_name VARCHAR(20) NOT NULL,        -- 班级（如：2026级1班）
    enrollment_year INTEGER NOT NULL,       -- 入学年份
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_students_class_name ON students(class_name);
```

#### grades 表

```sql
CREATE TABLE grades (
    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 成绩ID
    student_id VARCHAR(8) NOT NULL,               -- 学号（外键）
    subject VARCHAR(10) NOT NULL,                 -- 科目
    score DECIMAL(4,1) NOT NULL,                  -- 分数（0-100）
    exam_type VARCHAR(10) NOT NULL,               -- 考试类型
    exam_date DATE NOT NULL,                      -- 考试日期
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    UNIQUE(student_id, subject, exam_type)        -- 唯一约束
);

CREATE INDEX idx_grades_student_id ON grades(student_id);
```

### 3.2 业务规则

| 规则编号 | 规则描述 | 实现位置 |
|---------|---------|---------|
| BR-001 | 学号格式：4位年份 + 4位序号（如：20260001） | StudentSchema.validator |
| BR-002 | 姓名长度：2-20个字符 | StudentSchema.Field |
| BR-003 | 性别只能是"男"或"女" | StudentSchema.validator |
| BR-004 | 分数范围：0-100（支持1位小数） | GradeSchema.Field |
| BR-005 | 考试类型：期中、期末、月考、单元测试 | GradeSchema.validator |
| BR-006 | 同一学生同一科目同一考试类型唯一 | Grade 模型 UniqueConstraint |

### 3.3 枚举值定义

```python
# 科目列表
SUBJECTS = ["语文", "数学", "英语", "物理", "化学", "生物", "历史", "地理", "政治"]

# 考试类型
EXAM_TYPES = ["期中", "期末", "月考", "单元测试"]

# 性别选项
GENDERS = ["男", "女"]

# 分数范围
SCORE_MIN = 0.0
SCORE_MAX = 100.0
```

---

## 4. 验收标准

### 4.1 功能验收

| 验收项 | 验收标准 | 测试方法 |
|-------|---------|---------|
| 模型创建 | Student 和 Grade 模型能正确映射到数据库表 | 单元测试 |
| 数据库初始化 | 应用启动时自动创建数据库和表 | 集成测试 |
| CRUD 操作 | Repository 能执行增删改查操作 | 单元测试 |
| 数据验证 | Pydantic Schema 能正确验证输入数据 | 单元测试 |
| 唯一约束 | 重复的学生成绩记录被正确拒绝 | 单元测试 |
| 外键约束 | 不存在的学生无法录入成绩 | 单元测试 |

### 4.2 代码质量验收

| 验收项 | 验收标准 |
|-------|---------|
| 代码规范 | 遵循 PEP8 规范 |
| 类型提示 | 所有函数和方法包含类型提示 |
| 文档字符串 | 所有公开类和方法包含 docstring |
| 测试覆盖 | 核心功能测试覆盖率 > 80% |

---

## 5. 依赖关系

### 5.1 前置依赖

无（本任务是项目基础）

### 5.2 后续依赖

| 任务编号 | 任务名称 | 依赖说明 |
|---------|---------|---------|
| TASK-002 | 学生信息管理 API | 依赖 Student 模型和 Repository |
| TASK-003 | 成绩管理 API | 依赖 Grade 模型和 Repository |
| TASK-004 | 统计分析功能 | 依赖 Grade 模型和 Repository |

---

## 6. 风险与注意事项

| 风险项 | 说明 | 应对措施 |
|-------|------|---------|
| 数据库兼容性 | SQLite 特有语法可能影响未来迁移 | 使用 SQLAlchemy 标准 API，避免原生 SQL |
| 并发写入 | SQLite 并发写入能力有限 | 使用事务和适当的锁机制 |
| 数据迁移 | 模型变更可能需要数据库迁移 | 预留 Alembic 集成点 |

---

## 7. 工作量估算

| 子任务 | 预估工时 | 备注 |
|--------|---------|------|
| 核心配置层 | 2h | 配置、连接、异常 |
| 数据模型层 | 2h | ORM 模型定义 |
| 数据访问层 | 3h | Repository 实现 |
| 数据验证层 | 2h | Pydantic Schema |
| 单元测试 | 3h | 测试用例编写 |
| **合计** | **12h** | |

---

## 8. 输出物清单

- [x] `src/core/config.py` - 应用配置
- [x] `src/core/database.py` - 数据库连接
- [x] `src/core/constants.py` - 常量定义
- [x] `src/core/exceptions.py` - 自定义异常
- [x] `src/models/student.py` - Student 模型
- [x] `src/models/grade.py` - Grade 模型
- [x] `src/repositories/base.py` - 基础 Repository
- [x] `src/repositories/student_repo.py` - 学生 Repository
- [x] `src/repositories/grade_repo.py` - 成绩 Repository
- [x] `src/schemas/student.py` - 学生 Schema
- [x] `src/schemas/grade.py` - 成绩 Schema
- [x] `tests/unit/test_models/` - 模型单元测试
- [x] `tests/unit/test_repositories/` - Repository 单元测试

---

> **任务状态变更记录**
> 
> | 时间 | 状态变更 | 操作人 | 备注 |
> |------|---------|--------|------|
> | 2026-06-05 | - → TODO | PMO | 任务创建 |
> | 2026-06-05 | TODO → DONE | backend-dev | 所有子任务完成，33项单元测试全部通过 |
