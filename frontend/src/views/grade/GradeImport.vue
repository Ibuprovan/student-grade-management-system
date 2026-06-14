<template>
  <div class="grade-import page-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">批量成绩导入</h1>
      <el-button @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        <span class="btn-text">返回列表</span>
      </el-button>
    </div>

    <!-- 步骤指示器 -->
    <div class="steps-card page-card">
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="下载模板" description="获取导入模板" />
        <el-step title="上传文件" description="选择CSV文件" />
        <el-step title="数据预览" description="检查数据" />
        <el-step title="导入结果" description="查看结果" />
      </el-steps>
    </div>

    <!-- 步骤 1: 下载模板 -->
    <div v-if="currentStep === ImportStep.DOWNLOAD_TEMPLATE" class="step-card page-card">
      <div class="step-content">
        <div class="step-icon">
          <el-icon :size="48" color="var(--primary-color)"><Document /></el-icon>
        </div>
        <h3>第一步：下载导入模板</h3>
        <p class="step-desc">请先下载标准的 CSV 模板，按照模板格式填写成绩数据后再进行导入。</p>

        <div class="template-info">
          <h4>模板格式说明：</h4>
          <ul>
            <li><strong>学号：</strong>8位数字，如 20260001（必须在系统中已存在）</li>
            <li><strong>科目：</strong>语文、数学、英语、物理、化学、生物、历史、地理、政治</li>
            <li><strong>考试类型：</strong>期中、期末、月考、单元测试</li>
            <li><strong>分数：</strong>0-100，支持1位小数</li>
            <li><strong>考试日期：</strong>YYYY-MM-DD 格式，如 2026-04-15</li>
          </ul>
        </div>

        <div class="template-preview">
          <h4>模板预览：</h4>
          <el-table :data="templatePreviewData" size="small" border stripe>
            <el-table-column prop="student_id" label="学号" width="120" />
            <el-table-column prop="subject" label="科目" width="80" />
            <el-table-column prop="exam_type" label="考试类型" width="100" />
            <el-table-column prop="score" label="分数" width="80" />
            <el-table-column prop="exam_date" label="考试日期" width="120" />
          </el-table>
        </div>

        <div class="step-actions">
          <el-button type="primary" size="large" @click="downloadTemplate">
            <el-icon><Download /></el-icon>
            下载 CSV 模板
          </el-button>
          <el-button size="large" @click="currentStep = ImportStep.UPLOAD_FILE">
            跳过，直接上传
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 步骤 2: 上传文件 -->
    <div v-if="currentStep === ImportStep.UPLOAD_FILE" class="step-card page-card">
      <div class="step-content">
        <h3>第二步：上传成绩文件</h3>
        <p class="step-desc">选择已填写好的 CSV 文件进行上传，支持拖拽上传。</p>

        <div class="upload-params">
          <el-form :model="importForm" label-width="100px" :rules="formRules" ref="paramFormRef">
            <el-form-item label="考试类型" prop="exam_type">
              <el-select
                v-model="importForm.exam_type"
                placeholder="请选择考试类型"
                style="width: 100%"
              >
                <el-option
                  v-for="et in examTypeOptions"
                  :key="et"
                  :label="et"
                  :value="et"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="考试日期" prop="exam_date">
              <el-date-picker
                v-model="importForm.exam_date"
                type="date"
                placeholder="请选择考试日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-form>
        </div>

        <el-upload
          ref="uploadRef"
          class="upload-area"
          drag
          action="#"
          :auto-upload="false"
          :limit="1"
          accept=".csv"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          :on-exceed="handleExceed"
        >
          <el-icon class="el-icon--upload"><Upload /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击选择文件</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 .csv 格式文件，单次最多导入 500 条记录
            </div>
          </template>
        </el-upload>

        <div class="step-actions">
          <el-button @click="currentStep = ImportStep.DOWNLOAD_TEMPLATE">
            <el-icon><ArrowLeft /></el-icon>
            上一步
          </el-button>
          <el-button
            type="primary"
            size="large"
            :disabled="!selectedFile"
            @click="handleParseFile"
          >
            解析文件
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 步骤 3: 数据预览 -->
    <div v-if="currentStep === ImportStep.DATA_PREVIEW" class="step-card page-card">
      <div class="step-content">
        <h3>第三步：数据预览</h3>

        <div class="preview-summary">
          <el-alert
            :title="`共 ${previewData.length} 条数据，其中 ${validCount} 条有效，${invalidCount} 条有错误`"
            :type="invalidCount > 0 ? 'warning' : 'success'"
            show-icon
            :closable="false"
          />
        </div>

        <div class="preview-table">
          <el-table
            :data="previewData"
            size="small"
            border
            stripe
            max-height="400"
            :row-class-name="getPreviewRowClass"
          >
            <el-table-column type="index" label="行号" width="70" align="center" />
            <el-table-column prop="student_id" label="学号" width="120" />
            <el-table-column prop="subject" label="科目" width="80" />
            <el-table-column prop="exam_type" label="考试类型" width="100" />
            <el-table-column prop="score" label="分数" width="80" align="center" />
            <el-table-column prop="exam_date" label="考试日期" width="120" />
            <el-table-column label="状态" width="200">
              <template #default="{ row }">
                <template v-if="row.valid">
                  <el-tag type="success" size="small">
                    <el-icon><Check /></el-icon>
                    有效
                  </el-tag>
                </template>
                <template v-else>
                  <el-tooltip :content="row.error" placement="top">
                    <el-tag type="danger" size="small">
                      <el-icon><Close /></el-icon>
                      {{ row.error }}
                    </el-tag>
                  </el-tooltip>
                </template>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 导入进度条 -->
        <div v-if="importing" class="import-progress">
          <div class="progress-header">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>正在导入成绩数据...</span>
          </div>
          <el-progress
            :percentage="importProgress"
            :stroke-width="20"
            :text-inside="true"
            status="warning"
          />
          <div class="progress-info">
            <span>预计导入 {{ validCount }} 条记录</span>
            <span>{{ importProgressStatus }}</span>
          </div>
        </div>

        <div class="step-actions">
          <el-button @click="currentStep = ImportStep.UPLOAD_FILE" :disabled="importing">
            <el-icon><ArrowLeft /></el-icon>
            上一步
          </el-button>
          <el-button
            type="primary"
            size="large"
            :loading="importing"
            :disabled="validCount === 0 || importing"
            @click="handleStartImport"
          >
            <el-icon><Upload /></el-icon>
            {{ importing ? '导入中...' : `开始导入 (${validCount} 条)` }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 步骤 4: 导入结果 -->
    <div v-if="currentStep === ImportStep.IMPORT_RESULT" class="step-card page-card">
      <div class="step-content">
        <div class="result-icon">
          <el-icon
            :size="64"
            :color="importResult?.fail_count === 0 ? 'var(--success-color)' : 'var(--warning-color)'"
          >
            <CircleCheckFilled v-if="importResult?.fail_count === 0" />
            <WarningFilled v-else />
          </el-icon>
        </div>

        <h3>导入完成！</h3>

        <div class="result-stats">
          <div class="stat-item stat-success">
            <span class="stat-value">{{ importResult?.success_count || 0 }}</span>
            <span class="stat-label">成功</span>
          </div>
          <div class="stat-item stat-fail">
            <span class="stat-value">{{ importResult?.fail_count || 0 }}</span>
            <span class="stat-label">失败</span>
          </div>
          <div class="stat-item stat-total">
            <span class="stat-value">{{ importResult?.total || 0 }}</span>
            <span class="stat-label">总计</span>
          </div>
        </div>

        <!-- 失败记录 -->
        <div v-if="importResult?.failed_items && importResult.failed_items.length > 0" class="failed-list">
          <h4>失败记录：</h4>
          <el-table :data="importResult.failed_items" size="small" border stripe max-height="200">
            <el-table-column type="index" label="序号" width="70" align="center" />
            <el-table-column prop="student_id" label="学号" width="120" />
            <el-table-column prop="error" label="失败原因" />
          </el-table>
        </div>

        <div class="step-actions">
          <el-button
            v-if="importResult?.fail_count && importResult.fail_count > 0"
            type="warning"
            @click="handleDownloadFailed"
          >
            <el-icon><Download /></el-icon>
            下载失败记录
          </el-button>
          <el-button type="primary" @click="goBack">
            <el-icon><List /></el-icon>
            返回列表
          </el-button>
          <el-button @click="handleContinueImport">
            <el-icon><Plus /></el-icon>
            继续导入
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useGradeImport } from '@/composables/useGrade'
import { ImportStep } from '@/types/grade'
import type { ImportPreviewItem, BatchImportResponse } from '@/types/grade'
import type { UploadInstance, UploadFile, UploadRawFile, FormRules } from 'element-plus'
import { ElForm } from 'element-plus'
import { ElMessage } from 'element-plus'
import { testImport } from '@/api/grade'

