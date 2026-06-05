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
          <el-form-item label="学生" prop="student_id">
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

          <el-form-item label="科目" prop="subject">
            <el-select v-model="form.subject" placeholder="请选择科目" style="width: 100%">
              <el-option
                v-for="sub in subjectOptions"
                :key="sub"
                :label="sub"
                :value="sub"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="考试类型" prop="exam_type">
            <el-select v-model="form.exam_type" placeholder="请选择考试类型" style="width: 100%">
              <el-option
                v-for="et in examTypeOptions"
                :key="et"
                :label="et"
                :value="et"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="分数" prop="score">
            <el-input-number
              v-model="form.score"
              :min="0"
              :max="100"
              :precision="1"
              :step="0.5"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item label="考试日期" prop="exam_date">
            <el-date-picker
              v-model="form.exam_date"
              type="date"
              placeholder="选择考试日期"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>

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
          <h3>最近录入记录</h3>
        </div>
        <el-table :data="recentRecords" size="small" stripe>
          <el-table-column prop="student_id" label="学号" width="100" />
          <el-table-column prop="student_name" label="姓名" width="80" />
          <el-table-column prop="subject" label="科目" width="80" />
          <el-table-column prop="score" label="分数" width="80" align="center">
            <template #default="{ row }">
              <span :style="{ color: getScoreColor(row.score) }">
                {{ formatScore(row.score) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="time" label="时间" width="80" />
          <el-table-column label="状态" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
                {{ row.status === 'success' ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useGradeForm } from '@/composables/useGrade'
import { getScoreColor, formatScore } from '@/utils/format'
import { getStudentList, getStudentDetail } from '@/api/student'
import { getGradeDetail } from '@/api/grade'
import type { FormInstance, FormRules } from 'element-plus'
import type { Subject, ExamType } from '@/types/grade'
import type { Student } from '@/types/student'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()

const {
  subjectOptions,
  examTypeOptions,
  recentRecords,
  checkDuplicate,
  addRecentRecord,
  goBack,
  createGrade,
  updateGrade,
} = useGradeForm()

/** 是否编辑模式 */
const isEdit = computed(() => !!route.query.id)

/** 提交状态 */
const submitting = ref(false)

/** 表单引用 */
const formRef = ref<FormInstance>()

/** 学生搜索状态 */
const studentSearching = ref(false)

/** 学生选项 */
const studentOptions = ref<Student[]>([])

/** 表单数据 */
const form = reactive({
  student_id: '',
  subject: '' as Subject | '',
  exam_type: '' as ExamType | '',
  score: 80,
  exam_date: new Date().toISOString().split('T')[0],
})

/** 表单验证规则 */
const rules: FormRules = {
  student_id: [
    { required: true, message: '请选择学生', trigger: 'change' },
  ],
  subject: [
    { required: true, message: '请选择科目', trigger: 'change' },
  ],
  exam_type: [
    { required: true, message: '请选择考试类型', trigger: 'change' },
  ],
  score: [
    { required: true, message: '请输入分数', trigger: 'blur' },
    {
      validator: (_rule: unknown, value: number, callback: (error?: Error) => void) => {
        if (value < 0 || value > 100) {
          callback(new Error('分数必须在 0-100 之间'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  exam_date: [
    { required: true, message: '请选择考试日期', trigger: 'change' },
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
    const result = await getStudentList({ keyword: query, page_size: 20 })
    studentOptions.value = result.items
  } catch (error) {
    console.error('搜索学生失败:', error)
  } finally {
    studentSearching.value = false
  }
}

/** 学生选择变化 */
function handleStudentChange(studentId: string) {
  const student = studentOptions.value.find((s) => s.student_id === studentId)
  if (student) {
    // 可以在此处做额外处理
  }
}

/** 重复检测 */
async function handleDuplicateCheck() {
  if (!form.student_id || !form.subject || !form.exam_type) return false

  const exists = await checkDuplicate(
    form.student_id,
    form.subject as string,
    form.exam_type as string,
  )

  if (exists) {
    const confirmed = await ElMessageBox.confirm(
      '该学生该科目的此考试类型成绩已存在，是否继续录入将覆盖原有成绩？',
      '重复成绩提示',
      {
        confirmButtonText: '继续录入',
        cancelButtonText: '取消',
        type: 'warning',
      },
    ).catch(() => false)

    return confirmed
  }

  return true
}

/** 提交表单 */
async function handleSubmit(continueAfter: boolean) {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    // 重复检测
    const canProceed = await handleDuplicateCheck()
    if (!canProceed) return

    submitting.value = true
    try {
      const data = {
        student_id: form.student_id,
        subject: form.subject as Subject,
        score: form.score,
        exam_type: form.exam_type as ExamType,
        exam_date: form.exam_date,
      }

      if (isEdit.value) {
        await updateGrade(Number(route.query.id), data)
      } else {
        await createGrade(data)

        // 添加到最近记录
        const student = studentOptions.value.find((s) => s.student_id === form.student_id)
        addRecentRecord({
          student_id: form.student_id,
          student_name: student?.name || '-',
          subject: form.subject as string,
          score: form.score,
          status: 'success',
        })
      }

      if (continueAfter) {
        // 提交并继续：重置表单但保留部分字段
        handleReset()
        ElMessage.success('录入成功，请继续')
      } else {
        goBack()
      }
    } catch (error) {
      if (!continueAfter) return
      // 添加失败记录
      addRecentRecord({
        student_id: form.student_id,
        student_name: '-',
        subject: form.subject as string,
        score: form.score,
        status: 'error',
      })
    } finally {
      submitting.value = false
    }
  })
}

/** 重置表单 */
function handleReset() {
  formRef.value?.resetFields()
  form.score = 80
  form.exam_date = new Date().toISOString().split('T')[0]
}

/** 加载编辑数据 */
async function loadEditData() {
  if (!route.query.id) return

  try {
    const grade = await getGradeDetail(Number(route.query.id))
    form.student_id = grade.student_id
    form.subject = grade.subject
    form.exam_type = grade.exam_type
    form.score = grade.score
    form.exam_date = grade.exam_date

    // 通过 API 获取完整的学生信息
    const student = await getStudentDetail(grade.student_id)
    studentOptions.value = [student]
  } catch (error) {
    console.error('加载成绩详情失败:', error)
    ElMessage.error('加载成绩详情失败')
    goBack()
  }
}

/** 初始化 */
onMounted(() => {
  if (isEdit.value) {
    loadEditData()
  }
})
</script>

<style lang="scss" scoped>
.grade-form {
  .form-layout {
    display: flex;
    gap: 16px;
    align-items: flex-start;
  }

  .form-card {
    flex: 1;
    max-width: 640px;
  }

  .recent-card {
    width: 400px;
    flex-shrink: 0;

    .recent-header {
      margin-bottom: 12px;

      h3 {
        font-size: 15px;
        font-weight: 600;
        color: var(--text-color);
      }
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
  }
}

@media (max-width: 768px) {
  .grade-form {
    .page-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }

    .form-card {
      padding: 16px;
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
