/**
 * 权限指令
 *
 * 用于控制元素的显示/隐藏，基于用户角色进行权限控制
 *
 * 使用示例：
 * <el-button v-permission="'admin'">管理员操作</el-button>
 * <el-button v-permission="['admin', 'teacher']">教师以上操作</el-button>
 * <el-button v-permission.not="['student']">非学生操作</el-button>
 */

import type { Directive, DirectiveBinding } from 'vue'

/** 用户角色类型 */
type UserRole = 'admin' | 'teacher' | 'student'

/** 权限指令修饰符 */
interface PermissionModifiers {
  /** 取反：不在指定角色列表中时显示 */
  not?: boolean
}

/**
 * 获取当前用户角色
 * @returns 用户角色或 null
 */
function getCurrentUserRole(): UserRole | null {
  try {
    const userInfoStr = localStorage.getItem('user_info')
    if (!userInfoStr) {
      return null
    }
    const userInfo = JSON.parse(userInfoStr)
    return userInfo?.role || null
  } catch (error) {
    console.error('获取用户角色失败:', error)
    return null
  }
}

/**
 * 检查用户是否有指定角色
 * @param requiredRoles 需要的角色（单个角色或角色数组）
 * @param modifiers 修饰符
 * @returns 是否有权限
 */
function hasPermission(
  requiredRoles: UserRole | UserRole[],
  modifiers: PermissionModifiers = {},
): boolean {
  const currentRole = getCurrentUserRole()

  // 如果用户未登录，无权限
  if (!currentRole) {
    return false
  }

  // 将 requiredRoles 统一转为数组
  const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles]

  // 检查用户角色是否在允许列表中
  const hasRole = roles.includes(currentRole)

  // 如果有 not 修饰符，取反
  if (modifiers.not) {
    return !hasRole
  }

  return hasRole
}

/**
 * 权限指令
 *
 * 根据用户角色控制元素的显示/隐藏
 * 如果用户没有指定角色，将移除该元素
 */
export const permissionDirective: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding<UserRole | UserRole[]>) {
    const { value, modifiers } = binding

    // 如果没有指定角色，不做任何处理
    if (!value || (Array.isArray(value) && value.length === 0)) {
      return
    }

    // 检查权限
    const hasPerm = hasPermission(value, modifiers as PermissionModifiers)

    // 如果没有权限，移除元素
    if (!hasPerm) {
      // 使用注释节点占位，以便后续可能的恢复
      const comment = document.createComment(' v-permission ')
      el.parentNode?.replaceChild(comment, el)
      // 将原始元素存储在注释节点上，以便后续可能的恢复
      ;(comment as any).__vPermissionOriginal = el
    }
  },
}

/**
 * 权限检查工具函数
 *
 * 可以在 setup 中使用，用于条件渲染
 *
 * @example
 * ```vue
 * <script setup>
 * import { usePermission } from '@/directives/permission'
 * const { hasPermission } = usePermission()
 * </script>
 *
 * <template>
 *   <el-button v-if="hasPermission('admin')">管理员操作</el-button>
 *   <el-button v-if="hasPermission(['admin', 'teacher'])">教师以上操作</el-button>
 * </template>
 * ```
 */
export function usePermission() {
  /**
   * 检查是否有指定角色权限
   * @param roles 需要的角色（单个角色或角色数组）
   * @returns 是否有权限
   */
  function checkPermission(roles: UserRole | UserRole[]): boolean {
    return hasPermission(roles)
  }

  /**
   * 检查是否是指定角色
   * @param role 角色
   * @returns 是否是该角色
   */
  function isRole(role: UserRole): boolean {
    const currentRole = getCurrentUserRole()
    return currentRole === role
  }

  /**
   * 是否是管理员
   */
  function isAdmin(): boolean {
    return isRole('admin')
  }

  /**
   * 是否是教师
   */
  function isTeacher(): boolean {
    return isRole('teacher')
  }

  /**
   * 是否是学生
   */
  function isStudent(): boolean {
    return isRole('student')
  }

  return {
    hasPermission: checkPermission,
    isRole,
    isAdmin,
    isTeacher,
    isStudent,
  }
}

export default permissionDirective
