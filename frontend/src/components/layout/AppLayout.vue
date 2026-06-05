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
.app-layout {
  min-height: 100vh;
}

.layout-main {
  min-height: 100vh;
  transition: margin-left var(--transition-duration);
  display: flex;
  flex-direction: column;
}

.layout-content {
  flex: 1;
  padding: 16px;
  background: var(--bg-color);
  overflow-y: auto;
}

// 页面切换动画
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
