<template>
  <div class="student-form page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">{{ isEdit ? '编辑学生' : '添加学生' }}</h1>
      <el-button @click="handleCancel">
        <el-icon><Back /></el-icon>
        返回
      </el-button>
    </div>

    <!-- 表单卡片 -->
    <div class="form-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        label-position="right"
        :status-icon="true"
      >
        <!-- 学号 -->
        <el-form-item label="学号" prop="student_id">
          <el-input
            v-model="form.student_id"
            placeholder="请输入学号（8位数字，如：20260001）"
            :disabled="isEdit"
            maxlength="8"
            show-word-limit
            clearable
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
          <div class="form-tip">格式：4位年份 + 4位序号，如 20260001</div>
        </el-form-item>

        <!-- 姓名 -->
        <el-form-item label="姓名" prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入姓名（2-20个字符）"
            maxlength="20"
            show-word-limit
            clearable
          >
            <template #prefix>
              <el-icon><UserFilled /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <!-- 性别 -->
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender">
            <el-radio value="男">
              <el-icon><Male /></el-icon>
              男
            </el-radio>
            <el-radio value="女">
              <el-icon><Female /></el-icon>
              女
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 班级 -->
        <el-form-item label="班级" prop="class_name">
          <el-select
            v-model="form.class_name"
            placeholder="请选择或输入班级"
            filterable
            allow-create
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="cls in classOptions"
              :key="cls"
              :label="cls"
              :value="cls"
            />
          </el-select>
          <div class="form-tip">可选择已有班级或输入新班级名称</div>
        </el-form-item>

        <!-- 入学年份 -->
        <el-form-item label="入学年份" prop="enrollment_year">
          <el-select
            v-model="form.enrollment_year"
            placeholder="请选择入学年份"
            style="width: 100%"
          >
            <el-option
              v-for="year in yearOptions"
              :key="year"
              :label="year"
              :value="year"
            />
          </el-select>
        </el-form-item>

        <!-- 按钮区域 -->
        <el-form-item>
          <div class="form-actions">
            <el-button type="primary" :loading="loading" @click="handleSubmit">
              <el-icon><Check /></el-icon>
              {{ isEdit ? '保存修改' : '确认添加' }}
            </el-button>
            <el-button @click="handleReset">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
            <el-button @click="handleCancel">取消</el-button>
          </div>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStudentStore } from '@/stores/student'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const studentStore = useStudentStore()

/** 是否为编辑模式 */
const isEdit = computed(() => !!route.params.id)

/** 加载状态 */
const loading = ref(false)

/** 表单引用 */
const formRef = ref<FormInstance>()

/** 班级选项 */
const classOptions = computed(() => {
  if (studentStore.classList.length > 0) {
    return studentStore.classList
  }
  return ['三年一班', '三年二班', '三年三班', '三年四班']
})

/** 年份选项（2000-2100） */
const yearOptions = computed(() => {
  const years: number[] = []
  const currentYear = new Date().getFullYear()
  for (let year = currentYear + 1; year >= 2000; year--) {
    years.push(year)
  }
  return years
})

/** 表单数据 */
const form = reactive({
  student_id: '',
  name: '',
  gender: '男' as '男' | '女',
  class_name: '',
  enrollment_year: undefined as number | undefined,
})

/** 保存初始表单数据（用于重置） */
const initialForm = { ...form }

/** 表单验证规则 */
const rules: FormRules = {
  student_id: [
    { required: true, message: '请输入学号', trigger: 'blur' },
    {
      pattern: /^\d{8}$/,
      message: '学号格式不正确，应为8位数字（如：20260001）',
      trigger: 'blur',
    },
    {
      validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
        if (value && value.length === 8) {
          const year = parseInt(value.substring(0, 4))
          if (year < 2000 || year > 2100) {
            callback(new Error('学号年份部分应在2000-2100之间'))
          } else {
            callback()
          }
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度应为2-20个字符', trigger: 'blur' },
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' },
  ],
  class_name: [
    { required: true, message: '请选择或输入班级', trigger: 'change' },
    { min: 2, max: 20, message: '班级名称长度应为2-20个字符', trigger: 'blur' },
  ],
  enrollment_year: [
    { required: true, message: '请选择入学年份', trigger: 'change' },
    {
      validator: (_rule: unknown, value: number | undefined, callback: (error?: Error) => void) => {
        if (value && (value < 2000 || value > 2100)) {
          callback(new Error('入学年份应在2000-2100之间'))
        } else {
          callback()
        }
      },
      trigger: 'change',
    },
  ],
}

/** 初始化（编辑模式时加载数据） */
onMounted(async () => {
  // 获取班级列表
  studentStore.fetchClassList()

  if (isEdit.value) {
    const studentId = route.params.id as string
    loading.value = true
    try {
      await studentStore.fetchStudentDetail(studentId)
      if (studentStore.currentStudent) {
        Object.assign(form, {
          student_id: studentStore.currentStudent.student_id,
          name: studentStore.currentStudent.name,
          gender: studentStore.currentStudent.gender,
          class_name: studentStore.currentStudent.class_name,
          enrollment_year: studentStore.currentStudent.enrollment_year,
        })
      }
    } finally {
      loading.value = false
    }
  }
})

/** 提交表单 */
async function handleSubmit() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    ElMessage.warning('请检查表单填写是否正确')
    return
  }

  if (!form.enrollment_year) {
    ElMessage.warning('请选择入学年份')
    return
  }

  loading.value = true
  try {
    const data = {
      student_id: form.student_id,
      name: form.name,
      gender: form.gender,
      class_name: form.class_name,
      enrollment_year: form.enrollment_year,
    }

    if (isEdit.value) {
      await studentStore.updateStudent(form.student_id, data)
    } else {
      await studentStore.createStudent(data)
    }

    router.push('/student/list')
  } catch (error) {
    // 错误已在 store 中处理
    console.error('提交失败:', error)
  } finally {
    loading.value = false
  }
}

/** 重置表单 */
function handleReset() {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  if (isEdit.value && studentStore.currentStudent) {
    Object.assign(form, {
      student_id: studentStore.currentStudent.student_id,
      name: studentStore.currentStudent.name,
      gender: studentStore.currentStudent.gender,
      class_name: studentStore.currentStudent.class_name,
      enrollment_year: studentStore.currentStudent.enrollment_year,
    })
  } else {
    Object.assign(form, initialForm)
    form.enrollment_year = undefined
  }
}

/** 取消 */
function handleCancel() {
  router.back()
}
</script>

<style lang="scss" scoped>
.student-form {
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
  }

  .form-card {
    background: #fff;
    padding: 32px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    max-width: 700px;
  }

  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
    line-height: 1.4;
  }

  .form-actions {
    display: flex;
    gap: 12px;
  }

  :deep(.el-form-item__label) {
    font-weight: 500;
  }

  :deep(.el-radio) {
    margin-right: 24px;
  }
}

@media (max-width: 768px) {
  .student-form {
    .form-card {
      padding: 20px;
    }

    :deep(.el-form-item__label) {
      float: none;
      display: block;
      text-align: left;
      padding-bottom: 8px;
    }

    :deep(.el-form-item__content) {
      margin-left: 0 !important;
    }

    .form-actions {
      flex-direction: column;
      width: 100%;

      .el-button {
        width: 100%;
      }
    }
  }
}
</style>
