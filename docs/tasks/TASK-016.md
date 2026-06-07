# TASK-016: 安全增强 - 速率限制与批量限制

> **创建日期：** 2026-06-07  
> **负责人：** backend-dev  
> **优先级：** P2 (建议改进)  
> **状态：** DONE

---

## 1. 任务概述

### 1.1 任务描述

添加请求速率限制和批量操作数量限制，防止暴力攻击和资源耗尽。

### 1.2 关联需求

| 需求编号 | 需求名称 | 来源文档 |
|---------|---------|---------|
| SEC-005 | 批量操作无数量限制 | comprehensive-check-report.md |
| A04 | 不安全设计 | security-report.md |

---

## 2. 详细任务清单

### 2.1 速率限制

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 1.1 | 安装 slowapi | `requirements.txt` | 添加速率限制依赖 | TODO |
| 1.2 | 配置速率限制 | `src/main.py` | 全局速率限制配置 | TODO |
| 1.3 | 登录接口限制 | `src/api/routes/auth.py` | 登录接口 10次/分钟 | TODO |

### 2.2 批量操作限制

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 2.1 | 限制批量成绩数量 | `src/schemas/grade.py` | GradeBatchCreate 限制最大 500 条 | TODO |
| 2.2 | 添加分页参数上限 | `src/api/routes/grades.py` | page_size 最大 100 | TODO |

---

## 3. 技术规范

### 3.1 速率限制配置

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("10/minute")
def login(...):
    ...
```

### 3.2 批量限制

```python
class GradeBatchCreate(BaseModel):
    grades: List[GradeItem] = Field(..., max_length=500)
```

---

## 4. 验收标准

| 验收项 | 验收标准 |
|-------|---------|
| 速率限制 | 登录接口每分钟最多 10 次请求 |
| 批量限制 | 批量成绩最多 500 条 |
| 错误提示 | 超限时返回友好的错误信息 |

---

## 5. 工作量估算

| 子任务 | 预估工时 |
|--------|---------|
| 速率限制 | 2h |
| 批量限制 | 1h |
| 测试验证 | 1h |
| **合计** | **4h** |

---

> **任务状态变更记录**
> 
> | 时间 | 状态变更 | 操作人 | 备注 |
> |------|---------|--------|------|
> | 2026-06-07 | - → TODO | PMO | 任务创建 |
