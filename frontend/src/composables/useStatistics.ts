/**
 * 统计分析组合式函数
 * 封装统计相关的业务逻辑和状态
 */

import { ref, computed, onMounted, watch } from 'vue'
import { useStatisticsStore } from '@/stores/statistics'
import { useStudentStore } from '@/stores/student'
import { ElMessage } from 'element-plus'
import type { Subject, ExamType } from '@/types/grade'
import { SUBJECTS, EXAM_TYPES } from '@/types/grade'
import type { StatisticsQuery, RankingItem } from '@/types/statistics'
import { formatScore, formatPercent } from '@/utils/format'
import * as statisticsApi from '@/api/statistics'

/**
 * 统计概览组合式函数
 */
export function useStatisticsOverview() {
  const statisticsStore = useStatisticsStore()
  const studentStore = useStudentStore()

  /** 筛选表单 */
  const filterForm = ref({
    class_name: '',
    subject: '' as Subject | '',
    exam_type: '' as ExamType | '',
  })

  /** 科目选项 */
  const subjectOptions = SUBJECTS

  /** 考试类型选项 */
  const examTypeOptions = EXAM_TYPES

  /** 班级选项 */
  const classOptions = computed(() => studentStore.classList)

  /** 统计数据 */
  const statistics = computed(() => statisticsStore.overview)

  /** 排名数据 */
  const rankings = computed(() => statisticsStore.rankings)

  /** 加载状态 */
  const loading = computed(() => statisticsStore.loading)

  /** 报告数据（从后端获取的真实数据） */
  const reportData = ref<{
    statistics: {
      count: number
      average: number
      max_score: number
      min_score: number
      pass_rate: number
      excellent_rate: number
      score_distribution: Record<string, number>
    }
    top_students: Array<{ student_id: string; name: string; score: number }>
  } | null>(null)

  /** 统计卡片数据 */
  const statCards = computed(() => [
    {
      label: '学生总数',
      value: reportData.value?.statistics?.count ?? statisticsStore.totalStudents,
      icon: 'User',
      color: '#409EFF',
      format: (v: number) => v.toString(),
    },
    {
      label: '平均分',
      value: reportData.value?.statistics?.average ?? statisticsStore.averageScore,
      icon: 'TrendCharts',
      color: '#67C23A',
      format: (v: number) => formatScore(v),
    },
    {
      label: '最高分',
      value: reportData.value?.statistics?.max_score ?? statisticsStore.maxScore,
      icon: 'Trophy',
      color: '#E6A23C',
      format: (v: number) => formatScore(v),
    },
    {
      label: '及格率',
      value: reportData.value?.statistics?.pass_rate ?? statisticsStore.passRate,
      icon: 'CircleCheck',
      color: '#67C23A',
      format: (v: number) => formatPercent(v),
    },
    {
      label: '优秀率',
      value: reportData.value?.statistics?.excellent_rate ?? statisticsStore.excellentRate,
      icon: 'Star',
      color: '#F56C6C',
      format: (v: number) => formatPercent(v),
    },
    {
      label: '参考人数',
      value: reportData.value?.statistics?.count ?? statisticsStore.totalStudents,
      icon: 'User',
      color: '#909399',
      format: (v: number) => v.toString(),
    },
  ])

  /** 分数分布数据（用于柱状图） - 使用真实API数据 */
  const scoreDistributionData = computed(() => {
    const dist = reportData.value?.statistics?.score_distribution
    if (!dist) return { xData: [], yData: [] }
    return {
      xData: ['0-59', '60-69', '70-79', '80-89', '90-100'],
      yData: [
        dist['0-59'] || 0,
        dist['60-69'] || 0,
        dist['70-79'] || 0,
        dist['80-89'] || 0,
        dist['90-100'] || 0,
      ],
    }
  })

  /** 科目平均分数据（用于柱状图） - 从后端获取真实数据 */
  const subjectAverageData = ref<{ xData: string[]; yData: number[] }>({
    xData: [],
    yData: [],
  })

  /** 考试趋势数据（用于折线图） - 从后端获取真实数据 */
  const examTrendData = ref<{
    xData: string[]
    series: Array<{ name: string; data: number[]; color: string }>
  }>({
    xData: [],
    series: [],
  })

  /** 科目占比数据（用于饼图） - 从后端获取真实数据 */
  const subjectPieData = ref<Array<{ name: string; value: number; color: string }>>([])

  /** 能力雷达图数据 - 从后端获取真实数据 */
  const radarData = ref<{
    indicators: Array<{ name: string; max: number }>
    series: Array<{ name: string; data: number[]; color: string }>
  }>({
    indicators: [],
    series: [],
  })

  /** 加载图表数据 */
  async function loadChartData() {
    try {
      // 获取综合报告数据
      const reportParams: Record<string, string | number> = { top_n: 10 }
      if (filterForm.value.class_name) reportParams.class_name = filterForm.value.class_name
      if (filterForm.value.subject) reportParams.subject = filterForm.value.subject
      if (filterForm.value.exam_type) reportParams.exam_type = filterForm.value.exam_type

      const reportResponse = await statisticsApi.getReport(reportParams)
      // 响应拦截器返回 BackendResponse，实际数据在 .data 中
      const report = (reportResponse as any).data || reportResponse
      reportData.value = report || null

      // 获取各科目统计数据（用于饼图、雷达图、柱状图）
      const subjectStatsResponse = await statisticsApi.getBatchSubjectStatistics({
        class_name: filterForm.value.class_name || undefined,
        exam_type: filterForm.value.exam_type as ExamType || undefined,
      })
      // 响应拦截器返回 BackendResponse，实际数据在 .data 中
      const subjectStatsData = (subjectStatsResponse as any).data || subjectStatsResponse
      const subjects = subjectStatsData?.subjects || []
      const defaultColors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#8B5CF6', '#EC4899', '#06B6D4']

      // 更新科目平均分柱状图数据
      subjectAverageData.value = {
        xData: subjects.map((s: any) => s.subject),
        yData: subjects.map((s: any) => s.average_score),
      }

      // 更新饼图数据
      subjectPieData.value = subjects.map((s: any, i: number) => ({
        name: s.subject,
        value: s.average_score,
        color: defaultColors[i % defaultColors.length],
      }))

      // 更新雷达图数据
      radarData.value = {
        indicators: subjects.map((s: any) => ({ name: s.subject, max: 100 })),
        series: [
          {
            name: '平均分',
            data: subjects.map((s: any) => s.average_score),
            color: '#409EFF',
          },
          {
            name: '及格率',
            data: subjects.map((s: any) => s.pass_rate),
            color: '#67C23A',
          },
        ],
      }

      // 获取考试趋势数据（不同考试类型的平均分）
      const examTypes = EXAM_TYPES
      const trendResults = await Promise.all(
        examTypes.map(async (et) => {
          const statsResponse = await statisticsApi.getStatistics({
            class_name: filterForm.value.class_name || undefined,
            subject: filterForm.value.subject || undefined,
            exam_type: et,
            metrics: 'avg,max',
          })
          // 响应拦截器返回 BackendResponse，实际数据在 .data 中
          const statsData = (statsResponse as any).data || statsResponse
          return { exam_type: et, metrics: statsData?.metrics || {} }
        })
      )

      examTrendData.value = {
        xData: trendResults.map((r) => r.exam_type),
        series: [
          {
            name: '平均分',
            data: trendResults.map((r) => r.metrics.avg || 0),
            color: '#409EFF',
          },
          {
            name: '最高分',
            data: trendResults.map((r) => r.metrics.max || 0),
            color: '#67C23A',
          },
        ],
      }
    } catch (error) {
      console.error('加载图表数据失败:', error)
    }
  }

  /** 执行查询 */
  async function handleSearch() {
    const params: StatisticsQuery = {}
    if (filterForm.value.class_name) params.class_name = filterForm.value.class_name
    if (filterForm.value.subject) params.subject = filterForm.value.subject as Subject
    if (filterForm.value.exam_type) params.exam_type = filterForm.value.exam_type as ExamType

    await Promise.all([
      statisticsStore.fetchStatistics(params),
      statisticsStore.fetchRankings({
        subject: params.subject || '数学',
        exam_type: params.exam_type || '期中',
        class_name: params.class_name,
        scope: 'grade',
        limit: 10,
      }),
      loadChartData(),
    ])
  }

  /** 重置筛选 */
  function handleReset() {
    filterForm.value = {
      class_name: '',
      subject: '',
      exam_type: '',
    }
    statisticsStore.clearFilters()
    // 使用 nextTick 确保状态更新后再查询
    setTimeout(() => {
      handleSearch()
    }, 0)
  }

  /** 导出报告 */
  function handleExport() {
    ElMessage.info('导出功能开发中...')
  }

  /** 初始化班级列表 */
  onMounted(async () => {
    await studentStore.fetchClassList()
    statisticsStore.setClassOptions(studentStore.classList)
    await handleSearch()
  })

  return {
    filterForm,
    subjectOptions,
    examTypeOptions,
    classOptions,
    statistics,
    rankings,
    loading,
    statCards,
    scoreDistributionData,
    subjectAverageData,
    examTrendData,
    subjectPieData,
    radarData,
    handleSearch,
    handleReset,
    handleExport,
  }
}

