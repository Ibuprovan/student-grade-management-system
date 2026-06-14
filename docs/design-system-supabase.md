# Supabase 风格设计系统

> **文档版本：** V1.0  
> **创建日期：** 2026-06-15  
> **设计师：** PM Agent  
> **文档状态：** 初稿

---

## 1. 设计理念

### 1.1 设计方向
参考 Supabase 的现代、简洁、代码优先的设计风格，打造深色主题为主、翠绿色强调的学生成绩管理系统界面。

### 1.2 设计原则
- **现代简洁**：去除冗余装饰，突出内容本身
- **代码优先**：为开发者和教务人员提供清晰的数据展示
- **深色主题**：减少视觉疲劳，提升专业感
- **翠绿强调**：使用翠绿色作为主要强调色，体现活力与信任

---

## 2. 设计令牌（Design Tokens）

### 2.1 颜色系统

#### 主色调
```scss
// 主背景色 - 深色
$bg-primary: #0f0f23;
$bg-secondary: #1a1a2e;
$bg-tertiary: #16213e;

// 强调色 - 翠绿色
$accent-primary: #3ecf8e;
$accent-light: #6ee7b7;
$accent-dark: #059669;

// 文字颜色
$text-primary: #ffffff;
$text-secondary: #94a3b8;
$text-tertiary: #64748b;
$text-muted: #475569;

// 边框颜色
$border-primary: #1e293b;
$border-secondary: #334155;
$border-accent: rgba(62, 207, 142, 0.3);
```

#### 语义颜色
```scss
// 状态颜色
$success: #10b981;
$warning: #f59e0b;
$error: #ef4444;
$info: #3b82f6;

// 状态背景色
$success-bg: rgba(16, 185, 129, 0.1);
$warning-bg: rgba(245, 158, 11, 0.1);
$error-bg: rgba(239, 68, 68, 0.1);
$info-bg: rgba(59, 130, 246, 0.1);
```

#### 渐变色
```scss
// 主渐变
$gradient-primary: linear-gradient(135deg, #3ecf8e 0%, #059669 100%);
$gradient-accent: linear-gradient(135deg, #6ee7b7 0%, #3ecf8e 100%);

// 背景渐变
$gradient-bg: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%);
```

### 2.2 字体系统

#### 字体家族
```scss
// 主字体 - 现代无衬线字体
$font-sans: 'Geist Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', 
            'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 
            'Helvetica Neue', Helvetica, Arial, sans-serif;

// 代码字体 - 等宽字体
$font-mono: 'Geist Mono', 'SF Mono', 'Fira Code', 'Fira Mono', 
            'Roboto Mono', 'Courier New', monospace;
```

#### 字体大小
```scss
// 字体大小比例
$text-xs: 0.75rem;    // 12px
$text-sm: 0.875rem;   // 14px
$text-base: 1rem;     // 16px
$text-lg: 1.125rem;   // 18px
$text-xl: 1.25rem;    // 20px
$text-2xl: 1.5rem;    // 24px
$text-3xl: 1.875rem;  // 30px
$text-4xl: 2.25rem;   // 36px
```

#### 字体粗细
```scss
$font-light: 300;
$font-normal: 400;
$font-medium: 500;
$font-semibold: 600;
$font-bold: 700;
```

### 2.3 间距系统

#### 间距比例
```scss
$space-1: 0.25rem;   // 4px
$space-2: 0.5rem;    // 8px
$space-3: 0.75rem;   // 12px
$space-4: 1rem;      // 16px
$space-5: 1.25rem;   // 20px
$space-6: 1.5rem;    // 24px
$space-8: 2rem;      // 32px
$space-10: 2.5rem;   // 40px
$space-12: 3rem;     // 48px
$space-16: 4rem;     // 64px
```

### 2.4 圆角系统

```scss
$rounded-none: 0;
$rounded-sm: 0.25rem;   // 4px
$rounded-md: 0.5rem;    // 8px
$rounded-lg: 0.75rem;   // 12px
$rounded-xl: 1rem;      // 16px
$rounded-2xl: 1.5rem;   // 24px
$rounded-full: 9999px;
```

### 2.5 阴影系统

```scss
// 阴影效果
$shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
$shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 
            0 2px 4px -2px rgba(0, 0, 0, 0.1);
$shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 
            0 4px 6px -4px rgba(0, 0, 0, 0.1);
$shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 
            0 8px 10px -6px rgba(0, 0, 0, 0.1);

// 发光效果
$glow-sm: 0 0 10px rgba(62, 207, 142, 0.3);
$glow-md: 0 0 20px rgba(62, 207, 142, 0.4);
$glow-lg: 0 0 30px rgba(62, 207, 142, 0.5);
```

