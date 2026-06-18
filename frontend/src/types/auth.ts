/**
 * 认证相关类型定义
 *
 * 定义登录请求、Token 响应、用户信息等认证相关的数据模型
 */

/** 登录请求 */
export interface LoginRequest {
  username: string
  password: string
}

/** Token 响应 */
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

/** 刷新 Token 请求 */
export interface RefreshRequest {
  refresh_token: string
}

/** 用户信息 */
export interface UserInfo {
  id: number
  username: string
  role: 'admin' | 'teacher' | 'class_teacher' | 'subject_leader' | 'student'
  is_active: boolean
  need_change_password: boolean
}

/** 认证状态 */
export interface AuthState {
  user: UserInfo | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
}

/** 认证 API 响应 */
export interface AuthApiResponse<T = unknown> {
  success: boolean
  data: T
  message?: string
  error?: {
    code: string
    message: string
  } | null
}