/**
 * 班级统计组合式函数
 */
export function useClassStatistics() {
  const statisticsStore = useStatisticsStore()
  const studentStore = useStudentStore()

  /** 筛选表单 */
  const filterForm = ref({
    class_name: '',
    exam_type: '' as ExamType | '',
  })

  /** 考试类型选项 */
  const examTypeOptions = EXAM_TYPES

  /** 班级选项 */
  const classOptions = computed(() => studentStore.classList)

  /** 班级统计数据 */
  const classStats = computed(() => statisticsStore.classStatistics)

  /** 加载状态 */
  const loading = computed(() => statisticsStore.loading)

  /** 选中班级的详细统计 */
  const selectedClassStats = computed(() => {
    if (!filterForm.value.class_name) return null
    return classStats.value.find((s) => s.class_name === filterForm.value.class_name) || null
  })

  /** 班级对比图表数据 */
  const classComparisonData = computed(() => {
    return {
      xData: classStats.value.map((s) => s.class_name),
      yData: classStats.value.map((s) => s.average_score),
    }
  })

  /** 班级及格率对比数据 */
  const classPassRateData = computed(() => {
    return {
      xData: classStats.value.map((s) => s.class_name),
      series: [
        {
          name: '及格率',
          data: classStats.value.map((s) => s.pass_rate),
          color: '#67C23A',
        },
        {
          name: '优秀率',
          data: classStats.value.map((s) => s.excellent_rate),
          color: '#E6A23C',
        },
      ],
    }
  })

  /** 执行查询 */
  async function handleSearch() {
    await statisticsStore.fetchClassStatistics(
      filterForm.value.exam_type as ExamType || undefined
    )
  }

  /** 重置筛选 */
  function handleReset() {
    filterForm.value = {
      class_name: '',
      exam_type: '',
    }
    // 使用 setTimeout 确保状态更新后再查询
    setTimeout(() => {
      handleSearch()
    }, 0)
  }

  /** 导出报告 */
  function handleExport() {
    ElMessage.info('导出功能开发中...')
  }

  /** 初始化 */
  onMounted(async () => {
    await studentStore.fetchClassList()
    statisticsStore.setClassOptions(studentStore.classList)
    await handleSearch()
  })

  return {
    filterForm,
    examTypeOptions,
    classOptions,
    classStats,
    loading,
    selectedClassStats,
    classComparisonData,
    classPassRateData,
    handleSearch,
    handleReset,
    handleExport,
  }
}

