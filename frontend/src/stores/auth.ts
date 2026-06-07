/**
 * 认证状态管理
 *
 * 使用 Pinia 管理用户认证状态，包括：
 * - 用户信息
 * - Token 存储和管理
 * - 登录/登出操作
 * - Token 刷新机制
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo, TokenResponse } from '@/types/auth'
import * as authApi from '@/api/auth'
import { ElMessage } from 'element-plus'

/** localStorage 键名 */
const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_INFO: 'user_info',
} as const

export const useAuthStore = defineStore('auth', () => {
  // ========== 状态 ==========

  /** 当前用户信息 */
  const user = ref<UserInfo | null>(null)

  /** Access Token */
  const accessToken = ref<string | null>(null)

  /** Refresh Token */
  const refreshTokenValue = ref<string | null>(null)

  /** 加载状态 */
  const loading = ref(false)

  /** 是否正在刷新 Token */
  const isRefreshing = ref(false)

  /** Token 刷新队列 */
  let refreshSubscribers: Array<(token: string) => void> = []

  // ========== 计算属性 ==========

  /** 是否已认证 */
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)

  /** 用户角色 */
  const userRole = computed(() => user.value?.role || null)

  /** 是否是管理员 */
  const isAdmin = computed(() => user.value?.role === 'admin')

  /** 是否是教师 */
  const isTeacher = computed(() => user.value?.role === 'teacher')

  /** 是否是学生 */
  const isStudent = computed(() => user.value?.role === 'student')

  // ========== 辅助函数 ==========

  /**
   * 从 localStorage 加载认证状态
   */
  function loadFromStorage() {
    const storedAccessToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
    const storedRefreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN)
    const storedUserInfo = localStorage.getItem(STORAGE_KEYS.USER_INFO)

    if (storedAccessToken) {
      accessToken.value = storedAccessToken
    }

    if (storedRefreshToken) {
      refreshTokenValue.value = storedRefreshToken
    }

    if (storedUserInfo) {
      try {
        user.value = JSON.parse(storedUserInfo)
      } catch (e) {
        console.error('解析用户信息失败:', e)
        clearStorage()
      }
    }
  }

  /**
   * 保存认证状态到 localStorage
   */
  function saveToStorage(tokenResponse: TokenResponse, userInfo?: UserInfo) {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, tokenResponse.access_token)
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, tokenResponse.refresh_token)

    if (userInfo) {
      localStorage.setItem(STORAGE_KEYS.USER_INFO, JSON.stringify(userInfo))
    }
  }

  /**
   * 清除 localStorage 中的认证信息
   */
  function clearStorage() {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN)
    localStorage.removeItem(STORAGE_KEYS.USER_INFO)
  }

  /**
   * 更新 Token 响应到状态和 localStorage
   */
  function updateTokenResponse(tokenResponse: TokenResponse) {
    accessToken.value = tokenResponse.access_token
    refreshTokenValue.value = tokenResponse.refresh_token
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, tokenResponse.access_token)
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, tokenResponse.refresh_token)
  }

  /**
   * 将刷新失败的请求加入队列
   */
  function addRefreshSubscriber(callback: (token: string) => void) {
    refreshSubscribers.push(callback)
  }

  /**
   * 执行刷新队列中的请求
   */
  function onRefreshed(token: string) {
    refreshSubscribers.forEach((callback) => callback(token))
    refreshSubscribers = []
  }

  // ========== 操作 ==========

  /**
   * 用户登录
   * @param username 用户名
   * @param password 密码
   * @returns 是否登录成功
   */
  async function login(username: string, password: string): Promise<boolean> {
    loading.value = true
    try {
      const response = await authApi.login({ username, password })

      if (response.success && response.data) {
        const tokenResponse = response.data

        // 保存 Token
        updateTokenResponse(tokenResponse)

        // 获取用户信息
        const userResponse = await authApi.getCurrentUser()

        if (userResponse.success && userResponse.data) {
          user.value = userResponse.data
          localStorage.setItem(STORAGE_KEYS.USER_INFO, JSON.stringify(userResponse.data))
        }

        ElMessage.success('登录成功')
        return true
      }

      // 后端返回 success: false 但未抛出异常的情况
      ElMessage.error('登录失败，请检查用户名和密码')
      return false
    } catch (error: unknown) {
      console.error('登录失败:', error)

      // 兼容 FastAPI HTTPException 的 detail 字段和自定义 error 格式
      const errData = (error as { response?: { data?: { detail?: string; error?: { message?: string } } } })?.response?.data
      const message = errData?.detail || errData?.error?.message || '登录失败，请检查用户名和密码'
      ElMessage.error(message)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 用户登出
   */
  async function logout() {
    try {
      // 调用后端登出接口
      await authApi.logout()
    } catch (error) {
      // 即使后端登出失败，也要清除本地状态
      console.error('登出接口调用失败:', error)
    } finally {
      // 清除本地状态
      user.value = null
      accessToken.value = null
      refreshTokenValue.value = null
      clearStorage()

      ElMessage.success('已退出登录')
    }
  }

  /**
   * 刷新 Token
   * @returns 是否刷新成功
   */
  async function refreshToken(): Promise<boolean> {
    if (isRefreshing.value) {
      // 如果正在刷新，等待刷新完成
      return new Promise((resolve) => {
        addRefreshSubscriber((token) => {
          resolve(!!token)
        })
      })
    }

    if (!refreshTokenValue.value) {
      return false
    }

    isRefreshing.value = true

    try {
      const response = await authApi.refreshToken({
        refresh_token: refreshTokenValue.value,
      })

      if (response.success && response.data) {
        updateTokenResponse(response.data)
        onRefreshed(response.data.access_token)
        return true
      }

      return false
    } catch (error) {
      console.error('Token 刷新失败:', error)
      // 刷新失败，清除认证状态
      user.value = null
      accessToken.value = null
      refreshTokenValue.value = null
      clearStorage()
      onRefreshed('')
      return false
    } finally {
      isRefreshing.value = false
    }
  }

  /**
   * 获取当前用户信息
   */
  async function fetchCurrentUser() {
    try {
      const response = await authApi.getCurrentUser()

      if (response.success && response.data) {
        user.value = response.data
        localStorage.setItem(STORAGE_KEYS.USER_INFO, JSON.stringify(response.data))
        return response.data
      }

      return null
    } catch (error) {
      console.error('获取用户信息失败:', error)
      return null
    }
  }

  /**
   * 检查认证状态
   * 尝试从 localStorage 恢复状态，并验证 Token 是否有效
   */
  async function checkAuth() {
    // 从 localStorage 加载状态
    loadFromStorage()

    // 如果有 Token，尝试获取用户信息
    if (accessToken.value) {
      const userInfo = await fetchCurrentUser()
      if (!userInfo) {
        // Token 无效，尝试刷新
        const refreshed = await refreshToken()
        if (refreshed) {
          await fetchCurrentUser()
        }
      }
    }
  }

  /**
   * 设置认证状态（用于 Token 刷新后更新）
   */
  function setAuth(tokenResponse: TokenResponse, userInfo: UserInfo) {
    accessToken.value = tokenResponse.access_token
    refreshTokenValue.value = tokenResponse.refresh_token
    user.value = userInfo
    saveToStorage(tokenResponse, userInfo)
  }

  /**
   * 清除认证状态
   */
  function clearAuth() {
    user.value = null
    accessToken.value = null
    refreshTokenValue.value = null
    clearStorage()
  }

  // 初始化时从 localStorage 加载状态
  loadFromStorage()

  return {
    // 状态
    user,
    accessToken,
    refreshTokenValue,
    loading,
    isRefreshing,

    // 计算属性
    isAuthenticated,
    userRole,
    isAdmin,
    isTeacher,
    isStudent,

    // 操作
    login,
    logout,
    refreshToken,
    fetchCurrentUser,
    checkAuth,
    setAuth,
    clearAuth,
    loadFromStorage,
  }
})
