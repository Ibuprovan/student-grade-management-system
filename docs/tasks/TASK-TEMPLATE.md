# TASK-TEMPLATE

## 基本信息

| 字段 | 值 |
|------|-----|
| ID | TASK-XXX |
| 标题 | <任务标题> |
| 创建时间 | YYYY-MM-DD HH:MM |
| 负责人 | @agent-name |
| 优先级 | P0 / P1 / P2 / P3 |

## 状态流转

```
TODO → IN_PROGRESS → REVIEWS → DONE
                     ↑
                (拒绝 ≤ 3 次)     ↓ (拒绝 > 3 次)
              backend-dev 修正    BLOCKED (唤醒 architect 仲裁)
```

**当前状态：** TODO

## 任务描述

<详细描述任务需求>

## 验收标准

- [ ] 标准 1
- [ ] 标准 2
- [ ] 标准 3

## 关联文档

- PRD: `docs/prd.md`
- 架构: `docs/architecture.md`
- API: `docs/api-spec.md`

## 变更记录

| 时间 | 操作人 | 状态变更 | 备注 |
|------|--------|----------|------|
| - | - | - | - |
