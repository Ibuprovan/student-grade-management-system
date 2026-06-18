/**
 * 教师任课分配相关 API
 */

import { get, post, del } from '@/utils/request'

export interface TeacherAssignmentInfo {
  id: number
  subject: string
  subject_en: string
  class_name: string
  teacher_name: string
  username?: string
  user_id?: number
  created_at?: string
}

export interface AvailableCombination {
  subject: string
  subject_en: string
  class_name: string
  enrollment_year: number
  class_number: number
}

export function getAvailableCombinations() {
  return get<{ success: boolean; data: AvailableCombination[] }>('/teacher-assignments/available')
}

export function getTeacherAssignmentList() {
  return get<{ success: boolean; data: TeacherAssignmentInfo[] }>('/teacher-assignments')
}

export function createTeacherAssignment(data: { subject: string; class_name: string; teacher_name: string }) {
  return post<{ success: boolean; data: TeacherAssignmentInfo; message: string }>('/teacher-assignments', data)
}

export function deleteTeacherAssignment(id: number) {
  return del<{ success: boolean; message: string }>(`/teacher-assignments/${id}`)
}

export function getTDashboard(params?: { subject?: string; class_name?: string; exam_type?: string }) {
  return get<{ success: boolean; data: unknown[] }>('/teacher/dashboard', { params })
}

export function getTGrades(params?: { subject?: string; class_name?: string; exam_type?: string; search?: string; page?: number; page_size?: number }) {
  return get<{ success: boolean; data: { items: unknown[]; total: number; page: number; page_size: number; total_pages: number } }>('/teacher/grades', { params })
}

export function getTStatistics(params?: { subject?: string; class_name?: string; exam_type?: string }) {
  return get<{ success: boolean; data: unknown[] }>('/teacher/statistics', { params })
}
