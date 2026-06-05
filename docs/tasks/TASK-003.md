# TASK-003: 成绩管理 API

> **创建日期：** 2026-06-05  
> **负责人：** backend-dev  
> **优先级：** P0 (核心功能)  
> **状态：** DONE

---

## 1. 任务概述

### 1.1 任务描述

实现成绩管理的完整 API 层，包括单条成绩录入、批量成绩录入、成绩修改、成绩删除、以及多维度成绩查询功能。

### 1.2 业务背景

根据 PRD 的成绩录入模块（F-GRD）和成绩查询模块（F-QRY），需要实现成绩的完整生命周期管理。这是系统的核心业务功能。

### 1.3 关联需求

| 需求编号 | 需求名称 | 来源文档 |
|---------|---------|---------|
| F-GRD-001 | 单条成绩录入 | prd.md |
| F-GRD-002 | 批量成绩录入 | prd.md |
| F-GRD-003 | 成绩修改 | prd.md |
| F-GRD-004 | 成绩删除 | prd.md |
| F-QRY-001 | 按学生查询 | prd.md |
| F-QRY-002 | 按班级查询 | prd.md |
| F-QRY-003 | 按科目查询 | prd.md |
| F-QRY-004 | 组合条件查询 | prd.md |

---

## 2. 详细任务清单

### 2.1 业务逻辑层（services/）

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 1.1 | 创建 GradeService | `src/services/grade_service.py` | 成绩业务逻辑：录入、批量导入、修改、删除、查询 | TODO |

### 2.2 API 路由层（api/routes/）

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 2.1 | 创建成绩 API 路由 | `src/api/routes/grades.py` | RESTful 接口：成绩 CRUD 和查询 | TODO |

### 2.3 CLI 命令层（cli/）

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 3.1 | 创建成绩 CLI 命令 | `src/cli/commands/grade_cmd.py` | 命令行接口：input, batch, query, update, delete | TODO |

---

## 3. API 接口规范

### 3.1 接口列表

| 方法 | 路径 | 功能 | 请求参数 | 响应格式 |
|------|------|------|---------|---------|
| POST | `/api/grades` | 单条成绩录入 | GradeCreate | GradeResponse |
| POST | `/api/grades/batch` | 批量成绩录入 | GradeBatchCreate | BatchResponse |
| GET | `/api/grades/{grade_id}` | 查询单条成绩 | grade_id | GradeResponse |
| PUT | `/api/grades/{grade_id}` | 修改成绩 | GradeUpdate | GradeResponse |
| DELETE | `/api/grades/{grade_id}` | 删除成绩 | grade_id | SuccessResponse |
| GET | `/api/grades/student/{student_id}` | 按学生查询 | student_id | List[GradeResponse] |
| GET | `/api/grades/class/{class_name}` | 按班级查询 | class_name, subject, exam_type | List[GradeResponse] |
| GET | `/api/grades/subject/{subject}` | 按科目查询 | subject, exam_type | List[GradeResponse] |
| GET | `/api/grades/search` | 组合条件查询 | class_name, subject, exam_type | List[GradeResponse] |

### 3.2 请求/响应格式

#### 单条成绩录入 (POST /api/grades)

**请求体：**
```json
{
    "student_id": "20260001",
    "subject": "数学",
    "score": 95.5,
    "exam_type": "期中",
    "exam_date": "2026-06-01"
}
```

**成功响应 (201)：**
```json
{
    "success": true,
    "data": {
        "grade_id": 1,
        "student_id": "20260001",
        "subject": "数学",
        "score": 95.5,
        "exam_type": "期中",
        "exam_date": "2026-06-01",
        "created_at": "2026-06-05T10:00:00"
    }
}
```

**错误响应 (409)：**
```json
{
    "success": false,
    "error": {
        "code": "DUPLICATE",
        "message": "成绩 的 学生-科目-考试类型 '20260001-数学-期中' 已存在"
    }
}
```

#### 批量成绩录入 (POST /api/grades/batch)

**请求体：**
```json
{
    "subject": "数学",
    "exam_type": "期中",
    "exam_date": "2026-06-01",
    "grades": [
        {"student_id": "20260001", "score": 95.5},
        {"student_id": "20260002", "score": 88.0},
        {"student_id": "20260003", "score": 72.5}
    ]
}
```

**成功响应 (201)：**
```json
{
    "success": true,
    "data": {
        "total": 3,
        "success_count": 3,
        "failed_count": 0,
        "failed_items": []
    }
}
```

#### 按学生查询 (GET /api/grades/student/{student_id})

**成功响应 (200)：**
```json
{
    "success": true,
    "data": [
        {
            "grade_id": 1,
            "student_id": "20260001",
            "subject": "数学",
            "score": 95.5,
            "exam_type": "期中",
            "exam_date": "2026-06-01"
        },
        {
            "grade_id": 2,
            "student_id": "20260001",
            "subject": "语文",
            "score": 88.0,
            "exam_type": "期中",
            "exam_date": "2026-06-01"
        }
    ]
}
```

### 3.3 CLI 命令规范

```bash
# 单条成绩录入
python -m src.cli grade input --student-id 20260001 --subject 数学 --score 95.5 --exam-type 期中 --date 2026-06-01

# 批量成绩录入（从 CSV 文件）
python -m src.cli grade batch --subject 数学 --exam-type 期中 --date 2026-06-01 --file grades.csv

# 按学生查询
python -m src.cli grade query --student-id 20260001

# 按班级查询
python -m src.cli grade query --class 三年一班 [--subject 数学] [--exam-type 期中]

# 按科目查询
python -m src.cli grade query --subject 数学 [--exam-type 期中]

# 修改成绩
python -m src.cli grade update --grade-id 1 --score 98.0

# 删除成绩
python -m src.cli grade delete --grade-id 1
```

