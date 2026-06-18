<template>
  <div class="app-layout">
    <!-- 侧边栏 -->
    <AppSidebar />

    <!-- 主内容区 -->
    <div
      class="layout-main"
      :style="{ marginLeft: appStore.sidebarWidth }"
    >
      <!-- 头部导航 -->
      <AppHeader />

      <!-- 页面内容 -->
      <main class="layout-content">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

/** 初始化应用状态 */
onMounted(() => {
  appStore.initState()
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables.scss' as *;

.app-layout {
  min-height: 100vh;
  background: $bg-primary;
}

.layout-main {
  transition: margin-left $transition-normal;
  display: flex;
  flex-direction: column;
}

.layout-content {
  padding: $space-5;
  background: $bg-primary;
  overflow-x: hidden;
  width: 100%;
}

@media (max-width: $breakpoint-xl) {
  .layout-content {
    padding: $space-4;
  }
}

@media (max-width: $breakpoint-lg) {
  .layout-content {
    padding: $space-3;
  }
}

// 页面切换动画
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.25s ease;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-12px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(12px);
}

@media (prefers-reduced-motion: reduce) {
  .fade-transform-enter-active,
  .fade-transform-leave-active {
    transition: opacity 0.1s;
  }

  .fade-transform-enter-from,
  .fade-transform-leave-to {
    transform: none;
  }
}
</style>