/**
 * 科目统计组合式函数
 */
export function useSubjectStatistics() {
  const statisticsStore = useStatisticsStore()
  const studentStore = useStudentStore()

  /** 筛选表单 */
  const filterForm = ref({
    subject: '' as Subject | '',
    exam_type: '' as ExamType | '',
    class_name: '',
  })

  /** 科目选项 */
  const subjectOptions = SUBJECTS

  /** 考试类型选项 */
  const examTypeOptions = EXAM_TYPES

  /** 班级选项 */
  const classOptions = computed(() => studentStore.classList)

  /** 科目统计数据 */
  const subjectStats = computed(() => statisticsStore.subjectStatistics)

  /** 加载状态 */
  const loading = computed(() => statisticsStore.loading)

  /** 选中科目的详细统计 */
  const selectedSubjectStats = computed(() => {
    if (!filterForm.value.subject) return null
    return subjectStats.value.find((s) => s.subject === filterForm.value.subject) || null
  })

  /** 科目平均分对比图表数据 */
  const subjectComparisonData = computed(() => {
    return {
      xData: subjectStats.value.map((s) => s.subject),
      yData: subjectStats.value.map((s) => s.average_score),
    }
  })

  /** 科目及格率/优秀率对比数据 */
  const subjectRateData = computed(() => {
    return {
      xData: subjectStats.value.map((s) => s.subject),
      series: [
        {
          name: '及格率',
          data: subjectStats.value.map((s) => s.pass_rate),
          color: '#67C23A',
        },
        {
          name: '优秀率',
          data: subjectStats.value.map((s) => s.excellent_rate),
          color: '#E6A23C',
        },
      ],
    }
  })

  /** 分数分布图表数据 */
  const scoreDistributionData = computed(() => {
    if (!selectedSubjectStats.value) return { xData: [], yData: [] }
    const dist = selectedSubjectStats.value.score_distribution
    return {
      xData: ['0-59', '60-69', '70-79', '80-89', '90-100'],
      yData: [dist.fail, dist.pass, dist.medium, dist.good, dist.excellent],
    }
  })

  /** 能力雷达图数据 */
  const radarData = computed(() => {
    return {
      indicators: subjectStats.value.map((s) => ({
        name: s.subject,
        max: 100,
      })),
      series: [
        {
          name: '平均分',
          data: subjectStats.value.map((s) => s.average_score),
          color: '#409EFF',
        },
        {
          name: '及格率',
          data: subjectStats.value.map((s) => s.pass_rate),
          color: '#67C23A',
        },
      ],
    }
  })

  /** 执行查询 */
  async function handleSearch() {
    await statisticsStore.fetchSubjectStatistics(
      filterForm.value.class_name || undefined,
      filterForm.value.exam_type as ExamType || undefined
    )
  }

  /** 重置筛选 */
  function handleReset() {
    filterForm.value = {
      subject: '',
      exam_type: '',
      class_name: '',
    }
    // 使用 setTimeout 确保状态更新后再查询
    setTimeout(() => {
      handleSearch()
    }, 0)
  }

  /** 导出报告 */
  function handleExport() {
    ElMessage.info('导出功能开发中...')
  }

  /** 初始化 */
  onMounted(async () => {
    await studentStore.fetchClassList()
    statisticsStore.setClassOptions(studentStore.classList)
    await handleSearch()
  })

  return {
    filterForm,
    subjectOptions,
    examTypeOptions,
    classOptions,
    subjectStats,
    loading,
    selectedSubjectStats,
    subjectComparisonData,
    subjectRateData,
    scoreDistributionData,
    radarData,
    handleSearch,
    handleReset,
    handleExport,
  }
}
