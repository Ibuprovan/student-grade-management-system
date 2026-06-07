/**
 * 仪表盘状态管理
 *
 * 使用 Pinia 管理仪表盘页面的状态，包括：
 * - 统计数据（学生总数、成绩记录总数、平均分、及格率）
 * - 加载状态
 * - 错误状态
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { DashboardStats } from '@/api/dashboard'
import * as dashboardApi from '@/api/dashboard'

export const useDashboardStore = defineStore('dashboard', () => {
  // ========== 状态 ==========

  /** 统计数据 */
  const stats = ref<DashboardStats>({
    total_students: 0,
    total_grades: 0,
    average_score: 0,
    pass_rate: 0,
  })

  /** 加载状态 */
  const loading = ref(false)

  /** 错误信息 */
  const error = ref<string | null>(null)

  // ========== 操作 ==========

  /**
   * 获取仪表盘统计数据
   * 从后端 API 获取真实的统计数据
   */
  async function fetchDashboardStats() {
    loading.value = true
    error.value = null

    try {
      const response = await dashboardApi.getDashboardStats()

      if (response.success && response.data) {
        stats.value = response.data
      }
    } catch (err: unknown) {
      console.error('获取仪表盘统计数据失败:', err)
      error.value = (err as Error).message || '获取统计数据失败'
    } finally {
      loading.value = false
    }
  }

  /**
   * 重置状态
   */
  function resetStats() {
    stats.value = {
      total_students: 0,
      total_grades: 0,
      average_score: 0,
      pass_rate: 0,
    }
    error.value = null
  }

  return {
    // 状态
    stats,
    loading,
    error,

    // 操作
    fetchDashboardStats,
    resetStats,
  }
})
