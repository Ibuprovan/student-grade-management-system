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
        <el-button type="danger" @click="handleDeleteAll">
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
        @change="fetchRanking"
      >
        <el-option v-for="cls in classOptions" :key="cls" :label="cls" :value="cls" />
      </el-select>

      <el-select
        v-model="searchForm.exam_type"
        placeholder="考试类型"
        clearable
        class="search-item"
        @change="fetchRanking"
      >
        <el-option v-for="et in examTypeOptions" :key="et" :label="et" :value="et" />
      </el-select>

      <el-input
        v-model="searchForm.keyword"
        placeholder="学号/姓名搜索"
        clearable
        class="search-item search-keyword"
        @input="filterRankings"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <div class="search-buttons">
        <el-button type="primary" @click="fetchRanking" :loading="loading">
          <el-icon><Search /></el-icon>
          <span class="btn-text">查询排名</span>
        </el-button>
        <el-button @click="handleReset">
          <span class="btn-text">重置</span>
        </el-button>
      </div>
    </div>

    <!-- 总分排名表格 -->
    <div class="page-card">
      <el-table
        v-if="filteredRankings.length > 0"
        :data="filteredRankings"
        border
        stripe
        style="width: 100%"
        :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }"
        v-loading="loading"
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
        <el-table-column prop="student_id" label="学号" min-width="120" align="center" />
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
      <el-empty v-else-if="!loading" description="请选择考试类型后查询总分排名" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTotalRanking } from '@/api/statistics'
import { deleteAllGrades } from '@/api/grade'
import { getStudentList } from '@/api/student'
import { formatScore } from '@/utils/format'
import { SUBJECTS, EXAM_TYPES } from '@/types/grade'
import type { TotalRankingItem } from '@/types/statistics'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

const subjectOptions = SUBJECTS
const examTypeOptions = EXAM_TYPES

// ===== 筛选 =====
const searchForm = ref({
  class_name: '',
  exam_type: '',
  keyword: '',
})

// ===== 班级选项 =====
const classOptions = ref<string[]>([])

// ===== 排名数据 =====
const loading = ref(false)
const allRankings = ref<TotalRankingItem[]>([])

// ===== 按关键字过滤排名 =====
const filteredRankings = computed(() => {
  const kw = searchForm.value.keyword.trim().toLowerCase()
  if (!kw) return allRankings.value
  return allRankings.value.filter(
    (r) =>
      r.student_id.toLowerCase().includes(kw) ||
      r.student_name.toLowerCase().includes(kw)
  )
})

function filterRankings() {
  // computed 自动响应
}

// ===== 查询排名 =====
async function fetchRanking() {
  if (!searchForm.value.exam_type) {
    allRankings.value = []
    return
  }
  loading.value = true
  try {
    const res = await getTotalRanking({
      exam_type: searchForm.value.exam_type,
      class_name: searchForm.value.class_name || undefined,
    })
    const data = (res as any).data || res
    allRankings.value = data.rankings || []
  } catch {
    ElMessage.error('获取总分排名失败')
    allRankings.value = []
  } finally {
    loading.value = false
  }
}

// ===== 重置 =====
function handleReset() {
  searchForm.value = { class_name: '', exam_type: '', keyword: '' }
  allRankings.value = []
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
  } catch {
    return
  }

  try {
    const res = await deleteAllGrades(className ? { class_name: className } : undefined)
    const data = (res as any).data || res
    ElMessage.success(`成功删除 ${data.deleted_count} 条成绩记录`)
    fetchRanking()
  } catch {
    ElMessage.error('删除失败')
  }
}

// ===== 页面跳转 =====
function goToAdd() {
  router.push('/grade/input')
}
function goToImport() {
  router.push('/grade/import')
}
function handleExport() {
  ElMessage.info('导出功能开发中...')
}

// ===== 初始化 =====
onMounted(async () => {
  try {
    const res = await getStudentList({ page_size: 1 } as any)
    const data = (res as any).data || res
    const allRes = await getStudentList({ page_size: data.total || 1000 } as any)
    const allData = (allRes as any).data || allRes
    const classes = [...new Set((allData.items || []).map((s: any) => s.class_name))] as string[]
    classOptions.value = classes.filter(Boolean)
  } catch {
    // ignore
  }
})
</script>

<style lang="scss" scoped>
.grade-list {
  animation: fadeIn 0.3s ease;

  .header-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
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
      .search-item { width: 100%; }
      .search-keyword { width: 100%; }
      .search-buttons {
        width: 100%;
        margin-left: 0;
        justify-content: flex-end;
      }
    }
  }
}

@media (max-width: 480px) {
  .grade-list {
    .btn-text { display: none; }
  }
}
</style>
