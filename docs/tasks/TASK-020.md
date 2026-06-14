# TASK-020

【基础信息】
状态：DONE
负责人：frontend-dev
优先级：P0

【需求描述】
将学生成绩管理系统前端UI重设计为专业教育风格，替换现有的Supabase深色主题。

设计方向：
1. 浅色主题，主背景 #f5f7fa，卡片背景纯白 #ffffff
2. 专业蓝主色调 #2563eb
3. 温和灰阶，色彩明亮、清晰、有现代感
4. 禁止暗黑模式

设计规范：
1. 配色方案：
   - 主背景：#f5f7fa
   - 卡片背景：#ffffff
   - 主色调：#2563eb（专业蓝）
   - 成功色：#10b981
   - 警告色：#f59e0b
   - 错误色：#ef4444
   - 正文文字：#1f2937
   - 辅助文字：#6b7280
   - 边框：#e5e7eb

2. 布局规范：
   - 侧边栏宽度：220px（折叠64px）
   - 主内容区最大宽度：1440px，居中
   - 卡片间距：24px
   - 内边距：20-24px
   - 无水平滚动条

3. 图表规范：
   - 图表容器高度：360px
   - 图表不超出卡片边界
   - 坐标轴标签不裁剪
   - 图例位置：bottom或right

4. 表格规范：
   - 表格占满卡片宽度
   - 合理列宽分配
   - 单元格padding：12px 16px
   - 斑马纹或悬停高亮

5. 组件规范：
   - 卡片高度对齐
   - 行高：1.5-1.6
   - 标题层级：h1 24px, h2 20px, h3 16px
   - 图标与文字对齐

【输入依赖文件】
- frontend/src/assets/styles/variables.scss
- frontend/src/assets/styles/global.scss
- frontend/src/assets/styles/element-override.scss
- frontend/src/components/layout/AppSidebar.vue
- frontend/src/components/layout/AppHeader.vue
- frontend/src/components/layout/AppLayout.vue
- frontend/src/views/dashboard/Dashboard.vue
- frontend/src/views/student/StudentList.vue
- frontend/src/views/grade/GradeList.vue

【验收标准】
1. 浅色主题，禁止暗黑模式
2. 专业蓝 #2563eb 为主色调
3. 侧边栏220px，主内容区1440px最大宽度居中
4. 图表360px高度，不超出边界
5. 表格占满宽度，合理列宽
6. 卡片高度对齐，间距统一24px
7. 所有页面显示正常，无重叠无溢出
8. 响应式设计正常

【流转记录】
- [2026-06-15] PMO 创建任务 -> TODO
- [2026-06-15] PMO 开始执行 -> IN_PROGRESS
- [2026-06-15] PMO 完成阶段1：设计系统定义 -> IN_PROGRESS
- [2026-06-15] PMO 完成阶段2：组件重构 -> IN_PROGRESS
- [2026-06-15] PMO 完成阶段3：测试验证 -> IN_PROGRESS
- [2026-06-15] PMO 提交审查 -> REVIEWS
- [2026-06-15] Reviewer 审查通过 -> TESTING
- [2026-06-15] QA 测试通过 -> DONE