# TASK-004: 统计分析功能

> **创建日期：** 2026-06-05  
> **负责人：** backend-dev  
> **优先级：** P0 (核心功能)  
> **状态：** DONE

---

## 1. 任务概述

### 1.1 任务描述

实现成绩统计分析的完整功能，包括平均分、最高分、最低分、及格率、优秀率等统计指标计算，以及成绩排序和排名功能。

### 1.2 业务背景

根据 PRD 的成绩统计模块（F-STA）和成绩排序模块（F-SRT），统计分析是系统的核心价值之一，帮助教师和教务人员快速了解学生学业情况。

### 1.3 关联需求

| 需求编号 | 需求名称 | 来源文档 |
|---------|---------|---------|
| F-STA-001 | 平均分统计 | prd.md |
| F-STA-002 | 最高分统计 | prd.md |
| F-STA-003 | 最低分统计 | prd.md |
| F-STA-004 | 及格率统计 | prd.md |
| F-STA-005 | 综合统计报告 | prd.md |
| F-SRT-001 | 单科成绩排序 | prd.md |
| F-SRT-002 | 总分排序 | prd.md |
| F-SRT-003 | 班级排名 | prd.md |
| F-SRT-004 | 年级排名 | prd.md |

---

## 2. 详细任务清单

### 2.1 业务逻辑层（services/）

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 1.1 | 创建 StatisticsService | `src/services/statistics_service.py` | 统计业务逻辑：平均分、最高分、最低分、及格率、排名 | TODO |

### 2.2 API 路由层（api/routes/）

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 2.1 | 创建统计 API 路由 | `src/api/routes/statistics.py` | RESTful 接口：统计查询和排名 | TODO |

### 2.3 数据验证层（schemas/）

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 3.1 | 创建 Statistics Schema | `src/schemas/statistics.py` | Pydantic 模式：StatisticsQuery, StatisticsResponse | TODO |

### 2.4 CLI 命令层（cli/）

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 4.1 | 创建统计 CLI 命令 | `src/cli/commands/statistics_cmd.py` | 命令行接口：average, pass-rate, ranking | TODO |

---

## 3. API 接口规范

### 3.1 接口列表

| 方法 | 路径 | 功能 | 请求参数 | 响应格式 |
|------|------|------|---------|---------|
| GET | `/api/statistics/average` | 平均分统计 | class_name, subject, exam_type | AverageResponse |
| GET | `/api/statistics/max` | 最高分统计 | class_name, subject, exam_type | MaxScoreResponse |
| GET | `/api/statistics/min` | 最低分统计 | class_name, subject, exam_type | MinScoreResponse |
| GET | `/api/statistics/pass-rate` | 及格率统计 | class_name, subject, exam_type | PassRateResponse |
| GET | `/api/statistics/excellent-rate` | 优秀率统计 | class_name, subject, exam_type | ExcellentRateResponse |
| GET | `/api/statistics/report` | 综合统计报告 | class_name, subject | ReportResponse |
| GET | `/api/statistics/ranking/subject` | 单科排名 | subject, exam_type, class_name | RankingResponse |
| GET | `/api/statistics/ranking/total` | 总分排名 | exam_type, class_name | RankingResponse |

### 3.2 请求/响应格式

#### 平均分统计 (GET /api/statistics/average)

**查询参数：**
- `class_name`: 班级（可选）
- `subject`: 科目（可选）
- `exam_type`: 考试类型（可选）

**成功响应 (200)：**
```json
{
    "success": true,
    "data": {
        "average": 78.5,
        "count": 30,
        "subject": "数学",
        "exam_type": "期中",
        "class_name": "2026级1班"
    }
}
```

#### 及格率统计 (GET /api/statistics/pass-rate)

**成功响应 (200)：**
```json
{
    "success": true,
    "data": {
        "pass_rate": 83.33,
        "passed_count": 25,
        "total_count": 30,
        "subject": "数学",
        "exam_type": "期中",
        "class_name": "2026级1班"
    }
}
```

#### 综合统计报告 (GET /api/statistics/report)

**成功响应 (200)：**
```json
{
    "success": true,
    "data": {
        "class_name": "2026级1班",
        "subject": "数学",
        "exam_type": "期中",
        "statistics": {
            "count": 30,
            "average": 78.5,
            "max_score": 98.0,
            "min_score": 45.0,
            "pass_rate": 83.33,
            "excellent_rate": 20.0,
            "score_distribution": {
                "0-59": 5,
                "60-69": 8,
                "70-79": 7,
                "80-89": 6,
                "90-100": 4
            }
        },
        "top_students": [
            {"student_id": "20260001", "name": "张三", "score": 98.0},
            {"student_id": "20260005", "name": "李四", "score": 95.5}
        ]
    }
}
```

#### 单科排名 (GET /api/statistics/ranking/subject)

**查询参数：**
- `subject`: 科目（必填）
- `exam_type`: 考试类型（必填）
- `class_name`: 班级（可选，不填则为年级排名）
- `order`: 排序方式（asc/desc，默认 desc）

**成功响应 (200)：**
```json
{
    "success": true,
    "data": {
        "subject": "数学",
        "exam_type": "期中",
        "class_name": "2026级1班",
        "rankings": [
            {
                "rank": 1,
                "student_id": "20260001",
                "student_name": "张三",
                "score": 98.0
            },
            {
                "rank": 2,
                "student_id": "20260005",
                "student_name": "李四",
                "score": 95.5
            }
        ]
    }
}
```

### 3.3 CLI 命令规范

