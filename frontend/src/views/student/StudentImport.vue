<template>
  <div class="student-import page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">批量导入学生</h1>
      <div class="header-actions">
        <el-button @click="router.push('/student/list')">
          <el-icon><Back /></el-icon>
          返回列表
        </el-button>
      </div>
    </div>

    <!-- 导入步骤 -->
    <el-steps :active="currentStep" finish-status="success" class="import-steps">
      <el-step title="下载模板" description="下载导入模板并填写数据" />
      <el-step title="上传文件" description="上传填写好的Excel或CSV文件" />
      <el-step title="预览确认" description="预览数据并确认导入" />
      <el-step title="导入结果" description="查看导入结果" />
    </el-steps>

    <!-- 步骤1：下载模板 -->
    <div v-if="currentStep === 0" class="step-content">
      <el-card class="template-card">
        <template #header>
          <div class="card-header">
            <span>下载导入模板</span>
          </div>
        </template>
        
        <div class="template-info">
          <el-alert
            title="请先下载导入模板"
            description="使用标准模板可以确保数据格式正确，提高导入成功率。"
            type="info"
            show-icon
            :closable="false"
          />
          
          <div class="template-formats">
            <h4>模板格式说明：</h4>
            <ul>
              <li><strong>学号</strong>：8位数字，格式为年份+4位序号（如：20260001）</li>
              <li><strong>姓名</strong>：2-20个字符</li>
              <li><strong>性别</strong>：男 或 女</li>
              <li><strong>班级</strong>：2-20个字符（如：三年一班）</li>
              <li><strong>入学年份</strong>：2000-2100之间的整数</li>
            </ul>
          </div>
          
          <div class="template-actions">
            <el-button type="primary" @click="downloadTemplate('xlsx')">
              <el-icon><Download /></el-icon>
              下载 Excel 模板
            </el-button>
            <el-button @click="downloadTemplate('csv')">
              <el-icon><Download /></el-icon>
              下载 CSV 模板
            </el-button>
          </div>
        </div>
        
        <div class="step-actions">
          <el-button type="primary" @click="currentStep = 1">
            下一步
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 步骤2：上传文件 -->
    <div v-if="currentStep === 1" class="step-content">
      <el-card class="upload-card">
        <template #header>
          <div class="card-header">
            <span>上传导入文件</span>
          </div>
        </template>
        
        <el-upload
          ref="uploadRef"
          class="upload-area"
          drag
          :auto-upload="false"
          :limit="1"
          :on-change="handleFileChange"
          :on-exceed="handleExceed"
          :before-upload="beforeUpload"
          accept=".xlsx,.csv"
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 .xlsx 和 .csv 格式文件，文件大小不超过 10MB
            </div>
          </template>
        </el-upload>
        
        <div v-if="selectedFile" class="file-info">
          <el-descriptions title="已选文件" :column="1" border>
            <el-descriptions-item label="文件名">{{ selectedFile.name }}</el-descriptions-item>
            <el-descriptions-item label="文件大小">{{ formatFileSize(selectedFile.size) }}</el-descriptions-item>
            <el-descriptions-item label="文件类型">{{ selectedFile.name.split('.').pop()?.toUpperCase() }}</el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="step-actions">
          <el-button @click="currentStep = 0">
            <el-icon><ArrowLeft /></el-icon>
            上一步
          </el-button>
          <el-button 
            type="primary" 
            :disabled="!selectedFile"
            :loading="previewLoading"
            @click="handlePreview"
          >
            预览数据
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 步骤3：预览确认 -->
    <div v-if="currentStep === 2" class="step-content">
      <el-card class="preview-card">
        <template #header>
          <div class="card-header">
            <span>数据预览</span>
          </div>
        </template>
        
        <div v-if="previewData" class="preview-summary">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-statistic title="总行数" :value="previewData.total_rows" />
            </el-col>
            <el-col :span="8">
              <el-statistic title="有效行数" :value="previewData.valid_rows" class="statistic-success" />
            </el-col>
            <el-col :span="8">
              <el-statistic title="无效行数" :value="previewData.invalid_rows" class="statistic-danger" />
            </el-col>
          </el-row>
        </div>
        
        <!-- 预览表格 -->
        <div v-if="previewData && previewData.preview.length > 0" class="preview-table">
          <h4>数据预览（前10条）：</h4>
          <el-table :data="previewData.preview.slice(0, 10)" border stripe>
            <el-table-column prop="row" label="行号" width="70" />
            <el-table-column prop="student_id" label="学号" width="120" />
            <el-table-column prop="name" label="姓名" width="100" />
            <el-table-column prop="gender" label="性别" width="70" />
            <el-table-column prop="class_name" label="班级" width="120" />
            <el-table-column prop="enrollment_year" label="入学年份" width="100" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'valid' ? 'success' : 'danger'">
                  {{ row.status === 'valid' ? '有效' : '无效' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="errors" label="错误信息" min-width="150">
              <template #default="{ row }">
                <span v-if="row.errors" class="error-text">{{ row.errors.join('; ') }}</span>
                <span v-else class="success-text">-</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <!-- 错误汇总 -->
        <div v-if="previewData && previewData.errors.length > 0" class="error-summary">
          <el-alert
            :title="`发现 ${previewData.errors.length} 条错误`"
            type="warning"
            show-icon
            :closable="false"
          >
            <template #default>
              <div class="error-list">
                <div v-for="(error, index) in previewData.errors.slice(0, 5)" :key="index" class="error-item">
                  <span class="error-row">第{{ error.row }}行：</span>
                  <span class="error-message">{{ error.error }}</span>
                </div>
                <div v-if="previewData.errors.length > 5" class="error-more">
                  还有 {{ previewData.errors.length - 5 }} 条错误...
                </div>
              </div>
            </template>
          </el-alert>
        </div>
        
        <div class="step-actions">
          <el-button @click="currentStep = 1">
            <el-icon><ArrowLeft /></el-icon>
            上一步
          </el-button>
          <el-button 
            type="primary" 
            :disabled="!previewData || previewData.valid_rows === 0"
            :loading="importLoading"
            @click="handleImport"
          >
            确认导入
            <el-icon><Check /></el-icon>
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 步骤4：导入结果 -->
    <div v-if="currentStep === 3" class="step-content">
      <el-card class="result-card">
        <template #header>
          <div class="card-header">
            <span>导入结果</span>
          </div>
        </template>
        
        <div v-if="importResult" class="result-content">
          <div class="result-summary">
            <el-result
              :icon="importResult.fail_count === 0 ? 'success' : 'warning'"
              :title="importResult.fail_count === 0 ? '导入成功' : '导入完成（部分失败）'"
              :sub-title="`共 ${importResult.total_rows} 条记录，成功 ${importResult.success_count} 条，失败 ${importResult.fail_count} 条`"
            />
          </div>
          
          <!-- 成功统计 -->
          <div class="result-stats">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-statistic title="总记录数" :value="importResult.total_rows" />
              </el-col>
              <el-col :span="8">
                <el-statistic title="成功导入" :value="importResult.success_count" class="statistic-success" />
              </el-col>
              <el-col :span="8">
                <el-statistic title="导入失败" :value="importResult.fail_count" class="statistic-danger" />
              </el-col>
            </el-row>
          </div>
          
          <!-- 错误详情 -->
          <div v-if="importResult.errors.length > 0" class="result-errors">
            <h4>错误详情：</h4>
            <el-table :data="importResult.errors" border stripe max-height="300">
              <el-table-column prop="row" label="行号" width="70" />
              <el-table-column prop="student_id" label="学号" width="120" />
              <el-table-column prop="field" label="错误字段" width="100" />
              <el-table-column prop="error" label="错误信息" min-width="200" />
              <el-table-column prop="value" label="错误值" width="120" />
            </el-table>
            
            <div class="error-actions">
              <el-button @click="downloadErrorReport">
                <el-icon><Download /></el-icon>
                下载错误报告
              </el-button>
            </div>
          </div>
        </div>
        
        <div class="step-actions">
          <el-button @click="resetImport">
            <el-icon><RefreshLeft /></el-icon>
            重新导入
          </el-button>
          <el-button type="primary" @click="router.push('/student/list')">
            查看学生列表
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadFile, UploadInstance } from 'element-plus'
import { 
  Back, 
  Download, 
  ArrowRight, 
  ArrowLeft, 
  UploadFilled, 
  Check, 
  RefreshLeft 
} from '@element-plus/icons-vue'
import { importStudents, previewImport, downloadTemplate as downloadTemplateApi } from '@/api/import'

const router = useRouter()
const uploadRef = ref<UploadInstance>()

// 当前步骤
const currentStep = ref(0)

// 文件相关
const selectedFile = ref<File | null>(null)
const previewLoading = ref(false)
const importLoading = ref(false)

// 预览和导入结果
const previewData = ref<any>(null)
const importResult = ref<any>(null)

// 文件选择处理
const handleFileChange = (file: UploadFile) => {
  if (file.raw) {
    selectedFile.value = file.raw
  }
}

// 文件超出限制
const handleExceed = () => {
  ElMessage.warning('只能上传一个文件，请先删除已选文件')
}

// 上传前校验
const beforeUpload = (file: File) => {
  const allowedTypes = [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/csv',
    'application/csv'
  ]
  
  const allowedExtensions = ['.xlsx', '.csv']
  const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
  
  if (!allowedExtensions.includes(fileExtension)) {
    ElMessage.error('只能上传 .xlsx 或 .csv 格式的文件')
    return false
  }
  
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  
  return true
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 下载模板
const downloadTemplate = async (format: 'xlsx' | 'csv') => {
  try {
    const response = await downloadTemplateApi(format)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `student_import_template.${format}`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('模板下载成功')
  } catch (error: any) {
    ElMessage.error(error.message || '模板下载失败')
  }
}

// 预览数据
const handlePreview = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  previewLoading.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    const response = await previewImport(formData)
    previewData.value = response.data
    currentStep.value = 2
    
    if (previewData.value.invalid_rows > 0) {
      ElMessage.warning(`发现 ${previewData.value.invalid_rows} 条无效数据，请检查`)
    } else {
      ElMessage.success('数据预览成功，所有数据有效')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '数据预览失败')
  } finally {
    previewLoading.value = false
  }
}

