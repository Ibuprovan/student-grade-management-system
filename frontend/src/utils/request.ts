/**
 * Axios 请求工具封装
 * 配置拦截器、错误处理、请求方法
 *
 * 功能特性：
 * - 请求拦截器：自动附加 Token
 * - 响应拦截器：处理业务错误和 401 状态码
 * - Token 自动刷新：401 时自动尝试刷新 Token
 * - 请求队列：刷新期间其他请求排队等待
 */

import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { refreshToken as refreshTokenApi } from '@/api/auth'

/** 后端统一响应格式 */
interface BackendResponse<T = unknown> {
  success: boolean
  data: T
  error: {
    code: string
    message: string
  } | null
}

/** 请求队列项 */
interface QueueItem {
  resolve: (value: unknown) => void
  reject: (reason?: unknown) => void
}

/** Token 刷新状态 */
let isRefreshing = false
let failedQueue: QueueItem[] = []

/**
 * 处理失败队列
 * @param error 错误对象（如果刷新失败）
 * @param token 新的 Access Token（如果刷新成功）
 */
function processQueue(error: unknown, token: string | null = null) {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

/** 创建 Axios 实例 */
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/** 请求拦截器 */
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从 localStorage 获取 Token
    const token = localStorage.getItem('access_token')

    // 如果存在 Token，自动附加到请求头
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    console.error('请求拦截器错误:', error)
    return Promise.reject(error)
  },
)

/** 响应拦截器 */
service.interceptors.response.use(
  (response: AxiosResponse<BackendResponse>) => {
    const { data } = response

    // 如果后端返回 success === false，表示业务错误
    if (data.success === false && data.error) {
      const message = data.error.message || '请求失败'
      ElMessage.error(message)
      return Promise.reject(new Error(message))
    }

    // 返回完整响应数据
    return data as unknown as AxiosResponse
  },
  async (error) => {
    const originalRequest = error.config

    // 处理 HTTP 错误状态码
    let message = '网络错误，请稍后重试'

    // 登录/刷新接口的错误由调用方处理，不在拦截器中弹消息
    const isAuthRequest =
      originalRequest.url?.includes('/auth/login') ||
      originalRequest.url?.includes('/auth/refresh')

    if (error.response) {
      const { status, data } = error.response

      // 处理 401 错误 - 尝试刷新 Token（仅对非认证接口生效）
      if (status === 401 && !originalRequest._retry && !isAuthRequest) {
        // 如果正在刷新 Token，将请求加入队列
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject })
          })
            .then((token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`
              return service(originalRequest)
            })
            .catch((err) => {
              return Promise.reject(err)
            })
        }

        originalRequest._retry = true
        isRefreshing = true

        // 尝试刷新 Token
        const refreshToken = localStorage.getItem('refresh_token')

        if (!refreshToken) {
          handleAuthError()
          return Promise.reject(error)
        }

        try {
          const response = await refreshTokenApi({ refresh_token: refreshToken })

          const { access_token, refresh_token: newRefreshToken } = response.data

          // 更新 Token
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', newRefreshToken)

          // 处理队列中的请求
          processQueue(null, access_token)

          // 重试原始请求
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return service(originalRequest)
        } catch (refreshError) {
          // 刷新失败，清除认证状态
          processQueue(refreshError, null)
          handleAuthError()
          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      }

      switch (status) {
        case 400:
          message = data?.error?.message || data?.detail || '请求参数错误'
          break
        case 401:
          message = data?.detail || data?.error?.message || '用户名或密码错误'
          break
        case 403:
          message = data?.detail || data?.error?.message || '拒绝访问'
          break
        case 404:
          message = data?.error?.message || '请求的资源不存在'
          break
        case 409:
          message = data?.error?.message || '数据冲突'
          break
        case 422:
          message = data?.error?.message || '数据验证失败'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = data?.error?.message || `请求失败 (${status})`
      }

      // 有 HTTP 响应的认证接口错误直接拒绝，由调用方处理
      if (isAuthRequest) {
        return Promise.reject(error)
      }
    } else if (error.code === 'ECONNABORTED') {
      message = '请求超时，请稍后重试'
    } else if (!window.navigator.onLine) {
      message = '网络连接已断开，请检查网络'
    }

    // 认证接口（登录/刷新）的错误由调用方处理，不在拦截器中弹消息
    if (!isAuthRequest) {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  },
)

/**
 * 处理认证失败
 * 清除本地 Token 并跳转到登录页
 */
function handleAuthError() {
  // 清除本地存储的认证信息
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user_info')

  // 显示提示
  ElMessage.error('登录已过期，请重新登录')

  // 使用 setTimeout 确保在 Vue 应用初始化后再跳转
  setTimeout(() => {
    window.location.href = '/login'
  }, 100)
}

/**
 * 封装 GET 请求
 * @param url 请求地址
 * @param config 请求配置
 */
export function get<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return service.get(url, config) as unknown as Promise<T>
}

/**
 * 封装 POST 请求
 * @param url 请求地址
 * @param data 请求数据
 * @param config 请求配置
 */
export function post<T = unknown>(
  url: string,
  data?: unknown,
  config?: AxiosRequestConfig,
): Promise<T> {
  return service.post(url, data, config) as unknown as Promise<T>
}

/**
 * 封装 PUT 请求
 * @param url 请求地址
 * @param data 请求数据
 * @param config 请求配置
 */
export function put<T = unknown>(
  url: string,
  data?: unknown,
  config?: AxiosRequestConfig,
): Promise<T> {
  return service.put(url, data, config) as unknown as Promise<T>
}

/**
 * 封装 DELETE 请求
 * @param url 请求地址
 * @param config 请求配置
 */
export function del<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return service.delete(url, config) as unknown as Promise<T>
}

/**
 * 封装文件上传
 * @param url 上传地址
 * @param formData FormData 对象
 * @param config 请求配置
 */
export function upload<T = unknown>(
  url: string,
  formData: FormData,
  config?: AxiosRequestConfig,
): Promise<T> {
  return service.post(url, formData, {
    ...config,
    headers: {
      'Content-Type': 'multipart/form-data',
      ...config?.headers,
    },
  }) as unknown as Promise<T>
}

export default service
