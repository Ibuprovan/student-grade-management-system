<template>
  <div class="pagination-wrapper" :class="{ 'pagination-background': background }">
    <div class="pagination-info">
      <span v-if="showTotal" class="total-text">
        共 <strong>{{ total }}</strong> 条数据
      </span>
    </div>
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="currentPageSize"
      :page-sizes="pageSizes"
      :total="total"
      :layout="layout"
      :background="background"
      :small="small"
      :disabled="disabled"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
      @prev-click="handlePrevClick"
      @next-click="handleNextClick"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

/** Props 定义 */
interface Props {
  /** 当前页码 */
  currentPage?: number
  /** 每页条数 */
  pageSize?: number
  /** 总条数 */
  total?: number
  /** 每页条数选项 */
  pageSizes?: number[]
  /** 分页布局 */
  layout?: string
  /** 是否显示背景色 */
  background?: boolean
  /** 是否使用小尺寸 */
  small?: boolean
  /** 是否禁用 */
  disabled?: boolean
  /** 是否显示总数 */
  showTotal?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  currentPage: 1,
  pageSize: 20,
  total: 0,
  pageSizes: () => [10, 20, 50, 100],
  layout: 'sizes, prev, pager, next, jumper',
  background: true,
  small: false,
  disabled: false,
  showTotal: true,
})

/** Emits 定义 */
const emit = defineEmits<{
  'update:currentPage': [page: number]
  'update:pageSize': [size: number]
  'page-change': [page: number]
  'size-change': [size: number]
  'prev-click': [page: number]
  'next-click': [page: number]
}>()

/** 内部状态 */
const currentPage = ref(props.currentPage)
const currentPageSize = ref(props.pageSize)

/** 监听外部变化 */
watch(
  () => props.currentPage,
  (val) => {
    currentPage.value = val
  },
)

watch(
  () => props.pageSize,
  (val) => {
    currentPageSize.value = val
  },
)

/** 处理页码变化 */
function handlePageChange(page: number) {
  emit('update:currentPage', page)
  emit('page-change', page)
}

/** 处理每页条数变化 */
function handleSizeChange(size: number) {
  emit('update:pageSize', size)
  emit('size-change', size)
  // 切换每页条数时回到第一页
  if (currentPage.value !== 1) {
    currentPage.value = 1
    emit('update:currentPage', 1)
    emit('page-change', 1)
  }
}

/** 处理上一页 */
function handlePrevClick(page: number) {
  emit('prev-click', page)
}

/** 处理下一页 */
function handleNextClick(page: number) {
  emit('next-click', page)
}
</script>

<style lang="scss" scoped>
.pagination-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;

  &.pagination-background {
    padding: 16px 20px;
    background: var(--surface-color);
    border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-color-light);
    box-shadow: var(--shadow-xs);
  }
}

.pagination-info {
  .total-text {
    font-size: 13px;
    color: var(--text-color-secondary);

    strong {
      color: var(--primary-color);
      font-weight: 600;
    }
  }
}

@media (max-width: 768px) {
  .pagination-wrapper {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