// 确认导入
const handleImport = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要导入 ${previewData.value?.valid_rows} 条学生数据吗？`,
      '确认导入',
      {
        confirmButtonText: '确定导入',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    importLoading.value = true
    
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    const response = await importStudents(formData)
    importResult.value = response.data
    currentStep.value = 3
    
    if (importResult.value.fail_count === 0) {
      ElMessage.success(`成功导入 ${importResult.value.success_count} 条学生数据`)
    } else {
      ElMessage.warning(`导入完成：成功 ${importResult.value.success_count} 条，失败 ${importResult.value.fail_count} 条`)
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '导入失败')
    }
  } finally {
    importLoading.value = false
  }
}

// 下载错误报告
const downloadErrorReport = () => {
  if (!importResult.value || importResult.value.errors.length === 0) {
    ElMessage.warning('没有错误数据')
    return
  }
  
  // 生成 CSV 格式的错误报告
  const headers = ['行号', '学号', '错误字段', '错误信息', '错误值']
  const rows = importResult.value.errors.map((error: any) => [
    error.row,
    error.student_id || '',
    error.field || '',
    error.error,
    error.value || ''
  ])
  
  const csvContent = [
    headers.join(','),
    ...rows.map((row: string[]) => row.map(cell => `"${cell}"`).join(','))
  ].join('\n')
  
  // 添加 BOM 以支持 Excel 打开中文
  const bom = '\uFEFF'
  const blob = new Blob([bom + csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `import_errors_${new Date().toISOString().slice(0, 10)}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
  
  ElMessage.success('错误报告下载成功')
}

