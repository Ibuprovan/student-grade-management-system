<template>
  <div class="ct-grades page-container">
    <div class="page-header">
      <h1 class="page-title">成绩信息</h1>
      <div class="header-actions">
        <el-select v-model="filterExamType" placeholder="考试类型" clearable style="width: 140px" @change="fetchGrades">
          <el-option v-for="t in examTypes" :key="t" :label="t" :value="t" />
        </el-select>
      </div>
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
        <el-table-column prop="student_id" label="学号" min-width="100" fixed="left" />
        <el-table-column prop="student_name" label="姓名" min-width="90" fixed="left" />
        <el-table-column prop="exam_type" label="考试类型" min-width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="getExamTypeTag(row.exam_type)" size="small">{{ row.exam_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="exam_date" label="考试日期" min-width="100" align="center" />
        <el-table-column
          v-for="subj in subjects"
          :key="subj"
          :prop="subj"
          :label="subj"
          min-width="80"
          align="center"
        >
          <template #default="{ row }">
            <span v-if="row[subj] !== null && row[subj] !== undefined" :style="{ color: getScoreColor(row[subj]), fontWeight: 500 }">{{ row[subj] }}</span>
            <span v-else class="score-empty">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_score" label="总分" min-width="90" align="center" fixed="right">
          <template #default="{ row }">
            <span class="total-score">{{ row.total_score }}</span>
          </template>
        </el-table-column>
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
import { getCtGradesTotal } from '@/api/classTeacher'
import { EXAM_TYPES } from '@/types/grade'

interface GradeRow {
  student_id: string
  student_name: string
  exam_type: string
  exam_date: string
  total_score: number
  [subject: string]: unknown
}

const examTypes = EXAM_TYPES
const loading = ref(false)
const grades = ref<GradeRow[]>([])
const subjects = ref<string[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
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
    const res = await getCtGradesTotal({
      page: currentPage.value,
      page_size: pageSize.value,
      exam_type: filterExamType.value || undefined,
    })
    if (res?.data) {
      const d = res.data as { items: GradeRow[]; total: number; subjects: string[] }
      grades.value = d.items || []
      total.value = d.total || 0
      if (d.subjects && d.subjects.length > 0) {
        subjects.value = d.subjects
      }
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
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 12px;
    .page-title { margin: 0; font-size: 22px; font-weight: 700; }
    .header-actions { display: flex; gap: 12px; }
  }

  .score-empty {
    color: var(--text-color-secondary);
    font-size: 12px;
  }

  .total-score {
    font-weight: 700;
    font-size: 15px;
    color: #409eff;
  }

  .table-pagination {
    display: flex;
    justify-content: flex-end;
    padding: 16px 20px;
    border-top: 1px solid var(--border-color-light);
  }
}
</style>
