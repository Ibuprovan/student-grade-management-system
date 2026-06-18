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

    <!-- 首次登录修改密码对话框 -->
    <ChangePasswordDialog
      v-model="showChangePassword"
      @success="onPasswordChanged"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import ChangePasswordDialog from '@/components/common/ChangePasswordDialog.vue'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

const appStore = useAppStore()
const authStore = useAuthStore()

/** 是否显示修改密码对话框 */
const showChangePassword = ref(false)

/** 监听用户信息变化，检查是否需要修改密码 */
watch(() => authStore.user, (user) => {
  if (user?.need_change_password) {
    showChangePassword.value = true
  }
}, { immediate: true })

/** 密码修改成功回调 */
function onPasswordChanged() {
  showChangePassword.value = false
}

/** 初始化应用状态 */
onMounted(() => {
  appStore.initState()
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables.scss' as *;

.app-layout {
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