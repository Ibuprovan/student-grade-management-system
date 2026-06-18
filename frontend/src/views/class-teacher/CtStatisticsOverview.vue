<template>
  <div class="ct-stats-overview page-container">
    <div class="page-header">
      <h1 class="page-title">统计概览</h1>
      <div class="header-actions">
        <el-select v-model="filterExamType" placeholder="考试类型" clearable style="width: 140px" @change="fetchData">
          <el-option v-for="t in examTypes" :key="t" :label="t" :value="t" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="fetchData">
          <el-icon><Search /></el-icon>
          查询
        </el-button>
      </div>
    </div>

    <!-- 概览卡片 -->
    <el-row :gutter="16" class="overview-cards">
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--primary">
          <div class="overview-value">{{ data.student_count ?? '-' }}</div>
          <div class="overview-label">学生总数</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--info">
          <div class="overview-value">{{ data.exam_count ?? '-' }}</div>
          <div class="overview-label">参考人数</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--success">
          <div class="overview-value">{{ formatNum(data.avg_total_score) }}</div>
          <div class="overview-label">平均总分</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--warning">
          <div class="overview-value">{{ formatNum(data.max_total_score) }}</div>
          <div class="overview-label">最高总分</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--primary">
          <div class="overview-value">{{ formatPercent(data.total_pass_rate) }}</div>
          <div class="overview-label">及格率</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--accent">
          <div class="overview-value">{{ formatPercent(data.total_excellent_rate) }}</div>
          <div class="overview-label">优秀率</div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :md="12">
        <div class="page-card chart-card-wrapper">
          <h4 class="chart-title">总分分布</h4>
          <BarChart
            v-if="distData.xData.length > 0"
            title=""
            :xData="distData.xData"
            :yData="distData.yData"
            xLabel="分数段"
            yLabel="人数"
            color="#409EFF"
            :showValue="true"
            :height="340"
          />
          <div v-else class="chart-empty">暂无数据</div>
        </div>
      </el-col>
      <el-col :xs="24" :md="12">
        <div class="page-card chart-card-wrapper">
          <h4 class="chart-title">总分趋势</h4>
          <LineChart
            v-if="trendData.xData.length > 0"
            title=""
            :xData="trendData.xData"
            :series="trendData.series"
            xLabel="考试类型"
            yLabel="分数"
            :smooth="true"
            :showLegend="true"
            :height="340"
          />
          <div v-else class="chart-empty">暂无数据</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :md="12">
        <div class="page-card chart-card-wrapper">
          <h4 class="chart-title">各科目平均分占比</h4>
          <PieChart
            v-if="pieData.length > 0"
            :data="pieData"
            :height="340"
          />
          <div v-else class="chart-empty">暂无数据</div>
        </div>
      </el-col>
      <el-col :xs="24" :md="12">
        <div class="page-card chart-card-wrapper">
          <h4 class="chart-title">各科目能力雷达</h4>
          <RadarChart
            v-if="radarData.indicators.length > 0"
            title=""
            :indicators="radarData.indicators"
            :series="radarData.series"
            :height="340"
          />
          <div v-else class="chart-empty">暂无数据</div>
        </div>
      </el-col>
    </el-row>

    <!-- 排名表格 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :md="12">
        <div class="page-card">
          <h4 class="chart-title">总分排名前十</h4>
          <el-table :data="top10Total" border stripe size="small" :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }">
            <el-table-column prop="rank" label="名次" width="70" align="center" />
            <el-table-column prop="student_name" label="姓名" min-width="100" />
            <el-table-column prop="total_score" label="总分" min-width="100" align="center" />
          </el-table>
        </div>
      </el-col>
      <el-col :xs="24" :md="12">
        <div class="page-card">
          <h4 class="chart-title">各科排名前十</h4>
          <el-tabs v-model="activeSubjectTab" type="card">
            <el-tab-pane
              v-for="item in top10Subjects"
              :key="item.subject"
              :label="item.subject"
              :name="item.subject"
            >
              <el-table :data="item.top10" border stripe size="small" :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }">
                <el-table-column prop="rank" label="名次" width="70" align="center" />
                <el-table-column prop="student_name" label="姓名" min-width="100" />
                <el-table-column prop="score" label="分数" min-width="80" align="center" />
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getCtStatisticsOverview } from '@/api/classTeacher'
import { EXAM_TYPES } from '@/types/grade'
import BarChart from '@/components/chart/BarChart.vue'
import LineChart from '@/components/chart/LineChart.vue'
import PieChart from '@/components/chart/PieChart.vue'
import RadarChart from '@/components/chart/RadarChart.vue'

