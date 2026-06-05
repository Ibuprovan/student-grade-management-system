/**
 * 学生相关类型定义
 */

/** 学生信息 */
export interface Student {
  student_id: string
  name: string
  gender: '男' | '女'
  class_name: string
  enrollment_year: number
  created_at: string
  updated_at: string
}

/** 创建学生请求 */
export interface StudentCreate {
  student_id: string
  name: string
  gender: '男' | '女'
  class_name: string
  enrollment_year: number
}

/** 更新学生请求 */
export interface StudentUpdate {
  name?: string
  gender?: '男' | '女'
  class_name?: string
  enrollment_year?: number
}

/** 学生列表查询参数 */
export interface StudentListParams {
  page?: number
  page_size?: number
  class_name?: string
  keyword?: string
}

/** 分页响应 */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

/** 学生列表响应 */
export type StudentListResponse = PaginatedResponse<Student>

/** API 通用响应 */
export interface ApiResponse<T> {
  success: boolean
  data: T
  error: {
    code: string
    message: string
  } | null
}
