<template>
  <aside class="app-sidebar" :class="{ collapsed: appStore.sidebarCollapsed }">
    <!-- Logo -->
    <div class="sidebar-logo" @click="router.push('/dashboard')">
      <div class="logo-icon-wrap">
        <img src="@/assets/images/logo.svg" alt="Logo" class="logo-img" />
      </div>
      <transition name="fade">
        <div v-show="!appStore.sidebarCollapsed" class="logo-text-wrap">
          <span class="logo-text">成绩管理系统</span>
          <span class="logo-sub">Grade Manager</span>
        </div>
      </transition>
    </div>

    <!-- 菜单 -->
    <el-scrollbar class="sidebar-menu-wrapper">
      <el-menu
        :default-active="activeMenu"
        :model-value="activeMenu"
        :collapse="appStore.sidebarCollapsed"
        :collapse-transition="false"
        router
        class="sidebar-menu"
      >
        <!-- 仪表盘（所有角色可见） -->
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>

        <!-- 学生管理（仅管理员和教师可见） -->
        <el-sub-menu v-if="authStore.isAdmin || authStore.isTeacher" index="/student">
          <template #title>
            <el-icon><User /></el-icon>
            <span>学生管理</span>
          </template>
          <el-menu-item index="/student/list">
            <el-icon><List /></el-icon>
            <template #title>学生列表</template>
          </el-menu-item>
          <el-menu-item index="/student/add">
            <el-icon><CirclePlus /></el-icon>
            <template #title>添加学生</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- 成绩管理（仅管理员和教师可见） -->
        <el-sub-menu v-if="authStore.isAdmin || authStore.isTeacher" index="/grade">
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
          <!-- 统计概览（所有角色可见） -->
          <el-menu-item index="/statistics/overview">
            <el-icon><TrendCharts /></el-icon>
            <template #title>统计概览</template>
          </el-menu-item>
          <!-- 班级统计（仅管理员和教师可见） -->
          <el-menu-item v-if="authStore.isAdmin || authStore.isTeacher" index="/statistics/class">
            <el-icon><School /></el-icon>
            <template #title>班级统计</template>
          </el-menu-item>
          <!-- 科目统计（仅管理员和教师可见） -->
          <el-menu-item v-if="authStore.isAdmin || authStore.isTeacher" index="/statistics/subject">
            <el-icon><Collection /></el-icon>
            <template #title>科目统计</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- 我的成绩（仅学生可见） -->
        <el-menu-item v-if="authStore.isStudent" index="/my-grades">
          <el-icon><Trophy /></el-icon>
          <template #title>我的成绩</template>
        </el-menu-item>
      </el-menu>
    </el-scrollbar>

    <!-- 底部折叠提示 -->
    <div class="sidebar-footer">
      <transition name="fade">
        <span v-show="!appStore.sidebarCollapsed" class="footer-text">
          学生成绩管理系统 v1.0
        </span>
      </transition>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const authStore = useAuthStore()

