<template>
  <div class="teacher-assign page-container">
    <div class="page-header">
      <h1 class="page-title">教师任课管理</h1>
      <span class="page-count">共 {{ assignments.length }} 条记录</span>
      <el-button type="primary" @click="showDialog" :loading="comboLoading">
        <el-icon><Plus /></el-icon>添加教师
      </el-button>
    </div>

    <div class="page-card">
      <el-table :data="assignments" border stripe style="width: 100%" v-loading="loading" :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }">
        <el-table-column prop="username" label="用户名" min-width="140" />
        <el-table-column prop="teacher_name" label="教师姓名" min-width="100" />
        <el-table-column prop="subject" label="科目" min-width="80" align="center" />
        <el-table-column prop="class_name" label="班级" min-width="100" />
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-popconfirm title="确定删除该教师任课吗？关联用户账号将一并删除。" confirm-button-text="确定" cancel-button-text="取消" @confirm="handleDelete(row)">
              <template #reference>
                <el-button type="danger" size="small" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" title="添加教师" width="520px" :close-on-click-modal="false" destroy-on-close append-to-body>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="科目+班级" prop="combo_key">
          <el-select v-model="form.combo_key" placeholder="选择科目+班级" filterable style="width: 100%" :teleported="false" @change="onComboChange">
            <el-option v-for="c in combos" :key="c.key" :label="c.label" :value="c.key" />
          </el-select>
        </el-form-item>
        <el-form-item label="教师姓名" prop="teacher_name">
          <el-input v-model="form.teacher_name" placeholder="请输入教师姓名" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确认添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  getAvailableCombinations,
  getTeacherAssignmentList,
  createTeacherAssignment,
  deleteTeacherAssignment,
  type TeacherAssignmentInfo,
  type AvailableCombination,
} from '@/api/teacher'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const loading = ref(false)
const comboLoading = ref(false)
const submitting = ref(false)
const assignments = ref<TeacherAssignmentInfo[]>([])
const availableCombos = ref<AvailableCombination[]>([])
const dialogVisible = ref(false)
const formRef = ref<FormInstance>()

const form = ref({
  combo_key: '',
  subject: '',
  class_name: '',
  teacher_name: '',
})

const rules: FormRules = {
  combo_key: [{ required: true, message: '请选择科目+班级', trigger: 'change' }],
  teacher_name: [{ required: true, message: '请输入教师姓名', trigger: 'blur' }],
}

interface ComboOption {
  key: string
  label: string
  subject: string
  class_name: string
}

const combos = ref<ComboOption[]>([])

async function ensureAdminSession() {
  if (!authStore.isAuthenticated || !authStore.isAdmin) {
    await authStore.checkAuth()
  }
}

async function fetchAssignments() {
  loading.value = true
  try {
    await ensureAdminSession()
    const res = await getTeacherAssignmentList()
    if (res?.data) assignments.value = res.data as unknown as TeacherAssignmentInfo[]
  } catch (e) { console.error('获取教师列表失败:', e) } finally { loading.value = false }
}

async function fetchCombos() {
  comboLoading.value = true
  try {
    await ensureAdminSession()
    const res = await getAvailableCombinations()
    if (res?.data) {
      availableCombos.value = res.data as unknown as AvailableCombination[]
      combos.value = availableCombos.value.map(c => ({
        key: `${c.subject}|${c.class_name}`,
        label: `${c.subject} · ${c.class_name}`,
        subject: c.subject,
        class_name: c.class_name,
      }))
    }
  } catch (e) { console.error('获取可分配组合失败:', e) } finally { comboLoading.value = false }
}

function onComboChange(val: string) {
  const [subject, class_name] = val.split('|')
  form.value.subject = subject
  form.value.class_name = class_name
}

function showDialog() {
  form.value = { combo_key: '', subject: '', class_name: '', teacher_name: '' }
  fetchCombos()
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch { return }
  submitting.value = true
  try {
    await ensureAdminSession()
    const res = await createTeacherAssignment({
      subject: form.value.subject,
      class_name: form.value.class_name,
      teacher_name: form.value.teacher_name,
    })
    ElMessage.success(res?.message || '添加成功')
    dialogVisible.value = false
    fetchAssignments()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '添加失败')
  } finally { submitting.value = false }
}

async function handleDelete(row: TeacherAssignmentInfo) {
  try {
    await ensureAdminSession()
    const res = await deleteTeacherAssignment(row.id)
    ElMessage.success(res?.message || '删除成功')
    fetchAssignments()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  fetchAssignments()
})
</script>

<style lang="scss" scoped>
.teacher-assign {
  animation: fadeIn 0.3s ease;
  .page-header {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 20px; flex-wrap: wrap;
  }
  .page-title { margin: 0; font-size: 22px; font-weight: 700; }
  .page-count { font-size: 14px; color: var(--text-color-secondary); flex: 1; }
}

:deep(.el-dialog) {
  .el-select { width: 100%; }
  .el-select-dropdown__item { white-space: nowrap; }
}
</style>
