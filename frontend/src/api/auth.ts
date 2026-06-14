/**
 * 认证相关 API
 *
 * 提供用户认证相关的 API 接口封装
 */

import { post, get } from '@/utils/request'
import type {
  LoginRequest,
  TokenResponse,
  RefreshRequest,
  UserInfo,
  AuthApiResponse,
} from '@/types/auth'

/** API 路径前缀 */
const BASE_URL = '/auth'

/** 学生信息接口 */
export interface StudentInfo {
  student_id: string
  name: string
  gender: string
  class_name: string
  enrollment_year: number
}

/**
 * 用户登录
 * @param data 登录请求数据（用户名、密码）
 * @returns Token 响应（access_token、refresh_token）
 */
export function login(data: LoginRequest): Promise<AuthApiResponse<TokenResponse>> {
  return post<AuthApiResponse<TokenResponse>>(`${BASE_URL}/login`, data)
}

/**
 * 刷新 Token
 * @param data 刷新请求数据（refresh_token）
 * @returns 新的 Token 响应
 */
export function refreshToken(data: RefreshRequest): Promise<AuthApiResponse<TokenResponse>> {
  return post<AuthApiResponse<TokenResponse>>(`${BASE_URL}/refresh`, data)
}

/**
 * 用户登出
 * @returns 登出结果
 */
export function logout(): Promise<AuthApiResponse<void>> {
  return post<AuthApiResponse<void>>(`${BASE_URL}/logout`)
}

/**
 * 获取当前用户信息
 * @returns 用户信息
 */
export function getCurrentUser(): Promise<AuthApiResponse<UserInfo>> {
  return get<AuthApiResponse<UserInfo>>(`${BASE_URL}/me`)
}

/**
 * 获取当前学生用户关联的学生信息
 * @returns 学生信息（学号、姓名、班级等）
 */
export function getCurrentStudentInfo(): Promise<AuthApiResponse<StudentInfo>> {
  return get<AuthApiResponse<StudentInfo>>(`${BASE_URL}/me/student-info`)
}

/**
 * 修改密码
 * @param oldPassword 旧密码
 * @param newPassword 新密码
 * @returns 修改结果
 */
export function changePassword(oldPassword: string, newPassword: string): Promise<AuthApiResponse<void>> {
  return post<AuthApiResponse<void>>(`${BASE_URL}/change-password`, {
    old_password: oldPassword,
    new_password: newPassword,
  })
}
