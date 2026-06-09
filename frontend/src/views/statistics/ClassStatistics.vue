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

    <!-- 错误状态 -->
    <div v-if="error && queried" class="page-card">
      <div class="state-error">
        <el-icon :size="48" class="state-error__icon"><CircleCloseFilled /></el-icon>
        <h4 class="state-error__title">加载失败</h4>
        <p class="state-error__desc">{{ error }}</p>
        <el-button type="primary" @click="handleSearch">
          <el-icon><RefreshRight /></el-icon>
          重新加载
        </el-button>
      </div>
    </div>

    <!-- 加载骨架屏 -->
    <template v-else-if="loading && !queried">
      <div class="skeleton skeleton--card" style="height: 100px; margin-bottom: 16px;"></div>
      <div class="skeleton skeleton--card" style="height: 300px; margin-bottom: 16px;"></div>
      <el-row :gutter="16">
        <el-col :xs="24" :md="12">
          <div class="skeleton skeleton--chart"></div>
        </el-col>
        <el-col :xs="24" :md="12">
          <div class="skeleton skeleton--chart"></div>
        </el-col>
      </el-row>
    </template>

    <!-- 未查询空状态 -->
    <template v-else-if="!queried">
      <div class="page-card">
        <EmptyState
          :icon="School"
          icon-color="var(--primary-color)"
          title="请先选择班级和考试类型后查询"
          description="选择筛选条件并点击查询按钮，即可查看班级统计信息"
        />
      </div>
    </template>

    <!-- 正常数据展示 -->
    <template v-else>
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
          v-if="classStats.length > 0"
          :data="classStats"
          border
          stripe
          :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }"
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
        <EmptyState
          v-else
          size="small"
          :icon="School"
          title="暂无班级统计数据"
          description="当前筛选条件下无班级统计数据"
        />
      </div>

      <!-- 图表区域 -->
      <el-row :gutter="16">
        <!-- 班级平均分对比 -->
        <el-col :xs="24" :md="12">
          <div class="page-card">
            <BarChart
              v-if="classComparisonData.xData.length > 0"
              title="各班级平均分对比"
              :xData="classComparisonData.xData"
              :yData="classComparisonData.yData"
              xLabel="班级"
              yLabel="平均分"
              color="#409EFF"
              :showValue="true"
              :height="350"
            />
            <div v-else class="chart-empty-wrapper">
              <EmptyState
                size="small"
                :icon="DataLine"
                title="暂无班级对比数据"
                description="当前筛选条件下无班级对比数据"
              />
            </div>
          </div>
        </el-col>

        <!-- 班级及格率/优秀率对比 -->
        <el-col :xs="24" :md="12">
          <div class="page-card">
            <LineChart
              v-if="classPassRateData.xData.length > 0"
              title="班级及格率/优秀率对比"
              :xData="classPassRateData.xData"
              :series="classPassRateData.series"
              xLabel="班级"
              yLabel="百分比(%)"
              :smooth="true"
              :showLegend="true"
              :height="350"
            />
            <div v-else class="chart-empty-wrapper">
              <EmptyState
                size="small"
                :icon="TrendCharts"
                title="暂无及格率/优秀率数据"
                description="当前筛选条件下无率值数据"
              />
            </div>
          </div>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script setup lang="ts">
import { Download, Search, RefreshRight, School, DataLine, TrendCharts, CircleCloseFilled } from '@element-plus/icons-vue'
import { useClassStatistics } from '@/composables/useStatistics'
import { formatScore, formatPercent, getScoreColor } from '@/utils/format'
import type { ClassStatistics } from '@/types/statistics'
import BarChart from '@/components/chart/BarChart.vue'
import LineChart from '@/components/chart/LineChart.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const {
  filterForm,
  examTypeOptions,
  classOptions,
  classStats,
  loading,
  queried,
  error,
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
  animation: fadeIn 0.3s ease;

  .class-overview {
    background: linear-gradient(135deg, #1B2A3D 0%, #233B55 50%, #1F5C55 100%);
    color: #fff;
    margin-bottom: 16px;
    border: none;
    box-shadow: var(--shadow-md);

    .overview-item {
      text-align: center;
      padding: 16px 0;

      &__label {
        font-size: 13px;
        opacity: 0.8;
        margin-bottom: 8px;
        font-weight: 500;
      }

      &__value {
        font-size: 28px;
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

  .chart-empty-wrapper {
    height: 350px;
    display: flex;
    align-items: center;
    justify-content: center;
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
