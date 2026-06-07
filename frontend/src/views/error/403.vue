<template>
  <div class="error-page">
    <div class="error-content">
      <div class="error-icon">
        <el-icon :size="80" color="var(--warning-color)">
          <Lock />
        </el-icon>
      </div>
      <h1 class="error-code">403</h1>
      <h2 class="error-title">抱歉，您没有权限访问此页面</h2>
      <p class="error-desc">
        您当前的角色没有权限访问该资源，请联系管理员获取相应权限。
      </p>
      <div class="error-actions">
        <el-button type="primary" @click="goHome">
          <el-icon><HomeFilled /></el-icon>
          返回首页
        </el-button>
        <el-button @click="goBack">
          <el-icon><Back /></el-icon>
          返回上一页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Lock, HomeFilled, Back } from '@element-plus/icons-vue'

const router = useRouter()

/** 返回首页 */
function goHome() {
  router.push('/dashboard')
}

/** 返回上一页 */
function goBack() {
  router.back()
}
</script>

<style scoped>
.error-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--bg-color);
}

.error-content {
  text-align: center;
  padding: 48px;
  background: var(--surface-color);
  border-radius: var(--border-radius-xl);
  border: 1px solid var(--border-color-light);
  box-shadow: var(--shadow-sm);
  max-width: 480px;
}

.error-icon {
  margin-bottom: 20px;
  opacity: 0.8;
}

.error-code {
  font-size: 72px;
  font-weight: 800;
  color: var(--warning-color);
  margin: 0 0 12px 0;
  line-height: 1;
  letter-spacing: -0.04em;
}

.error-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 8px 0;
}

.error-desc {
  font-size: 14px;
  color: var(--text-color-secondary);
  margin: 0 0 32px 0;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style>
