<template>
  <div class="ct-grades page-container">
    <div class="page-header">
      <h1 class="page-title">成绩信息</h1>
    </div>

    <div class="search-bar">
      <el-select v-model="filterSubject" placeholder="科目" clearable style="width: 140px" @change="fetchGrades">
        <el-option v-for="s in subjects" :key="s" :label="s" :value="s" />
      </el-select>
      <el-select v-model="filterExamType" placeholder="考试类型" clearable style="width: 140px" @change="fetchGrades">
        <el-option v-for="t in examTypes" :key="t" :label="t" :value="t" />
      </el-select>
    </div>

    <div class="page-card">
      <el-table
        :data="grades"
        border
        stripe
        style="width: 100%"
        v-loading="loading"
        :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }"
      >
        <el-table-column prop="student_id" label="学号" min-width="120" />
        <el-table-column prop="student_name" label="姓名" min-width="100" />
        <el-table-column prop="subject" label="科目" min-width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.subject }}</el-tag>
          </template>
        </el-table-column>
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
        <el-table-column prop="exam_date" label="考试日期" min-width="120" align="center" />
      </el-table>

      <div class="table-pagination" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          :background="true"
          @current-change="fetchGrades"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getCtGrades } from '@/api/classTeacher'
import { SUBJECTS, EXAM_TYPES } from '@/types/grade'

interface GradeItem {
  grade_id: number
  student_id: string
  student_name: string
  subject: string
  score: number
  exam_type: string
  exam_date: string
  class_name: string
}

const subjects = SUBJECTS
const examTypes = EXAM_TYPES
const loading = ref(false)
const grades = ref<GradeItem[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterSubject = ref('')
const filterExamType = ref('')

function getScoreColor(score: number): string {
  if (score >= 90) return '#67c23a'
  if (score >= 60) return '#409eff'
  return '#f56c6c'
}

function getExamTypeTag(t: string): 'primary' | 'success' | 'warning' | 'info' {
  const map: Record<string, 'primary' | 'success' | 'warning' | 'info'> = {
    '期中': 'primary', '期末': 'success', '月考': 'warning', '单元测试': 'info',
  }
  return map[t] || 'info'
}

async function fetchGrades() {
  loading.value = true
  try {
    const res = await getCtGrades({
      page: currentPage.value,
      page_size: pageSize.value,
      subject: filterSubject.value || undefined,
      exam_type: filterExamType.value || undefined,
    })
    if (res?.data) {
      const d = res.data as { items: GradeItem[]; total: number }
      grades.value = d.items || []
      total.value = d.total || 0
    }
  } catch (e) {
    console.error('获取成绩列表失败:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchGrades()
})
</script>

<style lang="scss" scoped>
.ct-grades {
  animation: fadeIn 0.3s ease;

  .page-header {
    margin-bottom: 20px;
    .page-title { margin: 0; font-size: 22px; font-weight: 700; }
  }

  .search-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    flex-wrap: wrap;
  }

  .table-pagination {
    display: flex;
    justify-content: flex-end;
    padding: 16px 20px;
    border-top: 1px solid var(--border-color-light);
  }
}
</style>
