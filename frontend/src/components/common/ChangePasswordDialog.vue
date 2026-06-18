<template>
  <el-dialog
    v-model="visible"
    title="修改密码"
    width="420px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
    center
  >
    <div class="password-change-content">
      <el-alert
        title="首次登录请修改初始密码"
        type="warning"
        :closable="false"
        show-icon
        class="mb-4"
      />
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="0"
        @submit.prevent="handleSubmit"
      >
        <el-form-item prop="oldPassword">
          <el-input
            v-model="form.oldPassword"
            type="password"
            placeholder="当前密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>
        <el-form-item prop="newPassword">
          <el-input
            v-model="form.newPassword"
            type="password"
            placeholder="新密码（至少8位，包含大小写字母和数字）"
            size="large"
            :prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="确认新密码"
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
            class="submit-btn"
            :loading="loading"
            @click="handleSubmit"
          >
            {{ loading ? '提交中...' : '确认修改' }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage, ElForm } from 'element-plus'
import type { FormRules } from 'element-plus'
import { Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}>()

const authStore = useAuthStore()

/** 表单引用 */
const formRef = ref<InstanceType<typeof ElForm>>()

/** 加载状态 */
const loading = ref(false)

/** 对话框可见性 */
const visible = ref(props.modelValue)

/** 监听 props 变化 */
watch(() => props.modelValue, (val) => {
  visible.value = val
})

/** 监听 visible 变化 */
watch(visible, (val) => {
  emit('update:modelValue', val)
})

/** 表单数据 */
const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

/** 自定义确认密码验证 */
const validateConfirmPassword = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (value === '') {
    callback(new Error('请再次输入新密码'))
  } else if (value !== form.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

/** 表单验证规则 */
const rules: FormRules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' },
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, max: 128, message: '密码长度在 8 到 128 个字符', trigger: 'blur' },
    {
      pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
      message: '密码必须包含大小写字母和数字',
      trigger: 'blur',
    },
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

/** 提交表单 */
async function handleSubmit() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    const success = await authStore.changePassword(form.oldPassword, form.newPassword)
    if (success) {
      visible.value = false
      emit('success')
      // 重新获取用户信息以更新 need_change_password 状态
      await authStore.fetchCurrentUser()
    }
  } catch (error) {
    console.error('修改密码失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.password-change-content {
  padding: 0 20px;
}

.mb-4 {
  margin-bottom: 16px;
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 10px;
  background: linear-gradient(135deg, #2A9D8F, #238A7E);
  border: none;
  transition: all 0.2s ease;
}

.submit-btn:hover {
  background: linear-gradient(135deg, #238A7E, #1F7A6F);
  box-shadow: 0 4px 16px rgba(42, 157, 143, 0.4);
  transform: translateY(-1px);
}

.submit-btn:active {
  transform: translateY(0);
}
</style>
