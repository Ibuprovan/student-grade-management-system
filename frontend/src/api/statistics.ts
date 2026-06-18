/**
 * 统计分析相关 API
 */

import { get } from '@/utils/request'
import type {
  StatisticsQuery,
  StatisticsResponse,
  RankingResponse,
  TotalRankingResponse,
  StudentStatisticsResponse,
  ClassStatistics,
  SubjectStatistics,
} from '@/types/statistics'

/** API 路径前缀 */
const BASE_URL = '/statistics'

/**
 * 获取统计数据
 * @param params 查询参数（class_name、subject、exam_type、metrics）
 */
export function getStatistics(params?: StatisticsQuery & { metrics?: string }) {
  return get<StatisticsResponse>(BASE_URL, { params })
}

/**
 * 获取单科排名数据
 * @param params 查询参数（subject必填、exam_type必填、class_name、order、limit）
 */
export function getRanking(params: {
  class_name?: string
  subject: string
  exam_type: string
  scope?: 'class' | 'grade'
  limit?: number
}) {
  // 后端实际路径为 /ranking/subject（单科排名）
  const { scope, ...rest } = params
  return get<RankingResponse>(`${BASE_URL}/ranking/subject`, { params: rest })
}

/**
 * 获取总分排名数据
 * @param params 查询参数（exam_type必填、class_name、order、limit）
 */
export function getTotalRanking(params: {
  exam_type: string
  class_name?: string
  order?: 'asc' | 'desc'
  limit?: number
}) {
  return get<TotalRankingResponse>(`${BASE_URL}/ranking/total`, { params })
}

/**
 * 获取学生综合统计
 * @param studentId 学号
 * @param params 查询参数（exam_type）
 */
export function getStudentStatistics(studentId: string, params?: { exam_type?: string }) {
  return get<StudentStatisticsResponse>(`${BASE_URL}/student/${studentId}`, { params })
}

/**
 * 获取综合统计报告
 * @param params 查询参数（class_name、subject、exam_type、top_n）
 */
export function getReport(params?: {
  class_name?: string
  subject?: string
  exam_type?: string
  top_n?: number
}) {
  return get<{
    class_name?: string
    subject?: string
    exam_type?: string
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
  }>(`${BASE_URL}/report`, { params })
}

/**
 * 批量获取所有班级统计数据（避免 N+1 查询）
 * @param params 查询参数（exam_type）
 */
export function getBatchClassStatistics(params?: { exam_type?: string }) {
  return get<{ classes: ClassStatistics[] }>(`${BASE_URL}/batch/classes`, { params })
}

/**
 * 批量获取所有科目统计数据（避免 N+1 查询）
 * @param params 查询参数（class_name、exam_type）
 */
export function getBatchSubjectStatistics(params?: {
  class_name?: string
  exam_type?: string
}) {
  return get<{ subjects: SubjectStatistics[] }>(`${BASE_URL}/batch/subjects`, { params })
}
