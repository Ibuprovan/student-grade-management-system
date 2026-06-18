<template>
  <div class="data-table">
    <el-table
      v-loading="loading"
      :data="data"
      :border="border"
      :stripe="stripe"
      :height="height"
      :max-height="maxHeight"
      :row-key="rowKey"
      :highlight-current-row="highlightCurrentRow"
      :empty-text="emptyText"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
      @row-click="handleRowClick"
    >
      <!-- 选择列 -->
      <el-table-column v-if="showSelection" type="selection" width="55" align="center" />

      <!-- 序号列 -->
      <el-table-column v-if="showIndex" type="index" label="序号" width="70" align="center" />

      <!-- 数据列 -->
      <slot />

      <!-- 操作列 -->
      <el-table-column
        v-if="$slots.actions"
        label="操作"
        :width="actionsWidth"
        :fixed="actionsFixed"
        align="center"
      >
        <template #default="scope">
          <slot name="actions" v-bind="scope" />
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div v-if="showPagination" class="table-pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="currentPageSize"
        :page-sizes="pageSizes"
        :total="total"
        :layout="paginationLayout"
        :background="true"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

/** Props 定义 */
interface Props {
  /** 表格数据 */
  data: unknown[]
  /** 是否加载中 */
  loading?: boolean
  /** 是否显示边框 */
  border?: boolean
  /** 是否显示斑马纹 */
  stripe?: boolean
  /** 表格高度 */
  height?: string | number
  /** 表格最大高度 */
  maxHeight?: string | number
  /** 行数据的 Key */
  rowKey?: string
  /** 是否高亮当前行 */
  highlightCurrentRow?: boolean
  /** 空数据文本 */
  emptyText?: string
  /** 是否显示选择列 */
  showSelection?: boolean
  /** 是否显示序号列 */
  showIndex?: boolean
  /** 操作列宽度 */
  actionsWidth?: string | number
  /** 操作列是否固定 */
  actionsFixed?: boolean | string
  /** 是否显示分页 */
  showPagination?: boolean
  /** 当前页码 */
  currentPage?: number
  /** 每页条数 */
  pageSize?: number
  /** 总条数 */
  total?: number
  /** 每页条数选项 */
  pageSizes?: number[]
  /** 分页布局 */
  paginationLayout?: string
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  loading: false,
  border: true,
  stripe: true,
  rowKey: 'id',
  highlightCurrentRow: false,
  emptyText: '暂无数据',
  showSelection: false,
  showIndex: false,
  actionsWidth: 180,
  actionsFixed: 'right',
  showPagination: true,
  currentPage: 1,
  pageSize: 20,
  total: 0,
  pageSizes: () => [10, 20, 50, 100],
  paginationLayout: 'total, sizes, prev, pager, next, jumper',
})

/** Emits 定义 */
const emit = defineEmits<{
  'update:currentPage': [page: number]
  'update:pageSize': [size: number]
  'selection-change': [selection: unknown[]]
  'sort-change': [sort: { prop: string; order: string }]
  'row-click': [row: unknown, column: unknown, event: unknown]
}>()

/** 内部页码状态 */
const currentPage = ref(props.currentPage)
const currentPageSize = ref(props.pageSize)

/** 监听外部页码变化 */
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

/** 处理选择变化 */
function handleSelectionChange(selection: unknown[]) {
  emit('selection-change', selection)
}

/** 处理排序变化 */
function handleSortChange(sort: { prop: string; order: string }) {
  emit('sort-change', sort)
}

/** 处理行点击 */
function handleRowClick(row: unknown, column: unknown, event: unknown) {
  emit('row-click', row, column, event)
}

/** 处理页码变化 */
function handlePageChange(page: number) {
  emit('update:currentPage', page)
}

/** 处理每页条数变化 */
function handleSizeChange(size: number) {
  emit('update:pageSize', size)
  emit('update:currentPage', 1)
}
</script>

<style lang="scss" scoped>
.data-table {
  background: var(--surface-color);
  border-radius: var(--border-radius-lg);
  width: 100%;

  :deep(.el-table) {
    width: 100% !important;
  }
}

.table-pagination {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color-light);
}
</style>
