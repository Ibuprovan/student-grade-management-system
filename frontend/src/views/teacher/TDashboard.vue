<template>
  <div class="t-dashboard page-container">
    <div class="page-header">
      <h1 class="page-title">教师仪表盘</h1>
    </div>

    <el-row :gutter="16" class="overview-cards">
      <el-col :xs="12" :sm="8" :md="4" v-for="(card, idx) in cards" :key="idx">
        <div class="overview-card" :class="card.cls">
          <div class="overview-value">{{ card.value }}</div>
          <div class="overview-label">{{ card.label }}</div>
        </div>
      </el-col>
    </el-row>

    <div class="page-card" v-if="items.length > 0">
      <h4 class="section-title">任课详情</h4>
      <el-table :data="items" border stripe style="width: 100%" :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }">
        <el-table-column prop="subject" label="科目" min-width="80" align="center" />
        <el-table-column prop="class_name" label="班级" min-width="100" />
        <el-table-column prop="student_count" label="学生数" min-width="80" align="center" />
        <el-table-column prop="total_grades" label="成绩记录" min-width="80" align="center" />
        <el-table-column prop="average_score" label="平均分" min-width="80" align="center">
          <template #default="{ row }">
            <span style="font-weight:600">{{ formatNum(row.average_score) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="pass_rate" label="及格率" min-width="80" align="center">
          <template #default="{ row }">{{ formatPercent(row.pass_rate) }}</template>
        </el-table-column>
        <el-table-column prop="excellent_rate" label="优秀率" min-width="80" align="center">
          <template #default="{ row }">{{ formatPercent(row.excellent_rate) }}</template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getTDashboard } from '@/api/teacher'

interface DashboardItem {
  subject: string
  class_name: string
  student_count: number
  total_grades: number
  average_score: number
  pass_rate: number
  excellent_rate: number
}

const items = ref<DashboardItem[]>([])

function formatNum(v: unknown) { return v == null ? '-' : Number(v).toFixed(1) }
function formatPercent(v: unknown) { return v == null ? '-' : Number(v).toFixed(1) + '%' }

const cards = computed(() => {
  if (items.value.length === 0) return []
  const totalStudents = items.value.reduce((s, i) => s + i.student_count, 0)
  const totalGrades = items.value.reduce((s, i) => s + i.total_grades, 0)
  const avgScore = items.value.reduce((s, i) => s + i.average_score, 0) / items.value.length
  const avgPass = items.value.reduce((s, i) => s + i.pass_rate, 0) / items.value.length
  const avgExc = items.value.reduce((s, i) => s + i.excellent_rate, 0) / items.value.length
  return [
    { label: '学生总数', value: totalStudents, cls: 'overview-card--primary' },
    { label: '成绩记录', value: totalGrades, cls: 'overview-card--info' },
    { label: '平均分', value: formatNum(avgScore), cls: 'overview-card--success' },
    { label: '及格率', value: formatPercent(avgPass), cls: 'overview-card--warning' },
    { label: '优秀率', value: formatPercent(avgExc), cls: 'overview-card--accent' },
  ]
})

async function fetchData() {
  try {
    const res = await getTDashboard()
    if (res?.data) items.value = res.data as unknown as DashboardItem[]
  } catch (e) { console.error('获取仪表盘失败:', e) }
}

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.t-dashboard {
  animation: fadeIn 0.3s ease;
  .page-header { margin-bottom: 20px; }
  .page-title { margin: 0; font-size: 22px; font-weight: 700; }
  .section-title { font-size: 16px; font-weight: 600; color: var(--text-color); margin: 0 0 16px; }
  .overview-cards { margin-bottom: 16px; }
  .overview-card {
    padding: 20px 24px; background: var(--surface-color); border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-color-light); box-shadow: var(--shadow-xs); margin-bottom: 16px;
    text-align: center; transition: all var(--transition-duration);
    &:hover { transform: translateY(-2px); box-shadow: var(--shadow-sm); }
    .overview-value { font-size: 28px; font-weight: 700; line-height: 1.2; min-height: 34px; }
    .overview-label { font-size: 13px; color: var(--text-color-secondary); margin-top: 6px; font-weight: 500; }
    &--primary .overview-value { color: #409EFF; }
    &--info .overview-value { color: #909399; }
    &--success .overview-value { color: #67C23A; }
    &--warning .overview-value { color: #E6A23C; }
    &--accent .overview-value { color: #F56C6C; }
  }
}
</style>
