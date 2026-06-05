/**
 * 路由配置
 * 定义应用的所有路由规则
 */

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

/** 路由表 */
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/dashboard/Dashboard.vue'),
    meta: { title: '仪表盘', icon: 'Odometer' },
  },
  {
    path: '/student',
    name: 'Student',
    redirect: '/student/list',
    meta: { title: '学生管理', icon: 'User' },
    children: [
      {
        path: 'list',
        name: 'StudentList',
        component: () => import('@/views/student/StudentList.vue'),
        meta: { title: '学生列表', icon: 'List' },
      },
      {
        path: 'add',
        name: 'StudentAdd',
        component: () => import('@/views/student/StudentForm.vue'),
        meta: { title: '添加学生', icon: 'UserPlus' },
      },
      {
        path: 'edit/:id',
        name: 'StudentEdit',
        component: () => import('@/views/student/StudentForm.vue'),
        meta: { title: '编辑学生', icon: 'Edit', hidden: true },
      },
      {
        path: 'detail/:id',
        name: 'StudentDetail',
        component: () => import('@/views/student/StudentDetail.vue'),
        meta: { title: '学生详情', icon: 'User', hidden: true },
      },
    ],
  },
  {
    path: '/grade',
    name: 'Grade',
    redirect: '/grade/list',
    meta: { title: '成绩管理', icon: 'Document' },
    children: [
      {
        path: 'list',
        name: 'GradeList',
        component: () => import('@/views/grade/GradeList.vue'),
        meta: { title: '成绩列表', icon: 'List' },
      },
      {
        path: 'input',
        name: 'GradeInput',
        component: () => import('@/views/grade/GradeForm.vue'),
        meta: { title: '成绩录入', icon: 'Edit' },
      },
      {
        path: 'import',
        name: 'GradeImport',
        component: () => import('@/views/grade/GradeImport.vue'),
        meta: { title: '成绩导入', icon: 'Upload' },
      },
    ],
  },
  {
    path: '/statistics',
    name: 'Statistics',
    redirect: '/statistics/overview',
    meta: { title: '统计分析', icon: 'DataAnalysis' },
    children: [
      {
        path: 'overview',
        name: 'StatisticsOverview',
        component: () => import('@/views/statistics/StatisticsOverview.vue'),
        meta: { title: '统计概览', icon: 'PieChart' },
      },
      {
        path: 'class',
        name: 'ClassStatistics',
        component: () => import('@/views/statistics/ClassStatistics.vue'),
        meta: { title: '班级统计', icon: 'School' },
      },
      {
        path: 'subject',
        name: 'SubjectStatistics',
        component: () => import('@/views/statistics/SubjectStatistics.vue'),
        meta: { title: '科目统计', icon: 'Collection' },
      },
    ],
  },
  // 404 页面 - 放在最后
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/dashboard',
  },
]

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
router.beforeEach((to, _from, next) => {
  // 设置页面标题
  const title = to.meta.title as string
  document.title = title ? `${title} - 学生成绩管理系统` : '学生成绩管理系统'
  next()
})

/** 全局后置钩子 */
router.afterEach(() => {
  // 可在此处添加页面加载完成后的逻辑
})

export default router
