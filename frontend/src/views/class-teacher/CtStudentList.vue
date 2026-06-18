<template>
  <div class="ct-students page-container">
    <div class="page-header">
      <h1 class="page-title">学生信息</h1>
    </div>

    <div class="page-card">
      <el-table
        :data="students"
        border
        stripe
        style="width: 100%"
        v-loading="loading"
        :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }"
      >
        <el-table-column prop="student_id" label="学号" min-width="120" />
        <el-table-column prop="name" label="姓名" min-width="100" />
        <el-table-column prop="gender" label="性别" min-width="80" align="center" />
        <el-table-column prop="class_name" label="班级" min-width="120" />
        <el-table-column prop="enrollment_year" label="入学年份" min-width="100" align="center" />
      </el-table>

      <div class="table-pagination" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          :background="true"
          @current-change="fetchStudents"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getCtStudents } from '@/api/classTeacher'

interface StudentItem {
  student_id: string
  name: string
  gender: string
  class_name: string
  enrollment_year: number
}

const loading = ref(false)
const students = ref<StudentItem[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

async function fetchStudents() {
  loading.value = true
  try {
    const res = await getCtStudents({ page: currentPage.value, page_size: pageSize.value })
    if (res?.data) {
      const d = res.data as { items: StudentItem[]; total: number }
      students.value = d.items || []
      total.value = d.total || 0
    }
  } catch (e) {
    console.error('获取学生列表失败:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStudents()
})
</script>

<style lang="scss" scoped>
.ct-students {
  animation: fadeIn 0.3s ease;

  .page-header {
    margin-bottom: 20px;
    .page-title { margin: 0; font-size: 22px; font-weight: 700; }
  }

  .table-pagination {
    display: flex;
    justify-content: flex-end;
    padding: 16px 20px;
    border-top: 1px solid var(--border-color-light);
  }
}
</style>