/** 当前激活的菜单项 */
const activeMenu = computed(() => {
  const { path } = route
  // 对于子路由，返回对应的父级菜单项
  if (path.startsWith('/student/edit') || path.startsWith('/student/detail')) {
    return '/student/list'
  }
  if (path.startsWith('/student/import')) {
    return '/student/list'
  }
  if (path.startsWith('/grade/import')) {
    return '/grade/list'
  }
  return path
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables.scss' as *;

.app-sidebar {
  width: $sidebar-width;
  height: 100vh;
  background: $bg-secondary;
  transition: width $transition-normal;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 200;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-right: 1px solid $border-primary;

  &.collapsed {
    width: $sidebar-collapsed-width;
  }
}

// ===== Logo =====
.sidebar-logo {
  display: flex;
  align-items: center;
  height: 68px;
  padding: 0 $space-4;
  cursor: pointer;
  overflow: hidden;
  white-space: nowrap;
  flex-shrink: 0;
  border-bottom: 1px solid $border-primary;
}

.logo-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: $rounded-lg;
  background: $gradient-primary;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: $glow-sm;
}

.logo-img {
  width: 22px;
  height: 22px;
  filter: brightness(0) invert(1);
}

.logo-text-wrap {
  margin-left: $space-3;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.logo-text {
  font-size: $text-lg;
  font-weight: $font-bold;
  color: $text-primary;
  letter-spacing: 0.02em;
  line-height: 1.3;
}

.logo-sub {
  font-size: $text-xs;
  color: $text-muted;
  letter-spacing: 0.04em;
  line-height: 1.3;
}

// ===== 菜单区域 =====
.sidebar-menu-wrapper {
  flex: 1;
  overflow: hidden;
  padding: $space-2 0;
}

.sidebar-menu {
  border-right: none;
  background: transparent;
  padding: 0 $space-2;

  // 菜单项样式
  :deep(.el-menu-item) {
    color: $text-secondary;
    height: 44px;
    line-height: 44px;
    border-radius: $rounded-lg;
    margin-bottom: $space-1;
    padding-left: $space-4 !important;
    transition: all $transition-fast;
    background: transparent;
    border: none;

    .el-icon {
      font-size: 18px;
      margin-right: $space-3;
      transition: color $transition-fast;
    }

    &:hover {
      background: rgba(37, 99, 235, 0.1);
      color: $text-primary;
    }

    &.is-active {
      background: rgba(37, 99, 235, 0.2);
      color: $accent-primary;
      font-weight: $font-semibold;
      position: relative;

      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 3px;
        height: 20px;
        background: $accent-primary;
        border-radius: 0 3px 3px 0;
      }

      .el-icon {
        color: $accent-primary;
      }
    }
  }

  // 子菜单标题样式
  :deep(.el-sub-menu__title) {
    color: $text-secondary;
    height: 44px;
    line-height: 44px;
    border-radius: $rounded-lg;
    margin-bottom: $space-1;
    padding-left: $space-4 !important;
    transition: all $transition-fast;
    background: transparent;
    border: none;

    .el-icon {
      font-size: 18px;
      margin-right: $space-3;
      transition: color $transition-fast;
    }

    &:hover {
      background: rgba(37, 99, 235, 0.1);
      color: $text-primary;
    }
  }

  // 子菜单展开时父级高亮
  :deep(.el-sub-menu.is-opened > .el-sub-menu__title) {
    color: $text-primary;
    background: rgba(37, 99, 235, 0.05);

    .el-icon {
      color: $accent-primary;
    }
  }

  // 子菜单背景
  :deep(.el-menu--inline) {
    background: transparent;

    .el-menu-item {
      padding-left: 48px !important;
      height: 40px;
      line-height: 40px;
      font-size: $text-sm;
    }
  }

  // 展开箭头
  :deep(.el-sub-menu__icon-arrow) {
    color: $text-muted;
  }
}

// ===== 底部 =====
.sidebar-footer {
  padding: $space-3 $space-4;
  border-top: 1px solid $border-primary;
  flex-shrink: 0;
}

.footer-text {
  font-size: $text-xs;
  color: $text-muted;
  white-space: nowrap;
}

// 折叠动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

// 折叠状态下的特殊处理
.app-sidebar.collapsed {
  width: $sidebar-collapsed-width;

  .sidebar-logo {
    padding: 0;
    justify-content: center;
  }

  .sidebar-footer {
    display: none;
  }

  .sidebar-menu {
    padding: 0 $space-1;

    :deep(.el-menu-item),
    :deep(.el-sub-menu__title) {
      padding-left: 0 !important;
      justify-content: center;
      text-align: center;

      .el-icon {
        margin-right: 0;
        font-size: 20px;
      }
    }

    :deep(.el-menu--inline .el-menu-item) {
      padding-left: 0 !important;
      justify-content: center;
    }

    // 子菜单箭头隐藏
    :deep(.el-sub-menu__icon-arrow) {
      display: none;
    }
  }
}
</style>