// 重置导入
const resetImport = () => {
  currentStep.value = 0
  selectedFile.value = null
  previewData.value = null
  importResult.value = null
  uploadRef.value?.clearFiles()
}
</script>

<style scoped>
.student-import {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.import-steps {
  margin-bottom: 32px;
}

.step-content {
  margin-top: 20px;
}

.template-card,
.upload-card,
.preview-card,
.result-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-info {
  margin-bottom: 20px;
}

.template-formats {
  margin: 20px 0;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.template-formats h4 {
  margin-top: 0;
  margin-bottom: 12px;
  color: #303133;
}

.template-formats ul {
  margin: 0;
  padding-left: 20px;
}

.template-formats li {
  margin-bottom: 8px;
  color: #606266;
}

.template-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.upload-area {
  width: 100%;
}

.file-info {
  margin-top: 20px;
}

.step-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.preview-summary {
  margin-bottom: 24px;
}

.preview-table {
  margin-top: 20px;
}

.preview-table h4 {
  margin-bottom: 12px;
  color: #303133;
}

.error-text {
  color: #f56c6c;
  font-size: 12px;
}

.success-text {
  color: #67c23a;
}

.error-summary {
  margin-top: 20px;
}

.error-list {
  max-height: 200px;
  overflow-y: auto;
}

.error-item {
  margin-bottom: 8px;
  font-size: 14px;
}

.error-row {
  font-weight: 600;
  color: #303133;
}

.error-message {
  color: #f56c6c;
}

.error-more {
  color: #909399;
  font-style: italic;
}

.result-content {
  text-align: center;
}

.result-summary {
  margin-bottom: 24px;
}

.result-stats {
  margin-bottom: 24px;
}

.result-errors {
  text-align: left;
  margin-top: 24px;
}

.result-errors h4 {
  margin-bottom: 12px;
  color: #303133;
}

.error-actions {
  margin-top: 16px;
  text-align: center;
}

.statistic-success {
  color: #67c23a;
}

.statistic-danger {
  color: #f56c6c;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
  }
  
  .template-actions {
    flex-direction: column;
  }
  
  .step-actions {
    flex-direction: column;
  }
  
  .step-actions .el-button {
    width: 100%;
  }
}
</style>
