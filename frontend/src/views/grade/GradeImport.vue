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
    <div v-if="currentStep === 0" class="step-card page-card">
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
            <li><strong>姓名：</strong>学生姓名（用于校验，非必填但建议填写）</li>
            <li><strong>总分：</strong>该学生本次考试的总分（必填）</li>
            <li><strong>各科成绩：</strong>语文、数学、英语、物理、化学、生物、历史、地理、政治（0-100，留空表示未考试）</li>
            <li><strong>考试类型：</strong>期中、期末、月考、单元测试</li>
            <li><strong>考试日期：</strong>YYYY-MM-DD 格式，如 2026-04-15</li>
          </ul>
        </div>

        <div class="template-preview">
          <h4>模板预览：</h4>
          <el-table :data="templatePreviewData" size="small" border stripe>
            <el-table-column prop="student_id" label="学号" width="100" />
            <el-table-column prop="name" label="姓名" width="80" />
            <el-table-column prop="总分" label="总分" width="80" align="center" />
            <el-table-column prop="语文" label="语文" width="70" align="center" />
            <el-table-column prop="数学" label="数学" width="70" align="center" />
            <el-table-column prop="英语" label="英语" width="70" align="center" />
            <el-table-column prop="物理" label="物理" width="70" align="center" />
            <el-table-column prop="化学" label="化学" width="70" align="center" />
            <el-table-column prop="生物" label="生物" width="70" align="center" />
            <el-table-column prop="历史" label="历史" width="70" align="center" />
            <el-table-column prop="地理" label="地理" width="70" align="center" />
            <el-table-column prop="政治" label="政治" width="70" align="center" />
            <el-table-column prop="exam_type" label="考试类型" width="90" />
            <el-table-column prop="exam_date" label="考试日期" width="110" />
          </el-table>
        </div>

        <div class="step-actions">
          <el-button type="primary" size="large" @click="downloadTemplate">
            <el-icon><Download /></el-icon>
            下载 CSV 模板
          </el-button>
          <el-button size="large" @click="currentStep = 1">
            跳过，直接上传
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 步骤 2: 上传文件 -->
    <div v-if="currentStep === 1" class="step-card page-card">
      <div class="step-content">
        <h3>第二步：上传成绩文件</h3>
        <p class="step-desc">选择已填写好的 CSV 文件进行上传，支持拖拽上传。</p>

        <div class="upload-params">
          <el-form :model="importForm" label-width="100px" :rules="formRules" ref="paramFormRef">
            <el-form-item label="考试类型" prop="exam_type">
              <el-select v-model="importForm.exam_type" placeholder="请选择考试类型" style="width: 100%">
                <el-option v-for="et in examTypeOptions" :key="et" :label="et" :value="et" />
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
          <el-button @click="currentStep = 0">
            <el-icon><ArrowLeft /></el-icon>
            上一步
          </el-button>
          <el-button type="primary" size="large" :disabled="!selectedFile" @click="handleParseFile">
            解析文件
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 步骤 3: 数据预览 -->
    <div v-if="currentStep === 2" class="step-card page-card">
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
            <el-table-column type="index" label="行号" width="60" align="center" />
            <el-table-column prop="student_id" label="学号" width="100" />
            <el-table-column prop="name" label="姓名" width="80" />
            <el-table-column v-for="sub in subjectColumns" :key="sub" :prop="sub" :label="sub" width="65" align="center" />
            <el-table-column prop="exam_type" label="考试类型" width="80" />
            <el-table-column prop="exam_date" label="考试日期" width="100" />
            <el-table-column label="状态" width="150">
              <template #default="{ row }">
                <template v-if="row.valid">
                  <el-tag type="success" size="small">有效</el-tag>
                </template>
                <template v-else>
                  <el-tooltip :content="row.error" placement="top">
                    <el-tag type="danger" size="small">{{ row.error }}</el-tag>
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
          <el-progress :percentage="importProgress" :stroke-width="20" :text-inside="true" status="warning" />
          <div class="progress-info">
            <span>预计导入 {{ validCount }} 条记录</span>
            <span>{{ importProgressStatus }}</span>
          </div>
        </div>

        <div class="step-actions">
          <el-button @click="currentStep = 1" :disabled="importing">
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
    <div v-if="currentStep === 3" class="step-card page-card">
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
            <span class="stat-value">{{ importResult?.total_rows || 0 }}</span>
            <span class="stat-label">总计</span>
          </div>
        </div>

        <div class="step-actions">
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
import { batchCreateGrades } from '@/api/grade'
import { SUBJECTS, EXAM_TYPES } from '@/types/grade'
import type { ExamType } from '@/types/grade'
import type { UploadInstance, UploadFile, FormRules } from 'element-plus'
import { ElForm, ElMessage } from 'element-plus'

/** 科目列表 */
const subjectColumns = SUBJECTS

/** 考试类型选项 */
const examTypeOptions = EXAM_TYPES

/** 当前步骤 */
const currentStep = ref(0)

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

/** 预览数据 */
const previewData = ref<any[]>([])

