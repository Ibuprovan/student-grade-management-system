/**
 * 成绩相关组合式函数
 * 封装成绩相关的业务逻辑和状态
 */

import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useGradeStore } from '@/stores/grade'
import { useStudentStore } from '@/stores/student'
import { ElMessage, ElMessageBox } from 'element-plus'
import { downloadCSV } from '@/utils/export'
import { getStudentList, getStudentDetail } from '@/api/student'
import { getGradeDetail } from '@/api/grade'
import { useDebounce } from '@/composables/useCommon'
import type { Grade, GradeCreate, GradeListParams, Subject, ExamType, ImportPreviewItem } from '@/types/grade'
import type { Student } from '@/types/student'
import { SUBJECTS, EXAM_TYPES } from '@/types/grade'

/**
 * 成绩列表组合式函数
 */
export function useGradeList() {
  const router = useRouter()
  const gradeStore = useGradeStore()

  /** 搜索参数 */
  const searchForm = ref({
    class_name: '',
    subject: '' as Subject | '',
    exam_type: '' as ExamType | '',
    keyword: '',
  })

  /** 科目选项 */
  const subjectOptions = SUBJECTS

  /** 考试类型选项 */
  const examTypeOptions = EXAM_TYPES

  /** 班级选项（从学生模块获取） */
  const studentStore = useStudentStore()
  const classOptions = computed(() => studentStore.classList)

  /** 初始化班级列表 */
  studentStore.fetchClassList()

  /** 执行搜索 */
  function handleSearch() {
    const params: GradeListParams = {}
    if (searchForm.value.class_name) params.class_name = searchForm.value.class_name
    if (searchForm.value.subject) params.subject = searchForm.value.subject as Subject
    if (searchForm.value.exam_type) params.exam_type = searchForm.value.exam_type as ExamType
    if (searchForm.value.keyword) params.keyword = searchForm.value.keyword

    gradeStore.setSearchParams(params)
    gradeStore.fetchGrades()
  }

  /** 防抖搜索（用于关键字输入） */
  const { debounced: debouncedSearch } = useDebounce(handleSearch, 300)

  /** 重置搜索 */
  function handleReset() {
    searchForm.value = {
      class_name: '',
      subject: '',
      exam_type: '',
      keyword: '',
    }
    gradeStore.clearSearchParams()
    gradeStore.fetchGrades()
  }

  /** 页码变化 */
  function handlePageChange(page: number) {
    gradeStore.setPage(page)
    gradeStore.fetchGrades()
  }

  /** 每页条数变化 */
  function handleSizeChange(size: number) {
    gradeStore.setPageSize(size)
    gradeStore.fetchGrades()
  }

  /** 跳转录入页面 */
  function goToAdd() {
    router.push('/grade/input')
  }

  /** 跳转导入页面 */
  function goToImport() {
    router.push('/grade/import')
  }

  /** 跳转编辑页面 */
  function goToEdit(gradeId: number) {
    router.push({ path: '/grade/input', query: { id: gradeId } })
  }

  /** 删除成绩 */
  async function handleDelete(grade: Grade) {
    try {
      await ElMessageBox.confirm(
        `确定要删除学生 ${grade.student?.name || grade.student_id} 的 ${grade.subject} 成绩吗？`,
        '删除确认',
        { type: 'warning' },
      )
      await gradeStore.deleteGrade(grade.grade_id)
    } catch {
      // 用户取消
    }
  }

  /** 导出成绩 */
  async function handleExport() {
    try {
      const params: GradeListParams = {}
      if (searchForm.value.class_name) params.class_name = searchForm.value.class_name
      if (searchForm.value.subject) params.subject = searchForm.value.subject as Subject
      if (searchForm.value.exam_type) params.exam_type = searchForm.value.exam_type as ExamType
      if (searchForm.value.keyword) params.keyword = searchForm.value.keyword

      // 获取当前筛选条件下的所有成绩数据
      const response = await gradeStore.exportGrades(params)
      const grades = response.items || []

      if (grades.length === 0) {
        ElMessage.warning('没有可导出的数据')
        return
      }

      // 生成 CSV 内容
      const headers = ['学号', '姓名', '班级', '科目', '考试类型', '分数', '考试日期']
      const rows = grades.map((grade: any) => [
        grade.student_id,
        grade.student_name || '-',
        grade.class_name || '-',
        grade.subject,
        grade.exam_type,
        grade.score,
        grade.exam_date,
      ])

      downloadCSV(headers, rows, '成绩列表')
      ElMessage.success(`成功导出 ${grades.length} 条成绩记录`)
    } catch (error) {
      console.error('导出失败:', error)
      ElMessage.error('导出失败')
    }
  }

  return {
    // 状态
    searchForm,
    subjectOptions,
    examTypeOptions,
    classOptions,

    // 方法
    handleSearch,
    debouncedSearch,
    handleReset,
    handlePageChange,
    handleSizeChange,
    goToAdd,
    goToImport,
    goToEdit,
    handleDelete,
    handleExport,
  }
}

/**
 * 成绩录入组合式函数
 */