### 2.6 过渡动画

```scss
// 过渡时间
$transition-fast: 150ms ease;
$transition-normal: 250ms ease;
$transition-slow: 350ms ease;

// 过渡属性
$transition-colors: color 150ms ease, 
                    background-color 150ms ease, 
                    border-color 150ms ease;
$transition-shadow: box-shadow 250ms ease;
$transition-transform: transform 250ms ease;
```

---

## 3. 组件设计规范

### 3.1 按钮（Button）

#### 主要按钮
```scss
.btn-primary {
  background: $gradient-primary;
  color: $text-primary;
  border: none;
  border-radius: $rounded-md;
  padding: $space-2 $space-4;
  font-weight: $font-medium;
  transition: $transition-shadow;
  
  &:hover {
    box-shadow: $glow-md;
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
}
```

#### 次要按钮
```scss
.btn-secondary {
  background: transparent;
  color: $accent-primary;
  border: 1px solid $accent-primary;
  border-radius: $rounded-md;
  padding: $space-2 $space-4;
  font-weight: $font-medium;
  transition: $transition-colors;
  
  &:hover {
    background: rgba(62, 207, 142, 0.1);
  }
}
```

#### 幽灵按钮
```scss
.btn-ghost {
  background: transparent;
  color: $text-secondary;
  border: 1px solid $border-secondary;
  border-radius: $rounded-md;
  padding: $space-2 $space-4;
  font-weight: $font-medium;
  transition: $transition-colors;
  
  &:hover {
    color: $text-primary;
    border-color: $text-secondary;
  }
}
```

### 3.2 输入框（Input）

```scss
.input {
  background: $bg-tertiary;
  color: $text-primary;
  border: 1px solid $border-primary;
  border-radius: $rounded-md;
  padding: $space-2 $space-3;
  transition: $transition-colors;
  
  &:focus {
    outline: none;
    border-color: $accent-primary;
    box-shadow: 0 0 0 3px rgba(62, 207, 142, 0.2);
  }
  
  &::placeholder {
    color: $text-muted;
  }
}
```

### 3.3 卡片（Card）

```scss
.card {
  background: $bg-secondary;
  border: 1px solid $border-primary;
  border-radius: $rounded-lg;
  padding: $space-6;
  transition: $transition-shadow;
  
  &:hover {
    box-shadow: $shadow-lg;
    border-color: $border-accent;
  }
}
```

### 3.4 表格（Table）

```scss
.table {
  width: 100%;
  border-collapse: collapse;
  background: $bg-secondary;
  border-radius: $rounded-lg;
  overflow: hidden;
  
  th {
    background: $bg-tertiary;
    color: $text-secondary;
    font-weight: $font-semibold;
    text-align: left;
    padding: $space-3 $space-4;
    border-bottom: 1px solid $border-primary;
    font-size: $text-sm;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  td {
    color: $text-primary;
    padding: $space-3 $space-4;
    border-bottom: 1px solid $border-primary;
    font-size: $text-sm;
  }
  
  tr:hover {
    background: rgba(62, 207, 142, 0.05);
  }
}
```

### 3.5 侧边栏（Sidebar）

```scss
.sidebar {
  background: $bg-primary;
  border-right: 1px solid $border-primary;
  width: 250px;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 100;
  
  .logo {
    padding: $space-6;
    border-bottom: 1px solid $border-primary;
    
    img {
      height: 32px;
    }
  }
  
  .nav-item {
    display: flex;
    align-items: center;
    padding: $space-3 $space-4;
    color: $text-secondary;
    transition: $transition-colors;
    
    &:hover {
      background: rgba(62, 207, 142, 0.1);
      color: $text-primary;
    }
    
    &.active {
      background: rgba(62, 207, 142, 0.2);
      color: $accent-primary;
      border-right: 3px solid $accent-primary;
    }
  }
}
```

### 3.6 头部（Header）

```scss
.header {
  background: $bg-secondary;
  border-bottom: 1px solid $border-primary;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 $space-6;
  
  .user-info {
    display: flex;
    align-items: center;
    gap: $space-3;
    
    .avatar {
      width: 32px;
      height: 32px;
      border-radius: $rounded-full;
      background: $gradient-primary;
      display: flex;
      align-items: center;
      justify-content: center;
      color: $text-primary;
      font-weight: $font-semibold;
    }
  }
}
```

### 3.7 统计卡片（Stat Card）

```scss
.stat-card {
  background: $bg-secondary;
  border: 1px solid $border-primary;
  border-radius: $rounded-lg;
  padding: $space-6;
  
  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: $rounded-lg;
    background: rgba(62, 207, 142, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: $space-4;
    
    svg {
      color: $accent-primary;
    }
  }
  
  .stat-value {
    font-size: $text-3xl;
    font-weight: $font-bold;
    color: $text-primary;
    margin-bottom: $space-2;
  }
  
  .stat-label {
    font-size: $text-sm;
    color: $text-secondary;
  }
}
```