const {
  examTypeOptions,
  parseCSV,
  downloadTemplate,
  downloadFailedRecords,
  goBack,
  importGrades,
} = useGradeImport()

/** 当前步骤 */
const currentStep = ref(ImportStep.DOWNLOAD_TEMPLATE)

/** 上传组件引用 */
const uploadRef = ref<UploadInstance>()

/** 参数表单引用 */
const paramFormRef = ref<InstanceType<typeof ElForm>>()

/** 选中的文件 */
const selectedFile = ref<File | null>(null)

/** 导入中状态 */
const importing = ref(false)

/** 导入进度百分比 */
const importProgress = ref(0)

/** 进度状态文本 */
const importProgressStatus = ref('准备中...')

/** 进度定时器 */
let progressTimer: ReturnType<typeof setInterval> | null = null

/** 预览数据 */
const previewData = ref<ImportPreviewItem[]>([])

/** 导入结果 */
const importResult = ref<BatchImportResponse | null>(null)

/** 导入表单 */
const importForm = reactive({
  exam_type: '',
  exam_date: '',
})

/** 表单验证规则 */
const formRules: FormRules = {
  exam_type: [{ required: true, message: '请选择考试类型', trigger: 'change' }],
  exam_date: [{ required: true, message: '请选择考试日期', trigger: 'change' }],
}

