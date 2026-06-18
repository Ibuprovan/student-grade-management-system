<template>
  <div class="t-grades page-container">
    <div class="page-header">
      <h1 class="page-title">成绩管理</h1>
      <div class="header-actions">
        <el-select v-model="filterExamType" placeholder="考试类型" clearable style="width: 140px" @change="fetchGrades">
          <el-option v-for="t in examTypes" :key="t" :label="t" :value="t" />
        </el-select>
      </div>
    </div>

    <div class="search-bar">
      <el-input v-model="searchText" placeholder="学号或姓名搜索" clearable style="width: 220px" @clear="fetchGrades" @keyup.enter="fetchGrades">
        <template #append>
          <el-button @click="fetchGrades"><el-icon><Search /></el-icon></el-button>
        </template>
      </el-input>
    </div>

    <div class="page-card">
      <el-table :data="grades" border stripe style="width: 100%" v-loading="loading" :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }">
        <el-table-column prop="student_id" label="学号" min-width="110" />
        <el-table-column prop="student_name" label="姓名" min-width="100" />
        <el-table-column prop="class_name" label="班级" min-width="100" />
        <el-table-column prop="subject" label="科目" min-width="80" align="center" />
        <el-table-column prop="score" label="分数" min-width="80" align="center">
          <template #default="{ row }">
            <span :style="{ color: getScoreColor(row.score), fontWeight: 600 }">{{ row.score }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="exam_type" label="考试类型" min-width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getExamTypeTag(row.exam_type)" size="small">{{ row.exam_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="exam_date" label="考试日期" min-width="110" align="center" />
      </el-table>

      <div class="table-pagination" v-if="total > 0">
        <el-pagination v-model:current-page="currentPage" :page-size="pageSize" :total="total" layout="total, prev, pager, next" :background="true" @current-change="fetchGrades" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getTGrades } from '@/api/teacher'
import { EXAM_TYPES } from '@/types/grade'

interface GradeItem {
  grade_id: number
  student_id: string
  student_name: string
  class_name: string
  subject: string
  score: number
  exam_type: string
  exam_date: string
}

const examTypes = EXAM_TYPES
const loading = ref(false)
const grades = ref<GradeItem[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchText = ref('')
const filterExamType = ref('')

function getScoreColor(score: number) { return score >= 90 ? '#67c23a' : score >= 60 ? '#409eff' : '#f56c6c' }
function getExamTypeTag(t: string): 'primary' | 'success' | 'warning' | 'info' {
  const map: Record<string, 'primary' | 'success' | 'warning' | 'info'> = { '期中': 'primary', '期末': 'success', '月考': 'warning', '单元测试': 'info' }
  return map[t] || 'info'
}

async function fetchGrades() {
  loading.value = true
  try {
    const res = await getTGrades({
      page: currentPage.value,
      page_size: pageSize.value,
      exam_type: filterExamType.value || undefined,
      search: searchText.value || undefined,
    })
    if (res?.data) {
      const d = res.data as { items: GradeItem[]; total: number }
      grades.value = d.items || []
      total.value = d.total || 0
    }
  } catch (e) { console.error('获取成绩失败:', e) } finally { loading.value = false }
}

onMounted(() => { fetchGrades() })
</script>

<style lang="scss" scoped>
.t-grades {
  animation: fadeIn 0.3s ease;
  .page-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
  }
  .page-title { margin: 0; font-size: 22px; font-weight: 700; }
  .header-actions { display: flex; gap: 12px; }
  .search-bar { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
  .table-pagination { display: flex; justify-content: flex-end; padding: 16px 20px; border-top: 1px solid var(--border-color-light); }
}
</style>
