<template>
  <div class="dashboard">
    <div class="page-header">
      <h1 class="page-title">仪表盘</h1>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-cards">
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
      <el-row :gutter="16">
        <el-col :xs="12" :sm="8" :md="6">
          <button class="quick-action" @click="router.push('/student/add')">
            <div class="quick-action__icon quick-action__icon--primary">
              <el-icon :size="22"><UserPlus /></el-icon>
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
.dashboard {
  animation: fadeIn 0.3s ease;
}

// ===== 统计卡片 =====
.stat-cards {
  margin-bottom: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 22px 24px;
  background: var(--surface-color);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color-light);
  box-shadow: var(--shadow-xs);
  margin-bottom: 16px;
  transition: all var(--transition-duration);

  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-sm);
  }

  &__icon {
    width: 52px;
    height: 52px;
    border-radius: 14px;
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
    font-size: 28px;
    font-weight: 700;
    color: var(--text-color);
    line-height: 1.2;
    min-height: 34px;
    display: flex;
    align-items: center;
    letter-spacing: -0.02em;
  }

  &__label {
    font-size: 13px;
    color: var(--text-color-secondary);
    margin-top: 4px;
    font-weight: 500;
  }

  &--primary .stat-card__icon {
    background: linear-gradient(135deg, #2A9D8F, #3BBFA0);
  }

  &--success .stat-card__icon {
    background: linear-gradient(135deg, #52B788, #6CC49A);
  }

  &--warning .stat-card__icon {
    background: linear-gradient(135deg, #E9A23B, #F0B860);
  }

  &--accent .stat-card__icon {
    background: linear-gradient(135deg, #E06469, #E88286);
  }
}

// ===== 错误提示 =====
.error-alert {
  margin-bottom: 16px;
  border-radius: var(--border-radius-md);
}

// ===== 区块标题 =====
.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 18px;
}

// ===== 快捷操作 =====
.quick-section {
  margin-bottom: 16px;
}

.quick-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 20px 12px;
  background: var(--bg-color);
  border: 1px solid var(--border-color-light);
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-bottom: 12px;

  &:hover {
    background: var(--surface-color);
    border-color: var(--primary-color);
    box-shadow: var(--shadow-sm);
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }

  &__icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;

    &--primary { background: linear-gradient(135deg, #2A9D8F, #3BBFA0); }
    &--success { background: linear-gradient(135deg, #52B788, #6CC49A); }
    &--warning { background: linear-gradient(135deg, #E9A23B, #F0B860); }
    &--accent { background: linear-gradient(135deg, #E06469, #E88286); }
  }

  &__label {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-color);
  }
}

// ===== 功能介绍 =====
.welcome-section {
  .welcome-desc {
    color: var(--text-color-secondary);
    line-height: 1.7;
    margin-bottom: 24px;
    font-size: 14px;
  }
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 20px;
  background: var(--bg-color);
  border-radius: var(--border-radius-lg);
  transition: all var(--transition-fast);

  &:hover {
    background: var(--primary-lighter);
  }
}

.feature-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #fff;

  &--primary { background: linear-gradient(135deg, #2A9D8F, #3BBFA0); }
  &--success { background: linear-gradient(135deg, #52B788, #6CC49A); }
  &--warning { background: linear-gradient(135deg, #E9A23B, #F0B860); }
}

.feature-content {
  h4 {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-color);
    margin: 0 0 4px;
  }

  p {
    font-size: 13px;
    color: var(--text-color-secondary);
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