/** 导入结果 */
const importResult = ref<any>(null)

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
  { student_id: '20260001', name: '张三', 总分: 756, 语文: 88, 数学: 95, 英语: 82, 物理: 90, 化学: 85, 生物: 78, 历史: 92, 地理: 80, 政治: 86, exam_type: '期中', exam_date: '2026-04-15' },
  { student_id: '20260002', name: '李四', 总分: 698, 语文: 76, 数学: 88, 英语: 90, 物理: 72, 化学: 80, 生物: 85, 历史: 78, 地理: 88, 政治: 92, exam_type: '期中', exam_date: '2026-04-15' },
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
    const text = await selectedFile.value.text()
    const lines = text.split('\n').filter((line) => line.trim())

    if (lines.length < 2) {
      ElMessage.error('文件内容为空或格式不正确')
      return
    }

    // 解析表头
    const headers = lines[0].split(',').map((h) => h.trim().replace(/^\ufeff/, ''))

    // 解析数据
    const data: any[] = []
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map((v) => v.trim())
      const row: any = { _row: i + 1 }

      headers.forEach((header, idx) => {
        row[header] = values[idx] || ''
      })

      // 验证
      const errors: string[] = []
      if (!row['学号'] || row['学号'].length !== 8) {
        errors.push('学号格式错误')
      }

      // 解析总分
      const totalScore = parseFloat(row['总分'])
      if (isNaN(totalScore) || totalScore < 0) {
        errors.push('总分无效')
      } else {
        row['总分'] = totalScore
      }

      // 解析各科成绩
      let hasScore = false
      for (const sub of SUBJECTS) {
        const val = row[sub]
        if (val && val !== '') {
          const score = parseFloat(val)
          if (isNaN(score) || score < 0 || score > 100) {
            errors.push(`${sub}分数无效`)
          } else {
            row[sub] = score
            hasScore = true
          }
        } else {
          row[sub] = undefined
        }
      }

      if (!hasScore) {
        errors.push('至少需要一个科目成绩')
      }

      // 使用表单中的考试类型和日期（优先），否则使用CSV中的值
      row.exam_type = importForm.exam_type || row['考试类型'] || ''
      row.exam_date = importForm.exam_date || row['考试日期'] || ''

      if (!row.exam_type) errors.push('缺少考试类型')
      if (!row.exam_date) errors.push('缺少考试日期')

      row.valid = errors.length === 0
      row.error = errors.join('；')
      data.push(row)
    }

    previewData.value = data
    currentStep.value = 2
  } catch (error) {
    ElMessage.error((error as Error).message || '文件解析失败')
  }
}

/** 获取预览行样式 */
function getPreviewRowClass({ row }: { row: any }) {
  return row.valid ? '' : 'invalid-row'
}

/** 开始导入 */
async function handleStartImport() {
  if (!selectedFile.value) return

  importing.value = true
  importProgress.value = 0

  try {
    // 将预览数据转换为批量录入格式
    const allGrades: any[] = []
    const validRows = previewData.value.filter((r) => r.valid)

    for (const row of validRows) {
      const totalScore = row['总分']
      for (const sub of SUBJECTS) {
        const score = row[sub]
        if (score !== undefined && score !== null && !isNaN(score)) {
          allGrades.push({
            student_id: row['学号'],
            subject: sub,
            score: score,
            total_score: totalScore,
            exam_type: row.exam_type,
            exam_date: row.exam_date,
          })
        }
      }
    }

    importProgress.value = 30

    // 按考试类型和日期分组提交
    const groups = new Map<string, any[]>()
    for (const g of allGrades) {
      const key = `${g.exam_type}_${g.exam_date}`
      if (!groups.has(key)) groups.set(key, [])
      groups.get(key)!.push(g)
    }

    let totalSuccess = 0
    let totalFail = 0
    const groupCount = groups.size
    let groupIdx = 0

    for (const [key, grades] of groups) {
      const [examType, examDate] = key.split('_')
      try {
        await batchCreateGrades({
          subject: grades[0].subject,
          exam_type: examType as ExamType,
          exam_date: examDate,
          grades: grades.map((g) => ({ student_id: g.student_id, score: g.score })),
        })
        totalSuccess += grades.length
      } catch {
        totalFail += grades.length
      }
      groupIdx++
      importProgress.value = 30 + Math.round((groupIdx / groupCount) * 65)
    }

    importProgress.value = 100
    importResult.value = {
      total_rows: allGrades.length,
      success_count: totalSuccess,
      fail_count: totalFail,
      failed_items: [],
    }
    currentStep.value = 3
  } catch (error: any) {
    ElMessage.error(error?.message || '导入失败')
  } finally {
    importing.value = false
  }
}

/** 下载模板 */
function downloadTemplate() {
  const headers = ['学号', '姓名', '总分', ...SUBJECTS, '考试类型', '考试日期']
  const rows = templatePreviewData.map((row) =>
    headers.map((h) => (row as any)[h] ?? '').join(',')
  )
  const csv = '\ufeff' + headers.join(',') + '\n' + rows.join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = '成绩导入模板.csv'
  link.click()
  URL.revokeObjectURL(link.href)
}

/** 继续导入 */
function handleContinueImport() {
  currentStep.value = 0
  selectedFile.value = null
  previewData.value = []
  importResult.value = null
  importProgress.value = 0
  uploadRef.value?.clearFiles()
}

/** 返回列表 */
function goBack() {
  window.history.back()
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
      max-width: 1100px;
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
    overflow-x: auto;

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
    overflow-x: auto;

    :deep(.invalid-row) {
      background-color: rgba(245, 108, 108, 0.1) !important;
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

    .stat-success .stat-value { color: var(--success-color); }
    .stat-fail .stat-value { color: var(--danger-color); }
    .stat-total .stat-value { color: var(--primary-color); }
  }

  .step-actions {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin-top: 24px;
  }
}

@media (max-width: 768px) {
  .grade-import {
    .page-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
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
