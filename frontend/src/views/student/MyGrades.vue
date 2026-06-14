<template>
  <div class="my-grades page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">我的成绩</h1>
      <div class="header-actions">
        <el-select
          v-model="selectedExamType"
          placeholder="考试类型"
          clearable
          style="width: 140px"
          @change="fetchData"
        >
          <el-option
            v-for="et in examTypeOptions"
            :key="et"
            :label="et"
            :value="et"
          />
        </el-select>
      </div>
    </div>

    <!-- 概览卡片 -->
    <el-row :gutter="16" class="overview-cards">
      <el-col :xs="12" :sm="6">
        <div class="overview-card overview-card--primary">
          <div class="overview-value">{{ studentStats.average_score || '-' }}</div>
          <div class="overview-label">平均分</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="overview-card overview-card--success">
          <div class="overview-value">{{ studentStats.total_score || '-' }}</div>
          <div class="overview-label">总分</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="overview-card overview-card--warning">
          <div class="overview-value">
            {{ studentStats.class_rank_total ? `第${studentStats.class_rank_total}名` : '-' }}
          </div>
          <div class="overview-label">班级排名</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="overview-card overview-card--accent">
          <div class="overview-value">
            {{ studentStats.grade_rank_total ? `第${studentStats.grade_rank_total}名` : '-' }}
          </div>
          <div class="overview-label">年级排名</div>
        </div>
      </el-col>
    </el-row>

    <!-- 成绩趋势图 -->
    <div class="page-card chart-section">
      <LineChart
        title="成绩趋势"
        :x-data="trendXData"
        :series="trendSeries"
        :smooth="true"
        :area-style="true"
        :height="320"
        y-label="分数"
      />
    </div>

    <!-- 各科成绩表格 -->
    <div class="page-card">
      <h3 class="section-title">各科成绩明细</h3>
      <DataTable
        :data="grades"
        :loading="loading"
        :show-pagination="false"
      >
        <el-table-column prop="subject" label="科目" width="120" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.subject }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="分数" width="120" align="center" sortable="custom">
          <template #default="{ row }">
            <span :style="{ color: getScoreColor(row.score), fontWeight: 600, fontSize: '16px' }">
              {{ row.score }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="exam_type" label="考试类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getExamTypeTag(row.exam_type)" size="small">
              {{ row.exam_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="exam_date" label="考试日期" width="140" />
        <el-table-column label="班级排名" width="120" align="center">
          <template #default="{ row }">
            {{ row.class_rank ? `第${row.class_rank}名` : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="年级排名" width="120" align="center">
          <template #default="{ row }">
            {{ row.grade_rank ? `第${row.grade_rank}名` : '-' }}
          </template>
        </el-table-column>
      </DataTable>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getCurrentStudentInfo } from '@/api/auth'
import { getStudentStatistics } from '@/api/statistics'
import { getGradeList } from '@/api/grade'
import DataTable from '@/components/common/DataTable.vue'
import LineChart from '@/components/chart/LineChart.vue'
import type { StudentStatisticsResponse } from '@/types/statistics'
import type { Grade, ExamType } from '@/types/grade'
import { EXAM_TYPES } from '@/types/grade'
import { ElMessage } from 'element-plus'

/** 考试类型选项 */
const examTypeOptions = EXAM_TYPES

/** 选中的考试类型 */
const selectedExamType = ref<ExamType | ''>('')

/** 加载状态 */
const loading = ref(false)

/** 学生信息加载状态 */
const studentInfoLoading = ref(true)

/** 学生统计数据 */
const studentStats = ref<StudentStatisticsResponse>({
  student_id: '',
  student_name: '',
  class_name: '',
  subjects: [],
  total_score: 0,
  average_score: 0,
})

/** 成绩列表 */
const grades = ref<Grade[]>([])

/** 学生ID（从后端接口获取） */
const studentId = ref('')

/** 学生姓名 */
const studentName = ref('')

/** 趋势图 X 轴数据（按科目） */
const trendXData = computed(() => {
  return studentStats.value.subjects.map((s: { subject: string }) => s.subject)
})

/** 趋势图系列数据 */
const trendSeries = computed(() => {
  if (studentStats.value.subjects.length === 0) return []
  return [
    {
      name: '分数',
      data: studentStats.value.subjects.map((s: { score: number }) => s.score),
      color: '#2A9D8F',
    },
  ]
})

/** 获取分数颜色 */
function getScoreColor(score: number): string {
  if (score >= 90) return '#67c23a'
  if (score >= 80) return '#409eff'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
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

/** 获取学生信息 */
async function fetchStudentInfo() {
  try {
    const response = await getCurrentStudentInfo()
    if (response.success && response.data) {
      studentId.value = response.data.student_id
      studentName.value = response.data.name
      return true
    }
    return false
  } catch (error: any) {
    console.error('获取学生信息失败:', error)
    const message = error?.response?.data?.detail || '获取学生信息失败，请联系管理员'
    ElMessage.error(message)
    return false
  }
}

/** 获取成绩数据 */
async function fetchData() {
  // 如果还没有学生信息，先获取
  if (!studentId.value) {
    const success = await fetchStudentInfo()
    if (!success) return
  }

  // 再次检查 studentId
  if (!studentId.value) return

  loading.value = true
  try {
    const examType = selectedExamType.value || undefined

    // 并行获取统计数据和成绩列表
    const [statsRes, gradesRes] = await Promise.allSettled([
      getStudentStatistics(studentId.value, { exam_type: examType }),
      getGradeList({
        student_id: studentId.value,
        exam_type: examType as ExamType | undefined,
        page_size: 100,
      }),
    ])

    if (statsRes.status === 'fulfilled') {
      const data = (statsRes.value as any).data || statsRes.value
      studentStats.value = data
    }

    if (gradesRes.status === 'fulfilled') {
      const data = (gradesRes.value as any).data || gradesRes.value
      grades.value = data.items || []
    }
  } catch (error) {
    console.error('获取成绩数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  studentInfoLoading.value = true
  await fetchStudentInfo()
  studentInfoLoading.value = false
  fetchData()
})
</script>

<style lang="scss" scoped>
.my-grades {
  animation: fadeIn 0.3s ease;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .page-title {
      margin: 0;
      font-size: 22px;
      font-weight: 700;
    }
  }

  // ===== 概览卡片 =====
  .overview-cards {
    margin-bottom: 16px;
  }

  .overview-card {
    padding: 20px 24px;
    background: var(--surface-color);
    border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-color-light);
    box-shadow: var(--shadow-xs);
    margin-bottom: 16px;
    text-align: center;
    transition: all var(--transition-duration);

    &:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-sm);
    }

    .overview-value {
      font-size: 28px;
      font-weight: 700;
      color: var(--text-color);
      line-height: 1.2;
      min-height: 34px;
    }

    .overview-label {
      font-size: 13px;
      color: var(--text-color-secondary);
      margin-top: 6px;
      font-weight: 500;
    }

    &--primary .overview-value { color: #2A9D8F; }
    &--success .overview-value { color: #52B788; }
    &--warning .overview-value { color: #E9A23B; }
    &--accent .overview-value { color: #E06469; }
  }

  // ===== 图表区域 =====
  .chart-section {
    margin-bottom: 16px;
  }

  // ===== 区块标题 =====
  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-color);
    margin: 0 0 16px;
  }
}

// 响应式
@media (max-width: 768px) {
  .my-grades {
    .page-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }

    .overview-card .overview-value {
      font-size: 22px;
    }
  }
}
</style>
