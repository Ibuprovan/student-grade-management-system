<template>
  <div class="search-form">
    <el-form :model="formModel" :inline="true" @submit.prevent="handleSearch">
      <slot :form="formModel" />

      <el-form-item class="search-form-actions">
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="handleReset">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
        <el-button
          v-if="showCollapse"
          type="primary"
          link
          @click="isCollapsed = !isCollapsed"
        >
          {{ isCollapsed ? '展开' : '收起' }}
          <el-icon class="collapse-icon" :class="{ expanded: !isCollapsed }">
            <ArrowDown />
          </el-icon>
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'

/** Props 定义 */
interface Props {
  /** 初始表单数据 */
  modelValue?: Record<string, unknown>
  /** 是否显示展开/收起按钮 */
  showCollapse?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => ({}),
  showCollapse: false,
})

/** Emits 定义 */
const emit = defineEmits<{
  'update:modelValue': [value: Record<string, unknown>]
  search: [form: Record<string, unknown>]
  reset: []
}>()

/** 表单模型 */
const formModel = reactive<Record<string, unknown>>({ ...props.modelValue })

/** 是否收起状态 */
const isCollapsed = ref(true)

/** 监听外部值变化 */
watch(
  () => props.modelValue,
  (val) => {
    Object.assign(formModel, val)
  },
  { deep: true },
)

/** 处理搜索 */
function handleSearch() {
  emit('search', { ...formModel })
}

/** 处理重置 */
function handleReset() {
  // 重置表单字段
  Object.keys(formModel).forEach((key) => {
    formModel[key] = props.modelValue[key] ?? ''
  })
  emit('reset')
  emit('search', { ...formModel })
}

/** 暴露方法 */
defineExpose({
  /** 获取表单数据 */
  getFormData: () => ({ ...formModel }),
  /** 设置表单数据 */
  setFormData: (data: Record<string, unknown>) => {
    Object.assign(formModel, data)
  },
})
</script>

<style lang="scss" scoped>
.search-form {
  padding: 20px 24px;
  background: var(--surface-color);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color-light);
  box-shadow: var(--shadow-xs);
  margin-bottom: 16px;

  :deep(.el-form-item) {
    margin-bottom: 12px;
    margin-right: 16px;
  }

  :deep(.el-form-item__label) {
    font-weight: 500;
    color: var(--text-color);
  }
}

.search-form-actions {
  :deep(.el-form-item__content) {
    display: flex;
    gap: 8px;
  }
}

.collapse-icon {
  transition: transform var(--transition-duration);
  margin-left: 4px;

  &.expanded {
    transform: rotate(180deg);
  }
}
</style>
