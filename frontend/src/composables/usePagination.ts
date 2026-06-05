/**
 * 分页组合式函数
 * 封装分页逻辑，可复用于多个页面
 */

import { ref, computed } from 'vue'

export interface UsePaginationOptions {
  /** 初始页码 */
  defaultPage?: number
  /** 初始每页条数 */
  defaultPageSize?: number
  /** 默认每页条数选项 */
  pageSizes?: number[]
}

export function usePagination(options: UsePaginationOptions = {}) {
  const {
    defaultPage = 1,
    defaultPageSize = 20,
    pageSizes = [10, 20, 50, 100],
  } = options

  /** 当前页码 */
  const page = ref(defaultPage)

  /** 每页条数 */
  const pageSize = ref(defaultPageSize)

  /** 总条数 */
  const total = ref(0)

  /** 总页数 */
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  /** 是否有上一页 */
  const hasPrev = computed(() => page.value > 1)

  /** 是否有下一页 */
  const hasNext = computed(() => page.value < totalPages.value)

  /** 跳转到指定页 */
  function goToPage(p: number) {
    if (p >= 1 && p <= totalPages.value) {
      page.value = p
    }
  }

  /** 上一页 */
  function prevPage() {
    if (hasPrev.value) {
      page.value--
    }
  }

  /** 下一页 */
  function nextPage() {
    if (hasNext.value) {
      page.value++
    }
  }

  /** 设置每页条数 */
  function setPageSize(size: number) {
    pageSize.value = size
    page.value = 1 // 切换每页条数时回到第一页
  }

  /** 设置总条数 */
  function setTotal(t: number) {
    total.value = t
  }

  /** 重置为第一页 */
  function resetPage() {
    page.value = 1
  }

  return {
    page,
    pageSize,
    total,
    totalPages,
    hasPrev,
    hasNext,
    pageSizes,
    goToPage,
    prevPage,
    nextPage,
    setPageSize,
    setTotal,
    resetPage,
  }
}
