<template>
  <div class="dashboard">
    <div class="page-header">
      <h1 class="page-title">仪表盘</h1>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="24" class="stat-cards">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-card--primary">
          <div class="stat-card__icon">
            <el-icon :size="28"><User /></el-icon>
          </div>
          <div class="stat-card__content">
            <div class="stat-card__value">
              <el-skeleton v-if="loading" :rows="1" animated />
              <template v-else>{{ stats.total_students }}</template>
            </div>
            <div class="stat-card__label">学生总数</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-card--success">
          <div class="stat-card__icon">
            <el-icon :size="28"><Document /></el-icon>
          </div>
          <div class="stat-card__content">
            <div class="stat-card__value">
              <el-skeleton v-if="loading" :rows="1" animated />
              <template v-else>{{ stats.total_grades }}</template>
            </div>
            <div class="stat-card__label">成绩记录</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-card--warning">
          <div class="stat-card__icon">
            <el-icon :size="28"><TrendCharts /></el-icon>
          </div>
          <div class="stat-card__content">
            <div class="stat-card__value">
              <el-skeleton v-if="loading" :rows="1" animated />
              <template v-else>{{ stats.average_score }}</template>
            </div>
            <div class="stat-card__label">平均分</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-card--accent">
          <div class="stat-card__icon">
            <el-icon :size="28"><DataAnalysis /></el-icon>
          </div>
          <div class="stat-card__content">
            <div class="stat-card__value">
              <el-skeleton v-if="loading" :rows="1" animated />
              <template v-else>{{ stats.pass_rate }}%</template>
            </div>
            <div class="stat-card__label">及格率</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 错误提示 -->
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      closable
      @close="error = null"
      class="error-alert"
    />

    <!-- 快捷操作 -->
    <div class="page-card quick-section">
      <h3 class="section-title">快捷操作</h3>
      <el-row :gutter="24">
        <el-col :xs="12" :sm="8" :md="6">
          <button class="quick-action" @click="router.push('/student/add')">
            <div class="quick-action__icon quick-action__icon--primary">
              <el-icon :size="22"><CirclePlus /></el-icon>
            </div>
            <span class="quick-action__label">添加学生</span>
          </button>
        </el-col>
        <el-col :xs="12" :sm="8" :md="6">
          <button class="quick-action" @click="router.push('/grade/input')">
            <div class="quick-action__icon quick-action__icon--success">
              <el-icon :size="22"><Edit /></el-icon>
            </div>
            <span class="quick-action__label">录入成绩</span>
          </button>
        </el-col>
        <el-col :xs="12" :sm="8" :md="6">
          <button class="quick-action" @click="router.push('/grade/import')">
            <div class="quick-action__icon quick-action__icon--warning">
              <el-icon :size="22"><Upload /></el-icon>
            </div>
            <span class="quick-action__label">导入成绩</span>
          </button>
        </el-col>
        <el-col :xs="12" :sm="8" :md="6">
          <button class="quick-action" @click="router.push('/statistics/overview')">
            <div class="quick-action__icon quick-action__icon--accent">
              <el-icon :size="22"><DataAnalysis /></el-icon>
            </div>
            <span class="quick-action__label">查看统计</span>
          </button>
        </el-col>
      </el-row>
    </div>

    <!-- 功能介绍 -->
    <div class="page-card welcome-section">
      <h3 class="section-title">欢迎使用学生成绩管理系统</h3>
      <p class="welcome-desc">本系统提供学生成绩的录入、查询、统计分析等功能，帮助教师高效管理学生成绩数据。</p>
      <div class="feature-grid">
        <div class="feature-item">
          <div class="feature-icon feature-icon--primary">
            <el-icon :size="24"><User /></el-icon>
          </div>
          <div class="feature-content">
            <h4>学生管理</h4>
            <p>管理学生基本信息，支持增删改查</p>
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-icon feature-icon--success">
            <el-icon :size="24"><Document /></el-icon>
          </div>
          <div class="feature-content">
            <h4>成绩管理</h4>
            <p>录入、导入、查询学生成绩</p>
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-icon feature-icon--warning">
            <el-icon :size="24"><DataAnalysis /></el-icon>
          </div>
          <div class="feature-content">
            <h4>统计分析</h4>
            <p>多维度统计分析，数据可视化</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDashboardStore } from '@/stores/dashboard'

const router = useRouter()
const dashboardStore = useDashboardStore()

