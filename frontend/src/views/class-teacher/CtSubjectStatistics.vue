<template>
  <div class="ct-subject-stats page-container">
    <div class="page-header">
      <h1 class="page-title">科目统计</h1>
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

    <!-- 科目统计表格 -->
    <div class="page-card">
      <h3 class="section-title">科目统计信息</h3>
      <el-table
        v-if="subjects.length > 0"
        :data="subjects"
        border
        stripe
        style="width: 100%"
        :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }"
        highlight-current-row
        @row-click="handleRowClick"
      >
        <el-table-column prop="subject" label="科目" min-width="100" />
        <el-table-column prop="student_count" label="参考人数" min-width="100" align="center" />
        <el-table-column label="平均分" min-width="100" align="center">
          <template #default="{ row }">
            <span :style="{ color: getScoreColor(row.average_score) }">{{ formatScore(row.average_score) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="最高分" min-width="100" align="center">
          <template #default="{ row }">{{ formatScore(row.max_score) }}</template>
        </el-table-column>
        <el-table-column label="最低分" min-width="100" align="center">
          <template #default="{ row }">
            <span :style="{ color: row.min_score < 60 ? '#F56C6C' : '#606266' }">{{ formatScore(row.min_score) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="及格率" min-width="100" align="center">
          <template #default="{ row }">{{ formatPercent(row.pass_rate) }}</template>
        </el-table-column>
        <el-table-column label="优秀率" min-width="100" align="center">
          <template #default="{ row }">{{ formatPercent(row.excellent_rate) }}</template>
        </el-table-column>
      </el-table>
      <div v-else class="chart-empty">暂无数据</div>
    </div>

    <!-- 图表区域 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :md="12">
        <div class="page-card chart-card-wrapper">
          <h4 class="chart-title">各科目平均分对比</h4>
          <BarChart
            v-if="comparisonData.xData.length > 0"
            title=""
            :xData="comparisonData.xData"
            :yData="comparisonData.yData"
            xLabel="科目"
            yLabel="平均分"
            color="#67C23A"
            :showValue="true"
            :height="340"
          />
          <div v-else class="chart-empty">暂无数据</div>
        </div>
      </el-col>
      <el-col :xs="24" :md="12">
        <div class="page-card chart-card-wrapper">
          <h4 class="chart-title">科目及格率/优秀率对比</h4>
          <LineChart
            v-if="rateData.xData.length > 0"
            title=""
            :xData="rateData.xData"
            :series="rateData.series"
            xLabel="科目"
            yLabel="百分比(%)"
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
          <div class="chart-title-row">
            <h4 class="chart-title">成绩分布</h4>
            <el-select v-model="selectedSubject" placeholder="选择科目" style="width: 140px" size="small">
              <el-option v-for="s in subjects" :key="s.subject" :label="s.subject" :value="s.subject" />
            </el-select>
          </div>
          <BarChart
            v-if="distData.xData.length > 0"
            title=""
            :xData="distData.xData"
            :yData="distData.yData"
            xLabel="分数段"
            yLabel="人数"
            color="#E6A23C"
            :showValue="true"
            :height="340"
          />
          <div v-else class="chart-empty">请选择科目查看分布</div>
        </div>
      </el-col>
      <el-col :xs="24" :md="12">
        <div class="page-card chart-card-wrapper">
          <h4 class="chart-title">科目能力雷达图</h4>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getCtSubjectStatistics } from '@/api/classTeacher'
import { EXAM_TYPES } from '@/types/grade'
import type { ScoreDistribution } from '@/types/statistics'
import BarChart from '@/components/chart/BarChart.vue'
import LineChart from '@/components/chart/LineChart.vue'
import RadarChart from '@/components/chart/RadarChart.vue'

interface SubjectStat {
  subject: string
  student_count: number
  average_score: number
  max_score: number
  min_score: number
  pass_rate: number
  excellent_rate: number
  score_distribution: ScoreDistribution
}

const MAJOR_KEYS = ['0-89', '90-104', '105-119', '120-134', '135-150']
const NORMAL_KEYS = ['0-59', '60-69', '70-79', '80-89', '90-100']
function isMajor(s: string) { return ['语文', '数学', '英语'].includes(s) }
function getKeys(s: string) { return isMajor(s) ? MAJOR_KEYS : NORMAL_KEYS }

const examTypes = EXAM_TYPES
const loading = ref(false)
const filterExamType = ref('')
const selectedSubject = ref('')
const subjects = ref<SubjectStat[]>([])

function formatScore(v: number | undefined | null) {
  if (v === null || v === undefined) return '-'
  return Number(v).toFixed(1)
}
function formatPercent(v: number | undefined | null) {
  if (v === null || v === undefined) return '-'
  return Number(v).toFixed(1) + '%'
}
function getScoreColor(score: number) {
  if (score >= 90) return '#67c23a'
  if (score >= 60) return '#409eff'
  return '#f56c6c'
}

const selectedSubjectData = computed(() => {
  if (!selectedSubject.value) return null
  return subjects.value.find((s) => s.subject === selectedSubject.value) || null
})

const comparisonData = computed(() => ({
  xData: subjects.value.map((s) => s.subject),
  yData: subjects.value.map((s) => s.average_score),
}))

const rateData = computed(() => ({
  xData: subjects.value.map((s) => s.subject),
  series: [
    { name: '及格率', data: subjects.value.map((s) => s.pass_rate), color: '#67C23A' },
    { name: '优秀率', data: subjects.value.map((s) => s.excellent_rate), color: '#E6A23C' },
  ],
}))

const distData = computed(() => {
  if (!selectedSubjectData.value) return { xData: [] as string[], yData: [] as number[] }
  const dist = selectedSubjectData.value.score_distribution
  const keys = getKeys(selectedSubject.value)
  return {
    xData: [...keys],
    yData: keys.map((k) => dist[k as keyof ScoreDistribution] || 0),
  }
})

const radarData = computed(() => {
  if (subjects.value.length === 0) return { indicators: [] as Array<{ name: string; max: number }>, series: [] as Array<{ name: string; data: number[]; color: string }> }
  return {
    indicators: subjects.value.map((s) => ({ name: s.subject, max: isMajor(s.subject) ? 150 : 100 })),
    series: [
      { name: '平均分', data: subjects.value.map((s) => s.average_score), color: '#409EFF' },
      { name: '及格率', data: subjects.value.map((s) => s.pass_rate), color: '#67C23A' },
      { name: '优秀率', data: subjects.value.map((s) => s.excellent_rate), color: '#E6A23C' },
    ],
  }
})

function handleRowClick(row: SubjectStat) {
  selectedSubject.value = row.subject
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getCtSubjectStatistics({
      exam_type: filterExamType.value || undefined,
    })
    if (res?.data) {
      const d = res.data as { subjects: SubjectStat[] }
      subjects.value = d.subjects || []
      if (subjects.value.length > 0 && !selectedSubject.value) {
        selectedSubject.value = subjects.value[0].subject
      }
    }
  } catch (e) {
    console.error('获取科目统计数据失败:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.ct-subject-stats {
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

  .section-title { font-size: 16px; font-weight: 600; color: var(--text-color); margin: 0 0 16px; }

  .chart-row { margin-bottom: 16px; }

  .chart-card-wrapper {
    overflow: hidden;
    display: flex;
    flex-direction: column;
    flex: 1;
  }

  .chart-title { font-size: 16px; font-weight: 600; color: var(--text-color); margin: 0 0 16px; }

  .chart-title-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    .chart-title { margin: 0; }
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
      > .page-card { flex: 1; display: flex; flex-direction: column; }
    }
  }
}
</style>
