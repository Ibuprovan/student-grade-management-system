<template>
  <el-dialog
    v-model="visible"
    :title="title"
    :width="width"
    :close-on-click-modal="false"
    :close-on-press-escape="closeOnPressEscape"
    :show-close="showClose"
    :center="center"
    @close="handleClose"
  >
    <div class="confirm-content">
      <el-icon v-if="showIcon" :class="['confirm-icon', iconType]">
        <component :is="iconComponent" />
      </el-icon>
      <div class="confirm-message">
        <p v-if="message" class="message-text">{{ message }}</p>
        <slot />
      </div>
    </div>

    <template #footer>
      <div class="confirm-footer" :class="{ 'footer-center': center }">
        <el-button @click="handleCancel" :disabled="loading">
          {{ cancelText }}
        </el-button>
        <el-button
          :type="confirmButtonType"
          :loading="loading"
          @click="handleConfirm"
        >
          {{ confirmText }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

/** 对话框类型 */
type DialogType = 'info' | 'success' | 'warning' | 'danger'

/** Props 定义 */
interface Props {
  /** 是否显示对话框 */
  modelValue: boolean
  /** 标题 */
  title?: string
  /** 提示消息 */
  message?: string
  /** 对话框类型 */
  type?: DialogType
  /** 宽度 */
  width?: string | number
  /** 确认按钮文本 */
  confirmText?: string
  /** 取消按钮文本 */
  cancelText?: string
  /** 是否显示图标 */
  showIcon?: boolean
  /** 是否显示关闭按钮 */
  showClose?: boolean
  /** 是否居中 */
  center?: boolean
  /** 是否可通过按下 ESC 关闭 */
  closeOnPressEscape?: boolean
  /** 确认时是否显示加载状态 */
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '提示',
  message: '',
  type: 'warning',
  width: '420px',
  confirmText: '确定',
  cancelText: '取消',
  showIcon: true,
  showClose: true,
  center: false,
  closeOnPressEscape: true,
  loading: false,
})

/** Emits 定义 */
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: []
  cancel: []
  close: []
}>()

/** 内部可见状态 */
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

/** 图标组件 */
const iconComponent = computed(() => {
  const iconMap: Record<DialogType, string> = {
    info: 'InfoFilled',
    success: 'SuccessFilled',
    warning: 'WarningFilled',
    danger: 'CircleCloseFilled',
  }
  return iconMap[props.type]
})

/** 图标类型 */
const iconType = computed(() => props.type)

/** 确认按钮类型 */
const confirmButtonType = computed(() => {
  const typeMap: Record<DialogType, string> = {
    info: 'primary',
    success: 'success',
    warning: 'warning',
    danger: 'danger',
  }
  return typeMap[props.type] as 'primary' | 'success' | 'warning' | 'danger'
})

/** 处理确认 */
function handleConfirm() {
  emit('confirm')
}

/** 处理取消 */
function handleCancel() {
  visible.value = false
  emit('cancel')
}

/** 处理关闭 */
function handleClose() {
  emit('close')
}
</script>

<style lang="scss" scoped>
.confirm-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 10px 0;
}

.confirm-icon {
  font-size: 48px;
  flex-shrink: 0;

  &.info {
    color: var(--el-color-primary);
  }

  &.success {
    color: var(--el-color-success);
  }

  &.warning {
    color: var(--el-color-warning);
  }

  &.danger {
    color: var(--el-color-danger);
  }
}

.confirm-message {
  flex: 1;

  .message-text {
    font-size: 14px;
    line-height: 1.6;
    color: var(--el-text-color-regular);
    margin: 0;
  }
}

.confirm-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  &.footer-center {
    justify-content: center;
  }
}
</style>