### 3.8 标签（Tag）

```scss
.tag {
  display: inline-flex;
  align-items: center;
  padding: $space-1 $space-2;
  border-radius: $rounded-full;
  font-size: $text-xs;
  font-weight: $font-medium;
  
  &.success {
    background: $success-bg;
    color: $success;
  }
  
  &.warning {
    background: $warning-bg;
    color: $warning;
  }
  
  &.error {
    background: $error-bg;
    color: $error;
  }
  
  &.info {
    background: $info-bg;
    color: $info;
  }
}
```

### 3.9 对话框（Dialog）

```scss
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dialog {
  background: $bg-secondary;
  border: 1px solid $border-primary;
  border-radius: $rounded-xl;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  
  .dialog-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: $space-6;
    border-bottom: 1px solid $border-primary;
    
    .dialog-title {
      font-size: $text-lg;
      font-weight: $font-semibold;
      color: $text-primary;
    }
  }
  
  .dialog-body {
    padding: $space-6;
  }
  
  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: $space-3;
    padding: $space-6;
    border-top: 1px solid $border-primary;
  }
}
```

### 3.10 分页（Pagination）

```scss
.pagination {
  display: flex;
  align-items: center;
  gap: $space-2;
  
  .page-item {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: $rounded-md;
    color: $text-secondary;
    transition: $transition-colors;
    
    &:hover {
      background: rgba(62, 207, 142, 0.1);
      color: $text-primary;
    }
    
    &.active {
      background: $accent-primary;
      color: $text-primary;
    }
    
    &.disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
}
```

---

## 4. 页面布局规范

### 4.1 整体布局
```scss
.layout {
  display: flex;
  min-height: 100vh;
  background: $bg-primary;
  
  .sidebar {
    width: 250px;
    flex-shrink: 0;
  }
  
  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    
    .header {
      height: 64px;
      flex-shrink: 0;
    }
    
    .content {
      flex: 1;
      padding: $space-6;
      overflow-y: auto;
    }
  }
}
```

### 4.2 响应式断点
```scss
$breakpoint-sm: 640px;
$breakpoint-md: 768px;
$breakpoint-lg: 1024px;
$breakpoint-xl: 1280px;
$breakpoint-2xl: 1536px;

// 移动端侧边栏隐藏
@media (max-width: $breakpoint-lg) {
  .sidebar {
    transform: translateX(-100%);
    transition: $transition-transform;
    
    &.open {
      transform: translateX(0);
    }
  }
}
```

---

## 5. 图标系统

### 5.1 图标风格
- 使用线性图标（Line Icons）
- 图标大小：16px、20px、24px
- 图标颜色：继承父元素颜色
- 图标粗细：1.5px

### 5.2 常用图标
- 导航图标：Home、Users、BookOpen、BarChart3、Settings
- 操作图标：Plus、Edit、Trash、Search、Filter
- 状态图标：Check、X、AlertTriangle、Info
- 数据图标：TrendingUp、TrendingDown、Minus

---

## 6. 动画规范

### 6.1 页面过渡
```scss
.page-enter-active,
.page-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
```

### 6.2 列表动画
```scss
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.list-move {
  transition: transform 0.3s ease;
}
```

### 6.3 微交互
```scss
// 悬停效果
.hover-lift {
  transition: $transition-shadow;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: $shadow-lg;
  }
}

// 点击效果
.click-scale {
  transition: $transition-transform;
  
  &:active {
    transform: scale(0.98);
  }
}
```

---

## 7. 可访问性

### 7.1 颜色对比度
- 主要文字对比度：≥ 4.5:1
- 次要文字对比度：≥ 3:1
- 交互元素对比度：≥ 3:1

### 7.2 焦点状态
```scss
:focus-visible {
  outline: 2px solid $accent-primary;
  outline-offset: 2px;
}
```

### 7.3 屏幕阅读器
- 使用语义化HTML标签
- 提供适当的ARIA标签
- 确保键盘导航可用

---

## 8. 实施指南

### 8.1 CSS变量定义
在 `global.scss` 中定义所有设计令牌为CSS变量，便于主题切换。

### 8.2 组件库覆盖
覆盖Element Plus的默认样式变量，使其符合Supabase风格。

### 8.3 渐进式迁移
1. 先更新全局样式和设计令牌
2. 逐个更新布局组件（侧边栏、头部）
3. 更新页面组件样式
4. 测试响应式设计

---

> **文档结束**  
> 如有疑问请联系设计团队