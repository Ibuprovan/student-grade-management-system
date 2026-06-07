<template>
  <header class="app-header">
    <div class="header-left">
      <!-- 折叠按钮 -->
      <el-icon class="collapse-btn" @click="appStore.toggleSidebar">
        <component :is="appStore.sidebarCollapsed ? 'Expand' : 'Fold'" />
      </el-icon>
      <!-- 面包屑导航 -->
      <el-breadcrumb separator="/" class="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentRoute.meta.title">
          {{ currentRoute.meta.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="header-right">
      <!-- 全屏按钮 -->
      <el-tooltip content="全屏" placement="bottom">
        <el-icon class="header-action" @click="toggleFullscreen">
          <FullScreen />
        </el-icon>
      </el-tooltip>

      <!-- 用户信息 -->
      <el-dropdown trigger="click">
        <div class="user-info">
          <el-avatar :size="34" class="user-avatar" :style="{ backgroundColor: avatarColor }">
            {{ userInitial }}
          </el-avatar>
          <div class="user-detail">
            <span class="user-name">{{ displayName }}</span>
            <el-tag :type="roleTagType" size="small" class="role-tag" effect="plain">
              {{ roleLabel }}
            </el-tag>
          </div>
          <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item disabled>
              <el-icon><User /></el-icon>
              {{ displayName }} ({{ roleLabel }})
            </el-dropdown-item>
            <el-dropdown-item divided @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 退出确认对话框 -->
    <ConfirmDialog
      v-model="logoutDialogVisible"
      title="退出登录"
      message="确定要退出登录吗？退出后需要重新登录才能访问系统。"
      type="warning"
      confirm-text="确定退出"
      cancel-text="取消"
      :loading="logoutLoading"
      @confirm="confirmLogout"
    />
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const authStore = useAuthStore()

/** 退出登录对话框可见状态 */
const logoutDialogVisible = ref(false)

/** 退出登录加载状态 */
const logoutLoading = ref(false)

/** 当前路由信息 */
const currentRoute = computed(() => route)

/** 显示的用户名 */
const displayName = computed(() => {
  return authStore.user?.username || '未知用户'
})

/** 用户名首字母（用于头像显示） */
const userInitial = computed(() => {
  const username = authStore.user?.username
  if (username && username.length > 0) {
    return username.charAt(0).toUpperCase()
  }
  return 'U'
})

/** 头像背景颜色 */
const avatarColor = computed(() => {
  const colorMap: Record<string, string> = {
    admin: '#E06469',
    teacher: '#2A9D8F',
    student: '#52B788',
  }
  return colorMap[authStore.userRole || ''] || '#2A9D8F'
})

/** 角色标签类型 */
const roleTagType = computed(() => {
  const typeMap: Record<string, 'danger' | 'primary' | 'success' | 'info' | 'warning'> = {
    admin: 'danger',
    teacher: 'primary',
    student: 'success',
  }
  return typeMap[authStore.userRole || ''] || 'info'
})

/** 角色中文标签 */
const roleLabel = computed(() => {
  const labelMap: Record<string, string> = {
    admin: '管理员',
    teacher: '教师',
    student: '学生',
  }
  return labelMap[authStore.userRole || ''] || '未知角色'
})

/** 切换全屏 */
function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

/** 处理退出登录点击 */
function handleLogout() {
  logoutDialogVisible.value = true
}

/** 确认退出登录 */
async function confirmLogout() {
  logoutLoading.value = true
  try {
    await authStore.logout()
    // 退出成功后跳转到登录页
    router.push('/login')
  } catch (error) {
    console.error('退出登录失败:', error)
    ElMessage.error('退出登录失败，请重试')
  } finally {
    logoutLoading.value = false
    logoutDialogVisible.value = false
  }
}
</script>

<style lang="scss" scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--header-height);
  padding: 0 20px;
  background: var(--surface-color);
  border-bottom: 1px solid var(--border-color-light);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: var(--text-color-secondary);
  transition: color var(--transition-fast);
  border-radius: 8px;
  padding: 4px;

  &:hover {
    color: var(--primary-color);
    background: var(--primary-light);
  }
}

.breadcrumb {
  font-size: 14px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-action {
  font-size: 18px;
  cursor: pointer;
  color: var(--text-color-secondary);
  transition: all var(--transition-fast);
  border-radius: 8px;
  padding: 6px;

  &:hover {
    color: var(--primary-color);
    background: var(--primary-light);
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: var(--border-radius-md);
  transition: background-color var(--transition-fast);

  &:hover {
    background-color: var(--bg-color);
  }
}

.user-avatar {
  color: #fff;
  font-weight: 700;
  font-size: 14px;
}

.user-detail {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color);
  line-height: 1.2;
}

.role-tag {
  font-size: 11px;
  height: 18px;
  line-height: 16px;
  padding: 0 6px;
}

.dropdown-icon {
  font-size: 12px;
  color: var(--text-color-placeholder);
}
</style>