/** 模板预览数据 */
const templatePreviewData = [
  { student_id: '20260001', subject: '数学', exam_type: '期中', score: '95.0', exam_date: '2026-04-15' },
  { student_id: '20260001', subject: '语文', exam_type: '期中', score: '88.5', exam_date: '2026-04-15' },
  { student_id: '20260002', subject: '数学', exam_type: '期中', score: '92.0', exam_date: '2026-04-15' },
]

/** 有效数据数量 */
const validCount = computed(() => previewData.value.filter((item) => item.valid).length)

/** 无效数据数量 */
const invalidCount = computed(() => previewData.value.filter((item) => !item.valid).length)

/** 文件变化 */
function handleFileChange(file: UploadFile) {
  selectedFile.value = file.raw || null
}

/** 文件移除 */
function handleFileRemove() {
  selectedFile.value = null
}

/** 超出限制 */
function handleExceed() {
  ElMessage.warning('只能上传一个文件，请先删除已选文件')
}

/** 解析文件 */
async function handleParseFile() {
  if (!selectedFile.value) return

  // 验证参数表单
  if (!paramFormRef.value) return
  const valid = await paramFormRef.value.validate().catch(() => false)
  if (!valid) return

  try {
    previewData.value = await parseCSV(selectedFile.value)
    currentStep.value = ImportStep.DATA_PREVIEW
  } catch (error) {
    ElMessage.error((error as Error).message || '文件解析失败')
  }
}

/** 获取预览行样式 */
function getPreviewRowClass({ row }: { row: ImportPreviewItem }) {
  return row.valid ? '' : 'invalid-row'
}

/** 开始导入 */
async function handleStartImport() {
  if (!selectedFile.value) return

  // 验证表单
  if (!importForm.exam_type) {
    ElMessage.warning('请选择考试类型')
    return
  }
  if (!importForm.exam_date) {
    ElMessage.warning('请选择考试日期')
    return
  }

  importing.value = true
  importProgress.value = 0
  importProgressStatus.value = '正在上传文件...'

  // 启动进度模拟
  progressTimer = setInterval(() => {
    if (importProgress.value < 90) {
      // 前 30% 快速增长（文件上传阶段）
      if (importProgress.value < 30) {
        importProgress.value += 2
        importProgressStatus.value = '正在上传文件...'
      }
      // 30%-60% 中速增长（服务端处理阶段）
      else if (importProgress.value < 60) {
        importProgress.value += 1
        importProgressStatus.value = '服务端处理中...'
      }
      // 60%-90% 慢速增长（写入数据库阶段）
      else {
        importProgress.value += 0.5
        importProgressStatus.value = '正在写入数据库...'
      }
    }
  }, 100)

  try {
    // 先测试接口
    console.log('测试导入接口...')
    const testResult = await testImport(
      selectedFile.value,
      importForm.exam_type,
      importForm.exam_date,
    )
    console.log('测试结果:', testResult)
    
    // 正式导入
    const result = await importGrades(
      selectedFile.value,
      importForm.exam_type,
      importForm.exam_date,
    )
    // 完成时设置为 100%
    importProgress.value = 100
    importProgressStatus.value = '导入完成！'

    // 短暂延迟后显示结果
    await new Promise(resolve => setTimeout(resolve, 500))
    importResult.value = result
    currentStep.value = ImportStep.IMPORT_RESULT
  } catch (error: any) {
    console.error('导入失败:', error)
    // 显示后端返回的详细错误信息
    const errorMsg = error?.response?.data?.error?.message || error?.message || '导入失败，请稍后重试'
    importProgressStatus.value = '导入失败'
    ElMessage.error(errorMsg)
  } finally {
    if (progressTimer) {
      clearInterval(progressTimer)
      progressTimer = null
    }
    importing.value = false
  }
}

