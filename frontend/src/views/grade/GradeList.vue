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
        <el-button
          type="danger"
          plain
          :disabled="selectedGrades.length === 0"
          @click="handleBatchDelete"
        >
          <el-icon><Delete /></el-icon>
          <span class="btn-text">批量删除</span>
        </el-button>
        <el-button
          type="danger"
          @click="handleDeleteAll"
        >
          <el-icon><Delete /></el-icon>
          <span class="btn-text">删除全部</span>
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

    <!-- 视图切换 -->
    <el-tabs v-model="activeTab" class="view-tabs">
      <el-tab-pane label="成绩明细" name="detail">
        <!-- 数据表格 -->
        <DataTable
          :data="gradeStore.grades || []"
          :loading="gradeStore.loading"
          :current-page="gradeStore.pagination.page"
          :page-size="gradeStore.pagination.pageSize"
          :total="gradeStore.pagination.total"
          :show-index="false"
          :show-selection="true"
          :actions-width="150"
          @update:current-page="handlePageChange"
          @update:page-size="handleSizeChange"
          @selection-change="handleSelectionChange"
        >
      <el-table-column prop="student_id" label="学号" min-width="120" sortable="custom">
        <template #default="{ row }">
          <span class="student-id-link" @click="goToStudentDetail(row.student_id)">{{ row.student_id }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="student_name" label="姓名" min-width="100">
        <template #default="{ row }">
          {{ row.student_name || '-' }}
        </template>
      </el-table-column>

      <el-table-column prop="class_name" label="班级" min-width="120">
        <template #default="{ row }">
          {{ row.class_name || '-' }}
        </template>
      </el-table-column>

      <el-table-column prop="subject" label="科目" min-width="80" align="center">
        <template #default="{ row }">
          <el-tag size="small" effect="plain">{{ row.subject }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="exam_type" label="考试类型" min-width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getExamTypeTag(row.exam_type)" size="small">
            {{ row.exam_type }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="score" label="分数" min-width="100" align="center" sortable="custom">
        <template #default="{ row }">
          <span :style="{ color: getScoreColor(row.score), fontWeight: 600 }">
            {{ formatScore(row.score) }}
          </span>
        </template>
      </el-table-column>

      <el-table-column prop="exam_date" label="考试日期" min-width="120" sortable="custom" />

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
      </el-tab-pane>

      <el-tab-pane label="总分排名" name="ranking">
        <div class="ranking-section">
          <div class="ranking-filter">
            <el-select
              v-model="rankingExamType"
              placeholder="选择考试类型"
              clearable
              style="width: 160px"
              @change="fetchTotalRanking"
            >
              <el-option
                v-for="et in examTypeOptions"
                :key="et"
                :label="et"
                :value="et"
              />
            </el-select>
            <el-select
              v-model="rankingClassName"
              placeholder="选择班级"
              clearable
              style="width: 160px"
              @change="fetchTotalRanking"
            >
              <el-option
                v-for="cls in classOptions"
                :key="cls"
                :label="cls"
                :value="cls"
              />
            </el-select>
            <el-button type="primary" @click="fetchTotalRanking" :loading="rankingLoading">
              <el-icon><Search /></el-icon>
              查询排名
            </el-button>
          </div>
          <el-table
            v-if="totalRankings.length > 0"
            :data="totalRankings"
            border
            stripe
            style="width: 100%"
            :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }"
            v-loading="rankingLoading"
          >
            <el-table-column type="index" label="排名" width="70" align="center">
              <template #default="{ row }">
                <div class="rank-cell">
                  <span v-if="row.rank <= 3" class="rank-badge" :class="`rank-${row.rank}`">
                    {{ row.rank }}
                  </span>
                  <span v-else>{{ row.rank }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="student_id" label="学号" min-width="100" align="center" />
            <el-table-column prop="student_name" label="姓名" min-width="100" align="center" />
            <el-table-column prop="total_score" label="总分" min-width="100" align="center" sortable="custom">
              <template #default="{ row }">
                <span style="font-weight: 700; color: var(--primary-color); font-size: 16px;">
                  {{ formatScore(row.total_score) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="各科成绩" min-width="300">
              <template #default="{ row }">
                <div class="subject-scores-row">
                  <el-tag
                    v-for="(score, sub) in row.subject_scores"
                    :key="sub"
                    size="small"
                    effect="plain"
                    class="subject-score-tag"
                  >
                    {{ sub }}: {{ score }}
                  </el-tag>
                </div>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else-if="!rankingLoading" description="请选择考试类型后查询总分排名" />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useGradeStore } from '@/stores/grade'
import { useGradeList } from '@/composables/useGrade'
import { getTotalRanking } from '@/api/statistics'
import { batchDeleteGrades, deleteAllGrades } from '@/api/grade'
import DataTable from '@/components/common/DataTable.vue'
import { formatScore, getScoreColor } from '@/utils/format'
import type { TotalRankingItem } from '@/types/statistics'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

const gradeStore = useGradeStore()

// ===== 选中的成绩 =====
const selectedGrades = ref<any[]>([])

function handleSelectionChange(selection: any[]) {
  selectedGrades.value = selection
}

// ===== 批量删除 =====
async function handleBatchDelete() {
  if (selectedGrades.value.length === 0) return
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedGrades.value.length} 条成绩记录吗？此操作不可恢复。`,
      '确认批量删除',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
    )
  } catch { return }

  const ids = selectedGrades.value.map((g: any) => g.grade_id)
  try {
    await batchDeleteGrades(ids)
    ElMessage.success('批量删除成功')
    selectedGrades.value = []
    gradeStore.fetchGrades()
  } catch {
    ElMessage.error('批量删除失败')
  }
}

// ===== 删除全部 =====
async function handleDeleteAll() {
  const className = searchForm.value.class_name || ''
  const msg = className
    ? `确定要删除班级"${className}"的所有成绩记录吗？此操作不可恢复！`
    : '确定要删除所有成绩记录吗？此操作不可恢复！'
  try {
    await ElMessageBox.confirm(msg, '确认删除全部', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'error',
    })
  } catch { return }

  try {
    const res = await deleteAllGrades(className ? { class_name: className } : undefined)
    const data = (res as any).data || res
    ElMessage.success(`成功删除 ${data.deleted_count} 条成绩记录`)
    gradeStore.fetchGrades()
  } catch {
    ElMessage.error('删除失败')
  }
}

// ===== 总分排名 =====
const activeTab = ref('detail')
const rankingExamType = ref('')
const rankingClassName = ref('')
const rankingLoading = ref(false)
const totalRankings = ref<TotalRankingItem[]>([])

async function fetchTotalRanking() {
  if (!rankingExamType.value) {
    ElMessage.warning('请先选择考试类型')
    return
  }
  rankingLoading.value = true
  try {
    const res = await getTotalRanking({
      exam_type: rankingExamType.value,
      class_name: rankingClassName.value || undefined,
    })
    const data = (res as any).data || res
    totalRankings.value = data.rankings || []
  } catch {
    ElMessage.error('获取总分排名失败')
    totalRankings.value = []
  } finally {
    rankingLoading.value = false
  }
}

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
function getExamTypeTag(examType: string): 'primary' | 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<string, 'primary' | 'success' | 'warning' | 'danger' | 'info'> = {
    '期中': 'primary',
    '期末': 'success',
    '月考': 'warning',
    '单元测试': 'info',
  }
  return map[examType] || 'primary'
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

  // ===== 总分排名 =====
  .view-tabs {
    :deep(.el-tabs__header) {
      margin-bottom: 16px;
    }
  }

  .ranking-section {
    .ranking-filter {
      display: flex;
      gap: 12px;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }
  }

  .rank-cell {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .rank-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 700;
    color: #fff;

    &.rank-1 {
      background: linear-gradient(135deg, #ffd700, #ffed4e);
      color: #b8860b;
    }

    &.rank-2 {
      background: linear-gradient(135deg, #c0c0c0, #e8e8e8);
      color: #696969;
    }

    &.rank-3 {
      background: linear-gradient(135deg, #cd7f32, #daa520);
      color: #8b4513;
    }
  }

  .subject-scores-row {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }

  .subject-score-tag {
    font-size: 12px;
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
