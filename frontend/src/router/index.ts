/**
 * 路由配置
 * 定义应用的所有路由规则
 */

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

/** 用户角色类型 */
type UserRole = 'admin' | 'teacher' | 'student'

/** 路由元信息接口扩展 */
declare module 'vue-router' {
  interface RouteMeta {
    /** 页面标题 */
    title?: string
    /** 图标名称 */
    icon?: string
    /** 是否隐藏 */
    hidden?: boolean
    /** 是否公开路由（不需要认证） */
    public?: boolean
    /** 是否需要认证（默认 true） */
    requiresAuth?: boolean
    /** 允许访问的角色列表 */
    roles?: UserRole[]
  }
}

/** 公开路由（不需要认证） */
const publicRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/Login.vue'),
    meta: { title: '登录', public: true, requiresAuth: false },
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/error/403.vue'),
    meta: { title: '无权限', public: true, requiresAuth: false },
  },
  {
    path: '/404',
    name: 'NotFoundPage',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '页面不存在', public: true, requiresAuth: false },
  },
]

/** 受保护路由（需要认证） */
const protectedRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/dashboard/Dashboard.vue'),
    meta: { title: '仪表盘', icon: 'Odometer', requiresAuth: true, roles: ['admin', 'teacher', 'student'] },
  },
  {
    path: '/student',
    name: 'Student',
    redirect: '/student/list',
    meta: { title: '学生管理', icon: 'User', requiresAuth: true, roles: ['admin', 'teacher'] },
    children: [
      {
        path: 'list',
        name: 'StudentList',
        component: () => import('@/views/student/StudentList.vue'),
        meta: { title: '学生列表', icon: 'List', requiresAuth: true, roles: ['admin', 'teacher'] },
      },
      {
        path: 'add',
        name: 'StudentAdd',
        component: () => import('@/views/student/StudentForm.vue'),
        meta: { title: '添加学生', icon: 'UserPlus', requiresAuth: true, roles: ['admin', 'teacher'] },
      },
      {
        path: 'edit/:id',
        name: 'StudentEdit',
        component: () => import('@/views/student/StudentForm.vue'),
        meta: { title: '编辑学生', icon: 'Edit', hidden: true, requiresAuth: true, roles: ['admin', 'teacher'] },
      },
      {
        path: 'detail/:id',
        name: 'StudentDetail',
        component: () => import('@/views/student/StudentDetail.vue'),
        meta: { title: '学生详情', icon: 'User', hidden: true, requiresAuth: true, roles: ['admin', 'teacher'] },
      },
      {
        path: 'import',
        name: 'StudentImport',
        component: () => import('@/views/student/StudentImport.vue'),
        meta: { title: '批量导入', icon: 'Upload', requiresAuth: true, roles: ['admin', 'teacher'] },
      },
    ],
  },
  {
    path: '/grade',
    name: 'Grade',
    redirect: '/grade/list',
    meta: { title: '成绩管理', icon: 'Document', requiresAuth: true, roles: ['admin', 'teacher'] },
    children: [
      {
        path: 'list',
        name: 'GradeList',
        component: () => import('@/views/grade/GradeList.vue'),
        meta: { title: '成绩列表', icon: 'List', requiresAuth: true, roles: ['admin', 'teacher'] },
      },
      {
        path: 'input',
        name: 'GradeInput',
        component: () => import('@/views/grade/GradeForm.vue'),
        meta: { title: '成绩录入', icon: 'Edit', requiresAuth: true, roles: ['admin', 'teacher'] },
      },
      {
        path: 'import',
        name: 'GradeImport',
        component: () => import('@/views/grade/GradeImport.vue'),
        meta: { title: '成绩导入', icon: 'Upload', requiresAuth: true, roles: ['admin', 'teacher'] },
      },
    ],
  },
  {
    path: '/statistics',
    name: 'Statistics',
    redirect: '/statistics/overview',
    meta: { title: '统计分析', icon: 'DataAnalysis', requiresAuth: true, roles: ['admin', 'teacher', 'student'] },
    children: [
      {
        path: 'overview',
        name: 'StatisticsOverview',
        component: () => import('@/views/statistics/StatisticsOverview.vue'),
        meta: { title: '统计概览', icon: 'PieChart', requiresAuth: true, roles: ['admin', 'teacher', 'student'] },
      },
      {
        path: 'class',
        name: 'ClassStatistics',
        component: () => import('@/views/statistics/ClassStatistics.vue'),
        meta: { title: '班级统计', icon: 'School', requiresAuth: true, roles: ['admin', 'teacher'] },
      },
      {
        path: 'subject',
        name: 'SubjectStatistics',
        component: () => import('@/views/statistics/SubjectStatistics.vue'),
        meta: { title: '科目统计', icon: 'Collection', requiresAuth: true, roles: ['admin', 'teacher'] },
      },
    ],
  },
  {
    path: '/my-grades',
    name: 'MyGrades',
    component: () => import('@/views/student/MyGrades.vue'),
    meta: { title: '我的成绩', icon: 'Trophy', requiresAuth: true, roles: ['student'] },
  },
  // 404 页面 - 放在最后
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/404',
  },
]

/** 合并路由 */
const routes: RouteRecordRaw[] = [...publicRoutes, ...protectedRoutes]

/** 创建路由实例 */
const router = createRouter({
  history: createWebHistory(),
  routes,
  // 路由切换时滚动到顶部
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  },
})

/** 全局前置守卫 */
router.beforeEach(async (to, _from, next) => {
  // 设置页面标题
  const title = to.meta.title as string
  document.title = title ? `${title} - 学生成绩管理系统` : '学生成绩管理系统'

  // 动态导入 auth store（避免循环依赖）
  const { useAuthStore } = await import('@/stores/auth')
  const authStore = useAuthStore()

  // 检查是否是公开路由（不需要认证）
  const isPublicRoute = to.meta.public === true || to.meta.requiresAuth === false

  // 如果是公开路由
  if (isPublicRoute) {
    // 如果已登录，跳转到首页
    if (authStore.isAuthenticated && to.path === '/login') {
      next('/dashboard')
      return
    }
    next()
    return
  }

  // 受保护路由：检查认证状态
  if (!authStore.isAuthenticated) {
    // 尝试从 localStorage 恢复状态
    authStore.loadFromStorage()

    // 如果仍然未认证，检查 Token 是否存在
    if (!authStore.accessToken) {
      // 无 Token，跳转到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath },
      })
      return
    }

    // 有 Token 但未认证，尝试验证 Token
    try {
      await authStore.checkAuth()

      // 验证后仍未认证，跳转到登录页
      if (!authStore.isAuthenticated) {
        next({
          path: '/login',
          query: { redirect: to.fullPath },
        })
        return
      }
    } catch (error) {
      console.error('Token 验证失败:', error)
      next({
        path: '/login',
        query: { redirect: to.fullPath },
      })
      return
    }
  }

  // 检查角色权限
  const requiredRoles = to.meta.roles as UserRole[] | undefined

  if (requiredRoles && requiredRoles.length > 0) {
    const userRole = authStore.userRole

    // 如果用户没有角色，或者角色不在允许列表中
    if (!userRole || !requiredRoles.includes(userRole)) {
      console.warn(`权限不足: 用户角色 "${userRole}" 无权访问路由 "${to.path}"，需要角色: ${requiredRoles.join(', ')}`)
      next('/403')
      return
    }
  }

  // Token 有效且有权限，允许访问
  next()
})

/** 全局后置钩子 */
router.afterEach(() => {
  // 可在此处添加页面加载完成后的逻辑
})

export default router
