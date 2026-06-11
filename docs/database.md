# 数据库设计文档

> 本文档记录学生成绩管理系统的所有数据库表结构、字段说明和索引设计。
> 数据库类型：SQLite（开发/测试）/ PostgreSQL（生产可选）
> ORM 框架：SQLAlchemy 2.0（声明式映射）

---

## 1. ER 关系概览

```
┌───────────┐       ┌───────────┐       ┌───────────────┐
│   users   │       │ students  │──────<│    grades     │
│           │       │           │  1:N  │               │
└───────────┘       └───────────┘       └───────────────┘

┌───────────────┐
│  audit_logs   │   (独立表，记录所有关键操作)
└───────────────┘
```

**关系说明：**
- `students` ↔ `grades`：一对多关系。一个学生可有多条成绩记录，删除学生时级联删除其所有成绩（`CASCADE`）。
- `users`：独立表，用于系统认证与授权。
- `audit_logs`：独立表，记录系统操作审计日志。

---

## 2. 表结构详细定义

### 2.1 students — 学生信息表

存储学生基本信息，主键为学号。

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|---|---|---|---|---|
| `student_id` | VARCHAR(8) | PRIMARY KEY, INDEX | — | 学号，格式：YYYY + 4位序号（如 `20260001`） |
| `name` | VARCHAR(20) | NOT NULL | — | 学生姓名，2–20 个字符 |
| `gender` | VARCHAR(2) | NOT NULL | — | 性别，取值：`男` / `女` |
| `class_name` | VARCHAR(20) | NOT NULL, INDEX | — | 班级名称，如 `三年一班` |
| `enrollment_year` | INTEGER | NOT NULL | — | 入学年份 |
| `created_at` | DATETIME | — | UTC 当前时间 | 记录创建时间 |
| `updated_at` | DATETIME | — | UTC 当前时间（自动更新） | 记录最后更新时间 |

**索引：**

| 索引名 | 字段 | 用途 |
|---|---|---|
| `pk_students` | `student_id` | 主键索引（自动） |
| `ix_students_student_id` | `student_id` | 按学号快速查询 |
| `ix_students_class_name` | `class_name` | 按班级筛选学生 |
| `idx_students_class_name` | `class_name` | 按班级统计和筛选 |

---

### 2.2 grades — 成绩信息表

存储学生各科成绩，支持按科目和考试类型唯一约束。

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|---|---|---|---|---|
| `grade_id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | — | 成绩 ID（自增） |
| `student_id` | VARCHAR(8) | FOREIGN KEY → `students.student_id`, NOT NULL, INDEX | — | 学号（外键） |
| `subject` | VARCHAR(10) | NOT NULL | — | 科目名称，如 `语文`、`数学`、`英语` |
| `score` | FLOAT | NOT NULL | — | 分数，0–100，支持 1 位小数 |
| `exam_type` | VARCHAR(10) | NOT NULL | — | 考试类型：`期中` / `期末` / `月考` / `单元测试` |
| `exam_date` | DATE | NOT NULL | — | 考试日期 |
| `created_at` | DATETIME | — | UTC 当前时间 | 记录创建时间 |
| `updated_at` | DATETIME | — | UTC 当前时间（自动更新） | 记录最后更新时间 |

**约束：**

| 约束名 | 类型 | 字段 | 说明 |
|---|---|---|---|
| `uq_student_subject_exam` | UNIQUE | `student_id`, `subject`, `exam_type` | 同一学生、同一科目、同一考试类型只能有一条记录 |
| `fk_grades_student_id` | FOREIGN KEY | `student_id` → `students.student_id` | 删除学生时级联删除成绩（`ON DELETE CASCADE`） |

**索引：**

| 索引名 | 字段 | 用途 |
|---|---|---|
| `pk_grades` | `grade_id` | 主键索引（自动） |
| `ix_grades_student_id` | `student_id` | 按学生查询成绩 |
| `idx_grades_student_id` | `student_id` | 按学生 ID 快速查找 |
| `idx_grades_subject_exam_type` | `subject`, `exam_type` | 按科目和考试类型查询 |

---

### 2.3 users — 用户认证表

存储系统用户信息，用于登录认证和权限控制。

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|---|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | — | 用户 ID（自增） |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | — | 用户名，用于登录 |
| `hashed_password` | VARCHAR(128) | NOT NULL | — | bcrypt 哈希后的密码（禁止明文存储） |
| `role` | VARCHAR(20) | NOT NULL | `student` | 用户角色：`admin` / `teacher` / `student` |
| `is_active` | BOOLEAN | NOT NULL | `True` | 账户是否启用（可用于禁用账户而不删除） |
| `created_at` | DATETIME | — | UTC 当前时间 | 记录创建时间 |
| `updated_at` | DATETIME | — | UTC 当前时间（自动更新） | 记录最后更新时间 |

**索引：**

| 索引名 | 字段 | 用途 |
|---|---|---|
| `pk_users` | `id` | 主键索引（自动） |
| `ix_users_username` | `username` | 按用户名快速查询（登录） |

**角色权限说明：**
- `admin`（管理员）：拥有所有权限
- `teacher`（教师）：可以管理学生和成绩
- `student`（学生）：仅可查看自己的成绩

---

### 2.4 audit_logs — 操作审计日志表

记录系统中所有关键操作，用于安全审计和操作追踪。

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|---|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | — | 日志 ID（自增） |
| `user_id` | INTEGER | NOT NULL | — | 操作用户 ID |
| `username` | VARCHAR(50) | NOT NULL | — | 操作用户名（冗余存储，避免 JOIN 查询） |
| `action` | VARCHAR(20) | NOT NULL | — | 操作类型：`create` / `update` / `delete` / `login` / `logout` |
| `resource_type` | VARCHAR(20) | NOT NULL | — | 资源类型：`student` / `grade` / `user` |
| `resource_id` | VARCHAR(50) | NULLABLE | — | 资源标识符 |
| `details` | TEXT | NULLABLE | — | 操作详情（JSON 格式） |
| `ip_address` | VARCHAR(45) | NULLABLE | — | 客户端 IP 地址（支持 IPv6） |
| `created_at` | DATETIME | — | UTC 当前时间 | 操作时间 |

**索引：**

| 索引名 | 字段 | 用途 |
|---|---|---|
| `pk_audit_logs` | `id` | 主键索引（自动） |
| `idx_audit_logs_user_id` | `user_id` | 按用户查询操作记录 |
| `idx_audit_logs_action` | `action` | 按操作类型筛选 |
| `idx_audit_logs_resource_type` | `resource_type` | 按资源类型筛选 |
| `idx_audit_logs_created_at` | `created_at` | 按时间范围查询（最常用） |

---

## 3. 设计决策

### 3.1 级联删除策略
- 删除学生（`students`）时，通过 ORM `cascade="all, delete-orphan"` 和数据库 `ON DELETE CASCADE` 双重保障，自动删除关联的成绩记录（`grades`）。

### 3.2 审计日志冗余设计
- `audit_logs.username` 字段冗余存储用户名，避免每次查询日志时 JOIN `users` 表，提升查询性能。

### 3.3 时间字段统一
- 所有时间字段使用 UTC 时区，由应用层负责时区转换显示。

### 3.4 密码安全
- `users.hashed_password` 使用 bcrypt 算法哈希存储，数据库中不存储明文密码。
