/**
 * 成绩状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Grade,
  GradeCreate,
  GradeUpdate,
  GradeBatchCreate,
  GradeListParams,
  BatchImportResponse,
} from '@/types/grade'
import * as gradeApi from '@/api/grade'
import { ElMessage } from 'element-plus'

export const useGradeStore = defineStore('grade', () => {
  // ========== 状态 ==========

  /** 成绩列表 */
  const grades = ref<Grade[]>([])

  /** 当前查看的成绩 */
  const currentGrade = ref<Grade | null>(null)

  /** 加载状态 */
  const loading = ref(false)

  /** 分页信息 */
  const pagination = ref({
    page: 1,
    pageSize: 20,
    total: 0,
  })

  /** 搜索参数 */
  const searchParams = ref<GradeListParams>({})

  /** 最近导入结果 */
  const lastImportResult = ref<BatchImportResponse | null>(null)

  // ========== 计算属性 ==========

  /** 成绩总数 */
  const gradeCount = computed(() => pagination.value.total)

  /** 是否有成绩数据 */
  const hasGrades = computed(() => grades.value.length > 0)

  /** 总页数 */
  const totalPages = computed(() =>
    Math.ceil(pagination.value.total / pagination.value.pageSize),
  )

  // ========== 操作 ==========

  /**
   * 获取成绩列表
   * @param params 查询参数
   */
  async function fetchGrades(params?: GradeListParams) {
    loading.value = true
    try {
      const queryParams: GradeListParams = {
        page: pagination.value.page,
        page_size: pagination.value.pageSize,
        ...searchParams.value,
        ...params,
      }
      const response = await gradeApi.getGradeList(queryParams)
      // 响应拦截器返回 BackendResponse，实际数据在 .data 中
      const paginatedData = (response as any).data || response
      grades.value = paginatedData.items || []
      pagination.value.total = paginatedData.total || 0
    } catch (error) {
      console.error('获取成绩列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建成绩
   * @param data 成绩数据
   */
  async function createGrade(data: GradeCreate) {
    loading.value = true
    try {
      const newGrade = await gradeApi.createGrade(data)
      grades.value.unshift(newGrade)
      pagination.value.total++
      ElMessage.success('成绩录入成功')
      return newGrade
    } catch (error) {
      console.error('创建成绩失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新成绩
   * @param gradeId 成绩ID
   * @param data 更新数据
   */
  async function updateGrade(gradeId: number, data: GradeUpdate) {
    loading.value = true
    try {
      const updatedGrade = await gradeApi.updateGrade(gradeId, data)
      const index = grades.value.findIndex((g) => g.grade_id === gradeId)
      if (index !== -1) {
        grades.value[index] = updatedGrade
      }
      if (currentGrade.value?.grade_id === gradeId) {
        currentGrade.value = updatedGrade
      }
      ElMessage.success('成绩更新成功')
      return updatedGrade
    } catch (error) {
      console.error('更新成绩失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 批量创建成绩
   * @param data 批量成绩数据
   */
  async function batchCreateGrades(data: GradeBatchCreate) {
    loading.value = true
    try {
      const result = await gradeApi.batchCreateGrades(data)
      ElMessage.success(`成功录入 ${result.length} 条成绩`)
      // 刷新列表
      await fetchGrades()
      return result
    } catch (error) {
      console.error('批量创建成绩失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除成绩
   * @param gradeId 成绩ID
   */
  async function deleteGrade(gradeId: number) {
    loading.value = true
    try {
      await gradeApi.deleteGrade(gradeId)
      grades.value = grades.value.filter((g) => g.grade_id !== gradeId)
      pagination.value.total--
      ElMessage.success('成绩删除成功')
    } catch (error) {
      console.error('删除成绩失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 导入成绩
   * @param file 文件
   * @param examType 考试类型
   * @param examDate 考试日期
   */
  async function importGrades(file: File, examType: string, examDate: string) {
    loading.value = true
    try {
      const response = await gradeApi.importGrades(file, examType, examDate)
      // 响应拦截器返回完整的 BackendResponse，实际数据在 .data 中
      const result = (response as any).data || response
      lastImportResult.value = result
      ElMessage.success(`成功导入 ${result.success_count} 条成绩，失败 ${result.fail_count} 条`)
      // 刷新列表
      await fetchGrades()
      return result
    } catch (error) {
      console.error('导入成绩失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 检查成绩是否重复
   * @param studentId 学号
   * @param subject 科目
   * @param examType 考试类型
   */
  async function checkDuplicate(studentId: string, subject: string, examType: string) {
    try {
      const result = await gradeApi.checkGradeDuplicate(studentId, subject, examType)
      return result.exists
    } catch (error) {
      console.error('检查重复成绩失败:', error)
      return false
    }
  }

  /**
   * 导出成绩数据（获取所有符合条件的数据）
   * @param params 查询参数
   */
  async function exportGrades(params?: GradeListParams) {
    loading.value = true
    try {
      const queryParams: GradeListParams = {
        page: 1,
        page_size: 100, // 后端最大允许值
        ...searchParams.value,
        ...params,
      }
      const response = await gradeApi.getGradeList(queryParams)
      // 响应拦截器返回 BackendResponse，实际数据在 .data 中
      const paginatedData = (response as any).data || response
      return paginatedData
    } catch (error) {
      console.error('导出成绩数据失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /** 设置页码 */
  function setPage(page: number) {
    pagination.value.page = page
  }

  /** 设置每页条数 */
  function setPageSize(pageSize: number) {
    pagination.value.pageSize = pageSize
    pagination.value.page = 1
  }

  /** 设置搜索参数 */
  function setSearchParams(params: GradeListParams) {
    searchParams.value = params
    pagination.value.page = 1
  }

  /** 清空搜索参数 */
  function clearSearchParams() {
    searchParams.value = {}
    pagination.value.page = 1
  }

  return {
    // 状态
    grades,
    currentGrade,
    loading,
    pagination,
    searchParams,
    lastImportResult,

    // 计算属性
    gradeCount,
    hasGrades,
    totalPages,

    // 操作
    fetchGrades,
    createGrade,
    updateGrade,
    batchCreateGrades,
    deleteGrade,
    importGrades,
    exportGrades,
    checkDuplicate,
    setPage,
    setPageSize,
    setSearchParams,
    clearSearchParams,
  }
})
