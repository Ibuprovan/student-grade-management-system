<template>
  <div class="empty-state" :class="[`empty-state--${size}`]">
    <!-- 图标区域 -->
    <div class="empty-state__icon" :style="iconStyle">
      <el-icon :size="iconSize">
        <component :is="icon" v-if="icon" />
        <FolderOpened v-else />
      </el-icon>
    </div>

    <!-- 文案区域 -->
    <div class="empty-state__content">
      <h4 class="empty-state__title">{{ title }}</h4>
      <p v-if="description" class="empty-state__desc">{{ description }}</p>
    </div>

    <!-- 操作按钮（可选） -->
    <div v-if="actionText" class="empty-state__action">
      <el-button :type="actionType" @click="$emit('action')">
        <el-icon v-if="actionIcon"><component :is="actionIcon" /></el-icon>
        {{ actionText }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { FolderOpened } from '@element-plus/icons-vue'

interface EmptyStateProps {
  /** 自定义图标组件 */
  icon?: object
  /** 图标颜色 */
  iconColor?: string
  /** 标题文案 */
  title?: string
  /** 描述文案 */
  description?: string
  /** 操作按钮文案 */
  actionText?: string
  /** 操作按钮类型 */
  actionType?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  /** 操作按钮图标 */
  actionIcon?: object
  /** 尺寸：small | medium | large */
  size?: 'small' | 'medium' | 'large'
}

const props = withDefaults(defineProps<EmptyStateProps>(), {
  title: '暂无数据',
  description: '',
  actionText: '',
  actionType: 'primary',
  size: 'medium',
})

defineEmits<{
  action: []
}>()

const iconSize = computed(() => {
  const sizes = { small: 40, medium: 56, large: 72 }
  return sizes[props.size]
})

const iconStyle = computed(() => {
  if (props.iconColor) {
    return { color: props.iconColor }
  }
  return {}
})
</script>

<style lang="scss" scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  text-align: center;

  &--small {
    padding: 24px 16px;
  }

  &--large {
    padding: 60px 24px;
  }

  &__icon {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: var(--primary-light);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--primary-color);
    margin-bottom: 20px;

    .empty-state--small & {
      width: 60px;
      height: 60px;
      margin-bottom: 14px;
    }

    .empty-state--large & {
      width: 100px;
      height: 100px;
      margin-bottom: 24px;
    }
  }

  &__content {
    margin-bottom: 20px;
  }

  &__title {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-color);
    margin: 0 0 8px 0;
    line-height: 1.4;

    .empty-state--small & {
      font-size: 14px;
      margin-bottom: 4px;
    }
  }

  &__desc {
    font-size: 13px;
    font-weight: 400;
    color: var(--text-color-secondary);
    margin: 0;
    line-height: 1.6;
    max-width: 320px;

    .empty-state--small & {
      font-size: 12px;
      max-width: 240px;
    }
  }

  &__action {
    .el-button {
      height: 32px;
      font-size: 13px;
    }
  }
}
</style>
