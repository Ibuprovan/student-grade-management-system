<template>
  <div class="class-teacher-management page-container">
    <div class="page-header">
      <h1 class="page-title">班主任管理</h1>
      <el-button type="primary" :loading="loadingClasses" @click="handleOpenAdd">
        <el-icon><Plus /></el-icon>
        添加班主任
      </el-button>
    </div>

    <div class="page-card">
      <el-table
        :data="teachers"
        border
        stripe
        style="width: 100%"
        v-loading="loading"
        :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }"
      >
        <el-table-column prop="class_name" label="班级" min-width="120" />
        <el-table-column prop="teacher_name" label="班主任" min-width="100" />
        <el-table-column prop="username" label="登录账号" min-width="120" />
        <el-table-column prop="enrollment_year" label="入学年份" min-width="100" align="center" />
        <el-table-column prop="class_number" label="班级序号" min-width="100" align="center" />
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-popconfirm
              title="确定删除该班主任吗？将同时删除其登录账号。"
              confirm-button-text="确定"
              cancel-button-text="取消"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button type="danger" size="small" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 添加班主任对话框 - 仅当已加载数据时才渲染 -->
    <el-dialog
      v-if="showAddDialog"
      v-model="showAddDialog"
      title="添加班主任"
      width="520px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="选择班级" prop="class_name">
          <el-select
            v-model="form.class_name"
            placeholder="请选择班级"
            style="width: 100%"
            clearable
            @change="onClassChange"
          >
            <el-option
              v-for="cls in availableClasses"
              :key="cls.class_name"
              :label="cls.class_name + '（' + cls.student_count + '人）'"
              :value="cls.class_name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="班主任姓名" prop="teacher_name">
          <el-input
            v-model="form.teacher_name"
            placeholder="请输入班主任姓名"
            maxlength="20"
          />
        </el-form-item>
        <el-alert
          v-if="form.class_name && form.enrollment_year && form.class_number"
          :title="'账号：' + form.enrollment_year + String(form.class_number).padStart(3, '0')"
          description="初始密码为 123456，首次登录需修改密码"
          type="info"
          show-icon
          :closable="false"
        />
        <el-alert
          v-if="availableClasses.length === 0"
          title="暂无可分配的班级"
          description="所有有学生的班级均已分配班主任，或数据库中暂无学生数据"
          type="warning"
          show-icon
          :closable="false"
        />
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" :disabled="!form.class_name || availableClasses.length === 0" @click="handleAdd">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import {
  getClassTeacherList,
  createClassTeacher,
  deleteClassTeacher,
  getAvailableClasses,
  type ClassTeacherInfo,
  type AvailableClass,
} from '@/api/classTeacher'

const loading = ref(false)
const submitting = ref(false)
const loadingClasses = ref(false)
const teachers = ref<ClassTeacherInfo[]>([])
const availableClasses = ref<AvailableClass[]>([])
const showAddDialog = ref(false)
const formRef = ref<FormInstance>()
const authStore = useAuthStore()

const form = ref({
  class_name: '',
  enrollment_year: 0,
  class_number: 0,
  teacher_name: '',
})

const rules: FormRules = {
  class_name: [{ required: true, message: '请选择班级', trigger: 'change' }],
  teacher_name: [
    { required: true, message: '请输入班主任姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度为 2-20 个字符', trigger: 'blur' },
  ],
}

function onClassChange(className: string) {
  const cls = availableClasses.value.find((c) => c.class_name === className)
  if (cls) {
    form.value.enrollment_year = cls.enrollment_year
    form.value.class_number = cls.class_number
  }
}

async function ensureAdminSession(): Promise<boolean> {
  try {
    await authStore.checkAuth()
    if (!authStore.isAuthenticated || !authStore.isAdmin) {
      ElMessage.error('登录状态已失效，请重新登录管理员账号')
      return false
    }
    return true
  } catch (e) {
    console.error('管理员登录状态校验失败:', e)
    ElMessage.error('登录状态已失效，请重新登录管理员账号')
    return false
  }
}

async function fetchTeachers() {
  if (!(await ensureAdminSession())) return
  loading.value = true
  try {
    const res = await getClassTeacherList()
    if (res?.data) {
      teachers.value = res.data as unknown as ClassTeacherInfo[]
    }
  } catch (e) {
    console.error('获取班主任列表失败:', e)
    ElMessage.error('获取班主任列表失败')
  } finally {
    loading.value = false
  }
}

/** 先加载可用班级数据，成功后再打开对话框 */
async function handleOpenAdd() {
  if (!(await ensureAdminSession())) return
  loadingClasses.value = true
  try {
    const res = await getAvailableClasses()
    const rawData = res?.data
    if (rawData && Array.isArray(rawData)) {
      availableClasses.value = rawData
    } else if (rawData) {
      availableClasses.value = [rawData as AvailableClass]
    } else {
      availableClasses.value = []
    }
    // 重置表单
    form.value = { class_name: '', enrollment_year: 0, class_number: 0, teacher_name: '' }
    if (availableClasses.value.length > 0) {
      const first = availableClasses.value[0]
      form.value.class_name = first.class_name
      form.value.enrollment_year = first.enrollment_year
      form.value.class_number = first.class_number
    }
    // 数据加载成功后打开对话框
    showAddDialog.value = availableClasses.value.length > 0
    if (availableClasses.value.length === 0) {
      ElMessage.warning('暂无可分配的班级')
    }
  } catch (e) {
    console.error('获取可分配班级失败:', e)
    ElMessage.error('获取可分配班级失败')
  } finally {
    loadingClasses.value = false
  }
}

async function handleAdd() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const res = await createClassTeacher(form.value)
    ElMessage.success(res?.message || '添加成功')
    showAddDialog.value = false
    await fetchTeachers()
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    ElMessage.error(err?.response?.data?.detail || '添加失败')
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row: ClassTeacherInfo) {
  try {
    await deleteClassTeacher(row.id)
    ElMessage.success('删除成功')
    await fetchTeachers()
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    ElMessage.error(err?.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  fetchTeachers()
})
</script>

<style lang="scss" scoped>
.class-teacher-management {
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
}
</style>
