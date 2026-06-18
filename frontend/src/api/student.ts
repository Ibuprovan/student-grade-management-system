/**
 * 学生相关 API
 */

import { get, post, put, del } from '@/utils/request'
import type {
  Student,
  StudentCreate,
  StudentUpdate,
  StudentListParams,
  StudentListResponse,
  ApiResponse,
} from '@/types/student'

/** API 路径前缀 */
const BASE_URL = '/students'

/**
 * 获取学生列表（支持搜索和筛选）
 * @param params 查询参数（包含 keyword、class_name、page、page_size）
 */
export function getStudentList(params?: StudentListParams) {
  return get<StudentListResponse>(BASE_URL, { params })
}

/**
 * 获取学生详情
 * @param studentId 学号
 */
export function getStudentDetail(studentId: string) {
  return get<Student>(`${BASE_URL}/${studentId}`)
}

/**
 * 创建学生
 * @param data 学生数据
 */
export function createStudent(data: StudentCreate) {
  return post<Student>(BASE_URL, data)
}

/**
 * 更新学生信息
 * @param studentId 学号
 * @param data 更新数据
 */
export function updateStudent(studentId: string, data: StudentUpdate) {
  return put<Student>(`${BASE_URL}/${studentId}`, data)
}

/**
 * 删除学生
 * @param studentId 学号
 */
export function deleteStudent(studentId: string) {
  return del<void>(`${BASE_URL}/${studentId}`)
}

/**
 * 批量删除学生
 * @param studentIds 学号列表
 */
export function batchDeleteStudents(studentIds: string[]) {
  return post<{ total: number; success_count: number; fail_count: number }>(
    `${BASE_URL}/batch-delete`,
    { student_ids: studentIds }
  )
}

/**
 * 删除全部学生
 * @param params 筛选条件（可选）
 */
export function deleteAllStudents(params?: { class_name?: string }) {
  return del<{ deleted_count: number }>(`${BASE_URL}/delete-all`, { params })
}

/**
 * 获取班级列表
 * 返回系统中所有学生所属的去重班级名称列表
 */
export function getClassList() {
  return get<ApiResponse<string[]>>(`${BASE_URL}/classes`)
}
