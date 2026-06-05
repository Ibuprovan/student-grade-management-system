<template>
  <div class="student-list page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">学生列表</h1>
      <div class="header-actions">
        <el-button type="primary" @click="router.push('/student/add')">
          <el-icon><Plus /></el-icon>
          添加学生
        </el-button>
        <el-button
          type="danger"
          :disabled="selectedStudents.length === 0"
          @click="handleBatchDelete"
        >
          <el-icon><Delete /></el-icon>
          批量删除
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- 搜索区域 -->
    <div class="search-section">
      <el-form :model="searchForm" inline>
        <el-form-item label="学号">
          <el-input
            v-model="searchForm.student_id"
            placeholder="请输入学号"
            clearable
            style="width: 180px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入姓名"
            clearable
            style="width: 180px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="班级">
          <el-select
            v-model="searchForm.class_name"
            placeholder="请选择班级"
            clearable
            style="width: 200px"
          >
            <el-option
              v-for="cls in classOptions"
              :key="cls"
              :label="cls"
              :value="cls"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 桌面端表格视图 -->
    <div class="table-view desktop-only">
      <DataTable
        :data="studentStore.students"
        :loading="studentStore.loading"
        :current-page="studentStore.pagination.page"
        :page-size="studentStore.pagination.pageSize"
        :total="studentStore.pagination.total"
        :show-selection="true"
        row-key="student_id"
        @update:current-page="handlePageChange"
        @update:page-size="handleSizeChange"
        @selection-change="handleSelectionChange"
        @sort-change="handleSortChange"
      >
        <el-table-column
          prop="student_id"
          label="学号"
          width="120"
          sortable="custom"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <el-link type="primary" @click="handleView(row.student_id)">
              {{ row.student_id }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column
          prop="name"
          label="姓名"
          width="120"
          sortable="custom"
          show-overflow-tooltip
        />
        <el-table-column
          prop="gender"
          label="性别"
          width="80"
          align="center"
          sortable="custom"
        >
          <template #default="{ row }">
            <el-tag :type="row.gender === '男' ? '' : 'danger'" size="small">
              {{ row.gender }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="class_name"
          label="班级"
          width="150"
          sortable="custom"
          show-overflow-tooltip
        />
        <el-table-column
          prop="enrollment_year"
          label="入学年份"
          width="100"
          align="center"
          sortable="custom"
        />
        <el-table-column
          prop="created_at"
          label="创建时间"
          width="180"
          sortable="custom"
        >
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>

        <template #actions="{ row }">
          <div class="table-actions">
            <el-button type="primary" link size="small" @click="handleView(row.student_id)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button type="primary" link size="small" @click="handleEdit(row.student_id)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- 移动端卡片视图 -->
    <div class="card-view mobile-only">
      <div v-loading="studentStore.loading" class="student-cards">
        <el-empty v-if="!studentStore.loading && studentStore.students.length === 0" description="暂无数据" />
        <div
          v-for="student in studentStore.students"
          :key="student.student_id"
          class="student-card"
        >
          <div class="card-header">
            <div class="student-avatar">
              <el-icon :size="24"><User /></el-icon>
            </div>
            <div class="student-info">
              <div class="student-name">{{ student.name }}</div>
              <div class="student-id">{{ student.student_id }}</div>
            </div>
            <el-tag :type="student.gender === '男' ? '' : 'danger'" size="small">
              {{ student.gender }}
            </el-tag>
          </div>
          <div class="card-body">
            <div class="info-item">
              <span class="label">班级：</span>
              <span class="value">{{ student.class_name }}</span>
            </div>
            <div class="info-item">
              <span class="label">入学年份：</span>
              <span class="value">{{ student.enrollment_year }}</span>
            </div>
          </div>
          <div class="card-footer">
            <el-button type="primary" link size="small" @click="handleView(student.student_id)">
              查看详情
            </el-button>
            <el-button type="primary" link size="small" @click="handleEdit(student.student_id)">
              编辑
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(student)">
              删除
            </el-button>
          </div>
        </div>
      </div>

      <!-- 移动端分页 -->
      <div class="mobile-pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="currentPageSize"
          :page-sizes="[10, 20, 50]"
          :total="studentStore.pagination.total"
          layout="total, prev, pager, next"
          :background="true"
          small
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <ConfirmDialog
      v-model="deleteDialogVisible"
      title="确认删除"
      :message="deleteConfirmMessage"
      type="danger"
      confirm-text="确认删除"
      :loading="deleteLoading"
      @confirm="confirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStudentStore } from '@/stores/student'
import DataTable from '@/components/common/DataTable.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import { formatDateTime } from '@/utils/format'
import { ElMessage } from 'element-plus'
import type { Student } from '@/types/student'

const router = useRouter()
const studentStore = useStudentStore()

/** 搜索表单 */
const searchForm = reactive({
  student_id: '',
  name: '',
  class_name: '',
})

/** 班级选项（从 store 获取或使用默认值） */
const classOptions = computed(() => {
  if (studentStore.classList.length > 0) {
    return studentStore.classList
  }
  return ['三年一班', '三年二班', '三年三班', '三年四班']
})

/** 选中的学生 */
const selectedStudents = ref<Student[]>([])

/** 排序参数 */
const sortParams = ref<{ prop: string; order: string } | null>(null)

/** 分页相关 */
const currentPage = ref(1)
const currentPageSize = ref(20)

/** 删除相关 */
const deleteDialogVisible = ref(false)
const deleteTarget = ref<Student | null>(null)
const deleteLoading = ref(false)
const isBatchDelete = ref(false)

/** 删除确认消息 */
const deleteConfirmMessage = computed(() => {
  if (isBatchDelete.value) {
    return `确定要删除选中的 ${selectedStudents.value.length} 名学生吗？此操作不可恢复。`
  }
  return `确定要删除学生 ${deleteTarget.value?.name}（${deleteTarget.value?.student_id}）吗？此操作不可恢复。`
})

/** 初始化 */
onMounted(() => {
  studentStore.fetchStudents()
  studentStore.fetchClassList()
})

/** 搜索 */
function handleSearch() {
  const params: Record<string, string | undefined> = {}
  if (searchForm.student_id) {
    params.keyword = searchForm.student_id
  } else if (searchForm.name) {
    params.keyword = searchForm.name
  }
  if (searchForm.class_name) {
    params.class_name = searchForm.class_name
  }
  studentStore.setSearchParams(params)
  studentStore.fetchStudents()
}

/** 重置搜索 */
function handleReset() {
  searchForm.student_id = ''
  searchForm.name = ''
  searchForm.class_name = ''
  studentStore.clearSearchParams()
  studentStore.fetchStudents()
}

/** 页码变化 */
function handlePageChange(page: number) {
  currentPage.value = page
  studentStore.setPage(page)
  studentStore.fetchStudents()
}

/** 每页条数变化 */
function handleSizeChange(size: number) {
  currentPageSize.value = size
  studentStore.setPageSize(size)
  studentStore.fetchStudents()
}

/** 选择变化 */
function handleSelectionChange(selection: Student[]) {
  selectedStudents.value = selection
}

/** 排序变化 */
function handleSortChange(sort: { prop: string; order: string }) {
  sortParams.value = sort
  // 前端排序（如果后端不支持排序）
  // 这里可以根据实际需求决定是前端排序还是后端排序
}

/** 查看详情 */
function handleView(studentId: string) {
  router.push(`/student/detail/${studentId}`)
}

/** 编辑 */
function handleEdit(studentId: string) {
  router.push(`/student/edit/${studentId}`)
}

/** 删除单个学生 */
function handleDelete(student: Student) {
  isBatchDelete.value = false
  deleteTarget.value = student
  deleteDialogVisible.value = true
}

/** 批量删除 */
function handleBatchDelete() {
  if (selectedStudents.value.length === 0) {
    ElMessage.warning('请先选择要删除的学生')
    return
  }
  isBatchDelete.value = true
  deleteDialogVisible.value = true
}

/** 确认删除 */
async function confirmDelete() {
  deleteLoading.value = true
  try {
    if (isBatchDelete.value) {
      // 批量删除
      const promises = selectedStudents.value.map((student) =>
        studentStore.deleteStudent(student.student_id)
      )
      await Promise.all(promises)
      ElMessage.success(`成功删除 ${selectedStudents.value.length} 名学生`)
      selectedStudents.value = []
    } else if (deleteTarget.value) {
      // 单个删除
      await studentStore.deleteStudent(deleteTarget.value.student_id)
    }
    deleteDialogVisible.value = false
    deleteTarget.value = null
  } finally {
    deleteLoading.value = false
  }
}

/** 导出数据 */
function handleExport() {
  // 构建导出数据
  const headers = ['学号', '姓名', '性别', '班级', '入学年份', '创建时间']
  const data = studentStore.students.map((student) => [
    student.student_id,
    student.name,
    student.gender,
    student.class_name,
    student.enrollment_year,
    formatDateTime(student.created_at),
  ])

  // 生成 CSV 内容
  const csvContent = [
    headers.join(','),
    ...data.map((row) => row.join(',')),
  ].join('\n')

  // 创建下载链接
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `学生列表_${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  URL.revokeObjectURL(link.href)

  ElMessage.success('导出成功')
}
</script>

<style lang="scss" scoped>
.student-list {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .page-title {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
    }

    .header-actions {
      display: flex;
      gap: 12px;
    }
  }

  .search-section {
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

    :deep(.el-form-item) {
      margin-bottom: 0;
      margin-right: 16px;
    }
  }

  .table-view {
    background: #fff;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }

  .table-actions {
    display: flex;
    justify-content: center;
    gap: 8px;
  }

  // 移动端卡片视图
  .card-view {
    .student-cards {
      display: grid;
      gap: 16px;
    }

    .student-card {
      background: #fff;
      border-radius: 8px;
      padding: 16px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

      .card-header {
        display: flex;
        align-items: center;
        margin-bottom: 12px;

        .student-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: #e8f4fd;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #409eff;
          margin-right: 12px;
        }

        .student-info {
          flex: 1;

          .student-name {
            font-size: 16px;
            font-weight: 600;
            color: #303133;
          }

          .student-id {
            font-size: 13px;
            color: #909399;
            margin-top: 4px;
          }
        }
      }

      .card-body {
        padding: 12px 0;
        border-top: 1px solid #f0f0f0;
        border-bottom: 1px solid #f0f0f0;

        .info-item {
          display: flex;
          justify-content: space-between;
          padding: 8px 0;

          .label {
            color: #909399;
            font-size: 14px;
          }

          .value {
            color: #303133;
            font-size: 14px;
          }
        }
      }

      .card-footer {
        display: flex;
        justify-content: flex-end;
        gap: 12px;
        margin-top: 12px;
      }
    }

    .mobile-pagination {
      margin-top: 20px;
      display: flex;
      justify-content: center;
    }
  }
}

// 响应式显示控制
.desktop-only {
  display: block;
}

.mobile-only {
  display: none;
}

@media (max-width: 768px) {
  .student-list {
    .page-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 16px;

      .header-actions {
        width: 100%;
        flex-wrap: wrap;
      }
    }

    .search-section {
      :deep(.el-form-item) {
        width: 100%;
        margin-right: 0;

        .el-input,
        .el-select {
          width: 100% !important;
        }
      }
    }
  }

  .desktop-only {
    display: none;
  }

  .mobile-only {
    display: block;
  }
}
</style>
