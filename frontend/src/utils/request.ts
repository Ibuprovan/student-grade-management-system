/**
 * Axios 请求工具封装
 * 配置拦截器、错误处理、请求方法
 */

import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'

/** 后端统一响应格式 */
interface BackendResponse<T = unknown> {
  success: boolean
  data: T
  error: {
    code: string
    message: string
  } | null
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
    // 可在此处添加 token 等认证信息
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
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
  (error) => {
    // 处理 HTTP 错误状态码
    let message = '网络错误，请稍后重试'

    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 400:
          message = data?.error?.message || '请求参数错误'
          break
        case 401:
          message = '未授权，请重新登录'
          // 可在此处跳转到登录页
          break
        case 403:
          message = '拒绝访问'
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
    } else if (error.code === 'ECONNABORTED') {
      message = '请求超时，请稍后重试'
    } else if (!window.navigator.onLine) {
      message = '网络连接已断开，请检查网络'
    }

    ElMessage.error(message)
    return Promise.reject(error)
  },
)

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
