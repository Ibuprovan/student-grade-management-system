/**
 * 通用组合式函数
 * 封装常用的通用逻辑
 */

import { ref, onMounted, onUnmounted } from 'vue'

/**
 * 加载状态管理
 */
export function useLoading(initialState = false) {
  const loading = ref(initialState)

  /** 开始加载 */
  function startLoading() {
    loading.value = true
  }

  /** 结束加载 */
  function stopLoading() {
    loading.value = false
  }

  /**
   * 包装异步函数，自动管理加载状态
   * @param fn 异步函数
   * @returns 包装后的函数
   */
  async function withLoading<T>(fn: () => Promise<T>): Promise<T> {
    startLoading()
    try {
      return await fn()
    } finally {
      stopLoading()
    }
  }

  return {
    loading,
    startLoading,
    stopLoading,
    withLoading,
  }
}

/**
 * 防抖函数
 * @param fn 需要防抖的函数
 * @param delay 延迟时间（毫秒）
 */
export function useDebounce<T extends (...args: unknown[]) => unknown>(fn: T, delay = 300) {
  let timer: ReturnType<typeof setTimeout> | null = null

  function debounced(...args: Parameters<T>) {
    if (timer) {
      clearTimeout(timer)
    }
    timer = setTimeout(() => {
      fn(...args)
      timer = null
    }, delay)
  }

  /** 取消防抖 */
  function cancel() {
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
  }

  return { debounced, cancel }
}

/**
 * 节流函数
 * @param fn 需要节流的函数
 * @param interval 间隔时间（毫秒）
 */
export function useThrottle<T extends (...args: unknown[]) => unknown>(fn: T, interval = 300) {
  let lastTime = 0

  function throttled(...args: Parameters<T>) {
    const now = Date.now()
    if (now - lastTime >= interval) {
      fn(...args)
      lastTime = now
    }
  }

  return { throttled }
}

/**
 * 窗口大小监听
 */
export function useWindowSize() {
  const width = ref(window.innerWidth)
  const height = ref(window.innerHeight)

  function updateSize() {
    width.value = window.innerWidth
    height.value = window.innerHeight
  }

  onMounted(() => {
    window.addEventListener('resize', updateSize)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', updateSize)
  })

  return { width, height }
}