/** 统计数据 */
const stats = computed(() => dashboardStore.stats)

/** 加载状态 */
const loading = computed(() => dashboardStore.loading)

/** 错误信息 */
const error = computed({
  get: () => dashboardStore.error,
  set: (val: string | null) => {
    if (val === null) {
      dashboardStore.error = null
    }
  },
})

/** 组件挂载时获取数据 */
onMounted(() => {
  dashboardStore.fetchDashboardStats()
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables.scss' as *;

.dashboard {
  animation: fadeIn 0.3s ease;
}

// ===== 统计卡片 =====
.stat-cards {
  margin-bottom: $space-6;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: $space-4;
  padding: $space-5 $space-6;
  background: $bg-secondary;
  border-radius: $rounded-lg;
  border: 1px solid $border-primary;
  box-shadow: $shadow-sm;
  margin-bottom: $space-6;
  transition: all $transition-normal;

  &:hover {
    transform: translateY(-2px);
    box-shadow: $shadow-lg;
    border-color: $border-accent;
  }

  &__icon {
    width: 52px;
    height: 52px;
    border-radius: $rounded-xl;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    flex-shrink: 0;
  }

  &__content {
    flex: 1;
    min-width: 0;
  }

  &__value {
    font-size: $text-3xl;
    font-weight: $font-bold;
    color: $text-primary;
    line-height: 1.2;
    min-height: 34px;
    display: flex;
    align-items: center;
    letter-spacing: -0.02em;
  }

  &__label {
    font-size: $text-sm;
    color: $text-secondary;
    margin-top: $space-1;
    font-weight: $font-medium;
  }

  &--primary .stat-card__icon {
    background: $gradient-primary;
  }

  &--success .stat-card__icon {
    background: linear-gradient(135deg, #10b981, #34d399);
  }

  &--warning .stat-card__icon {
    background: linear-gradient(135deg, #f59e0b, #fbbf24);
  }

  &--accent .stat-card__icon {
    background: linear-gradient(135deg, #ef4444, #f87171);
  }
}

// ===== 错误提示 =====
.error-alert {
  margin-bottom: $space-4;
  border-radius: $rounded-md;
}

// ===== 区块标题 =====
.section-title {
  font-size: $text-xl;
  font-weight: $font-semibold;
  color: $text-primary;
  margin-bottom: $space-4;
}

// ===== 快捷操作 =====
.quick-section {
  margin-bottom: $space-6;
}

.quick-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $space-3;
  width: 100%;
  padding: $space-5 $space-3;
  background: $bg-tertiary;
  border: 1px solid $border-primary;
  border-radius: $rounded-lg;
  cursor: pointer;
  transition: all $transition-fast;
  margin-bottom: $space-3;

  &:hover {
    background: $bg-secondary;
    border-color: $accent-primary;
    box-shadow: $glow-sm;
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }

  &__icon {
    width: 44px;
    height: 44px;
    border-radius: $rounded-lg;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;

    &--primary { background: $gradient-primary; }
    &--success { background: linear-gradient(135deg, #10b981, #34d399); }
    &--warning { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
    &--accent { background: linear-gradient(135deg, #ef4444, #f87171); }
  }

  &__label {
    font-size: $text-sm;
    font-weight: $font-medium;
    color: $text-primary;
  }
}

// ===== 功能介绍 =====
.welcome-section {
  .welcome-desc {
    color: $text-secondary;
    line-height: 1.7;
    margin-bottom: $space-6;
    font-size: $text-sm;
  }
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $space-4;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: $space-4;
  padding: $space-5;
  background: $bg-tertiary;
  border-radius: $rounded-lg;
  transition: all $transition-fast;

  &:hover {
    background: rgba(37, 99, 235, 0.1);
  }
}

.feature-icon {
  width: 44px;
  height: 44px;
  border-radius: $rounded-lg;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #fff;

  &--primary { background: $gradient-primary; }
  &--success { background: linear-gradient(135deg, #10b981, #34d399); }
  &--warning { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
}

.feature-content {
  h4 {
    font-size: $text-base;
    font-weight: $font-semibold;
    color: $text-primary;
    margin: 0 0 $space-1;
  }

  p {
    font-size: $text-sm;
    color: $text-secondary;
    margin: 0;
    line-height: 1.5;
  }
}

// ===== 响应式 =====
@media (max-width: 768px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .stat-card:hover {
    transform: none;
  }
  
  .quick-action:hover {
    transform: none;
  }
}
</style>