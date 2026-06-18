<template>
  <div class="grade-form page-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">{{ isEdit ? '编辑成绩' : '成绩录入' }}</h1>
      <el-button @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        <span class="btn-text">返回列表</span>
      </el-button>
    </div>

    <div class="form-layout">
      <!-- 表单区域 -->
      <div class="form-card page-card">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="100px"
          label-position="right"
          :disabled="submitting"
        >
          <!-- 考试信息 -->
          <div class="form-section">
            <h3 class="form-section-title">考试信息</h3>
            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="考试类型" prop="exam_type">
                  <el-select v-model="form.exam_type" placeholder="请选择考试类型" style="width: 100%">
                    <el-option v-for="et in examTypeOptions" :key="et" :label="et" :value="et" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="考试日期" prop="exam_date">
                  <el-date-picker
                    v-model="form.exam_date"
                    type="date"
                    placeholder="选择考试日期"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="总分" prop="total_score">
                  <el-input-number
                    v-model="form.total_score"
                    :min="0"
                    :max="900"
                    :precision="1"
                    :step="1"
                    controls-position="right"
                    placeholder="请输入总分"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <!-- 学生信息 -->
          <div class="form-section">
            <h3 class="form-section-title">学生信息</h3>
            <el-form-item label="选择学生" prop="student_id">
              <el-select
                v-model="form.student_id"
                filterable
                remote
                reserve-keyword
                placeholder="输入学号或姓名搜索学生"
                :remote-method="searchStudents"
                :loading="studentSearching"
                style="width: 100%"
                @change="handleStudentChange"
              >
                <el-option
                  v-for="student in studentOptions"
                  :key="student.student_id"
                  :label="`${student.student_id} - ${student.name}`"
                  :value="student.student_id"
                >
                  <div class="student-option">
                    <span class="student-id">{{ student.student_id }}</span>
                    <span class="student-name">{{ student.name }}</span>
                    <el-tag size="small" type="info">{{ student.class_name }}</el-tag>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
            <div v-if="selectedStudent" class="student-info-bar">
              <el-tag type="info" size="small">{{ selectedStudent.student_id }}</el-tag>
              <el-tag size="small">{{ selectedStudent.name }}</el-tag>
              <el-tag type="warning" size="small">{{ selectedStudent.class_name }}</el-tag>
            </div>
          </div>

          <!-- 各科成绩 -->
          <div class="form-section">
            <h3 class="form-section-title">
              各科成绩
              <span class="total-score-display" v-if="computedTotalScore > 0">
                总分：<strong>{{ computedTotalScore }}</strong>
              </span>
            </h3>
            <div class="subject-grid">
              <div v-for="sub in subjectOptions" :key="sub" class="subject-item">
                <label class="subject-label">{{ sub }}</label>
                <el-input-number
                  v-model="form.scores[sub]"
                  :min="0"
                  :max="100"
                  :precision="1"
                  :step="0.5"
                  controls-position="right"
                  placeholder="0"
                  size="default"
                />
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <el-form-item>
            <div class="form-actions">
              <el-button type="primary" :loading="submitting" @click="handleSubmit(false)">
                <el-icon><Check /></el-icon>
                提交
              </el-button>
              <el-button
                v-if="!isEdit"
                type="success"
                :loading="submitting"
                @click="handleSubmit(true)"
              >
                <el-icon><Plus /></el-icon>
                提交并继续
              </el-button>
              <el-button @click="handleReset">
                <el-icon><RefreshLeft /></el-icon>
                重置
              </el-button>
            </div>
          </el-form-item>
        </el-form>
      </div>

      <!-- 最近录入记录 -->
      <div v-if="!isEdit && recentRecords.length > 0" class="recent-card page-card">
        <div class="recent-header">
          <h3>最近录入</h3>
        </div>
        <div class="recent-list">
          <div v-for="(record, idx) in recentRecords" :key="idx" class="recent-item">
            <div class="recent-info">
              <span class="recent-name">{{ record.student_name }}</span>
              <span class="recent-score">总分 {{ record.total_score }}</span>
            </div>
            <el-tag :type="record.status === 'success' ? 'success' : 'danger'" size="small">
              {{ record.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { batchCreateGrades, saveExamTotal } from '@/api/grade'
import { getStudentList } from '@/api/student'
import { getScoreColor } from '@/utils/format'
import type { FormRules } from 'element-plus'
import type { Subject, ExamType } from '@/types/grade'
import { SUBJECTS, EXAM_TYPES } from '@/types/grade'
import { ElMessage } from 'element-plus'
import { ElForm } from 'element-plus'

const route = useRoute()

/** 科目选项 */
const subjectOptions = SUBJECTS

/** 考试类型选项 */
const examTypeOptions = EXAM_TYPES

/** 是否编辑模式 */
const isEdit = computed(() => !!route.query.id)

/** 提交状态 */
const submitting = ref(false)

/** 表单引用 */
const formRef = ref<InstanceType<typeof ElForm>>()

/** 学生搜索状态 */
const studentSearching = ref(false)

/** 学生选项 */
const studentOptions = ref<Array<{ student_id: string; name: string; class_name: string }>>([])

/** 选中的学生 */
const selectedStudent = ref<{ student_id: string; name: string; class_name: string } | null>(null)

/** 最近录入记录 */
const recentRecords = ref<Array<{ student_name: string; total_score: number; status: string }>>([])

/** 表单数据 */
const form = reactive({
  student_id: '',
  exam_type: '' as ExamType | '',
  exam_date: new Date().toISOString().split('T')[0],
  total_score: undefined as number | undefined,
  scores: {} as Record<string, number | undefined>,
})

/** 计算总分 */
const computedTotalScore = computed(() => {
  let total = 0
  for (const sub of subjectOptions) {
    const score = form.scores[sub]
    if (score !== undefined && score !== null) {
      total += score
    }
  }
  return Math.round(total * 10) / 10
})

/** 已填写科目数 */
const filledSubjectCount = computed(() => {
  return subjectOptions.filter((sub) => {
    const score = form.scores[sub]
    return score !== undefined && score !== null && score > 0
  }).length
})

/** 表单验证规则 */
const rules: FormRules = {
  student_id: [
    { required: true, message: '请选择学生', trigger: 'change' },
  ],
  exam_type: [
    { required: true, message: '请选择考试类型', trigger: 'change' },
  ],
  exam_date: [
    { required: true, message: '请选择考试日期', trigger: 'change' },
  ],
  total_score: [
    { required: true, message: '请输入总分', trigger: 'blur' },
  ],
}

/** 搜索学生 */
async function searchStudents(query: string) {
  if (!query || query.length < 1) {
    studentOptions.value = []
    return
  }
  studentSearching.value = true
  try {
    const res = await getStudentList({ keyword: query, page_size: 20 } as any)
    const data = (res as any).data || res
    studentOptions.value = (data.items || []).map((s: any) => ({
      student_id: s.student_id,
      name: s.name,
      class_name: s.class_name,
    }))
  } catch {
    studentOptions.value = []
  } finally {
    studentSearching.value = false
  }
}

/** 学生选择变化 */
function handleStudentChange(studentId: string) {
  selectedStudent.value = studentOptions.value.find((s) => s.student_id === studentId) || null
}

/** 提交表单 */
async function handleSubmit(continueAfter: boolean) {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  if (!form.student_id) {
    ElMessage.warning('请选择学生')
    return
  }
  if (!form.exam_type) {
    ElMessage.warning('请选择考试类型')
    return
  }
  if (form.total_score === undefined || form.total_score === null) {
    ElMessage.warning('请输入总分')
    return
  }
  if (filledSubjectCount.value === 0) {
    ElMessage.warning('请至少填写一个科目的成绩')
    return
  }

  submitting.value = true
  try {
    // 构建批量成绩数据
    const grades = []
    for (const sub of subjectOptions) {
      const score = form.scores[sub]
      if (score !== undefined && score !== null && score > 0) {
        grades.push({
          student_id: form.student_id,
          subject: sub,
          score: score,
          exam_type: form.exam_type as ExamType,
          exam_date: form.exam_date,
        })
      }
    }

    await batchCreateGrades({
      subject: grades[0].subject, // 会被后端忽略，因为每条记录有自己的subject
      exam_type: form.exam_type as ExamType,
      exam_date: form.exam_date,
      grades: grades.map(g => ({ student_id: g.student_id, score: g.score })),
    })

    // 保存总分
    await saveExamTotal({
      student_id: form.student_id,
      exam_type: form.exam_type as ExamType,
      exam_date: form.exam_date,
      total_score: form.total_score!,
    })

    // 添加到最近记录
    recentRecords.value.unshift({
      student_name: selectedStudent.value?.name || form.student_id,
      total_score: computedTotalScore.value,
      status: 'success',
    })
    if (recentRecords.value.length > 10) {
      recentRecords.value = recentRecords.value.slice(0, 10)
    }

    if (continueAfter) {
      handleReset()
      ElMessage.success('录入成功，请继续')
    } else {
      ElMessage.success('录入成功')
      goBack()
    }
  } catch (error: any) {
    const msg = error?.response?.data?.message || error?.message || '提交失败'
    ElMessage.error(msg)
    recentRecords.value.unshift({
      student_name: selectedStudent.value?.name || form.student_id,
      total_score: computedTotalScore.value,
      status: 'error',
    })
  } finally {
    submitting.value = false
  }
}

/** 重置表单 */
function handleReset() {
  formRef.value?.resetFields()
  form.scores = {}
  form.exam_date = new Date().toISOString().split('T')[0]
  selectedStudent.value = null
  studentOptions.value = []
}

/** 返回列表 */
function goBack() {
  window.history.back()
}

/** 初始化 */
onMounted(() => {
  // 初始化所有科目分数为 undefined
  for (const sub of subjectOptions) {
    form.scores[sub] = undefined
  }
})
</script>

<style lang="scss" scoped>
.grade-form {
  animation: fadeIn 0.3s ease;

  .form-layout {
    display: flex;
    gap: 16px;
    align-items: flex-start;
  }

  .form-card {
    flex: 1;
    max-width: 800px;
  }

  .recent-card {
    width: 320px;
    flex-shrink: 0;

    .recent-header {
      margin-bottom: 12px;

      h3 {
        font-size: 15px;
        font-weight: 600;
        color: var(--text-color);
      }
    }

    .recent-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .recent-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 12px;
      background: var(--bg-color);
      border-radius: var(--border-radius-md);

      .recent-info {
        display: flex;
        flex-direction: column;
        gap: 2px;

        .recent-name {
          font-size: 14px;
          font-weight: 500;
          color: var(--text-color);
        }

        .recent-score {
          font-size: 12px;
          color: var(--text-color-secondary);
        }
      }
    }
  }

  .form-section {
    margin-bottom: 24px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--border-color-light);

    &:last-of-type {
      border-bottom: none;
    }
  }

  .form-section-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-color);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 12px;

    .total-score-display {
      margin-left: auto;
      font-size: 14px;
      font-weight: 500;
      color: var(--primary-color);

      strong {
        font-size: 20px;
      }
    }
  }

  .student-info-bar {
    display: flex;
    gap: 8px;
    margin-top: -8px;
    margin-bottom: 16px;
  }

  .subject-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }

  .subject-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: var(--bg-color);
    border-radius: var(--border-radius-md);

    .subject-label {
      font-size: 14px;
      font-weight: 500;
      color: var(--text-color);
      min-width: 36px;
    }

    :deep(.el-input-number) {
      flex: 1;
    }
  }

  .form-actions {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }

  .student-option {
    display: flex;
    align-items: center;
    gap: 12px;

    .student-id {
      color: var(--text-color-secondary);
      font-size: 13px;
    }

    .student-name {
      flex: 1;
      font-weight: 500;
    }
  }
}

/* 响应式布局 */
@media (max-width: 992px) {
  .grade-form {
    .form-layout {
      flex-direction: column;
    }

    .form-card {
      max-width: 100%;
    }

    .recent-card {
      width: 100%;
    }

    .subject-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
}

@media (max-width: 768px) {
  .grade-form {
    .page-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }

    .subject-grid {
      grid-template-columns: 1fr;
    }
  }
}

@media (max-width: 480px) {
  .grade-form {
    .btn-text {
      display: none;
    }
  }
}
</style>