```bash
# 平均分统计
python -m src.cli stats average [--class 2026级1班] [--subject 数学] [--exam-type 期中]

# 及格率统计
python -m src.cli stats pass-rate [--class 2026级1班] [--subject 数学] [--exam-type 期中]

# 优秀率统计
python -m src.cli stats excellent-rate [--class 2026级1班] [--subject 数学] [--exam-type 期中]

# 综合统计报告
python -m src.cli stats report [--class 2026级1班] [--subject 数学]

# 单科排名
python -m src.cli stats ranking --subject 数学 --exam-type 期中 [--class 2026级1班] [--order desc]

# 总分排名
python -m src.cli stats total-ranking --exam-type 期中 [--class 2026级1班]
```

---

## 4. 业务逻辑规范

### 4.1 统计指标计算公式

```python
# 平均分
average = sum(scores) / len(scores)

# 及格率（>=60分）
pass_rate = (count(score >= 60 for score in scores) / len(scores)) * 100

# 优秀率（>=90分）
excellent_rate = (count(score >= 90 for score in scores) / len(scores)) * 100

# 最高分
max_score = max(scores)

# 最低分
min_score = min(scores)
```

### 4.2 排名规则

| 规则编号 | 规则描述 | 实现位置 |
|---------|---------|---------|
| BR-STA-001 | 默认按分数降序排列（从高到低） | StatisticsService.get_ranking() |
| BR-STA-002 | 分数相同时按学号升序排列 | StatisticsService.get_ranking() |
| BR-STA-003 | 支持升序/降序切换 | StatisticsService.get_ranking() |
| BR-STA-004 | 总分排名需要计算学生所有科目总分 | StatisticsService.get_total_ranking() |

### 4.3 分数分布统计

```python
# 分数段划分
score_distribution = {
    "0-59": count(score < 60),
    "60-69": count(60 <= score < 70),
    "70-79": count(70 <= score < 80),
    "80-89": count(80 <= score < 90),
    "90-100": count(score >= 90)
}
```

### 4.4 查询条件处理

| 查询条件 | 处理逻辑 |
|---------|---------|
| 仅指定班级 | 统计该班级所有科目 |
| 仅指定科目 | 统计该科目所有班级 |
| 仅指定考试类型 | 统计该考试类型所有数据 |
| 班级 + 科目 | 统计该班级该科目 |
| 班级 + 科目 + 考试类型 | 精确统计 |
| 无条件 | 统计所有数据 |

---

## 5. 验收标准

### 5.1 功能验收

| 验收项 | 验收标准 | 测试方法 |
|-------|---------|---------|
| 平均分计算 | 计算结果精确到小数点后2位 | 单元测试 |
| 最高分查询 | 返回正确的最高分和学生信息 | API 测试 |
| 最低分查询 | 返回正确的最低分和学生信息 | API 测试 |
| 及格率计算 | 百分比精确到小数点后2位 | 单元测试 |
| 优秀率计算 | 百分比精确到小数点后2位 | 单元测试 |
| 综合报告 | 包含所有统计指标和分数分布 | API 测试 |
| 单科排名 | 排序正确，相同分数按学号排序 | API 测试 |
| 总分排名 | 总分计算正确，排序正确 | API 测试 |
| CLI 命令 | 所有 CLI 命令正常工作 | 集成测试 |

### 5.2 性能验收

| 验收项 | 验收标准 | 测试方法 |
|-------|---------|---------|
| 统计计算 | 10000 条数据统计 < 500ms | 性能测试 |
| 排名查询 | 10000 条数据排名 < 1000ms | 性能测试 |

---

## 6. 依赖关系

### 6.1 前置依赖

| 任务编号 | 任务名称 | 依赖说明 |
|---------|---------|---------|
| TASK-001 | 数据库模型实现 | 依赖 Grade 模型和 Repository |
| TASK-003 | 成绩管理 API | 依赖 GradeService 的查询功能 |

### 6.2 后续依赖

无

---

## 7. 风险与注意事项

| 风险项 | 说明 | 应对措施 |
|-------|------|---------|
| 计算精度 | 浮点数计算可能有精度问题 | 使用 Decimal 或保留2位小数 |
| 大数据量统计 | 统计大量数据可能很慢 | 使用数据库聚合函数，减少数据传输 |
| 空数据处理 | 没有成绩数据时除零错误 | 统计前检查数据是否存在 |
| 排名算法 | 大量数据排序可能慢 | 使用数据库 ORDER BY，添加索引 |

---

## 8. 工作量估算

| 子任务 | 预估工时 | 备注 |
|--------|---------|------|
| StatisticsService | 5h | 统计业务逻辑 |
| API 路由 | 3h | RESTful 接口 |
| Schema 定义 | 1h | 数据验证模式 |
| CLI 命令 | 2h | 命令行接口 |
| 单元测试 | 3h | 测试用例编写 |
| **合计** | **14h** | |

---

## 9. 输出物清单

- [ ] `src/services/statistics_service.py` - 统计业务逻辑
- [ ] `src/api/routes/statistics.py` - 统计 API 路由
- [ ] `src/schemas/statistics.py` - 统计 Schema
- [ ] `src/cli/commands/statistics_cmd.py` - 统计 CLI 命令
- [ ] `tests/unit/test_services/test_statistics_service.py` - Service 单元测试
- [ ] `tests/integration/test_api/test_statistics.py` - API 集成测试

---

> **任务状态变更记录**
> 
> | 时间 | 状态变更 | 操作人 | 备注 |
> |------|---------|--------|------|
> | 2026-06-05 | - → TODO | PMO | 任务创建 |
