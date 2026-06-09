/**
 * 学生状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Student, StudentCreate, StudentUpdate, StudentListParams } from '@/types/student'
import * as studentApi from '@/api/student'
import { ElMessage } from 'element-plus'

export const useStudentStore = defineStore('student', () => {
  // ========== 状态 ==========

  /** 学生列表 */
  const students = ref<Student[]>([])

  /** 当前查看的学生 */
  const currentStudent = ref<Student | null>(null)

  /** 加载状态 */
  const loading = ref(false)

  /** 分页信息 */
  const pagination = ref({
    page: 1,
    pageSize: 20,
    total: 0,
  })

  /** 搜索参数 */
  const searchParams = ref<StudentListParams>({})

  /** 班级列表 */
  const classList = ref<string[]>([])

  // ========== 计算属性 ==========

  /** 学生总数 */
  const studentCount = computed(() => pagination.value.total)

  /** 是否有学生数据 */
  const hasStudents = computed(() => students.value.length > 0)

  /** 总页数 */
  const totalPages = computed(() =>
    Math.ceil(pagination.value.total / pagination.value.pageSize),
  )

  // ========== 操作 ==========

  /**
   * 获取学生列表
   * @param params 查询参数
   */
  async function fetchStudents(params?: StudentListParams) {
    loading.value = true
    try {
      const queryParams: StudentListParams = {
        page: pagination.value.page,
        page_size: pagination.value.pageSize,
        ...searchParams.value,
        ...params,
      }
      const response = await studentApi.getStudentList(queryParams)
      // 响应拦截器返回完整的 BackendResponse { success, data, error }
      // 实际数据在 response.data 中（PaginatedResponse 的 data 字段包含 items 和 total）
      const paginatedData = (response as any).data || response
      students.value = paginatedData.items || []
      pagination.value.total = paginatedData.total || 0
    } catch (error) {
      console.error('获取学生列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取学生详情
   * @param studentId 学号
   */
  async function fetchStudentDetail(studentId: string) {
    loading.value = true
    try {
      const response = await studentApi.getStudentDetail(studentId)
      // 响应拦截器返回 BackendResponse，实际数据在 .data 中
      currentStudent.value = (response as any).data || response
    } catch (error) {
      console.error('获取学生详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建学生
   * @param data 学生数据
   */
  async function createStudent(data: StudentCreate) {
    loading.value = true
    try {
      const response = await studentApi.createStudent(data)
      // 响应拦截器返回 BackendResponse，实际数据在 .data 中
      const newStudent = (response as any).data || response
      students.value.unshift(newStudent)
      pagination.value.total++
      ElMessage.success('学生创建成功')
      return newStudent
    } catch (error) {
      console.error('创建学生失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新学生信息
   * @param studentId 学号
   * @param data 更新数据
   */
  async function updateStudent(studentId: string, data: StudentUpdate) {
    loading.value = true
    try {
      const response = await studentApi.updateStudent(studentId, data)
      // 响应拦截器返回 BackendResponse，实际数据在 .data 中
      const updatedStudent = (response as any).data || response
      const index = students.value.findIndex((s) => s.student_id === studentId)
      if (index !== -1) {
        students.value[index] = updatedStudent
      }
      if (currentStudent.value?.student_id === studentId) {
        currentStudent.value = updatedStudent
      }
      ElMessage.success('学生信息更新成功')
      return updatedStudent
    } catch (error) {
      console.error('更新学生失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除学生
   * @param studentId 学号
   */
  async function deleteStudent(studentId: string) {
    loading.value = true
    try {
      await studentApi.deleteStudent(studentId)
      students.value = students.value.filter((s) => s.student_id !== studentId)
      pagination.value.total--
      if (currentStudent.value?.student_id === studentId) {
        currentStudent.value = null
      }
      ElMessage.success('学生删除成功')
    } catch (error) {
      console.error('删除学生失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取班级列表（调用专用接口）
   */
  async function fetchClassList() {
    try {
      const response = await studentApi.getClassList()
      // 响应拦截器返回 BackendResponse，班级列表在 .data 中
      const classes = (response as any).data || response
      classList.value = Array.isArray(classes) ? [...classes].sort() : []
    } catch (error) {
      console.error('获取班级列表失败:', error)
      classList.value = []
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
  function setSearchParams(params: StudentListParams) {
    searchParams.value = params
    pagination.value.page = 1
  }

  /** 清空搜索参数 */
  function clearSearchParams() {
    searchParams.value = {}
    pagination.value.page = 1
  }

  /** 重置当前学生 */
  function clearCurrentStudent() {
    currentStudent.value = null
  }

  return {
    // 状态
    students,
    currentStudent,
    loading,
    pagination,
    searchParams,
    classList,

    // 计算属性
    studentCount,
    hasStudents,
    totalPages,

    // 操作
    fetchStudents,
    fetchStudentDetail,
    createStudent,
    updateStudent,
    deleteStudent,
    fetchClassList,
    setPage,
    setPageSize,
    setSearchParams,
    clearSearchParams,
    clearCurrentStudent,
  }
})