---

## 4. 业务逻辑规范

### 4.1 单条成绩录入流程

```
1. 接收请求数据
2. Pydantic 验证数据格式
3. 检查学生是否存在
   - 不存在 → 返回 404 错误
   - 存在 → 继续
4. 检查成绩记录是否已存在（学生+科目+考试类型）
   - 存在 → 返回 409 错误
   - 不存在 → 继续
5. 验证分数范围（0-100）
6. 创建成绩记录
7. 返回创建成功响应
```

### 4.2 批量成绩录入流程

```
1. 接收批量请求数据
2. 遍历每条成绩记录：
   a. 检查学生是否存在
   b. 检查成绩是否已存在
   c. 验证分数范围
3. 统计成功/失败数量
4. 批量插入成功的记录
5. 返回批量处理结果
```

### 4.3 查询逻辑

| 查询类型 | 查询条件 | 返回结果 |
|---------|---------|---------|
| 按学生 | student_id | 该学生所有科目成绩 |
| 按班级 | class_name | 该班级所有学生成绩 |
| 按科目 | subject | 该科目所有学生成绩 |
| 组合查询 | class_name + subject + exam_type | 筛选后的成绩列表 |

### 4.4 业务规则

| 规则编号 | 规则描述 | 实现位置 |
|---------|---------|---------|
| BR-GRD-001 | 分数范围 0-100，支持1位小数 | GradeSchema.Field |
| BR-GRD-002 | 考试类型只能是：期中、期末、月考、单元测试 | GradeSchema.validator |
| BR-GRD-003 | 科目只能是预定义列表 | GradeSchema.validator |
| BR-GRD-004 | 同一学生同一科目同一考试类型唯一 | Grade 模型 UniqueConstraint |
| BR-GRD-005 | 学生不存在时拒绝录入成绩 | GradeService.create_grade() |
| BR-GRD-006 | 批量录入时部分失败不影响成功的记录 | GradeService.batch_create_grades() |

---

## 5. 验收标准

### 5.1 功能验收

| 验收项 | 验收标准 | 测试方法 |
|-------|---------|---------|
| 单条录入 | 成功创建成绩记录 | API 测试 |
| 学生不存在 | 返回 404 错误 | API 测试 |
| 成绩重复 | 返回 409 错误 | API 测试 |
| 分数超范围 | 返回 422 错误 | API 测试 |
| 批量录入 | 正确处理多条记录，统计成功/失败 | API 测试 |
| 按学生查询 | 返回该学生所有成绩 | API 测试 |
| 按班级查询 | 返回该班级所有成绩 | API 测试 |
| 按科目查询 | 返回该科目所有成绩 | API 测试 |
| 组合查询 | 正确筛选结果 | API 测试 |
| CLI 命令 | 所有 CLI 命令正常工作 | 集成测试 |

### 5.2 性能验收

| 验收项 | 验收标准 | 测试方法 |
|-------|---------|---------|
| 单条录入 | 响应时间 < 50ms | 性能测试 |
| 批量录入 500 条 | 处理时间 < 1 分钟 | 性能测试 |
| 查询响应 | 响应时间 < 100ms | 性能测试 |

---

## 6. 依赖关系

### 6.1 前置依赖

| 任务编号 | 任务名称 | 依赖说明 |
|---------|---------|---------|
| TASK-001 | 数据库模型实现 | 依赖 Grade 模型、Repository、Schema |

### 6.2 后续依赖

| 任务编号 | 任务名称 | 依赖说明 |
|---------|---------|---------|
| TASK-004 | 统计分析功能 | 依赖 GradeService 的查询功能 |

---

## 7. 风险与注意事项

| 风险项 | 说明 | 应对措施 |
|-------|------|---------|
| 批量导入性能 | 大量数据导入可能很慢 | 使用批量插入 + 事务 |
| 数据一致性 | 批量导入部分失败 | 事务控制，记录失败项 |
| 查询性能 | 多条件组合查询可能慢 | 索引优化 + 分页 |

---

## 8. 工作量估算

| 子任务 | 预估工时 | 备注 |
|--------|---------|------|
| GradeService | 4h | 业务逻辑实现 |
| API 路由 | 3h | RESTful 接口 |
| CLI 命令 | 2h | 命令行接口 |
| 单元测试 | 3h | 测试用例编写 |
| **合计** | **12h** | |

---

## 9. 输出物清单

- [ ] `src/services/grade_service.py` - 成绩业务逻辑
- [ ] `src/api/routes/grades.py` - 成绩 API 路由
- [ ] `src/cli/commands/grade_cmd.py` - 成绩 CLI 命令
- [ ] `tests/unit/test_services/test_grade_service.py` - Service 单元测试
- [ ] `tests/integration/test_api/test_grades.py` - API 集成测试

---

> **任务状态变更记录**
> 
> | 时间 | 状态变更 | 操作人 | 备注 |
> |------|---------|--------|------|
> | 2026-06-05 | - → TODO | PMO | 任务创建 |
> | 2026-06-06 | TODO → IN_PROGRESS → REVIEWS → DONE | Reviewer | 审查通过，114个测试全部通过 |

