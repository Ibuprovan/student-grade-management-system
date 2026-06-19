<template>
  <div class="t-statistics page-container">
    <div class="page-header">
      <h1 class="page-title">统计概览</h1>
      <div class="header-actions">
        <el-select v-model="filterExamType" placeholder="考试类型" clearable style="width: 140px" @change="fetchData">
          <el-option v-for="t in examTypes" :key="t" :label="t" :value="t" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="fetchData">
          <el-icon><Search /></el-icon>查询
        </el-button>
      </div>
    </div>

    <div v-for="(stat, idx) in stats" :key="idx" class="stat-section">
      <h3 class="section-title">{{ stat.subject }} — {{ stat.class_name }}</h3>

      <!-- 概览卡片 -->
      <div class="overview-cards">
        <div class="overview-card overview-card--primary">
          <div class="overview-value">{{ stat.student_count }}</div>
          <div class="overview-label">学生总数</div>
        </div>
        <div class="overview-card overview-card--info">
          <div class="overview-value">{{ stat.reference_count }}</div>
          <div class="overview-label">参考人数</div>
        </div>
        <div class="overview-card overview-card--success">
          <div class="overview-value">{{ formatNum(stat.average_score) }}</div>
          <div class="overview-label">平均分</div>
        </div>
        <div class="overview-card overview-card--info">
          <div class="overview-value">{{ formatNum(stat.max_score) }}</div>
          <div class="overview-label">最高分</div>
        </div>
        <div class="overview-card overview-card--warning">
          <div class="overview-value">{{ formatNum(stat.min_score) }}</div>
          <div class="overview-label">最低分</div>
        </div>
        <div class="overview-card overview-card--primary">
          <div class="overview-value">{{ formatPercent(stat.pass_rate) }}</div>
          <div class="overview-label">及格率</div>
        </div>
        <div class="overview-card overview-card--accent">
          <div class="overview-value">{{ formatPercent(stat.excellent_rate) }}</div>
          <div class="overview-label">优秀率</div>
        </div>
      </div>

      <!-- 图表 -->
      <el-row :gutter="16" class="chart-row">
        <el-col :xs="24" :md="12">
          <div class="page-card chart-card-wrapper">
            <h4 class="chart-title">分数分布</h4>
            <BarChart v-if="getDistData(stat).xData.length > 0" title="" :xData="getDistData(stat).xData" :yData="getDistData(stat).yData" xLabel="分数段" yLabel="人数" color="#E6A23C" :showValue="true" :height="340" />
            <div v-else class="chart-empty">暂无数据</div>
          </div>
        </el-col>
        <el-col :xs="24" :md="12">
          <div class="page-card">
            <h4 class="chart-title">班级内排名前十</h4>
            <el-table :data="stat.top10" border stripe size="small" :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }">
              <el-table-column prop="rank" label="名次" width="70" align="center" />
              <el-table-column prop="student_id" label="学号" min-width="110" />
              <el-table-column prop="student_name" label="姓名" min-width="100" />
              <el-table-column prop="score" label="分数" min-width="80" align="center">
                <template #default="{ row }">
                  <span :style="{ color: getScoreColor(row.score), fontWeight: 600 }">{{ row.score }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getTStatistics } from '@/api/teacher'
import { EXAM_TYPES } from '@/types/grade'
import BarChart from '@/components/chart/BarChart.vue'

interface StatItem {
  subject: string
  class_name: string
  student_count: number
  grade_count: number
  reference_count: number
  average_score: number
  max_score: number
  min_score: number
  pass_rate: number
  excellent_rate: number
  distribution: Record<string, number>
  top10: Array<{ rank: number; student_id: string; student_name: string; score: number }>
}

const examTypes = EXAM_TYPES
const loading = ref(false)
const filterExamType = ref('')
const stats = ref<StatItem[]>([])

function formatNum(v: unknown) { return v == null ? '-' : Number(v).toFixed(1) }
function formatPercent(v: unknown) { return v == null ? '-' : Number(v).toFixed(1) + '%' }
function getScoreColor(score: number) { return score >= 90 ? '#67c23a' : score >= 60 ? '#409eff' : '#f56c6c' }

function getDistData(stat: StatItem) {
  const dist = stat.distribution
  if (!dist) return { xData: [] as string[], yData: [] as number[] }
  return { xData: Object.keys(dist), yData: Object.values(dist) }
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getTStatistics({
      exam_type: filterExamType.value || undefined,
    })
    if (res?.data) stats.value = res.data as unknown as StatItem[]
  } catch (e) { console.error('获取统计数据失败:', e) } finally { loading.value = false }
}

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.t-statistics {
  animation: fadeIn 0.3s ease;
  .page-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
  }
  .page-title { margin: 0; font-size: 22px; font-weight: 700; }
  .header-actions { display: flex; gap: 12px; }
  .stat-section {
    margin-bottom: 32px;
    &:last-child { margin-bottom: 0; }
  }
  .section-title { font-size: 18px; font-weight: 600; color: var(--text-color); margin: 0 0 16px; }
  .overview-cards { margin-bottom: 16px; display: flex; gap: 12px; flex-wrap: wrap; }
  .overview-card {
    flex: 1; min-width: 100px; padding: 16px 12px; background: var(--surface-color); border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-color-light); box-shadow: var(--shadow-xs);
    text-align: center; transition: all var(--transition-duration);
    &:hover { transform: translateY(-2px); box-shadow: var(--shadow-sm); }
    .overview-value { font-size: 20px; font-weight: 700; line-height: 1.2; min-height: 26px; }
    .overview-label { font-size: 12px; color: var(--text-color-secondary); margin-top: 4px; font-weight: 500; }
    &--primary .overview-value { color: #409EFF; }
    &--info .overview-value { color: #909399; }
    &--success .overview-value { color: #67C23A; }
    &--warning .overview-value { color: #E6A23C; }
    &--accent .overview-value { color: #F56C6C; }
  }
  .chart-row { margin-bottom: 16px; }
  .chart-card-wrapper { overflow: hidden; display: flex; flex-direction: column; flex: 1; }
  .chart-title { font-size: 16px; font-weight: 600; color: var(--text-color); margin: 0 0 16px; }
  .chart-empty { height: 340px; display: flex; align-items: center; justify-content: center; color: var(--text-color-secondary); }
  :deep(.chart-row) { .el-col { display: flex; flex-direction: column; > .page-card { flex: 1; display: flex; flex-direction: column; } } }
}
</style>
