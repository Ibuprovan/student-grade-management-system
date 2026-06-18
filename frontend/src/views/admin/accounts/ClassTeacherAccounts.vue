<template>
  <div class="account-page page-container">
    <div class="page-header">
      <h1 class="page-title">班主任账号管理</h1>
      <span class="page-count">共 {{ accounts.length }} 个账号</span>
    </div>

    <div class="page-card">
      <el-table :data="accounts" border stripe style="width: 100%" v-loading="loading" :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }">
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column label="班主任姓名" min-width="100">
          <template #default="{ row }">{{ row.detail?.teacher_name ?? '-' }}</template>
        </el-table-column>
        <el-table-column label="负责班级" min-width="110">
          <template #default="{ row }">{{ row.detail?.class_name ?? '-' }}</template>
        </el-table-column>
        <el-table-column label="入学年份" min-width="90" align="center">
          <template #default="{ row }">{{ row.detail?.enrollment_year ?? '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" min-width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">{{ row.is_active ? '正常' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="需改密" min-width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.need_change_password" type="warning" size="small">是</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-popconfirm title="确定将密码重置为 123456 吗？" confirm-button-text="确定" cancel-button-text="取消" @confirm="handleReset(row)">
              <template #reference>
                <el-button type="warning" size="small" link>重置密码</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getClassTeacherAccounts, resetAccountPassword, type AccountInfo } from '@/api/account'

const loading = ref(false)
const accounts = ref<AccountInfo[]>([])

async function fetchAccounts() {
  loading.value = true
  try {
    const res = await getClassTeacherAccounts()
    if (res?.data) accounts.value = res.data as unknown as AccountInfo[]
  } catch (e) { console.error('获取班主任账号失败:', e) } finally { loading.value = false }
}

async function handleReset(row: AccountInfo) {
  try {
    const res = await resetAccountPassword(row.user_id)
    ElMessage.success(res?.message || '密码重置成功')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '重置失败')
  }
}

onMounted(() => { fetchAccounts() })
</script>

<style lang="scss" scoped>
.account-page {
  animation: fadeIn 0.3s ease;
  .page-header { display: flex; align-items: baseline; gap: 12px; margin-bottom: 20px; }
  .page-title { margin: 0; font-size: 22px; font-weight: 700; }
  .page-count { font-size: 14px; color: var(--text-color-secondary); }
}
</style>