export function useGradeForm() {
  const router = useRouter()
  const gradeStore = useGradeStore()

  /** 科目选项 */
  const subjectOptions = SUBJECTS

  /** 考试类型选项 */
  const examTypeOptions = EXAM_TYPES

  /** 最近录入记录 */
  const recentRecords = ref<Array<{
    student_id: string
    student_name: string
    subject: string
    score: number
    time: string
    status: 'success' | 'error'
  }>>([])

  /** 学生搜索状态 */
  const studentSearching = ref(false)

  /** 学生选项（搜索结果） */
  const studentOptions = ref<Student[]>([])

  /** 搜索学生（用于表单下拉选择） */
  async function searchStudents(query: string) {
    if (!query || query.length < 1) {
      studentOptions.value = []
      return
    }

    studentSearching.value = true
    try {
      const result = await getStudentList({ keyword: query, page_size: 20 })
      studentOptions.value = result.items
    } catch (error) {
      console.error('搜索学生失败:', error)
    } finally {
      studentSearching.value = false
    }
  }

  /**
   * 加载成绩详情（编辑模式）
   * 同时加载关联的学生信息
   */
  async function loadGradeForEdit(gradeId: number) {
    const grade = await getGradeDetail(gradeId)
    const student = await getStudentDetail(grade.student_id)
    studentOptions.value = [student]
    return { grade, student }
  }

  /** 检查重复 */
  async function checkDuplicate(studentId: string, subject: string, examType: string) {
    return await gradeStore.checkDuplicate(studentId, subject, examType)
  }

  /** 添加最近记录 */
  function addRecentRecord(record: {
    student_id: string
    student_name: string
    subject: string
    score: number
    status: 'success' | 'error'
  }) {
    recentRecords.value.unshift({
      ...record,
      time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    })
    // 只保留最近 10 条
    if (recentRecords.value.length > 10) {
      recentRecords.value = recentRecords.value.slice(0, 10)
    }
  }

  /** 返回列表 */
  function goBack() {
    router.push('/grade/list')
  }

  return {
    subjectOptions,
    examTypeOptions,
    recentRecords,
    studentSearching,
    studentOptions,
    searchStudents,
    loadGradeForEdit,
    checkDuplicate,
    addRecentRecord,
    goBack,
    createGrade: gradeStore.createGrade,
    updateGrade: gradeStore.updateGrade,
  }
}

/**
 * 成绩导入组合式函数
 */
export function useGradeImport() {
  const router = useRouter()
  const gradeStore = useGradeStore()

  /** 科目选项 */
  const subjectOptions = SUBJECTS

  /** 考试类型选项 */
  const examTypeOptions = EXAM_TYPES

  /** CSV 模板内容 */
  const csvTemplate = '学号,科目,考试类型,分数,考试日期\n20260001,数学,期中,95.0,2026-04-15\n20260001,语文,期中,88.5,2026-04-15\n20260002,数学,期中,92.0,2026-04-15'

  /**
   * 解析 CSV 文件
   * @param file CSV 文件
   * @returns 解析后的数据
   */
  function parseCSV(file: File): Promise<ImportPreviewItem[]> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const text = e.target?.result as string
          const lines = text.split('\n').filter((line) => line.trim())

          if (lines.length < 2) {
            reject(new Error('CSV 文件为空或格式错误'))
            return
          }

          // 跳过标题行
          const dataLines = lines.slice(1)
          const items: ImportPreviewItem[] = dataLines.map((line, index) => {
            const parts = line.split(',').map((p) => p.trim())
            const item: ImportPreviewItem = {
              row: index + 2,
              student_id: parts[0] || '',
              subject: parts[1] || '',
              exam_type: parts[2] || '',
              score: parseFloat(parts[3]) || 0,
              exam_date: parts[4] || '',
              valid: true,
            }

            // 验证数据
            const errors: string[] = []
            if (!item.student_id || !/^\d{8}$/.test(item.student_id)) {
              errors.push('学号格式错误')
            }
            if (!SUBJECTS.includes(item.subject as Subject)) {
              errors.push('科目不存在')
            }
            if (!EXAM_TYPES.includes(item.exam_type as ExamType)) {
              errors.push('考试类型不存在')
            }
            if (isNaN(item.score) || item.score < 0 || item.score > 100) {
              errors.push('分数超出范围')
            }
            if (!item.exam_date || !/^\d{4}-\d{2}-\d{2}$/.test(item.exam_date)) {
              errors.push('日期格式错误')
            }

            if (errors.length > 0) {
              item.valid = false
              item.error = errors.join('；')
            }

            return item
          })

          resolve(items)
        } catch (error) {
          reject(error)
        }
      }
      reader.onerror = () => reject(new Error('文件读取失败'))
      reader.readAsText(file)
    })
  }

  /**
   * 下载 CSV 模板
   */
  function downloadTemplate() {
    const blob = new Blob(['\uFEFF' + csvTemplate], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '成绩导入模板.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  /**
   * 下载失败记录
   * @param failedItems 失败的数据项
   */
  function downloadFailedRecords(failedItems: Array<{ student_id: string; error: string }>) {
    const header = '学号,错误原因'
    const rows = failedItems.map((item) => `${item.student_id},${item.error}`)
    const csv = [header, ...rows].join('\n')
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '导入失败记录.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  /** 返回列表 */
  function goBack() {
    router.push('/grade/list')
  }

  /** 继续导入 */
  function continueImport() {
    // 重置状态由组件处理
  }

  return {
    subjectOptions,
    examTypeOptions,
    parseCSV,
    downloadTemplate,
    downloadFailedRecords,
    goBack,
    continueImport,
    importGrades: gradeStore.importGrades,
  }
}
