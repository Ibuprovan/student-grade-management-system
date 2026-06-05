/**
 * 学生组合式函数
 * 封装学生相关业务逻辑，可复用于多个页面
 */

import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useStudentStore } from '@/stores/student'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Student, StudentCreate, StudentUpdate, StudentListParams } from '@/types/student'

export interface UseStudentOptions {
  /** 是否自动加载数据 */
  autoLoad?: boolean
  /** 默认每页条数 */
  defaultPageSize?: number
}

export function useStudent(options: UseStudentOptions = {}) {
  const { autoLoad = false, defaultPageSize = 20 } = options

  const router = useRouter()
  const studentStore = useStudentStore()

  /** 加载状态 */
  const loading = ref(false)

  /** 搜索参数 */
  const searchParams = ref<StudentListParams>({})

  /** 选中的学生 */
  const selectedStudents = ref<Student[]>([])

  /** 学生列表 */
  const students = computed(() => studentStore.students)

  /** 当前学生 */
  const currentStudent = computed(() => studentStore.currentStudent)

  /** 分页信息 */
  const pagination = computed(() => studentStore.pagination)

  /** 班级列表 */
  const classList = computed(() => studentStore.classList)

  /** 是否有数据 */
  const hasStudents = computed(() => studentStore.hasStudents)

  /** 学生总数 */
  const studentCount = computed(() => studentStore.studentCount)

  /**
   * 获取学生列表
   * @param params 查询参数
   */
  async function fetchStudents(params?: StudentListParams) {
    loading.value = true
    try {
      await studentStore.fetchStudents(params)
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
      await studentStore.fetchStudentDetail(studentId)
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
      const newStudent = await studentStore.createStudent(data)
      ElMessage.success('学生创建成功')
      return newStudent
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
      const updatedStudent = await studentStore.updateStudent(studentId, data)
      ElMessage.success('学生信息更新成功')
      return updatedStudent
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除学生
   * @param studentId 学号
   * @param confirm 是否显示确认对话框
   */
  async function deleteStudent(studentId: string, confirm = true) {
    if (confirm) {
      try {
        await ElMessageBox.confirm('确定要删除该学生吗？此操作不可恢复。', '确认删除', {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
        })
      } catch {
        return false
      }
    }

    loading.value = true
    try {
      await studentStore.deleteStudent(studentId)
      return true
    } finally {
      loading.value = false
    }
  }

  /**
   * 批量删除学生
   * @param students 要删除的学生列表
   */
  async function batchDeleteStudents(students: Student[]) {
    if (students.length === 0) {
      ElMessage.warning('请先选择要删除的学生')
      return false
    }

    try {
      await ElMessageBox.confirm(
        `确定要删除选中的 ${students.length} 名学生吗？此操作不可恢复。`,
        '批量删除确认',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )
    } catch {
      return false
    }

    loading.value = true
    try {
      const promises = students.map((student) =>
        studentStore.deleteStudent(student.student_id)
      )
      await Promise.all(promises)
      ElMessage.success(`成功删除 ${students.length} 名学生`)
      selectedStudents.value = []
      return true
    } finally {
      loading.value = false
    }
  }

  /**
   * 搜索学生
   * @param params 搜索参数
   */
  function search(params: StudentListParams) {
    searchParams.value = params
    studentStore.setSearchParams(params)
    studentStore.fetchStudents()
  }

  /**
   * 重置搜索
   */
  function resetSearch() {
    searchParams.value = {}
    studentStore.clearSearchParams()
    studentStore.fetchStudents()
  }

  /**
   * 设置页码
   * @param page 页码
   */
  function setPage(page: number) {
    studentStore.setPage(page)
    studentStore.fetchStudents()
  }

  /**
   * 设置每页条数
   * @param pageSize 每页条数
   */
  function setPageSize(pageSize: number) {
    studentStore.setPageSize(pageSize)
    studentStore.fetchStudents()
  }

  /**
   * 跳转到添加页面
   */
  function goToAdd() {
    router.push('/student/add')
  }

  /**
   * 跳转到编辑页面
   * @param studentId 学号
   */
  function goToEdit(studentId: string) {
    router.push(`/student/edit/${studentId}`)
  }

  /**
   * 跳转到详情页面
   * @param studentId 学号
   */
  function goToDetail(studentId: string) {
    router.push(`/student/detail/${studentId}`)
  }

  /**
   * 返回列表页面
   */
  function goToList() {
    router.push('/student/list')
  }

  /**
   * 导出学生数据
   * @param data 要导出的数据
   * @param filename 文件名
   */
  function exportStudents(data: Student[], filename?: string) {
    const headers = ['学号', '姓名', '性别', '班级', '入学年份', '创建时间']
    const rows = data.map((student) => [
      student.student_id,
      student.name,
      student.gender,
      student.class_name,
      student.enrollment_year,
      student.created_at,
    ])

    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.join(',')),
    ].join('\n')

    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename || `学生列表_${new Date().toISOString().slice(0, 10)}.csv`
    link.click()
    URL.revokeObjectURL(link.href)

    ElMessage.success('导出成功')
  }

  /**
   * 获取班级列表
   */
  function fetchClassList() {
    studentStore.fetchClassList()
  }

  // 初始化
  if (autoLoad) {
    fetchStudents()
    fetchClassList()
  }

  return {
    // 状态
    loading,
    students,
    currentStudent,
    pagination,
    searchParams,
    selectedStudents,
    classList,
    hasStudents,
    studentCount,

    // 方法
    fetchStudents,
    fetchStudentDetail,
    createStudent,
    updateStudent,
    deleteStudent,
    batchDeleteStudents,
    search,
    resetSearch,
    setPage,
    setPageSize,
    goToAdd,
    goToEdit,
    goToDetail,
    goToList,
    exportStudents,
    fetchClassList,
  }
}
