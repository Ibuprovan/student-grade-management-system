<template>
  <div class="sl-dashboard page-container">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">学科仪表盘</h1>
        <span class="page-subtitle" v-if="stats.subject">{{ stats.subject }}</span>
      </div>
      <div class="header-filters">
        <el-select v-model="examType" placeholder="考试类型" clearable style="width: 140px" @change="fetchData">
          <el-option v-for="t in examTypes" :key="t" :label="t" :value="t" />
        </el-select>
      </div>
    </div>

    <el-row :gutter="16" class="overview-cards">
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--primary">
          <div class="overview-value">{{ stats.total_students ?? '-' }}</div>
          <div class="overview-label">学生总数</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--info">
          <div class="overview-value">{{ stats.total_grades ?? '-' }}</div>
          <div class="overview-label">成绩记录</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--success">
          <div class="overview-value">{{ formatNum(stats.average_score) }}</div>
          <div class="overview-label">平均分</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--warning">
          <div class="overview-value">{{ formatPercent(stats.pass_rate) }}</div>
          <div class="overview-label">及格率</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--accent">
          <div class="overview-value">{{ formatPercent(stats.excellent_rate) }}</div>
          <div class="overview-label">优秀率</div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getSlDashboard } from '@/api/subjectLeader'
import { EXAM_TYPES } from '@/types/grade'

const examTypes = EXAM_TYPES
const examType = ref('')
const stats = ref<Record<string, unknown>>({})

function formatNum(v: unknown) { return v == null ? '-' : Number(v).toFixed(1) }
function formatPercent(v: unknown) { return v == null ? '-' : Number(v).toFixed(1) + '%' }

async function fetchData() {
  try {
    const params: Record<string, string> = {}
    if (examType.value) params.exam_type = examType.value
    const res = await getSlDashboard(params)
    if (res?.data) stats.value = res.data as Record<string, unknown>
  } catch (e) { console.error('获取仪表盘数据失败:', e) }
}

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.sl-dashboard {
  animation: fadeIn 0.3s ease;
  .page-header {
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    .header-left { display: flex; align-items: baseline; gap: 12px; }
    .header-filters { display: flex; gap: 12px; align-items: center; }
  }
  .page-title { margin: 0; font-size: 22px; font-weight: 700; }
  .page-subtitle { font-size: 16px; color: var(--text-color-secondary); font-weight: 500; }
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
    .overview-value { font-size: 28px; font-weight: 700; line-height: 1.2; min-height: 34px; }
    .overview-label { font-size: 13px; color: var(--text-color-secondary); margin-top: 6px; font-weight: 500; }
    &--primary .overview-value { color: #409EFF; }
    &--info .overview-value { color: #909399; }
    &--success .overview-value { color: #67C23A; }
    &--warning .overview-value { color: #E6A23C; }
    &--accent .overview-value { color: #F56C6C; }
  }
}
</style>
