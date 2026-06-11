<template>
  <div class="grade-list page-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">成绩列表</h1>
      <div class="header-actions">
        <el-button type="primary" @click="goToAdd">
          <el-icon><Plus /></el-icon>
          <span class="btn-text">录入成绩</span>
        </el-button>
        <el-button @click="goToImport">
          <el-icon><Upload /></el-icon>
          <span class="btn-text">批量导入</span>
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          <span class="btn-text">导出</span>
        </el-button>
      </div>
    </div>

    <!-- 查询区域 -->
    <div class="search-bar">
      <el-select
        v-model="searchForm.class_name"
        placeholder="选择班级"
        clearable
        class="search-item"
      >
        <el-option
          v-for="cls in classOptions"
          :key="cls"
          :label="cls"
          :value="cls"
        />
      </el-select>

      <el-select
        v-model="searchForm.subject"
        placeholder="选择科目"
        clearable
        class="search-item"
      >
        <el-option
          v-for="sub in subjectOptions"
          :key="sub"
          :label="sub"
          :value="sub"
        />
      </el-select>

      <el-select
        v-model="searchForm.exam_type"
        placeholder="考试类型"
        clearable
        class="search-item"
      >
        <el-option
          v-for="et in examTypeOptions"
          :key="et"
          :label="et"
          :value="et"
        />
      </el-select>

      <el-input
        v-model="searchForm.keyword"
        placeholder="学号/姓名搜索"
        clearable
        class="search-item search-keyword"
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <div class="search-buttons">
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          <span class="btn-text">查询</span>
        </el-button>
        <el-button @click="handleReset">
          <span class="btn-text">重置</span>
        </el-button>
      </div>
    </div>

    <!-- 数据表格 -->
    <DataTable
      :data="gradeStore.grades || []"
      :loading="gradeStore.loading"
      :current-page="gradeStore.pagination.page"
      :page-size="gradeStore.pagination.pageSize"
      :total="gradeStore.pagination.total"
      :show-index="false"
      :actions-width="150"
      @update:current-page="handlePageChange"
      @update:page-size="handleSizeChange"
    >
      <el-table-column prop="student_id" label="学号" width="120" sortable="custom">
        <template #default="{ row }">
          <span class="student-id-link" @click="goToStudentDetail(row.student_id)">{{ row.student_id }}</span>
        </template>
      </el-table-column>

      <el-table-column label="姓名" width="100" sortable="custom">
        <template #default="{ row }">
          {{ row.student?.name || '-' }}
        </template>
      </el-table-column>

      <el-table-column label="班级" width="120">
        <template #default="{ row }">
          {{ row.student?.class_name || '-' }}
        </template>
      </el-table-column>

      <el-table-column prop="subject" label="科目" width="80" align="center">
        <template #default="{ row }">
          <el-tag size="small" effect="plain">{{ row.subject }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="exam_type" label="考试类型" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getExamTypeTag(row.exam_type)" size="small">
            {{ row.exam_type }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="score" label="分数" width="100" align="center" sortable="custom">
        <template #default="{ row }">
          <span :style="{ color: getScoreColor(row.score), fontWeight: 600 }">
            {{ formatScore(row.score) }}
          </span>
        </template>
      </el-table-column>

      <el-table-column prop="exam_date" label="考试日期" width="120" sortable="custom" />

      <template #actions="{ row }">
        <div class="table-actions">
          <el-button type="primary" link size="small" @click="goToEdit(row.grade_id)">
            编辑
          </el-button>
          <el-button type="danger" link size="small" @click="handleDelete(row)">
            删除
          </el-button>
        </div>
      </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useGradeStore } from '@/stores/grade'
import { useGradeList } from '@/composables/useGrade'
import DataTable from '@/components/common/DataTable.vue'
import { formatScore, getScoreColor } from '@/utils/format'

const router = useRouter()

const gradeStore = useGradeStore()

const {
  searchForm,
  subjectOptions,
  examTypeOptions,
  classOptions,
  handleSearch,
  debouncedSearch,
  handleReset,
  handlePageChange,
  handleSizeChange,
  goToAdd,
  goToImport,
  goToEdit,
  handleDelete,
  handleExport,
} = useGradeList()

/** 监听关键字输入，自动防抖搜索 */
watch(
  () => searchForm.value.keyword,
  () => {
    debouncedSearch()
  },
)

/** 监听下拉选择变化，立即搜索 */
watch(
  () => [searchForm.value.class_name, searchForm.value.subject, searchForm.value.exam_type],
  () => {
    handleSearch()
  },
)

/** 跳转到学生详情 */
function goToStudentDetail(studentId: string) {
  router.push(`/student/detail/${studentId}`)
}

/** 获取考试类型标签样式 */
function getExamTypeTag(examType: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<string, '' | 'success' | 'warning' | 'danger' | 'info'> = {
    '期中': '',
    '期末': 'success',
    '月考': 'warning',
    '单元测试': 'info',
  }
  return map[examType] || ''
}

/** 初始化 */
onMounted(() => {
  gradeStore.fetchGrades()
})
</script>

<style lang="scss" scoped>
.grade-list {
  animation: fadeIn 0.3s ease;

  .header-actions {
    display: flex;
    gap: 8px;
  }

  .search-item {
    width: 160px;
  }

  .search-keyword {
    width: 200px;
  }

  .search-buttons {
    display: flex;
    gap: 8px;
    margin-left: auto;
  }

  .student-id-link {
    color: var(--primary-color);
    cursor: pointer;
    font-weight: 500;

    &:hover {
      text-decoration: underline;
    }
  }
}

/* 响应式布局 */
@media (max-width: 992px) {
  .grade-list {
    .search-item {
      width: 140px;
    }

    .search-keyword {
      width: 160px;
    }
  }
}

@media (max-width: 768px) {
  .grade-list {
    .page-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;

      .header-actions {
        width: 100%;
        flex-wrap: wrap;
      }
    }

    .search-bar {
      .search-item {
        width: 100%;
      }

      .search-keyword {
        width: 100%;
      }

      .search-buttons {
        width: 100%;
        margin-left: 0;
        justify-content: flex-end;
      }
    }

    :deep(.el-table) {
      .el-table__header-wrapper {
        overflow-x: auto;
      }
    }
  }
}

@media (max-width: 480px) {
  .grade-list {
    .btn-text {
      display: none;
    }
  }
}
</style>
