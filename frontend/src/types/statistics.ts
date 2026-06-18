/**
 * 统计相关类型定义
 */

import type { Subject, ExamType } from './grade'

/** 统计查询参数 */
export interface StatisticsQuery {
  class_name?: string
  subject?: Subject
  exam_type?: ExamType
  metrics?: string
}

/** 统计响应 */
export interface StatisticsResponse {
  query: {
    class_name?: string
    subject?: string
    exam_type?: string
  }
  total_students: number
  metrics: Record<string, number>
}

/** 排名项 */
export interface RankingItem {
  rank: number
  student_id: string
  student_name: string
  score: number
}

/** 排名响应 */
export interface RankingResponse {
  query: {
    class_name?: string
    subject: string
    exam_type: string
    scope?: string
  }
  rankings: RankingItem[]
}

/** 总分排名项 */
export interface TotalRankingItem {
  rank: number
  student_id: string
  student_name: string
  total_score: number
  subject_scores: Record<string, number>
}

/** 总分排名响应 */
export interface TotalRankingResponse {
  exam_type?: string
  class_name?: string
  total_count: number
  rankings: TotalRankingItem[]
}

/** 学生科目统计 */
export interface StudentSubjectStats {
  subject: string
  score: number
  class_rank?: number
  grade_rank?: number
}

/** 学生综合统计响应 */
export interface StudentStatisticsResponse {
  student_id: string
  student_name: string
  class_name: string
  exam_type?: string
  subjects: StudentSubjectStats[]
  total_score: number
  average_score: number
  class_rank_total?: number
  grade_rank_total?: number
}

// ========== 前端展示用类型（非 API 响应） ==========

/** 班级统计信息（前端展示用） */
export interface ClassStatistics {
  class_name: string
  student_count: number
  average_score: number
  max_score: number
  min_score: number
  pass_rate: number
  excellent_rate: number
}

/** 科目统计信息（前端展示用） */
export interface SubjectStatistics {
  subject: Subject
  student_count: number
  average_score: number
  max_score: number
  min_score: number
  pass_rate: number
  excellent_rate: number
  score_distribution: ScoreDistribution
}

/** 分数分布（前端展示用） */
export interface ScoreDistribution {
  '0-59': number
  '60-69': number
  '70-79': number
  '80-89': number
  '90-100': number
}
