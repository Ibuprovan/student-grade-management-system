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
            <el-dropdown-item divided @click="showPasswordDialog">
              <el-icon><Lock /></el-icon>
              修改密码
            </el-dropdown-item>
            <el-dropdown-item @click="handleLogout">
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

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="420px"
      :close-on-click-modal="false"
      @close="resetPasswordForm"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="80px"
        @keyup.enter="confirmChangePassword"
      >
        <el-form-item label="旧密码" prop="oldPassword">
          <el-input
            v-model="passwordForm.oldPassword"
            type="password"
            placeholder="请输入旧密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            placeholder="请输入新密码（至少8位，含大小写字母和数字）"
            show-password
          />
          <div v-if="passwordForm.newPassword" class="password-strength">
            <div class="strength-bars">
              <div
                v-for="i in 3"
                :key="i"
                class="strength-bar"
                :class="{ active: passwordStrength >= i, [strengthLevel]: passwordStrength >= i }"
              />
            </div>
            <span class="strength-text" :class="strengthLevel">{{ strengthText }}</span>
          </div>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="passwordLoading"
          @click="confirmChangePassword"
        >
          确认修改
        </el-button>
      </template>
    </el-dialog>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const authStore = useAuthStore()

/** 退出登录对话框可见状态 */
const logoutDialogVisible = ref(false)

/** 退出登录加载状态 */
const logoutLoading = ref(false)

/** 密码修改对话框可见状态 */
const passwordDialogVisible = ref(false)

/** 密码修改加载状态 */
const passwordLoading = ref(false)

/** 密码表单引用 */
const passwordFormRef = ref<FormInstance>()

/** 密码表单 */
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

/** 密码强度（0-3） */
const passwordStrength = computed(() => {
  const pwd = passwordForm.value.newPassword
  if (!pwd) return 0
  let score = 0
  if (pwd.length >= 8) score++
  if (/[A-Z]/.test(pwd) && /[a-z]/.test(pwd)) score++
  if (/\d/.test(pwd)) return score + 1
  return score
})

/** 强度等级 */
const strengthLevel = computed(() => {
  const s = passwordStrength.value
  if (s <= 1) return 'weak'
  if (s === 2) return 'medium'
  return 'strong'
})

/** 强度文字 */
const strengthText = computed(() => {
  const s = passwordStrength.value
  if (s <= 1) return '弱'
  if (s === 2) return '中'
  return '强'
})

/** 密码校验规则 */
const validatePasswordStrength = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (!value) {
    callback(new Error('请输入新密码'))
    return
  }
  if (value.length < 8) {
    callback(new Error('密码长度至少8位'))
    return
  }
  if (!/[A-Z]/.test(value)) {
    callback(new Error('密码需包含大写字母'))
    return
  }
  if (!/[a-z]/.test(value)) {
    callback(new Error('密码需包含小写字母'))
    return
  }
  if (!/\d/.test(value)) {
    callback(new Error('密码需包含数字'))
    return
  }
  callback()
}

const validateConfirmPassword = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (!value) {
    callback(new Error('请再次输入新密码'))
    return
  }
  if (value !== passwordForm.value.newPassword) {
    callback(new Error('两次输入的密码不一致'))
    return
  }
  callback()
}

/** 密码表单验证规则 */
const passwordRules: FormRules = {
  oldPassword: [
    { required: true, message: '请输入旧密码', trigger: 'blur' },
  ],
  newPassword: [
    { required: true, validator: validatePasswordStrength, trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

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
    class_teacher: '#E8A838',
    subject_leader: '#7C3AED',
    student: '#52B788',
  }
  return colorMap[authStore.userRole || ''] || '#2A9D8F'
})

/** 角色标签类型 */
const roleTagType = computed(() => {
  const typeMap: Record<string, 'danger' | 'primary' | 'success' | 'info' | 'warning'> = {
    admin: 'danger',
    teacher: 'primary',
    class_teacher: 'warning',
    subject_leader: 'info',
    student: 'success',
  }
  return typeMap[authStore.userRole || ''] || 'info'
})

/** 角色中文标签 */
const roleLabel = computed(() => {
  const labelMap: Record<string, string> = {
    admin: '管理员',
    teacher: '教师',
    class_teacher: '班主任',
    subject_leader: '学科组长',
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

/** 显示密码修改对话框 */
function showPasswordDialog() {
  passwordDialogVisible.value = true
}

/** 重置密码表单 */
function resetPasswordForm() {
  passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
  passwordFormRef.value?.resetFields()
}

/** 确认修改密码 */
async function confirmChangePassword() {
  if (!passwordFormRef.value) return
  try {
    await passwordFormRef.value.validate()
  } catch {
    return
  }

  passwordLoading.value = true
  try {
    const success = await authStore.changePassword(
      passwordForm.value.oldPassword,
      passwordForm.value.newPassword,
    )
    if (success) {
      passwordDialogVisible.value = false
      resetPasswordForm()
    }
  } finally {
    passwordLoading.value = false
  }
}
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables.scss' as *;

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: $header-height;
  padding: 0 $space-5;
  background: $bg-secondary;
  border-bottom: 1px solid $border-primary;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: $space-4;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: $text-secondary;
  transition: color $transition-fast;
  border-radius: $rounded-md;
  padding: $space-1;

  &:hover {
    color: $accent-primary;
    background: rgba(37, 99, 235, 0.1);
  }
}

.breadcrumb {
  font-size: $text-sm;
}

.header-right {
  display: flex;
  align-items: center;
  gap: $space-4;
}

.header-action {
  font-size: 18px;
  cursor: pointer;
  color: $text-secondary;
  transition: all $transition-fast;
  border-radius: $rounded-md;
  padding: $space-2;

  &:hover {
    color: $accent-primary;
    background: rgba(37, 99, 235, 0.1);
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: $space-3;
  cursor: pointer;
  padding: $space-2 $space-3;
  border-radius: $rounded-md;
  transition: background-color $transition-fast;

  &:hover {
    background-color: $bg-tertiary;
  }
}

.user-avatar {
  color: #fff;
  font-weight: $font-bold;
  font-size: $text-sm;
}

.user-detail {
  display: flex;
  flex-direction: column;
  gap: $space-1;
}

.user-name {
  font-size: $text-sm;
  font-weight: $font-medium;
  color: $text-primary;
  line-height: 1.2;
}

.role-tag {
  font-size: $text-xs;
  height: 18px;
  line-height: 16px;
  padding: 0 $space-2;
}

.dropdown-icon {
  font-size: $text-xs;
  color: $text-muted;
}

// ===== 密码强度指示器 =====
.password-strength {
  display: flex;
  align-items: center;
  gap: $space-2;
  margin-top: $space-2;

  .strength-bars {
    display: flex;
    gap: $space-1;
  }

  .strength-bar {
    width: 40px;
    height: 4px;
    border-radius: 2px;
    background: $border-secondary;
    transition: background-color 0.3s;

    &.active.weak { background: $error; }
    &.active.medium { background: $warning; }
    &.active.strong { background: $success; }
  }

  .strength-text {
    font-size: $text-xs;
    &.weak { color: $error; }
    &.medium { color: $warning; }
    &.strong { color: $success; }
  }
}
</style>