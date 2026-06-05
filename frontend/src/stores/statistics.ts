/**
 * 统计状态管理
 * 管理统计数据、图表配置、筛选条件
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  StatisticsQuery,
  StatisticsResponse,
  RankingResponse,
  RankingItem,
  ClassStatistics,
  SubjectStatistics,
} from '@/types/statistics'
import type { Subject, ExamType } from '@/types/grade'
import { SUBJECTS, EXAM_TYPES } from '@/types/grade'
import * as statisticsApi from '@/api/statistics'
import { ElMessage } from 'element-plus'

export const useStatisticsStore = defineStore('statistics', () => {
  // ========== 状态 ==========

  /** 统计概览数据 */
  const overview = ref<StatisticsResponse | null>(null)

  /** 排名数据 */
  const rankings = ref<RankingItem[]>([])

  /** 班级统计数据 */
  const classStatistics = ref<ClassStatistics[]>([])

  /** 科目统计数据 */
  const subjectStatistics = ref<SubjectStatistics[]>([])

  /** 加载状态 */
  const loading = ref(false)

  /** 筛选条件 */
  const filters = ref<StatisticsQuery>({
    class_name: '',
    subject: '' as Subject | '',
    exam_type: '' as ExamType | '',
  })

  /** 科目选项 */
  const subjectOptions = SUBJECTS

  /** 考试类型选项 */
  const examTypeOptions = EXAM_TYPES

  /** 班级选项 */
  const classOptions = ref<string[]>([])

  // ========== 计算属性 ==========

  /** 是否有统计数据 */
  const hasData = computed(() => overview.value !== null)

  /** 学生总数 */
  const totalStudents = computed(() => overview.value?.total_students || 0)

  /** 统计指标 */
  const metrics = computed(() => overview.value?.metrics || {})

  /** 平均分 */
  const averageScore = computed(() => metrics.value.average || 0)

  /** 最高分 */
  const maxScore = computed(() => metrics.value.max_score || 0)

  /** 最低分 */
  const minScore = computed(() => metrics.value.min_score || 0)

  /** 及格率 */
  const passRate = computed(() => metrics.value.pass_rate || 0)

  /** 优秀率 */
  const excellentRate = computed(() => metrics.value.excellent_rate || 0)

  /** 分数分布 */
  const scoreDistribution = computed(() => {
    const dist = metrics.value.score_distribution
    if (!dist) return null
    return {
      excellent: dist['90-100'] || 0,
      good: dist['80-89'] || 0,
      medium: dist['70-79'] || 0,
      pass: dist['60-69'] || 0,
      fail: dist['0-59'] || 0,
    }
  })

  /** 排名前10 */
  const top10Rankings = computed(() => rankings.value.slice(0, 10))

  // ========== 操作 ==========

  /**
   * 获取统计数据
   * @param params 查询参数
   */
  async function fetchStatistics(params?: StatisticsQuery) {
    loading.value = true
    try {
      const queryParams: StatisticsQuery = { ...filters.value, ...params }
      // 清理空值
      Object.keys(queryParams).forEach((key) => {
        if (!queryParams[key as keyof StatisticsQuery]) {
          delete queryParams[key as keyof StatisticsQuery]
        }
      })
      overview.value = await statisticsApi.getStatistics(queryParams)
    } catch (error) {
      console.error('获取统计数据失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取排名数据
   * @param params 查询参数
   */
  async function fetchRankings(params: {
    class_name?: string
    subject: string
    exam_type: string
    scope?: 'class' | 'grade'
    limit?: number
  }) {
    loading.value = true
    try {
      const response = await statisticsApi.getRanking(params)
      rankings.value = response.rankings
    } catch (error) {
      console.error('获取排名数据失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取班级统计数据（使用批量接口，避免 N+1 查询）
   * @param examType 考试类型
   */
  async function fetchClassStatistics(examType?: ExamType) {
    loading.value = true
    try {
      const response = await statisticsApi.getBatchClassStatistics({
        exam_type: examType,
      })
      classStatistics.value = response.classes
    } catch (error) {
      console.error('获取班级统计数据失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取科目统计数据（使用批量接口，避免 N+1 查询）
   * @param className 班级名称
   * @param examType 考试类型
   */
  async function fetchSubjectStatistics(className?: string, examType?: ExamType) {
    loading.value = true
    try {
      const response = await statisticsApi.getBatchSubjectStatistics({
        class_name: className,
        exam_type: examType,
      })
      subjectStatistics.value = response.subjects
    } catch (error) {
      console.error('获取科目统计数据失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取班级列表
   * @param classes 班级数组
   */
  function setClassOptions(classes: string[]) {
    classOptions.value = classes
  }

  /**
   * 设置筛选条件
   * @param newFilters 新的筛选条件
   */
  function setFilters(newFilters: Partial<StatisticsQuery>) {
    filters.value = { ...filters.value, ...newFilters }
  }

  /**
   * 清空筛选条件
   */
  function clearFilters() {
    filters.value = {
      class_name: '',
      subject: '' as Subject | '',
      exam_type: '' as ExamType | '',
    }
  }

  /**
   * 重置所有状态
   */
  function resetState() {
    overview.value = null
    rankings.value = []
    classStatistics.value = []
    subjectStatistics.value = []
    clearFilters()
  }

  return {
    // 状态
    overview,
    rankings,
    classStatistics,
    subjectStatistics,
    loading,
    filters,
    subjectOptions,
    examTypeOptions,
    classOptions,

    // 计算属性
    hasData,
    totalStudents,
    metrics,
    averageScore,
    maxScore,
    minScore,
    passRate,
    excellentRate,
    scoreDistribution,
    top10Rankings,

    // 操作
    fetchStatistics,
    fetchRankings,
    fetchClassStatistics,
    fetchSubjectStatistics,
    setClassOptions,
    setFilters,
    clearFilters,
    resetState,
  }
})
