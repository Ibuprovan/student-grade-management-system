# TASK-014: 后端性能优化

> **创建日期：** 2026-06-07  
> **负责人：** backend-dev  
> **优先级：** P1 (重要功能)  
> **状态：** DONE

---

## 1. 任务概述

### 1.1 任务描述

修复后端代码中的性能问题，包括搜索学生时的内存分页和班级列表获取的低效方式。

### 1.2 关联需求

| 需求编号 | 需求名称 | 来源文档 |
|---------|---------|---------|
| CODE-001 | 搜索学生性能问题 | comprehensive-check-report.md |
| CODE-002 | 班级列表获取低效 | comprehensive-check-report.md |

---

## 2. 详细任务清单

### 2.1 搜索学生优化

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 1.1 | 重构 search_students | `src/services/student_service.py` | 将内存分页改为数据库分页 | TODO |
| 1.2 | 更新 Repository | `src/repositories/student_repo.py` | 添加支持分页的搜索方法 | TODO |

### 2.2 班级列表接口

| 序号 | 子任务 | 文件路径 | 说明 | 状态 |
|-----|--------|---------|------|------|
| 2.1 | 添加班级列表接口 | `src/api/routes/students.py` | GET /api/v1/students/classes | TODO |
| 2.2 | 添加 Repository 方法 | `src/repositories/student_repo.py` | 获取去重的班级列表 | TODO |

---

## 3. 技术规范

### 3.1 搜索学生优化

**当前问题：**
```python
# 先获取所有匹配记录到内存
all_students = self.repo.search(keyword=keyword, skip=0, limit=10000)
# 再在 Python 中分页
students = all_students[skip:skip + page_size]
```

**优化方案：**
```python
# 直接在数据库层面分页
students = self.repo.search(keyword=keyword, skip=skip, limit=page_size)
total = self.repo.count_search(keyword=keyword)
```

### 3.2 班级列表接口

```
GET /api/v1/students/classes
Response: { "success": true, "data": ["2026级1班", "2026级2班", ...] }
```

---

## 4. 验收标准

| 验收项 | 验收标准 |
|-------|---------|
| 搜索性能 | 搜索学生时不会加载所有记录到内存 |
| 分页正确 | 搜索结果的分页信息准确 |
| 班级列表 | 专门的班级列表接口正常工作 |

---

## 5. 工作量估算

| 子任务 | 预估工时 |
|--------|---------|
| 搜索学生优化 | 2h |
| 班级列表接口 | 1h |
| 测试验证 | 1h |
| **合计** | **4h** |

---

> **任务状态变更记录**
> 
> | 时间 | 状态变更 | 操作人 | 备注 |
> |------|---------|--------|------|
> | 2026-06-07 | - → TODO | PMO | 任务创建 |
