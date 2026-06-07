/**
 * 仪表盘相关 API
 */

import { get } from '@/utils/request'

/** 仪表盘统计数据响应类型 */
export interface DashboardStats {
  /** 学生总数 */
  total_students: number
  /** 成绩记录总数 */
  total_grades: number
  /** 平均分 */
  average_score: number
  /** 及格率（百分比） */
  pass_rate: number
}

/** API 路径前缀 */
const BASE_URL = '/dashboard'

/**
 * 获取仪表盘统计数据
 * 返回学生总数、成绩记录总数、平均分和及格率
 */
export function getDashboardStats() {
  return get<{ success: boolean; data: DashboardStats }>(`${BASE_URL}/stats`)
}
