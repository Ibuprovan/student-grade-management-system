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
        <div class="overview-card overview-card--success">
          <div class="overview-value">{{ formatScore(studentStats.total_score) }}</div>
          <div class="overview-label">总分</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="overview-card overview-card--primary">
          <div class="overview-value">{{ studentStats.pass_count ?? '-' }}</div>
          <div class="overview-label">及格科目</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="overview-card overview-card--warning">
          <div class="overview-value">{{ studentStats.excellent_count ?? '-' }}</div>
          <div class="overview-label">优秀科目</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="overview-card overview-card--accent">
          <div class="overview-value">{{ studentStats.class_name || '-' }}</div>
          <div class="overview-label">班级</div>
        </div>
      </el-col>
    </el-row>

    <!-- 评分标准提示 -->
    <div class="standard-hint">
      <span class="hint-item hint-pass">≥60 及格</span>
      <span class="hint-item hint-excellent">≥90 优秀</span>
    </div>

    <!-- 各科成绩表格 -->
    <div class="page-card table-card">
      <h3 class="section-title">各科成绩明细</h3>
      <DataTable
        :data="grades"
        :loading="loading"
        :show-pagination="false"
      >
        <el-table-column prop="subject" label="科目" min-width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.subject }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="我的分数" min-width="100" align="center">
          <template #default="{ row }">
            <span :style="{ color: getScoreColor(row.score), fontWeight: 600, fontSize: '16px' }">
              {{ formatScore(row.score) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="班级平均分" min-width="100" align="center">
          <template #default="{ row }">
            <span class="text-secondary">{{ formatScore(row.class_average) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="班级最高分" min-width="100" align="center">
          <template #default="{ row }">
            <span class="text-success">{{ formatScore(row.class_max) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="班级最低分" min-width="100" align="center">
          <template #default="{ row }">
            <span class="text-danger">{{ formatScore(row.class_min) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="exam_type" label="考试类型" min-width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getExamTypeTag(row.exam_type)" size="small">
              {{ row.exam_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="exam_date" label="考试日期" min-width="120" align="center" />
      </DataTable>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getCurrentStudentInfo } from '@/api/auth'
import { getStudentStatistics } from '@/api/statistics'
import DataTable from '@/components/common/DataTable.vue'
import type { StudentStatisticsResponse, StudentSubjectStats } from '@/types/statistics'
import type { ExamType } from '@/types/grade'
import { EXAM_TYPES } from '@/types/grade'
import { ElMessage } from 'element-plus'

/** 考试类型选项 */
const examTypeOptions = EXAM_TYPES

/** 选中的考试类型 */
const selectedExamType = ref<ExamType | ''>('')

/** 加载状态 */
const loading = ref(false)

/** 学生统计数据 */
const studentStats = ref<StudentStatisticsResponse>({
  student_id: '',
  student_name: '',
  class_name: '',
  subjects: [],
  total_score: 0,
  average_score: 0,
})

/** 成绩列表（包含班级统计） */
const grades = ref<StudentSubjectStats[]>([])

/** 学生ID（从后端接口获取） */
const studentId = ref('')

/** 格式化分数（保留1位小数） */
function formatScore(score: number | undefined | null): string {
  if (score === undefined || score === null) return '-'
  return Number(score).toFixed(1)
}

/** 获取分数颜色 */
function getScoreColor(score: number): string {
  if (score >= 90) return '#67c23a'
  if (score >= 80) return '#409eff'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

/** 获取考试类型标签样式 */
function getExamTypeTag(examType: string): 'primary' | 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<string, 'primary' | 'success' | 'warning' | 'danger' | 'info'> = {
    '期中': 'primary',
    '期末': 'success',
    '月考': 'warning',
    '单元测试': 'info',
  }
  return map[examType] || 'info'
}

/** 获取学生信息 */
async function fetchStudentInfo() {
  try {
    const response = await getCurrentStudentInfo()
    if (response.success && response.data) {
      studentId.value = response.data.student_id
      return true
    }
    return false
  } catch (error: unknown) {
    console.error('获取学生信息失败:', error)
    const err = error as { response?: { data?: { detail?: string } } }
    const message = err?.response?.data?.detail || '获取学生信息失败，请联系管理员'
    ElMessage.error(message)
    return false
  }
}

/** 获取成绩数据 */
async function fetchData() {
  if (!studentId.value) {
    const success = await fetchStudentInfo()
    if (!success) return
  }

  if (!studentId.value) return

  loading.value = true
  try {
    const examType = selectedExamType.value || undefined
    const res = await getStudentStatistics(studentId.value, { exam_type: examType }) as unknown as { success: boolean; data: StudentStatisticsResponse }
    if (res?.success && res.data) {
      studentStats.value = res.data
      grades.value = res.data.subjects || []
    }
  } catch (error) {
    console.error('获取成绩数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
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

  // ===== 表格卡片 =====
  .table-card {
    width: 100%;
    overflow: hidden;
  }

  // ===== 评分标准提示 =====
  .standard-hint {
    display: flex;
    gap: 16px;
    margin-bottom: 12px;
    padding-left: 4px;

    .hint-item {
      font-size: 12px;
      font-weight: 500;
      padding: 2px 8px;
      border-radius: 4px;
      line-height: 1.6;

      &.hint-pass {
        color: #67c23a;
        background: #f0f9eb;
      }

      &.hint-excellent {
        color: #52B788;
        background: #ecf7f1;
      }
    }
  }

  // ===== 区块标题 =====
  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-color);
    margin: 0 0 16px;
  }

  // ===== 文本颜色 =====
  .text-secondary {
    color: var(--text-color-secondary);
  }

  .text-success {
    color: #67c23a;
  }

  .text-danger {
    color: #f56c6c;
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
