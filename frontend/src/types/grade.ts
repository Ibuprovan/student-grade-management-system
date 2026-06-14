/**
 * 成绩相关类型定义
 */

/** 考试类型 */
export type ExamType = '期中' | '期末' | '月考' | '单元测试'

/** 科目 */
export type Subject =
  | '语文'
  | '数学'
  | '英语'
  | '物理'
  | '化学'
  | '生物'
  | '历史'
  | '地理'
  | '政治'

/** 科目列表常量 */
export const SUBJECTS: Subject[] = [
  '语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治',
]

/** 考试类型列表常量 */
export const EXAM_TYPES: ExamType[] = ['期中', '期末', '月考', '单元测试']

/** 成绩信息 */
export interface Grade {
  grade_id: number
  student_id: string
  subject: Subject
  score: number
  exam_type: ExamType
  exam_date: string
  created_at: string
  updated_at: string
  /** 关联的学生信息（可选） */
  student?: {
    student_id: string
    name: string
    class_name: string
  }
}

/** 创建成绩请求 */
export interface GradeCreate {
  student_id: string
  subject: Subject
  score: number
  exam_type: ExamType
  exam_date: string
}

/** 批量创建成绩请求 */
export interface GradeBatchCreate {
  grades: GradeCreate[]
}

/** 更新成绩请求 */
export interface GradeUpdate {
  score?: number
  exam_date?: string
  subject?: Subject
  exam_type?: ExamType
}

/** 成绩列表查询参数 */
export interface GradeListParams {
  page?: number
  page_size?: number
  student_id?: string
  subject?: Subject
  exam_type?: ExamType
  class_name?: string
  /** 学号或姓名模糊搜索 */
  keyword?: string
}

/** 成绩列表响应 */
export type GradeListResponse = PaginatedResponse<Grade>

/** 批量导入响应 */
export interface BatchImportResponse {
  total_rows: number
  success_count: number
  fail_count: number
  success_items: BatchImportSuccessItem[]
  failed_items: BatchImportFailedItem[]
  errors: BatchImportError[]
}

/** 批量导入成功项 */
export interface BatchImportSuccessItem {
  row: number
  student_id: string
  name?: string
  subject: string
  score: number
}

/** 批量导入失败项 */
export interface BatchImportFailedItem {
  row: number
  student_id: string
  subject: string
  score: number
  error: string
}

/** 批量导入错误 */
export interface BatchImportError {
  row: number
  student_id?: string
  field?: string
  error: string
  value?: string
}

/** CSV 导入预览数据项 */
export interface ImportPreviewItem {
  row: number
  student_id: string
  subject: Subject | string
  exam_type: ExamType | string
  score: number
  exam_date: string
  valid: boolean
  error?: string
}

/** 导入步骤枚举 */
export enum ImportStep {
  DOWNLOAD_TEMPLATE = 0,
  UPLOAD_FILE = 1,
  DATA_PREVIEW = 2,
  IMPORT_RESULT = 3,
}

/** 导入类型 - 从 student.ts 导入 */
import type { PaginatedResponse } from './student'
