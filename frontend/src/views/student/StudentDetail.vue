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

        <!-- 成绩信息卡片 -->
        <div class="info-card">
          <div class="card-title">
            <el-icon><Document /></el-icon>
            <span>成绩记录</span>
            <el-tag type="info" size="small" class="grade-count">
              共 {{ grades.length }} 条
            </el-tag>
          </div>
          <div class="card-body">
            <!-- 桌面端表格 -->
            <div class="grade-table desktop-only">
              <el-table :data="grades" border stripe empty-text="暂无成绩数据">
                <el-table-column prop="subject" label="科目" width="120" align="center" />
                <el-table-column prop="exam_type" label="考试类型" width="120" align="center">
                  <template #default="{ row }">
                    <el-tag size="small">{{ row.exam_type }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="score" label="分数" width="120" align="center">
                  <template #default="{ row }">
                    <span :class="getScoreClass(row.score)">{{ row.score }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="exam_date" label="考试日期" width="150" align="center">
                  <template #default="{ row }">
                    {{ formatDate(row.exam_date) }}
                  </template>
                </el-table-column>
                <el-table-column label="等级" width="100" align="center">
                  <template #default="{ row }">
                    <el-tag :type="getScoreTagType(row.score)" size="small">
                      {{ getScoreLevel(row.score) }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <!-- 移动端卡片 -->
            <div class="grade-cards mobile-only">
              <el-empty v-if="grades.length === 0" description="暂无成绩数据" />
              <div v-for="grade in grades" :key="grade.grade_id" class="grade-card">
                <div class="grade-header">
                  <span class="subject">{{ grade.subject }}</span>
                  <el-tag size="small">{{ grade.exam_type }}</el-tag>
                </div>
                <div class="grade-body">
                  <div class="score" :class="getScoreClass(grade.score)">
                    {{ grade.score }}
                    <span class="unit">分</span>
                  </div>
                  <el-tag :type="getScoreTagType(grade.score)" size="small">
                    {{ getScoreLevel(grade.score) }}
                  </el-tag>
                </div>
                <div class="grade-footer">
                  考试日期：{{ formatDate(grade.exam_date) }}
                </div>
              </div>
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
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStudentStore } from '@/stores/student'
import { getGradeList } from '@/api/grade'
import { formatDateTime, formatDate, getScoreLevel, getScoreColor } from '@/utils/format'
import type { Student } from '@/types/student'
import type { Grade } from '@/types/grade'

const route = useRoute()
const router = useRouter()
const studentStore = useStudentStore()

/** 加载状态 */
const loading = ref(false)

/** 学生信息 */
const student = ref<Student | null>(null)

/** 成绩列表 */
const grades = ref<Grade[]>([])

/** 初始化 */
onMounted(async () => {
  const studentId = route.params.id as string
  loading.value = true
  try {
    // 获取学生详情
    await studentStore.fetchStudentDetail(studentId)
    student.value = studentStore.currentStudent

    // 获取该学生的成绩列表
    const gradeResponse = await getGradeList({
      student_id: studentId,
      page: 1,
      page_size: 100,
    })
    grades.value = gradeResponse.items
  } catch (error) {
    console.error('获取学生详情失败:', error)
  } finally {
    loading.value = false
  }
})

/** 编辑 */
function handleEdit() {
  router.push(`/student/edit/${route.params.id}`)
}

/** 获取分数样式类 */
function getScoreClass(score: number): string {
  if (score >= 90) return 'score-excellent'
  if (score >= 80) return 'score-good'
  if (score >= 70) return 'score-medium'
  if (score >= 60) return 'score-pass'
  return 'score-fail'
}

/** 获取分数标签类型 */
function getScoreTagType(score: number): '' | 'success' | 'warning' | 'danger' | 'info' {
  if (score >= 90) return 'success'
  if (score >= 80) return ''
  if (score >= 70) return 'warning'
  if (score >= 60) return 'warning'
  return 'danger'
}
</script>

<style lang="scss" scoped>
.student-detail {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .page-title {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
    }

    .header-actions {
      display: flex;
      gap: 12px;
    }
  }

  .detail-content {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .info-card {
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    overflow: hidden;

    .card-title {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 16px 20px;
      background: #fafafa;
      border-bottom: 1px solid #f0f0f0;
      font-size: 16px;
      font-weight: 600;
      color: #303133;

      .grade-count {
        margin-left: auto;
      }
    }

    .card-body {
      padding: 20px;
    }
  }

  .info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 16px;

    .info-item {
      display: flex;
      flex-direction: column;
      gap: 8px;

      .label {
        font-size: 13px;
        color: #909399;
      }

      .value {
        font-size: 14px;
        color: #303133;
        font-weight: 500;
      }
    }
  }

  // 分数样式
  .score-excellent {
    color: #67c23a;
    font-weight: 600;
  }

  .score-good {
    color: #409eff;
    font-weight: 600;
  }

  .score-medium {
    color: #e6a23c;
    font-weight: 600;
  }

  .score-pass {
    color: #f56c6c;
    font-weight: 600;
  }

  .score-fail {
    color: #909399;
    font-weight: 600;
  }

  // 移动端成绩卡片
  .grade-cards {
    display: grid;
    gap: 12px;

    .grade-card {
      background: #fafafa;
      border-radius: 8px;
      padding: 16px;

      .grade-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;

        .subject {
          font-size: 16px;
          font-weight: 600;
          color: #303133;
        }
      }

      .grade-body {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;

        .score {
          font-size: 28px;
          font-weight: 700;

          .unit {
            font-size: 14px;
            font-weight: 400;
            color: #909399;
          }
        }
      }

      .grade-footer {
        font-size: 13px;
        color: #909399;
      }
    }
  }
}

// 响应式显示控制
.desktop-only {
  display: block;
}

.mobile-only {
  display: none;
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
  }

  .desktop-only {
    display: none;
  }

  .mobile-only {
    display: block;
  }
}
</style>
