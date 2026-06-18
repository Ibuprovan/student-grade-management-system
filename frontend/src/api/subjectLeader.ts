/**
 * 学科教研组组长相关 API
 */

import { get, post, del } from '@/utils/request'

export interface SubjectLeaderInfo {
  id: number
  subject: string
  subject_en: string
  leader_name: string
  username?: string
  user_id?: number
  created_at?: string
}

export interface AvailableSubject {
  subject: string
  subject_en: string
}

export function getAvailableSubjects() {
  return get<{ success: boolean; data: AvailableSubject[] }>('/subject-leaders/available-subjects')
}

export function getSubjectLeaderList() {
  return get<{ success: boolean; data: SubjectLeaderInfo[] }>('/subject-leaders')
}

export function createSubjectLeader(data: { subject: string; leader_name: string }) {
  return post<{ success: boolean; data: SubjectLeaderInfo; message: string }>('/subject-leaders', data)
}

export function deleteSubjectLeader(id: number) {
  return del<{ success: boolean; message: string }>(`/subject-leaders/${id}`)
}

export function getSlDashboard(params?: { subject?: string }) {
  return get<{ success: boolean; data: Record<string, unknown> }>('/subject-leader/dashboard', { params })
}

export function getSlGrades(params?: { subject?: string; class_name?: string; exam_type?: string; search?: string; page?: number; page_size?: number }) {
  return get<{ success: boolean; data: { items: unknown[]; total: number; page: number; page_size: number; total_pages: number } }>('/subject-leader/grades', { params })
}

export function getSlStatistics(params?: { subject?: string; class_name?: string; exam_type?: string }) {
  return get<{ success: boolean; data: Record<string, unknown> }>('/subject-leader/statistics', { params })
}
