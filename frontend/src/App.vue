<template>
  <el-config-provider :locale="zhCn">
    <!-- 登录页面：不显示布局 -->
    <template v-if="isLoginPage">
      <router-view />
    </template>

    <!-- 其他页面：显示完整布局 -->
    <template v-else>
      <AppLayout />
    </template>
  </el-config-provider>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import AppLayout from '@/components/layout/AppLayout.vue'

const route = useRoute()

/** 是否是登录页面 */
const isLoginPage = computed(() => route.path === '/login')
</script>

<style>
html,
body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial,
    sans-serif;
}

#app {
  height: 100%;
}
</style>
