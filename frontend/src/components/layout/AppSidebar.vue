<template>
  <aside class="app-sidebar" :class="{ collapsed: appStore.sidebarCollapsed }">
    <!-- Logo -->
    <div class="sidebar-logo" @click="router.push('/dashboard')">
      <img src="@/assets/images/logo.svg" alt="Logo" class="logo-img" />
      <transition name="fade">
        <span v-show="!appStore.sidebarCollapsed" class="logo-text">成绩管理系统</span>
      </transition>
    </div>

    <!-- 菜单 -->
    <el-scrollbar class="sidebar-menu-wrapper">
      <el-menu
        :default-active="activeMenu"
        :collapse="appStore.sidebarCollapsed"
        :collapse-transition="false"
        router
        class="sidebar-menu"
      >
        <!-- 仪表盘 -->
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>

        <!-- 学生管理 -->
        <el-sub-menu index="/student">
          <template #title>
            <el-icon><User /></el-icon>
            <span>学生管理</span>
          </template>
          <el-menu-item index="/student/list">
            <el-icon><List /></el-icon>
            <template #title>学生列表</template>
          </el-menu-item>
          <el-menu-item index="/student/add">
            <el-icon><UserPlus /></el-icon>
            <template #title>添加学生</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- 成绩管理 -->
        <el-sub-menu index="/grade">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>成绩管理</span>
          </template>
          <el-menu-item index="/grade/list">
            <el-icon><List /></el-icon>
            <template #title>成绩列表</template>
          </el-menu-item>
          <el-menu-item index="/grade/input">
            <el-icon><Edit /></el-icon>
            <template #title>成绩录入</template>
          </el-menu-item>
          <el-menu-item index="/grade/import">
            <el-icon><Upload /></el-icon>
            <template #title>成绩导入</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- 统计分析 -->
        <el-sub-menu index="/statistics">
          <template #title>
            <el-icon><DataAnalysis /></el-icon>
            <span>统计分析</span>
          </template>
          <el-menu-item index="/statistics/overview">
            <el-icon><PieChart /></el-icon>
            <template #title>统计概览</template>
          </el-menu-item>
          <el-menu-item index="/statistics/class">
            <el-icon><School /></el-icon>
            <template #title>班级统计</template>
          </el-menu-item>
          <el-menu-item index="/statistics/subject">
            <el-icon><Collection /></el-icon>
            <template #title>科目统计</template>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-scrollbar>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

/** 当前激活的菜单项 */
const activeMenu = computed(() => {
  const { path } = route
  // 对于子路由，返回父级路径
  if (path.startsWith('/student/edit') || path.startsWith('/student/detail')) {
    return '/student/list'
  }
  return path
})
</script>

<style lang="scss" scoped>
.app-sidebar {
  width: var(--sidebar-width);
  height: 100vh;
  background: #304156;
  transition: width var(--transition-duration);
  position: fixed;
  left: 0;
  top: 0;
  z-index: 200;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  &.collapsed {
    width: var(--sidebar-collapsed-width);
  }
}

.sidebar-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  height: var(--header-height);
  padding: 0 16px;
  background: #263445;
  cursor: pointer;
  overflow: hidden;
  white-space: nowrap;
}

.logo-img {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
}

.logo-text {
  margin-left: 12px;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
}

.sidebar-menu-wrapper {
  flex: 1;
  overflow: hidden;
}

.sidebar-menu {
  border-right: none;
  background: #304156;

  // 菜单项样式
  :deep(.el-menu-item) {
    color: #bfcbd9;

    &:hover {
      background: #263445;
      color: #fff;
    }

    &.is-active {
      background: var(--primary-color) !important;
      color: #fff;
    }
  }

  // 子菜单标题样式
  :deep(.el-sub-menu__title) {
    color: #bfcbd9;

    &:hover {
      background: #263445;
      color: #fff;
    }
  }

  // 子菜单背景
  :deep(.el-menu--inline) {
    background: #1f2d3d;
  }
}

// 折叠动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
