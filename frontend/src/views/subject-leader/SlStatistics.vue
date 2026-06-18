<template>
  <div class="sl-statistics page-container">
    <div class="page-header">
      <h1 class="page-title">统计概览</h1>
      <span class="page-subtitle" v-if="data.subject">{{ data.subject }}</span>
      <div class="header-actions">
        <el-select v-model="filterClass" placeholder="班级" clearable style="width: 140px" @change="fetchData">
          <el-option v-for="c in classOptions" :key="c" :label="c" :value="c" />
        </el-select>
        <el-select v-model="filterExamType" placeholder="考试类型" clearable style="width: 140px" @change="fetchData">
          <el-option v-for="t in examTypes" :key="t" :label="t" :value="t" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="fetchData">
          <el-icon><Search /></el-icon>查询
        </el-button>
      </div>
    </div>

    <!-- 概览卡片 -->
    <el-row :gutter="16" class="overview-cards">
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--primary">
          <div class="overview-value">{{ data.grade_count ?? '-' }}</div>
          <div class="overview-label">成绩记录</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--success">
          <div class="overview-value">{{ formatNum(data.average_score) }}</div>
          <div class="overview-label">平均分</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--info">
          <div class="overview-value">{{ formatNum(data.max_score) }}</div>
          <div class="overview-label">最高分</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--warning">
          <div class="overview-value">{{ formatNum(data.min_score) }}</div>
          <div class="overview-label">最低分</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--primary">
          <div class="overview-value">{{ formatPercent(data.pass_rate) }}</div>
          <div class="overview-label">及格率</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="overview-card overview-card--accent">
          <div class="overview-value">{{ formatPercent(data.excellent_rate) }}</div>
          <div class="overview-label">优秀率</div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :md="12">
        <div class="page-card chart-card-wrapper">
          <h4 class="chart-title">分数分布</h4>
          <BarChart v-if="distData.xData.length > 0" title="" :xData="distData.xData" :yData="distData.yData" xLabel="分数段" yLabel="人数" color="#E6A23C" :showValue="true" :height="340" />
          <div v-else class="chart-empty">暂无数据</div>
        </div>
      </el-col>
      <el-col :xs="24" :md="12">
        <div class="page-card chart-card-wrapper">
          <h4 class="chart-title">各班级平均分/最高分/最低分对比</h4>
          <BarChart v-if="classAvgData.xData.length > 0" title="" :xData="classAvgData.xData" :yData="classAvgData.yData" xLabel="班级" yLabel="分数" color="#409EFF" :showValue="true" :height="340" />
          <div v-else class="chart-empty">暂无数据</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :md="12">
        <div class="page-card chart-card-wrapper">
          <h4 class="chart-title">各班级及格率/优秀率对比</h4>
          <LineChart v-if="rateData.xData.length > 0" title="" :xData="rateData.xData" :series="rateData.series" xLabel="班级" yLabel="百分比(%)" :smooth="true" :showLegend="true" :height="340" />
          <div v-else class="chart-empty">暂无数据</div>
        </div>
      </el-col>
      <el-col :xs="24" :md="12">
        <div class="page-card">
          <h4 class="chart-title">排名前十</h4>
          <el-table :data="top10" border stripe size="small" :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }">
            <el-table-column prop="rank" label="名次" width="70" align="center" />
            <el-table-column prop="student_name" label="姓名" min-width="100" />
            <el-table-column prop="class_name" label="班级" min-width="100" />
            <el-table-column prop="score" label="分数" min-width="80" align="center" />
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getSlStatistics } from '@/api/subjectLeader'
import { EXAM_TYPES } from '@/types/grade'
import BarChart from '@/components/chart/BarChart.vue'
import LineChart from '@/components/chart/LineChart.vue'

const examTypes = EXAM_TYPES
const loading = ref(false)
const filterClass = ref('')
const filterExamType = ref('')
const classOptions = ref<string[]>([])
const data = ref<Record<string, unknown>>({})
const top10 = ref<Array<{ rank: number; student_name: string; class_name: string; score: number }>>([])

function formatNum(v: unknown) { return v == null ? '-' : Number(v).toFixed(1) }
function formatPercent(v: unknown) { return v == null ? '-' : Number(v).toFixed(1) + '%' }

const isMajor = computed(() => {
  const subj = data.value.subject as string
  return ['语文', '数学', '英语'].includes(subj)
})

const distData = computed(() => {
  const dist = data.value.distribution as Record<string, number> | undefined
  if (!dist) return { xData: [] as string[], yData: [] as number[] }
  return { xData: Object.keys(dist), yData: Object.values(dist) }
})

const classAvgData = computed(() => {
  const cc = data.value.class_comparison as Array<{ class_name: string; average: number }> | undefined
  if (!cc || cc.length === 0) return { xData: [] as string[], yData: [] as number[] }
  return { xData: cc.map((c) => c.class_name), yData: cc.map((c) => c.average) }
})

const rateData = computed(() => {
  const cc = data.value.class_comparison as Array<{ class_name: string; pass_rate: number; excellent_rate: number }> | undefined
  if (!cc || cc.length === 0) return { xData: [] as string[], series: [] as Array<{ name: string; data: number[]; color: string }> }
  return {
    xData: cc.map((c) => c.class_name),
    series: [
      { name: '及格率', data: cc.map((c) => c.pass_rate), color: '#67C23A' },
      { name: '优秀率', data: cc.map((c) => c.excellent_rate), color: '#E6A23C' },
    ],
  }
})

async function fetchData() {
  loading.value = true
  try {
    const res = await getSlStatistics({
      class_name: filterClass.value || undefined,
      exam_type: filterExamType.value || undefined,
    })
    if (res?.data) {
      data.value = res.data as Record<string, unknown>
      top10.value = (data.value.top10 as typeof top10.value) || []
      const cc = data.value.class_comparison as Array<{ class_name: string }> | undefined
      if (cc) classOptions.value = cc.map((c) => c.class_name).sort()
    }
  } catch (e) { console.error('获取统计数据失败:', e) } finally { loading.value = false }
}

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.sl-statistics {
  animation: fadeIn 0.3s ease;
  .page-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
    .page-title { margin: 0; font-size: 22px; font-weight: 700; }
    .page-subtitle { font-size: 16px; color: var(--text-color-secondary); font-weight: 500; }
    .header-actions { display: flex; gap: 12px; }
  }
  .overview-cards { margin-bottom: 16px; }
  .overview-card {
    padding: 18px 20px; background: var(--surface-color); border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-color-light); box-shadow: var(--shadow-xs); margin-bottom: 16px;
    text-align: center; transition: all var(--transition-duration);
    &:hover { transform: translateY(-2px); box-shadow: var(--shadow-sm); }
    .overview-value { font-size: 22px; font-weight: 700; line-height: 1.2; min-height: 28px; }
    .overview-label { font-size: 13px; color: var(--text-color-secondary); margin-top: 4px; font-weight: 500; }
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