const examTypes = EXAM_TYPES
const loading = ref(false)
const filterExamType = ref('')
const activeSubjectTab = ref('')
const data = ref<Record<string, unknown>>({})

function formatNum(v: unknown): string {
  if (v === null || v === undefined) return '-'
  return Number(v).toFixed(1)
}

function formatPercent(v: unknown): string {
  if (v === null || v === undefined) return '-'
  return Number(v).toFixed(1) + '%'
}

const distData = computed(() => {
  const dist = data.value.total_distribution as Record<string, number> | undefined
  if (!dist) return { xData: [] as string[], yData: [] as number[] }
  return {
    xData: Object.keys(dist),
    yData: Object.values(dist),
  }
})

const trendData = computed(() => {
  const trend = data.value.total_trend as Array<{ exam_type: string; avg_total: number; max_total: number }> | undefined
  if (!trend || trend.length === 0) return { xData: [] as string[], series: [] as Array<{ name: string; data: number[]; color: string }> }
  return {
    xData: trend.map((t) => t.exam_type),
    series: [
      { name: '平均总分', data: trend.map((t) => t.avg_total), color: '#409EFF' },
      { name: '最高总分', data: trend.map((t) => t.max_total), color: '#67C23A' },
    ],
  }
})

const pieData = computed(() => {
  const avgs = data.value.subject_averages as Array<{ subject: string; average: number }> | undefined
  if (!avgs) return []
  return avgs.map((a) => ({ name: a.subject, value: a.average }))
})

const radarData = computed(() => {
  const rd = data.value.subject_radar as Array<{ subject: string; average: number; pass_rate: number; excellent_rate: number }> | undefined
  if (!rd || rd.length === 0) return { indicators: [] as Array<{ name: string; max: number }>, series: [] as Array<{ name: string; data: number[]; color: string }> }
  return {
    indicators: rd.map((r) => ({ name: r.subject, max: 150 })),
    series: [
      { name: '平均分', data: rd.map((r) => r.average), color: '#409EFF' },
      { name: '及格率', data: rd.map((r) => r.pass_rate), color: '#67C23A' },
      { name: '优秀率', data: rd.map((r) => r.excellent_rate), color: '#E6A23C' },
    ],
  }
})

const top10Total = computed(() => {
  return (data.value.top10_total as Array<{ rank: number; student_name: string; total_score: number }>) || []
})

const top10Subjects = computed(() => {
  const items = (data.value.top10_subjects as Array<{ subject: string; top10: Array<{ rank: number; student_name: string; score: number }> }>) || []
  if (items.length > 0 && !activeSubjectTab.value) {
    activeSubjectTab.value = items[0].subject
  }
  return items
})

async function fetchData() {
  loading.value = true
  try {
    const res = await getCtStatisticsOverview({
      exam_type: filterExamType.value || undefined,
    })
    if (res?.data) {
      data.value = res.data as Record<string, unknown>
    }
  } catch (e) {
    console.error('获取统计数据失败:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.ct-stats-overview {
  animation: fadeIn 0.3s ease;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 12px;
    .page-title { margin: 0; font-size: 22px; font-weight: 700; }
    .header-actions { display: flex; gap: 12px; }
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
    .overview-value { font-size: 24px; font-weight: 700; color: var(--text-color); line-height: 1.2; min-height: 30px; }
    .overview-label { font-size: 13px; color: var(--text-color-secondary); margin-top: 6px; font-weight: 500; }
    &--primary .overview-value { color: #409EFF; }
    &--info .overview-value { color: #909399; }
    &--success .overview-value { color: #67C23A; }
    &--warning .overview-value { color: #E6A23C; }
    &--accent .overview-value { color: #F56C6C; }
  }

  .chart-row { margin-bottom: 16px; }

  .chart-card-wrapper {
    overflow: hidden;
    display: flex;
    flex-direction: column;
    flex: 1;
  }

  .chart-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-color);
    margin: 0 0 16px;
  }

  .chart-empty {
    height: 340px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-color-secondary);
  }

  :deep(.chart-row) {
    .el-col {
      display: flex;
      flex-direction: column;
      > .page-card {
        flex: 1;
        display: flex;
        flex-direction: column;
      }
    }
  }
}
</style>
