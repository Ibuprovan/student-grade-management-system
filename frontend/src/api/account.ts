/**
 * 账号管理 API
 */

import { get, post } from '@/utils/request'

export interface AccountInfo {
  user_id: number
  username: string
  role: string
  is_active: boolean
  need_change_password: boolean
  detail: Record<string, unknown> | null
}

export function getAccounts(role?: string) {
  return get<{ success: boolean; data: AccountInfo[] }>('/accounts', { params: role ? { role } : undefined })
}

export function getStudentAccounts() {
  return get<{ success: boolean; data: AccountInfo[] }>('/accounts/students')
}

export function getClassTeacherAccounts() {
  return get<{ success: boolean; data: AccountInfo[] }>('/accounts/class-teachers')
}

export function getSubjectLeaderAccounts() {
  return get<{ success: boolean; data: AccountInfo[] }>('/accounts/subject-leaders')
}

export function resetAccountPassword(userId: number) {
  return post<{ success: boolean; message: string; data: { username: string; new_password: string } }>(`/accounts/${userId}/reset-password`)
}
