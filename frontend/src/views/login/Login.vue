<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="login-bg">
      <div class="bg-shape bg-shape-1"></div>
      <div class="bg-shape bg-shape-2"></div>
      <div class="bg-shape bg-shape-3"></div>
    </div>

    <div class="login-card">
      <!-- 头部 Logo -->
      <div class="login-header">
        <div class="logo-icon">
          <el-icon :size="32" color="#fff"><School /></el-icon>
        </div>
        <h1 class="title">学生成绩管理系统</h1>
        <p class="subtitle">Student Grade Management System</p>
      </div>

      <!-- 登录表单 -->
      <el-form
        ref="formRef"
        :model="loginForm"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 底部提示 -->
      <div class="login-footer"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElForm } from 'element-plus'
import type { FormRules } from 'element-plus'
import { User, Lock, School } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

/** 表单引用 */
const formRef = ref<InstanceType<typeof ElForm>>()

/** 加载状态 */
const loading = ref(false)

/** 登录表单 */
const loginForm = reactive({
  username: '',
  password: '',
})

/** 表单验证规则 */
const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 128, message: '密码长度在 6 到 128 个字符', trigger: 'blur' },
  ],
}

/**
 * 处理登录
 */
async function handleLogin() {
  if (!formRef.value) {
    ElMessage.warning('页面加载异常，请刷新后重试')
    return
  }

  // 表单验证 —— 不依赖 validate() 的返回值，
  // 只区分 resolved（验证通过）和 rejected（验证失败）两种状态
  try {
    await formRef.value.validate()
  } catch {
    // rejected = 验证失败，表单已自动显示行内错误提示，直接返回
    return
  }

  loading.value = true
  try {
    const success = await authStore.login(loginForm.username, loginForm.password)

    if (success) {
      // 登录成功，跳转到目标页面或默认首页
      const redirect = (route.query.redirect as string) || '/dashboard'
      await router.push(redirect)
    }
  } catch {
    ElMessage.error('登录失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1B2A3D 0%, #233B55 40%, #1F5C55 100%);
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.login-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.08;
}

.bg-shape-1 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #2A9D8F, transparent 70%);
  top: -150px;
  right: -100px;
}

.bg-shape-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #52B788, transparent 70%);
  bottom: -120px;
  left: -80px;
}

.bg-shape-3 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, #E9A23B, transparent 70%);
  top: 40%;
  left: 60%;
}

/* 登录卡片 */
.login-card {
  width: 420px;
  padding: 44px 40px 36px;
  background: rgba(255, 255, 255, 0.97);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  z-index: 10;
  animation: cardEnter 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(24px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 头部 */
.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.logo-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #2A9D8F, #3BBFA0);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  box-shadow: 0 4px 16px rgba(42, 157, 143, 0.35);
}

.title {
  font-size: 24px;
  font-weight: 700;
  color: #1A1A2E;
  margin: 0 0 6px 0;
  letter-spacing: -0.01em;
}

.subtitle {
  font-size: 13px;
  color: #7B8794;
  margin: 0;
  letter-spacing: 0.02em;
}

/* 表单 */
.login-form {
  margin-bottom: 20px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #E8EAED inset;
  padding: 4px 12px;
  transition: box-shadow 0.2s ease;
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #D0D5DD inset;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(42, 157, 143, 0.25) inset, 0 0 0 1px #2A9D8F inset;
}

.login-button {
  width: 100%;
  height: 46px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  margin-top: 4px;
  background: linear-gradient(135deg, #2A9D8F, #238A7E);
  border: none;
  letter-spacing: 0.05em;
  transition: all 0.2s ease;
}

.login-button:hover {
  background: linear-gradient(135deg, #238A7E, #1F7A6F);
  box-shadow: 0 4px 16px rgba(42, 157, 143, 0.4);
  transform: translateY(-1px);
}

.login-button:active {
  transform: translateY(0);
}

/* 底部提示 */
.login-footer {
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-card {
    width: calc(100% - 32px);
    padding: 32px 24px 28px;
    margin: 16px;
  }

  .title {
    font-size: 20px;
  }

  .login-button {
    height: 42px;
    font-size: 15px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .login-card {
    animation: none;
  }
}
</style>
