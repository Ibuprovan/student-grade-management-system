/**
 * 成绩相关 API
 */

import { get, post, put, del, upload } from '@/utils/request'
import type {
  Grade,
  GradeCreate,
  GradeBatchCreate,
  GradeUpdate,
  GradeListParams,
  GradeListResponse,
  BatchImportResponse,
} from '@/types/grade'

/** API 路径前缀 */
const BASE_URL = '/grades'

/**
 * 获取成绩列表（支持多维度筛选）
 * @param params 查询参数（包含 student_id、class_name、subject、exam_type、keyword、page、page_size）
 */
export function getGradeList(params?: GradeListParams) {
  return get<GradeListResponse>(`${BASE_URL}/search`, { params })
}

/**
 * 获取成绩详情
 * @param gradeId 成绩ID
 */
export function getGradeDetail(gradeId: number) {
  return get<Grade>(`${BASE_URL}/${gradeId}`)
}

/**
 * 创建成绩
 * @param data 成绩数据
 */
export function createGrade(data: GradeCreate) {
  return post<Grade>(BASE_URL, data)
}

/**
 * 批量创建成绩
 * @param data 批量成绩数据
 */
export function batchCreateGrades(data: GradeBatchCreate) {
  return post<Grade[]>(`${BASE_URL}/batch`, data)
}

/**
 * 更新成绩
 * @param gradeId 成绩ID
 * @param data 更新数据
 */
export function updateGrade(gradeId: number, data: GradeUpdate) {
  return put<Grade>(`${BASE_URL}/${gradeId}`, data)
}

/**
 * 删除成绩
 * @param gradeId 成绩ID
 */
export function deleteGrade(gradeId: number) {
  return del<void>(`${BASE_URL}/${gradeId}`)
}

/**
 * 导入成绩（CSV）
 * @param file 文件
 * @param examType 考试类型
 * @param examDate 考试日期
 */
export function importGrades(file: File, examType: string, examDate: string) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('exam_type', examType)
  formData.append('exam_date', examDate)
  return upload<BatchImportResponse>('/import/grades', formData)
}

/**
 * 导出成绩数据
 * @param params 筛选参数
 */
export function exportGrades(params?: {
  class_name?: string
  subject?: string
  exam_type?: string
  format?: 'csv' | 'json'
}) {
  return get('/export/grades', { params, responseType: 'blob' })
}

/**
 * 检查成绩是否重复
 * @param studentId 学号
 * @param subject 科目
 * @param examType 考试类型
 */
export function checkGradeDuplicate(
  studentId: string,
  subject: string,
  examType: string,
) {
  return get<{ exists: boolean }>(`${BASE_URL}/check-duplicate`, {
    params: { student_id: studentId, subject, exam_type: examType },
  })
}
