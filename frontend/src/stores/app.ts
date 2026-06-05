/**
 * 应用全局状态
 * 侧边栏折叠状态、全局配置等
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // ========== 状态 ==========

  /** 侧边栏是否折叠 */
  const sidebarCollapsed = ref(false)

  /** 页面加载状态 */
  const pageLoading = ref(false)

  /** 全局尺寸 */
  const componentSize = ref<'default' | 'small' | 'large'>('default')

  // ========== 计算属性 ==========

  /** 侧边栏宽度 */
  const sidebarWidth = computed(() => {
    return sidebarCollapsed.value ? '64px' : '220px'
  })

  // ========== 操作 ==========

  /** 切换侧边栏折叠状态 */
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
    // 保存到 localStorage
    localStorage.setItem('sidebarCollapsed', String(sidebarCollapsed.value))
  }

  /** 设置侧边栏折叠状态 */
  function setSidebarCollapsed(collapsed: boolean) {
    sidebarCollapsed.value = collapsed
    localStorage.setItem('sidebarCollapsed', String(collapsed))
  }

  /** 设置页面加载状态 */
  function setPageLoading(loading: boolean) {
    pageLoading.value = loading
  }

  /** 设置组件尺寸 */
  function setComponentSize(size: 'default' | 'small' | 'large') {
    componentSize.value = size
    localStorage.setItem('componentSize', size)
  }

  /** 初始化状态（从 localStorage 恢复） */
  function initState() {
    const savedCollapsed = localStorage.getItem('sidebarCollapsed')
    if (savedCollapsed !== null) {
      sidebarCollapsed.value = savedCollapsed === 'true'
    }

    const savedSize = localStorage.getItem('componentSize') as 'default' | 'small' | 'large'
    if (savedSize) {
      componentSize.value = savedSize
    }
  }

  return {
    // 状态
    sidebarCollapsed,
    pageLoading,
    componentSize,

    // 计算属性
    sidebarWidth,

    // 操作
    toggleSidebar,
    setSidebarCollapsed,
    setPageLoading,
    setComponentSize,
    initState,
  }
})
