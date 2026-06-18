<template>
  <div class="statistics-overview page-container">
    <div class="page-header">
      <h1 class="page-title">统计概览</h1>
      <div class="page-actions">
        <el-button type="primary" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出报告
        </el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <div class="search-bar">
      <el-select v-model="filterForm.class_name" placeholder="选择班级" clearable style="width: 160px">
        <el-option v-for="cls in classOptions" :key="cls" :label="cls" :value="cls" />
      </el-select>
      <el-select v-model="filterForm.exam_type" placeholder="考试类型" clearable style="width: 140px">
        <el-option v-for="type in examTypeOptions" :key="type" :label="type" :value="type" />
      </el-select>
      <el-button type="primary" @click="handleSearch" :loading="loading">
        <el-icon><Search /></el-icon>
        查询
      </el-button>
      <el-button @click="handleReset">
        <el-icon><RefreshRight /></el-icon>
        重置
      </el-button>
    </div>

    <!-- 错误状态 -->
    <div v-if="error && queried" class="page-card">
      <div class="state-error">
        <el-icon :size="48" class="state-error__icon"><CircleCloseFilled /></el-icon>
        <h4 class="state-error__title">加载失败</h4>
        <p class="state-error__desc">{{ error }}</p>
        <el-button type="primary" @click="handleSearch">
          <el-icon><RefreshRight /></el-icon>
          重新加载
        </el-button>
      </div>
    </div>

    <!-- 未查询空状态 -->
    <template v-else-if="!queried">
      <div class="page-card">
        <EmptyState
          icon-color="var(--primary-color)"
          title="请先选择考试类型后查询"
          description="选择筛选条件并点击查询按钮，即可查看统计分析报告"
        />
      </div>
    </template>

    <!-- 正常数据展示 -->
    <template v-else>
      <!-- 总分统计卡片 -->
      <el-row :gutter="16" class="stat-cards">
        <el-col v-for="(card, index) in statCards" :key="index" :xs="12" :sm="8" :md="4">
          <div class="stat-card" :style="{ borderLeft: `4px solid ${card.color}` }">
            <div class="stat-card__icon" :style="{ color: card.color }">
              <el-icon :size="24"><component :is="card.icon" /></el-icon>
            </div>
            <div class="stat-card__content">
              <div class="stat-card__value">{{ card.format(card.value) }}</div>
              <div class="stat-card__label">{{ card.label }}</div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 图表区域 -->
      <el-row :gutter="16" class="chart-section chart-row">
        <!-- 总分分布柱状图 -->
        <el-col :xs="24" :md="12">
          <div class="page-card chart-card-wrapper">
            <BarChart
              title="总分分布"
              :xData="scoreDistributionData.xData"
              :yData="scoreDistributionData.yData"
              xLabel="分数段"
              yLabel="人数"
              color="#409EFF"
              :showValue="true"
              :height="360"
            />
            <div v-if="scoreDistributionData.xData.length === 0" class="chart-empty-wrapper">
              <EmptyState size="small" title="暂无数据" />
            </div>
          </div>
        </el-col>

        <!-- 成绩趋势折线图 -->
        <el-col :xs="24" :md="12">
          <div class="page-card chart-card-wrapper">
            <LineChart
              title="各考试类型总分趋势"
              :xData="examTrendData.xData"
              :series="examTrendData.series"
              xLabel="考试类型"
              yLabel="总分"
              :smooth="true"
              :areaStyle="true"
              :height="360"
            />
            <div v-if="examTrendData.xData.length === 0" class="chart-empty-wrapper">
              <EmptyState size="small" title="暂无趋势数据" />
            </div>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="16" class="chart-section chart-row">
        <!-- 科目平均分占比饼图 -->
        <el-col :xs="24" :md="12">
          <div class="page-card chart-card-wrapper">
            <div class="chart-header">
              <h4 class="chart-title">各科目平均分占比</h4>
              <p class="desc-text">各科目平均分在总分中的权重</p>
            </div>
            <PieChart
              v-if="subjectPieData.length > 0"
              :data="subjectPieData"
              :isRing="true"
              centerTitle="科目"
              :height="360"
            />
            <div v-else class="chart-empty-wrapper">
              <EmptyState size="small" title="暂无科目数据" />
            </div>
          </div>
        </el-col>

        <!-- 能力雷达图 -->
        <el-col :xs="24" :md="12">
          <div class="page-card chart-card-wrapper">
            <div class="chart-header">
              <h4 class="chart-title">各科目能力雷达</h4>
              <p class="desc-text">各科目平均分与及格率对比</p>
            </div>
            <RadarChart
              v-if="radarData.indicators.length > 0"
              title=""
              :indicators="radarData.indicators"
              :series="radarData.series"
              :height="360"
            />
            <div v-else class="chart-empty-wrapper">
              <EmptyState size="small" title="暂无能力数据" />
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 总分排名表格 -->
      <div class="page-card">
        <div class="card-header">
          <h3 class="section-title">总分排名（前10名）</h3>
          <el-tag type="info" size="small" v-if="filterForm.exam_type">{{ filterForm.exam_type }}</el-tag>
        </div>
        <el-table
          v-if="totalRankings.length > 0"
          :data="totalRankings"
          border
          stripe
          style="width: 100%"
          :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }"
        >
          <el-table-column type="index" label="排名" width="70" align="center">
            <template #default="{ $index }">
              <div class="rank-cell">
                <span v-if="$index < 3" class="rank-badge" :class="`rank-${$index + 1}`">{{ $index + 1 }}</span>
                <span v-else>{{ $index + 1 }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="student_id" label="学号" min-width="100" align="center" />
          <el-table-column prop="student_name" label="姓名" min-width="100" align="center" />
          <el-table-column prop="total_score" label="总分" min-width="100" align="center" sortable="custom">
            <template #default="{ row }">
              <span style="font-weight: 700; color: var(--primary-color); font-size: 16px;">{{ formatScore(row.total_score) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="各科成绩" min-width="300">
            <template #default="{ row }">
              <div class="subject-scores-row">
                <el-tag v-for="(score, sub) in row.subject_scores" :key="sub" size="small" effect="plain" class="subject-score-tag">
                  {{ sub }}: {{ score }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <EmptyState v-else size="small" :icon="Trophy" title="暂无总分排名数据" description="选择考试类型后查询" />
      </div>

      <!-- 单科排名 -->
      <div class="page-card">
        <div class="card-header">
          <h3 class="section-title">单科排名（前10名）</h3>
          <div class="rank-filter">
            <el-select v-model="selectedRankSubject" placeholder="选择科目" style="width: 120px" @change="fetchSubjectRanking">
              <el-option v-for="sub in subjectOptions" :key="sub" :label="sub" :value="sub" />
            </el-select>
          </div>
        </div>
        <el-table
          v-if="subjectRankings.length > 0"
          :data="subjectRankings"
          border
          stripe
          style="width: 100%"
          :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }"
        >
          <el-table-column type="index" label="排名" width="70" align="center">
            <template #default="{ $index }">
              <div class="rank-cell">
                <span v-if="$index < 3" class="rank-badge" :class="`rank-${$index + 1}`">{{ $index + 1 }}</span>
                <span v-else>{{ $index + 1 }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="student_id" label="学号" min-width="120" align="center" />
          <el-table-column prop="student_name" label="姓名" min-width="120" align="center" />
          <el-table-column prop="score" label="分数" min-width="100" align="center" sortable="custom">
            <template #default="{ row }">
              <span style="font-weight: 700; color: var(--primary-color); font-size: 16px;">{{ formatScore(row.score) }}</span>
            </template>
          </el-table-column>
        </el-table>
        <EmptyState v-else size="small" title="请选择科目查看排名" />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Download, Search, RefreshRight, Trophy, CircleCloseFilled } from '@element-plus/icons-vue'
import { useStatisticsStore } from '@/stores/statistics'
import { useStudentStore } from '@/stores/student'
import { getTotalRanking, getRanking, getBatchSubjectStatistics, getReport } from '@/api/statistics'
import { formatScore, formatPercent } from '@/utils/format'
import { SUBJECTS, EXAM_TYPES } from '@/types/grade'
import type { ExamType } from '@/types/grade'
import type { TotalRankingItem, RankingItem } from '@/types/statistics'
import BarChart from '@/components/chart/BarChart.vue'
import LineChart from '@/components/chart/LineChart.vue'
import PieChart from '@/components/chart/PieChart.vue'
import RadarChart from '@/components/chart/RadarChart.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const statisticsStore = useStatisticsStore()
const studentStore = useStudentStore()

/** 科目选项 */
const subjectOptions = SUBJECTS

/** 考试类型选项 */
const examTypeOptions = EXAM_TYPES

/** 班级选项 */
const classOptions = computed(() => studentStore.classList)

/** 是否已查询 */
const queried = ref(false)

/** 加载状态 */
const loading = ref(false)

/** 错误状态 */
const error = ref<string | null>(null)

/** 筛选表单 */
const filterForm = ref({
  class_name: '',
  exam_type: '' as ExamType | '',
})

/** 总分排名数据 */
const totalRankings = ref<TotalRankingItem[]>([])

/** 单科排名数据 */
const subjectRankings = ref<RankingItem[]>([])

/** 选中的排名科目 */
const selectedRankSubject = ref('语文')

/** 报告数据 */
const reportData = ref<any>(null)

/** 科目统计数据 */
const subjectStatsData = ref<any[]>([])

/** 统计卡片 */
const statCards = computed(() => {
  const stats = reportData.value?.statistics
  return [
    { label: '学生总数', value: stats?.count ?? 0, icon: 'User', color: '#409EFF', format: (v: number) => v.toString() },
    { label: '平均总分', value: stats?.average ?? 0, icon: 'TrendCharts', color: '#67C23A', format: (v: number) => formatScore(v) },
    { label: '最高总分', value: stats?.max_score ?? 0, icon: 'Trophy', color: '#E6A23C', format: (v: number) => formatScore(v) },
    { label: '及格率', value: stats?.pass_rate ?? 0, icon: 'CircleCheck', color: '#67C23A', format: (v: number) => formatPercent(v) },
    { label: '优秀率', value: stats?.excellent_rate ?? 0, icon: 'Star', color: '#F56C6C', format: (v: number) => formatPercent(v) },
    { label: '参考人数', value: stats?.count ?? 0, icon: 'User', color: '#909399', format: (v: number) => v.toString() },
  ]
})

/** 分数分布数据 */
const scoreDistributionData = computed(() => {
  const dist = reportData.value?.statistics?.score_distribution
  if (!dist) return { xData: [] as string[], yData: [] as number[] }
  return {
    xData: ['0-59', '60-69', '70-79', '80-89', '90-100'],
    yData: [dist['0-59'] || 0, dist['60-69'] || 0, dist['70-79'] || 0, dist['80-89'] || 0, dist['90-100'] || 0],
  }
})

/** 考试趋势数据 */
const examTrendData = computed(() => {
  // 使用各科目平均分作为趋势
  const subjects = subjectStatsData.value
  if (!subjects || subjects.length === 0) return { xData: [] as string[], series: [] as any[] }
  return {
    xData: subjects.map((s: any) => s.subject),
    series: [
      { name: '平均分', data: subjects.map((s: any) => s.average_score), color: '#409EFF' },
      { name: '及格率', data: subjects.map((s: any) => s.pass_rate), color: '#67C23A' },
    ],
  }
})

/** 科目饼图数据 */
const subjectPieData = computed(() => {
  const subjects = subjectStatsData.value
  if (!subjects || subjects.length === 0) return [] as any[]
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16']
  return subjects.map((s: any, i: number) => ({
    name: s.subject,
    value: s.average_score,
    color: colors[i % colors.length],
  }))
})

/** 雷达图数据 */
const radarData = computed(() => {
  const subjects = subjectStatsData.value
  if (!subjects || subjects.length === 0) return { indicators: [] as any[], series: [] as any[] }
  return {
    indicators: subjects.map((s: any) => ({ name: s.subject, max: 100 })),
    series: [
      { name: '平均分', data: subjects.map((s: any) => s.average_score), color: '#409EFF' },
      { name: '及格率', data: subjects.map((s: any) => s.pass_rate), color: '#67C23A' },
    ],
  }
})

/** 执行查询 */
async function handleSearch() {
  loading.value = true
  error.value = null
  try {
    const examType = filterForm.value.exam_type || '期中'
    const className = filterForm.value.class_name || undefined

    // 并行获取数据
    const [reportRes, subjectStatsRes, totalRankRes] = await Promise.allSettled([
      getReport({ exam_type: examType, class_name: className, top_n: 10 }),
      getBatchSubjectStatistics({ exam_type: examType as ExamType, class_name: className }),
      getTotalRanking({ exam_type: examType, class_name: className }),
    ])

    if (reportRes.status === 'fulfilled') {
      reportData.value = (reportRes.value as any).data || reportRes.value
    }

    if (subjectStatsRes.status === 'fulfilled') {
      const data = (subjectStatsRes.value as any).data || subjectStatsRes.value
      subjectStatsData.value = data.subjects || []
    }

    if (totalRankRes.status === 'fulfilled') {
      const data = (totalRankRes.value as any).data || totalRankRes.value
      totalRankings.value = data.rankings || []
    }

    // 获取默认科目排名
    await fetchSubjectRanking()

    queried.value = true
  } catch (err) {
    error.value = '查询失败，请稍后重试'
    queried.value = true
  } finally {
    loading.value = false
  }
}

/** 获取单科排名 */
async function fetchSubjectRanking() {
  if (!selectedRankSubject.value || !filterForm.value.exam_type) return
  try {
    const res = await getRanking({
      subject: selectedRankSubject.value,
      exam_type: filterForm.value.exam_type,
      class_name: filterForm.value.class_name || undefined,
      limit: 10,
    })
    const data = (res as any).data || res
    subjectRankings.value = data.rankings || []
  } catch {
    subjectRankings.value = []
  }
}

/** 重置筛选 */
function handleReset() {
  filterForm.value = { class_name: '', exam_type: '' }
  queried.value = false
  error.value = null
  reportData.value = null
  subjectStatsData.value = []
  totalRankings.value = []
  subjectRankings.value = []
}

/** 导出报告 */
function handleExport() {
  ElMessage.info('导出功能开发中...')
}

/** 初始化 */
onMounted(async () => {
  await studentStore.fetchClassList()
})
</script>

<style lang="scss" scoped>
.statistics-overview {
  animation: fadeIn 0.3s ease;

  .stat-cards {
    margin-bottom: 16px;
  }

  .stat-card {
    display: flex;
    align-items: center;
    padding: 20px;
    background: var(--surface-color);
    border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-color-light);
    box-shadow: var(--shadow-xs);
    margin-bottom: 16px;
    transition: all 0.25s ease;

    &:hover {
      box-shadow: var(--shadow-sm);
      transform: translateY(-2px);
    }

    &__icon {
      width: 48px;
      height: 48px;
      border-radius: 14px;
      background: var(--primary-light);
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 16px;
      flex-shrink: 0;
    }

    &__content { flex: 1; }

    &__value {
      font-size: 28px;
      font-weight: 700;
      color: var(--text-color);
      line-height: 1.2;
      letter-spacing: -0.02em;
    }

    &__label {
      font-size: 13px;
      color: var(--text-color-secondary);
      margin-top: 4px;
      font-weight: 500;
    }
  }

  .chart-section {
    margin-bottom: 16px;

    :deep(.el-row) {
      display: flex;
      flex-wrap: wrap;
    }

    :deep(.el-col) {
      display: flex;
    }

    :deep(.page-card) {
      flex: 1;
      display: flex;
      flex-direction: column;
    }
  }

  .chart-card-wrapper {
    overflow: hidden;
    display: flex;
    flex-direction: column;
    flex: 1;
  }

  .chart-empty-wrapper {
    height: 360px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 1;
  }

  .chart-header {
    margin-bottom: 16px;
  }

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-color);
    margin: 0;
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
  }

  .rank-filter {
    display: flex;
    gap: 8px;
  }

  .rank-cell {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .rank-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 700;
    color: #fff;

    &.rank-1 { background: linear-gradient(135deg, #ffd700, #ffed4e); color: #b8860b; }
    &.rank-2 { background: linear-gradient(135deg, #c0c0c0, #e8e8e8); color: #696969; }
    &.rank-3 { background: linear-gradient(135deg, #cd7f32, #daa520); color: #8b4513; }
  }

  .subject-scores-row {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }

  .subject-score-tag {
    font-size: 12px;
  }
}

@media (max-width: 768px) {
  .statistics-overview {
    .stat-card {
      padding: 16px;

      &__value { font-size: 20px; }
      &__icon { width: 40px; height: 40px; margin-right: 12px; }
    }
  }
}
</style>