/** 下载失败记录 */
function handleDownloadFailed() {
  if (!importResult.value?.failed_items) return
  downloadFailedRecords(importResult.value.failed_items)
}

/** 继续导入 */
function handleContinueImport() {
  currentStep.value = ImportStep.DOWNLOAD_TEMPLATE
  selectedFile.value = null
  previewData.value = []
  importResult.value = null
  importProgress.value = 0
  importProgressStatus.value = '准备中...'
  uploadRef.value?.clearFiles()
}
</script>

<style lang="scss" scoped>
.grade-import {
  animation: fadeIn 0.3s ease;

  .steps-card {
    margin-bottom: 16px;
  }

  .step-card {
    .step-content {
      max-width: 800px;
      margin: 0 auto;
      text-align: center;
    }

    .step-icon {
      margin-bottom: 16px;
    }

    h3 {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-color);
      margin-bottom: 8px;
    }

    .step-desc {
      color: var(--text-color-secondary);
      margin-bottom: 24px;
    }
  }

  .template-info {
    text-align: left;
    background: var(--bg-color);
    border-radius: var(--border-radius-lg);
    padding: 20px 24px;
    margin-bottom: 20px;

    h4 {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-color);
      margin-bottom: 12px;
    }

    ul {
      padding-left: 20px;

      li {
        font-size: 13px;
        color: var(--text-color-secondary);
        line-height: 2;

        strong {
          color: var(--text-color);
        }
      }
    }
  }

  .template-preview {
    text-align: left;
    margin-bottom: 24px;

    h4 {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-color);
      margin-bottom: 12px;
    }
  }

  .upload-params {
    text-align: left;
    background: var(--bg-color);
    border-radius: var(--border-radius-lg);
    padding: 24px;
    margin-bottom: 24px;

    :deep(.el-input__wrapper) {
      border-radius: var(--border-radius-md);
    }
  }

  .upload-area {
    max-width: 500px;
    margin: 0 auto;
  }

  .preview-summary {
    margin-bottom: 16px;
  }

  .preview-table {
    text-align: left;
    margin-bottom: 24px;

    :deep(.invalid-row) {
      background-color: var(--danger-light) !important;
    }
  }

  .import-progress {
    margin: 24px 0;
    padding: 24px;
    background: var(--bg-color);
    border-radius: var(--border-radius-lg);

    .progress-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 16px;
      font-size: 15px;
      font-weight: 600;
      color: var(--text-color);

      .is-loading {
        color: var(--primary-color);
      }
    }

    .progress-info {
      display: flex;
      justify-content: space-between;
      margin-top: 12px;
      font-size: 13px;
      color: var(--text-color-secondary);
    }
  }

  .result-icon {
    margin-bottom: 16px;
  }

  .result-stats {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin: 24px 0;

    .stat-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 16px 24px;
      background: var(--bg-color);
      border-radius: var(--border-radius-lg);
      min-width: 100px;

      .stat-value {
        font-size: 36px;
        font-weight: 700;
      }

      .stat-label {
        font-size: 13px;
        color: var(--text-color-secondary);
        margin-top: 4px;
        font-weight: 500;
      }
    }

    .stat-success .stat-value {
      color: var(--success-color);
    }

    .stat-fail .stat-value {
      color: var(--danger-color);
    }

    .stat-total .stat-value {
      color: var(--primary-color);
    }
  }

  .failed-list {
    text-align: left;
    margin-bottom: 24px;

    h4 {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-color);
      margin-bottom: 12px;
    }
  }

  .step-actions {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin-top: 24px;
  }
}

/* 响应式布局 */
@media (max-width: 768px) {
  .grade-import {
    .page-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }

    .step-card {
      .step-content {
        padding: 0 8px;
      }
    }

    .result-stats {
      gap: 16px;

      .stat-item {
        padding: 12px 16px;
        min-width: 80px;

        .stat-value {
          font-size: 28px;
        }
      }
    }

    .step-actions {
      flex-direction: column;
      align-items: stretch;
    }
  }
}

@media (max-width: 480px) {
  .grade-import {
    .btn-text {
      display: none;
    }
  }
}
</style>
