<template>
  <div class="subject-statistics page-container">
    <div class="page-header">
      <h1 class="page-title">科目统计</h1>
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
        v-model="filterForm.subject"
        placeholder="选择科目"
        clearable
        style="width: 160px"
      >
        <el-option
          v-for="sub in subjectOptions"
          :key="sub"
          :label="sub"
          :value="sub"
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
      <el-select
        v-model="filterForm.class_name"
        placeholder="选择班级"
        clearable
        style="width: 160px"
      >
        <el-option
          v-for="cls in classOptions"
          :key="cls"
          :label="cls"
          :value="cls"
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

    <!-- 科目概览卡片 -->
    <div v-if="selectedSubjectStats" class="page-card subject-overview">
      <el-row :gutter="24">
        <el-col :xs="12" :sm="6">
          <div class="overview-item">
            <div class="overview-item__icon">
              <el-icon :size="32"><Collection /></el-icon>
            </div>
            <div class="overview-item__content">
              <div class="overview-item__value">{{ selectedSubjectStats.subject }}</div>
              <div class="overview-item__label">科目</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="overview-item">
            <div class="overview-item__icon">
              <el-icon :size="32"><User /></el-icon>
            </div>
            <div class="overview-item__content">
              <div class="overview-item__value">{{ selectedSubjectStats.student_count }}</div>
              <div class="overview-item__label">参考人数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="overview-item">
            <div class="overview-item__icon">
              <el-icon :size="32"><TrendCharts /></el-icon>
            </div>
            <div class="overview-item__content">
              <div class="overview-item__value">{{ formatScore(selectedSubjectStats.average_score) }}</div>
              <div class="overview-item__label">平均分</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="overview-item">
            <div class="overview-item__icon">
              <el-icon :size="32"><CircleCheck /></el-icon>
            </div>
            <div class="overview-item__content">
              <div class="overview-item__value">{{ formatPercent(selectedSubjectStats.pass_rate) }}</div>
              <div class="overview-item__label">及格率</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 科目统计表格 -->
    <div class="page-card">
      <h3 class="section-title">科目统计信息</h3>
      <el-table
        :data="subjectStats"
        border
        stripe
        :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }"
        @row-click="handleRowClick"
        highlight-current-row
        empty-text="暂无科目统计数据"
      >
        <el-table-column prop="subject" label="科目" width="100" />
        <el-table-column prop="student_count" label="参考人数" width="100" align="center" />
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
            {{ formatPercent(row.pass_rate) }}
          </template>
        </el-table-column>
        <el-table-column label="优秀率" width="100" align="center">
          <template #default="{ row }">
            {{ formatPercent(row.excellent_rate) }}
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 图表区域 -->
    <el-row :gutter="16">
      <!-- 科目平均分对比 -->
      <el-col :xs="24" :md="12">
        <div class="page-card">
          <BarChart
            v-if="subjectComparisonData.xData.length > 0"
            title="各科目平均分对比"
            :xData="subjectComparisonData.xData"
            :yData="subjectComparisonData.yData"
            xLabel="科目"
            yLabel="平均分"
            color="#67C23A"
            :showValue="true"
            :height="350"
          />
          <div v-else class="chart-empty-wrapper">
            <el-empty description="暂无科目对比数据" :image-size="80" />
          </div>
        </div>
      </el-col>

      <!-- 科目及格率/优秀率对比 -->
      <el-col :xs="24" :md="12">
        <div class="page-card">
          <LineChart
            v-if="subjectRateData.xData.length > 0"
            title="科目及格率/优秀率对比"
            :xData="subjectRateData.xData"
            :series="subjectRateData.series"
            xLabel="科目"
            yLabel="百分比(%)"
            :smooth="true"
            :showLegend="true"
            :height="350"
          />
          <div v-else class="chart-empty-wrapper">
            <el-empty description="暂无及格率/优秀率数据" :image-size="80" />
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <!-- 分数分布 -->
      <el-col :xs="24" :md="12">
        <div class="page-card">
          <BarChart
            v-if="scoreDistributionData.xData.length > 0"
            :title="selectedSubjectStats ? `${selectedSubjectStats.subject}成绩分布` : '成绩分布'"
            :xData="scoreDistributionData.xData"
            :yData="scoreDistributionData.yData"
            xLabel="分数段"
            yLabel="人数"
            color="#E6A23C"
            :showValue="true"
            :height="350"
          />
          <div v-else class="chart-empty-wrapper">
            <el-empty description="暂无分数分布数据" :image-size="80" />
          </div>
        </div>
      </el-col>

      <!-- 能力雷达图 -->
      <el-col :xs="24" :md="12">
        <div class="page-card">
          <RadarChart
            title="科目能力雷达图"
            :indicators="radarData.indicators"
            :series="radarData.series"
            :height="350"
          />
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { Download, Search, RefreshRight, Collection, User, TrendCharts, CircleCheck } from '@element-plus/icons-vue'
import { useSubjectStatistics } from '@/composables/useStatistics'
import { formatScore, formatPercent, getScoreColor } from '@/utils/format'
import type { SubjectStatistics } from '@/types/statistics'
import BarChart from '@/components/chart/BarChart.vue'
import LineChart from '@/components/chart/LineChart.vue'
import RadarChart from '@/components/chart/RadarChart.vue'

const {
  filterForm,
  subjectOptions,
  examTypeOptions,
  classOptions,
  subjectStats,
  loading,
  selectedSubjectStats,
  subjectComparisonData,
  subjectRateData,
  scoreDistributionData,
  radarData,
  handleSearch,
  handleReset,
  handleExport,
} = useSubjectStatistics()

/** 点击表格行 */
function handleRowClick(row: SubjectStatistics) {
  filterForm.value.subject = row.subject
}
</script>

<style lang="scss" scoped>
.subject-statistics {
  animation: fadeIn 0.3s ease;

  .subject-overview {
    background: linear-gradient(135deg, #1F5C55 0%, #2A9D8F 50%, #3BBFA0 100%);
    color: #fff;
    margin-bottom: 16px;
    border: none;
    box-shadow: var(--shadow-md);

    .overview-item {
      display: flex;
      align-items: center;
      padding: 16px 0;

      &__icon {
        width: 56px;
        height: 56px;
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;
        flex-shrink: 0;
      }

      &__content {
        flex: 1;
      }

      &__value {
        font-size: 24px;
        font-weight: 700;
        line-height: 1.2;
      }

      &__label {
        font-size: 13px;
        opacity: 0.8;
        margin-top: 4px;
        font-weight: 500;
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
  .subject-statistics {
    .subject-overview {
      .overview-item {
        padding: 12px 0;

        &__icon {
          width: 48px;
          height: 48px;
          margin-right: 12px;
        }

        &__value {
          font-size: 20px;
        }
      }
    }
  }
}
</style>
