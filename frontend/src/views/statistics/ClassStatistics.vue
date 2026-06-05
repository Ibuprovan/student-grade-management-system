<template>
  <div class="class-statistics page-container">
    <div class="page-header">
      <h1 class="page-title">班级统计</h1>
      <div class="page-actions">
        <el-button type="primary" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出报告
        </el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <div class="search-bar">
      <el-select
        v-model="filterForm.class_name"
        placeholder="选择班级"
        clearable
        style="width: 200px"
      >
        <el-option
          v-for="cls in classOptions"
          :key="cls"
          :label="cls"
          :value="cls"
        />
      </el-select>
      <el-select
        v-model="filterForm.exam_type"
        placeholder="考试类型"
        clearable
        style="width: 160px"
      >
        <el-option
          v-for="type in examTypeOptions"
          :key="type"
          :label="type"
          :value="type"
        />
      </el-select>
      <el-button type="primary" @click="handleSearch" :loading="loading">
        <el-icon><Search /></el-icon>
        查询
      </el-button>
      <el-button @click="handleReset">
        <el-icon><RefreshRight /></el-icon>
        重置
      </el-button>
    </div>

    <!-- 班级概览卡片 -->
    <div v-if="selectedClassStats" class="page-card class-overview">
      <el-row :gutter="24">
        <el-col :xs="12" :sm="6">
          <div class="overview-item">
            <div class="overview-item__label">班级</div>
            <div class="overview-item__value">{{ selectedClassStats.class_name }}</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="overview-item">
            <div class="overview-item__label">学生人数</div>
            <div class="overview-item__value">{{ selectedClassStats.student_count }}</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="overview-item">
            <div class="overview-item__label">平均分</div>
            <div class="overview-item__value">{{ formatScore(selectedClassStats.average_score) }}</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="overview-item">
            <div class="overview-item__label">及格率</div>
            <div class="overview-item__value">{{ formatPercent(selectedClassStats.pass_rate) }}</div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 班级统计表格 -->
    <div class="page-card">
      <h3 class="section-title">班级统计信息</h3>
      <el-table
        :data="classStats"
        border
        stripe
        :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
        @row-click="handleRowClick"
        highlight-current-row
      >
        <el-table-column prop="class_name" label="班级" width="150" />
        <el-table-column prop="student_count" label="学生人数" width="100" align="center" />
        <el-table-column label="平均分" width="100" align="center">
          <template #default="{ row }">
            <span :style="{ color: getScoreColor(row.average_score) }">
              {{ formatScore(row.average_score) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="最高分" width="100" align="center">
          <template #default="{ row }">
            {{ formatScore(row.max_score) }}
          </template>
        </el-table-column>
        <el-table-column label="最低分" width="100" align="center">
          <template #default="{ row }">
            <span :style="{ color: row.min_score < 60 ? '#F56C6C' : '#606266' }">
              {{ formatScore(row.min_score) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="及格率" width="100" align="center">
          <template #default="{ row }">
            <el-progress
              :percentage="row.pass_rate"
              :color="getProgressColor(row.pass_rate)"
              :stroke-width="8"
              :show-text="false"
              style="width: 60px; display: inline-block; margin-right: 8px"
            />
            {{ formatPercent(row.pass_rate) }}
          </template>
        </el-table-column>
        <el-table-column label="优秀率" width="100" align="center">
          <template #default="{ row }">
            <el-progress
              :percentage="row.excellent_rate"
              :color="getProgressColor(row.excellent_rate)"
              :stroke-width="8"
              :show-text="false"
              style="width: 60px; display: inline-block; margin-right: 8px"
            />
            {{ formatPercent(row.excellent_rate) }}
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 图表区域 -->
    <el-row :gutter="16">
      <!-- 班级平均分对比 -->
      <el-col :xs="24" :md="12">
        <div class="page-card">
          <BarChart
            title="各班级平均分对比"
            :xData="classComparisonData.xData"
            :yData="classComparisonData.yData"
            xLabel="班级"
            yLabel="平均分"
            color="#409EFF"
            :showValue="true"
            :height="350"
          />
        </div>
      </el-col>

      <!-- 班级及格率/优秀率对比 -->
      <el-col :xs="24" :md="12">
        <div class="page-card">
          <LineChart
            title="班级及格率/优秀率对比"
            :xData="classPassRateData.xData"
            :series="classPassRateData.series"
            xLabel="班级"
            yLabel="百分比(%)"
            :smooth="true"
            :showLegend="true"
            :height="350"
          />
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { Download, Search, RefreshRight } from '@element-plus/icons-vue'
import { useClassStatistics } from '@/composables/useStatistics'
import { formatScore, formatPercent, getScoreColor } from '@/utils/format'
import type { ClassStatistics } from '@/types/statistics'
import BarChart from '@/components/chart/BarChart.vue'
import LineChart from '@/components/chart/LineChart.vue'

const {
  filterForm,
  examTypeOptions,
  classOptions,
  classStats,
  loading,
  selectedClassStats,
  classComparisonData,
  classPassRateData,
  handleSearch,
  handleReset,
  handleExport,
} = useClassStatistics()

/** 点击表格行 */
function handleRowClick(row: ClassStatistics) {
  filterForm.value.class_name = row.class_name
}

/** 获取进度条颜色 */
function getProgressColor(value: number): string {
  if (value >= 90) return '#67C23A'
  if (value >= 80) return '#409EFF'
  if (value >= 60) return '#E6A23C'
  return '#F56C6C'
}
</script>

<style lang="scss" scoped>
.class-statistics {
  .class-overview {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    margin-bottom: 16px;

    .overview-item {
      text-align: center;
      padding: 16px 0;

      &__label {
        font-size: 13px;
        opacity: 0.9;
        margin-bottom: 8px;
      }

      &__value {
        font-size: 24px;
        font-weight: 700;
      }
    }
  }

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-color);
    margin-bottom: 16px;
  }
}

@media (max-width: 768px) {
  .class-statistics {
    .class-overview {
      .overview-item {
        padding: 12px 0;

        &__value {
          font-size: 20px;
        }
      }
    }
  }
}
</style>
