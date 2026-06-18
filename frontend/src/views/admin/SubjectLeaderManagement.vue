<template>
  <div class="subject-leader-management page-container">
    <div class="page-header">
      <h1 class="page-title">学科组长管理</h1>
      <el-button type="primary" :loading="loadingSubjects" @click="handleOpenAdd">
        <el-icon><Plus /></el-icon>
        添加学科组长
      </el-button>
    </div>

    <div class="page-card">
      <el-table
        :data="leaders"
        border
        stripe
        style="width: 100%"
        v-loading="loading"
        :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }"
      >
        <el-table-column prop="subject" label="学科" min-width="100" />
        <el-table-column prop="subject_en" label="英文名" min-width="100" />
        <el-table-column prop="leader_name" label="组长" min-width="100" />
        <el-table-column prop="username" label="登录账号" min-width="120" />
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-popconfirm
              title="确定删除该学科组长吗？将同时删除其登录账号。"
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

    <el-dialog
      v-if="showAddDialog"
      v-model="showAddDialog"
      title="添加学科组长"
      width="480px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="选择学科" prop="subject">
          <el-select v-model="form.subject" placeholder="请选择学科" style="width: 100%" @change="onSubjectChange">
            <el-option
              v-for="s in availableSubjects"
              :key="s.subject"
              :label="s.subject + '（' + s.subject_en + '）'"
              :value="s.subject"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="组长姓名" prop="leader_name">
          <el-input v-model="form.leader_name" placeholder="请输入组长姓名" maxlength="20" />
        </el-form-item>
        <el-alert
          v-if="form.subject && form.subject_en"
          :title="'账号：' + form.subject_en.toLowerCase()"
          description="初始密码为 123456，首次登录需修改密码"
          type="info"
          show-icon
          :closable="false"
        />
        <el-alert
          v-if="availableSubjects.length === 0"
          title="暂无可分配的学科"
          description="所有学科均已分配组长"
          type="warning"
          show-icon
          :closable="false"
        />
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" :disabled="!form.subject || availableSubjects.length === 0" @click="handleAdd">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  getSubjectLeaderList,
  createSubjectLeader,
  deleteSubjectLeader,
  getAvailableSubjects,
  type SubjectLeaderInfo,
  type AvailableSubject,
} from '@/api/subjectLeader'

const loading = ref(false)
const submitting = ref(false)
const loadingSubjects = ref(false)
const leaders = ref<SubjectLeaderInfo[]>([])
const availableSubjects = ref<AvailableSubject[]>([])
const showAddDialog = ref(false)
const formRef = ref<FormInstance>()

const form = ref({ subject: '', subject_en: '', leader_name: '' })

const rules: FormRules = {
  subject: [{ required: true, message: '请选择学科', trigger: 'change' }],
  leader_name: [
    { required: true, message: '请输入组长姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度为 2-20 个字符', trigger: 'blur' },
  ],
}

function onSubjectChange(subject: string) {
  const s = availableSubjects.value.find((x) => x.subject === subject)
  if (s) form.value.subject_en = s.subject_en
}

async function fetchLeaders() {
  loading.value = true
  try {
    const res = await getSubjectLeaderList()
    if (res?.data) leaders.value = res.data as unknown as SubjectLeaderInfo[]
  } catch (e) {
    console.error('获取学科组长列表失败:', e)
    ElMessage.error('获取学科组长列表失败')
  } finally {
    loading.value = false
  }
}

async function handleOpenAdd() {
  loadingSubjects.value = true
  try {
    const res = await getAvailableSubjects()
    const rawData = res?.data
    availableSubjects.value = Array.isArray(rawData) ? rawData : []
    form.value = { subject: '', subject_en: '', leader_name: '' }
    if (availableSubjects.value.length > 0) {
      const first = availableSubjects.value[0]
      form.value.subject = first.subject
      form.value.subject_en = first.subject_en
    }
    showAddDialog.value = availableSubjects.value.length > 0
    if (availableSubjects.value.length === 0) ElMessage.warning('暂无可分配的学科')
  } catch (e) {
    console.error('获取可分配学科失败:', e)
    ElMessage.error('获取可分配学科失败')
  } finally {
    loadingSubjects.value = false
  }
}

async function handleAdd() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const res = await createSubjectLeader({ subject: form.value.subject, leader_name: form.value.leader_name })
    ElMessage.success(res?.message || '添加成功')
    showAddDialog.value = false
    await fetchLeaders()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '添加失败')
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row: SubjectLeaderInfo) {
  try {
    await deleteSubjectLeader(row.id)
    ElMessage.success('删除成功')
    await fetchLeaders()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

onMounted(() => { fetchLeaders() })
</script>

<style lang="scss" scoped>
.subject-leader-management {
  animation: fadeIn 0.3s ease;
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    .page-title { margin: 0; font-size: 22px; font-weight: 700; }
  }
}
</style>
