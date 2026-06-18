/**
 * 班主任相关 API
 */

import { get, post, del } from '@/utils/request'

/** 班主任信息 */
export interface ClassTeacherInfo {
  id: number
  class_name: string
  enrollment_year: number
  class_number: number
  teacher_name: string
  username?: string
  user_id?: number
  created_at?: string
}

/** 可分配班级信息 */
export interface AvailableClass {
  class_name: string
  enrollment_year: number
  class_number: number
  student_count: number
}

/** 创建班主任请求 */
export interface ClassTeacherCreateRequest {
  class_name: string
  enrollment_year: number
  class_number: number
  teacher_name: string
}

/** 管理员：获取可分配的班级列表 */
export function getAvailableClasses() {
  return get<{ success: boolean; data: AvailableClass[] }>('/class-teachers/available-classes')
}

/** 管理员：获取班主任列表 */
export function getClassTeacherList() {
  return get<{ success: boolean; data: ClassTeacherInfo[] }>('/class-teachers')
}

/** 管理员：添加班主任 */
export function createClassTeacher(data: ClassTeacherCreateRequest) {
  return post<{ success: boolean; data: ClassTeacherInfo; message: string }>('/class-teachers', data)
}

/** 管理员：删除班主任 */
export function deleteClassTeacher(id: number) {
  return del<{ success: boolean; message: string }>(`/class-teachers/${id}`)
}

/** 班主任：获取班级仪表盘 */
export function getCtDashboard(class_name?: string) {
  return get<{ success: boolean; data: Record<string, unknown> }>('/class-teacher/dashboard', {
    params: class_name ? { class_name } : undefined,
  })
}

/** 班主任：获取班级学生列表 */
export function getCtStudents(params?: { class_name?: string; page?: number; page_size?: number }) {
  return get<{ success: boolean; data: { items: unknown[]; total: number; page: number; page_size: number; total_pages: number } }>('/class-teacher/students', { params })
}

/** 班主任：获取班级成绩列表 */
export function getCtGrades(params?: { class_name?: string; subject?: string; exam_type?: string; page?: number; page_size?: number }) {
  return get<{ success: boolean; data: { items: unknown[]; total: number; page: number; page_size: number; total_pages: number } }>('/class-teacher/grades', { params })
}

/** 班主任：获取班级统计概览 */
export function getCtStatisticsOverview(params?: { class_name?: string; exam_type?: string }) {
  return get<{ success: boolean; data: Record<string, unknown> }>('/class-teacher/statistics/overview', { params })
}

/** 班主任：获取班级科目统计 */
export function getCtSubjectStatistics(params?: { class_name?: string; subject?: string; exam_type?: string }) {
  return get<{ success: boolean; data: Record<string, unknown> }>('/class-teacher/statistics/subject', { params })
}
