<template>
  <div class="student-detail page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">学生详情</h1>
      <div class="header-actions">
        <el-button @click="router.back()">
          <el-icon><Back /></el-icon>
          返回列表
        </el-button>
        <el-button type="primary" @click="handleEdit">
          <el-icon><Edit /></el-icon>
          编辑
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-loading="loading" class="detail-content">
      <template v-if="student">
        <!-- 基本信息卡片 -->
        <div class="info-card">
          <div class="card-title">
            <el-icon><User /></el-icon>
            <span>基本信息</span>
          </div>
          <div class="card-body">
            <div class="info-grid">
              <div class="info-item">
                <span class="label">学号</span>
                <span class="value">{{ student.student_id }}</span>
              </div>
              <div class="info-item">
                <span class="label">姓名</span>
                <span class="value">{{ student.name }}</span>
              </div>
              <div class="info-item">
                <span class="label">性别</span>
                <span class="value">
                  <el-tag :type="student.gender === '男' ? '' : 'danger'" size="small">
                    {{ student.gender }}
                  </el-tag>
                </span>
              </div>
              <div class="info-item">
                <span class="label">班级</span>
                <span class="value">{{ student.class_name }}</span>
              </div>
              <div class="info-item">
                <span class="label">入学年份</span>
                <span class="value">{{ student.enrollment_year }}</span>
              </div>
              <div class="info-item">
                <span class="label">创建时间</span>
                <span class="value">{{ formatDateTime(student.created_at) }}</span>
              </div>
              <div class="info-item">
                <span class="label">更新时间</span>
                <span class="value">{{ formatDateTime(student.updated_at) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 成绩汇总卡片 -->
        <div class="info-card" v-if="subjectCount > 0">
          <div class="card-title">
            <el-icon><TrendCharts /></el-icon>
            <span>成绩汇总</span>
            <el-tag type="info" size="small" v-if="filterExamType">{{ filterExamType }}</el-tag>
          </div>
          <div class="card-body">
            <div class="summary-grid">
              <div class="summary-item summary-item--primary">
                <div class="summary-value">{{ totalScore }}</div>
                <div class="summary-label">总分</div>
              </div>
              <div class="summary-item summary-item--success">
                <div class="summary-value">{{ averageScore }}</div>
                <div class="summary-label">平均分</div>
              </div>
              <div class="summary-item summary-item--info">
                <div class="summary-value">{{ subjectCount }}</div>
                <div class="summary-label">科目数</div>
              </div>
              <div class="summary-item summary-item--warning">
                <div class="summary-value">{{ excellentCount }}</div>
                <div class="summary-label">优秀科目</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 成绩信息卡片 -->
        <div class="info-card">
          <div class="card-title">
            <el-icon><Document /></el-icon>
            <span>成绩记录</span>
            <div class="card-title-right">
              <el-select v-model="filterExamType" placeholder="考试类型" clearable size="small" style="width: 120px" @change="handleExamTypeChange">
                <el-option v-for="t in examTypes" :key="t" :label="t" :value="t" />
              </el-select>
              <el-tag type="info" size="small">共 {{ gradeTotal }} 条</el-tag>
            </div>
          </div>
          <div class="card-body">
            <el-table :data="grades" border stripe empty-text="暂无成绩数据" style="width: 100%">
              <el-table-column prop="subject" label="科目" min-width="120" align="center" />
              <el-table-column prop="exam_type" label="考试类型" min-width="100" align="center">
                <template #default="{ row }">
                  <el-tag size="small">{{ row.exam_type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="score" label="分数" min-width="100" align="center">
                <template #default="{ row }">
                  <span :class="getScoreClass(row.score)">{{ row.score }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="exam_date" label="考试日期" min-width="120" align="center">
                <template #default="{ row }">
                  {{ formatDate(row.exam_date) }}
                </template>
              </el-table-column>
              <el-table-column label="等级" min-width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="getScoreTagType(row.score)" size="small">
                    {{ getScoreLevel(row.score) }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
            <div class="pagination-wrapper" v-if="gradeTotal > pageSize">
              <el-pagination
                v-model:current-page="currentPage"
                :page-size="pageSize"
                :total="gradeTotal"
                layout="total, prev, pager, next"
                @current-change="fetchGrades"
              />
            </div>
          </div>
        </div>
      </template>

      <!-- 空状态 -->
      <el-empty v-if="!loading && !student" description="未找到学生信息">
        <el-button type="primary" @click="router.push('/student/list')">返回列表</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStudentStore } from '@/stores/student'
import { getGradeList } from '@/api/grade'
import { getStudentStatistics } from '@/api/statistics'
import { formatDateTime, formatDate, getScoreLevel } from '@/utils/format'
import { EXAM_TYPES } from '@/types/grade'
import type { Student } from '@/types/student'
import type { Grade } from '@/types/grade'

const route = useRoute()
const router = useRouter()
const studentStore = useStudentStore()

const examTypes = EXAM_TYPES
const loading = ref(false)
const student = ref<Student | null>(null)
const grades = ref<Grade[]>([])
const filterExamType = ref('')
const currentPage = ref(1)
const pageSize = 20
const gradeTotal = ref(0)

const totalScore = ref(0)
const averageScore = ref(0)
const subjectCount = ref(0)
const excellentCount = ref(0)

async function fetchGrades(page?: number) {
  if (page) currentPage.value = page
  const studentId = route.params.id as string
  const params: Record<string, unknown> = {
    student_id: studentId,
    page: currentPage.value,
    page_size: pageSize,
  }
  if (filterExamType.value) params.exam_type = filterExamType.value
  const res = await getGradeList(params as any)
  grades.value = res.data?.items || []
  gradeTotal.value = res.data?.total || 0
}

async function fetchSummary() {
  const studentId = route.params.id as string
  const params: Record<string, string> = {}
  if (filterExamType.value) params.exam_type = filterExamType.value
  const res = await getStudentStatistics(studentId, params)
  const data = (res as any).data || res
  totalScore.value = data.total_score || 0
  averageScore.value = data.average_score || 0
  subjectCount.value = data.subject_count || 0
  excellentCount.value = data.excellent_count || 0
}

function handleExamTypeChange() {
  currentPage.value = 1
  fetchGrades()
  fetchSummary()
}

onMounted(async () => {
  const studentId = route.params.id as string
  loading.value = true
  try {
    await studentStore.fetchStudentDetail(studentId)
    student.value = studentStore.currentStudent
    await fetchGrades()
    await fetchSummary()
  } catch (error) {
    console.error('获取学生详情失败:', error)
  } finally {
    loading.value = false
  }
})

function handleEdit() {
  router.push(`/student/edit/${route.params.id}`)
}

function getScoreClass(score: number): string {
  if (score >= 90) return 'score-excellent'
  if (score >= 80) return 'score-good'
  if (score >= 70) return 'score-medium'
  if (score >= 60) return 'score-pass'
  return 'score-fail'
}

function getScoreTagType(score: number): 'primary' | 'success' | 'warning' | 'danger' | 'info' {
  if (score >= 90) return 'success'
  if (score >= 80) return 'primary'
  if (score >= 70) return 'warning'
  if (score >= 60) return 'warning'
  return 'danger'
}
</script>

<style lang="scss" scoped>
.student-detail {
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

    .header-actions {
      display: flex;
      gap: 12px;
    }
  }

  .detail-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .info-card {
    background: var(--surface-color);
    border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-color-light);
    box-shadow: var(--shadow-xs);
    overflow: hidden;

    .card-title {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 16px 24px;
      background: var(--bg-color);
      border-bottom: 1px solid var(--border-color-light);
      font-size: 15px;
      font-weight: 600;
      color: var(--text-color);

      .card-title-right {
        margin-left: auto;
        display: flex;
        align-items: center;
        gap: 12px;
      }
    }

    .card-body {
      padding: 24px;
    }
  }

  .info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;

    .info-item {
      display: flex;
      flex-direction: column;
      gap: 6px;

      .label {
        font-size: 13px;
        color: var(--text-color-secondary);
        font-weight: 500;
      }

      .value {
        font-size: 14px;
        color: var(--text-color);
        font-weight: 500;
      }
    }
  }

  .summary-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;

    .summary-item {
      text-align: center;
      padding: 16px;
      background: var(--bg-color);
      border-radius: var(--border-radius-md);

      .summary-value {
        font-size: 28px;
        font-weight: 700;
        line-height: 1.2;
      }

      .summary-label {
        font-size: 13px;
        color: var(--text-color-secondary);
        margin-top: 6px;
        font-weight: 500;
      }

      &--primary .summary-value { color: #2A9D8F; }
      &--success .summary-value { color: #52B788; }
      &--info .summary-value { color: #409EFF; }
      &--warning .summary-value { color: #E9A23B; }
    }
  }

  .pagination-wrapper {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
  }

  .score-excellent { color: var(--success-color); font-weight: 600; }
  .score-good { color: var(--primary-color); font-weight: 600; }
  .score-medium { color: var(--warning-color); font-weight: 600; }
  .score-pass { color: var(--danger-color); font-weight: 600; }
  .score-fail { color: var(--info-color); font-weight: 600; }
}

@media (max-width: 768px) {
  .student-detail {
    .page-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 16px;

      .header-actions {
        width: 100%;
      }
    }

    .info-grid {
      grid-template-columns: 1fr;
    }

    .summary-grid {
      grid-template-columns: repeat(2, 1fr);

      .summary-item .summary-value {
        font-size: 22px;
      }
    }
  }
}
</style>
