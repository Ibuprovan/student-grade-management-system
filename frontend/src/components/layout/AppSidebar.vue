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
            <el-icon><TrendCharts /></el-icon>
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
  background: var(--sidebar-bg);
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

// ===== Logo =====
.sidebar-logo {
  display: flex;
  align-items: center;
  height: 68px;
  padding: 0 18px;
  cursor: pointer;
  overflow: hidden;
  white-space: nowrap;
  flex-shrink: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.logo-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--primary-color), #3BBFA0);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(42, 157, 143, 0.35);
}

.logo-img {
  width: 22px;
  height: 22px;
  filter: brightness(0) invert(1);
}

.logo-text-wrap {
  margin-left: 12px;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.logo-text {
  font-size: 15px;
  font-weight: 700;
  color: #FFFFFF;
  letter-spacing: 0.02em;
  line-height: 1.3;
}

.logo-sub {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.45);
  letter-spacing: 0.04em;
  line-height: 1.3;
}

// ===== 菜单区域 =====
.sidebar-menu-wrapper {
  flex: 1;
  overflow: hidden;
  padding: 8px 0;
}

.sidebar-menu {
  border-right: none;
  background: transparent;
  padding: 0 8px;

  // 菜单项样式
  :deep(.el-menu-item) {
    color: var(--sidebar-text);
    height: 44px;
    line-height: 44px;
    border-radius: 10px;
    margin-bottom: 2px;
    padding-left: 14px !important;
    transition: all var(--transition-fast);

    .el-icon {
      font-size: 18px;
      margin-right: 10px;
    }

    &:hover {
      background: var(--sidebar-hover-bg);
      color: var(--sidebar-text-active);
    }

    &.is-active {
      background: var(--sidebar-active-bg);
      color: var(--primary-color);
      font-weight: 600;
      position: relative;

      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 3px;
        height: 20px;
        background: var(--primary-color);
        border-radius: 0 3px 3px 0;
      }
    }
  }

  // 子菜单标题样式
  :deep(.el-sub-menu__title) {
    color: var(--sidebar-text);
    height: 44px;
    line-height: 44px;
    border-radius: 10px;
    margin-bottom: 2px;
    padding-left: 14px !important;
    transition: all var(--transition-fast);

    .el-icon {
      font-size: 18px;
      margin-right: 10px;
    }

    &:hover {
      background: var(--sidebar-hover-bg);
      color: var(--sidebar-text-active);
    }
  }

  // 子菜单背景
  :deep(.el-menu--inline) {
    background: transparent;

    .el-menu-item {
      padding-left: 48px !important;
      height: 40px;
      line-height: 40px;
      font-size: 13px;
    }
  }

  // 展开箭头
  :deep(.el-sub-menu__icon-arrow) {
    color: rgba(255, 255, 255, 0.3);
  }
}

// ===== 底部 =====
.sidebar-footer {
  padding: 12px 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.footer-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.25);
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
  .sidebar-logo {
    padding: 0;
    justify-content: center;
  }

  .sidebar-menu {
    padding: 0 6px;

    :deep(.el-menu-item),
    :deep(.el-sub-menu__title) {
      padding-left: 0 !important;
      justify-content: center;

      .el-icon {
        margin-right: 0;
      }
    }

    :deep(.el-menu--inline .el-menu-item) {
      padding-left: 0 !important;
    }
  }
}
</style>
