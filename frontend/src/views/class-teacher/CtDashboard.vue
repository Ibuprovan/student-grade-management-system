<template>
  <div class="ct-dashboard page-container">
    <div class="page-header">
      <h1 class="page-title">班级仪表盘</h1>
    </div>

    <el-row :gutter="16" class="overview-cards">
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--primary">
          <div class="overview-value">{{ stats.total_students ?? '-' }}</div>
          <div class="overview-label">班级学生总数</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--info">
          <div class="overview-value">{{ stats.total_grades ?? '-' }}</div>
          <div class="overview-label">成绩记录条数</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--success">
          <div class="overview-value">{{ formatNum(stats.average_score) }}</div>
          <div class="overview-label">班级平均分</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--warning">
          <div class="overview-value">{{ formatPercent(stats.pass_rate) }}</div>
          <div class="overview-label">班级及格率</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--accent">
          <div class="overview-value">{{ formatPercent(stats.excellent_rate) }}</div>
          <div class="overview-label">班级优秀率</div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getCtDashboard } from '@/api/classTeacher'

const stats = ref<Record<string, unknown>>({})

function formatNum(v: unknown): string {
  if (v === null || v === undefined) return '-'
  return Number(v).toFixed(1)
}

function formatPercent(v: unknown): string {
  if (v === null || v === undefined) return '-'
  return Number(v).toFixed(1) + '%'
}

async function fetchDashboard() {
  try {
    const res = await getCtDashboard()
    if (res?.data) {
      stats.value = res.data as Record<string, unknown>
    }
  } catch (e) {
    console.error('获取仪表盘数据失败:', e)
  }
}

onMounted(() => {
  fetchDashboard()
})
</script>

<style lang="scss" scoped>
.ct-dashboard {
  animation: fadeIn 0.3s ease;

  .page-header {
    margin-bottom: 20px;
    .page-title { margin: 0; font-size: 22px; font-weight: 700; }
  }

  .overview-cards { margin-bottom: 16px; }

  .overview-card {
    padding: 20px 24px;
    background: var(--surface-color);
    border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-color-light);
    box-shadow: var(--shadow-xs);
    margin-bottom: 16px;
    text-align: center;
    transition: all var(--transition-duration);

    &:hover { transform: translateY(-2px); box-shadow: var(--shadow-sm); }
    .overview-value { font-size: 28px; font-weight: 700; color: var(--text-color); line-height: 1.2; min-height: 34px; }
    .overview-label { font-size: 13px; color: var(--text-color-secondary); margin-top: 6px; font-weight: 500; }

    &--primary .overview-value { color: #409EFF; }
    &--info .overview-value { color: #909399; }
    &--success .overview-value { color: #67C23A; }
    &--warning .overview-value { color: #E6A23C; }
    &--accent .overview-value { color: #F56C6C; }
  }
}
</style>
