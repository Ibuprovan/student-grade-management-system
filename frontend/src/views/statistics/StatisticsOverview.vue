<template>
  <div class="statistics-overview page-container">
    <div class="page-header">
      <h1 class="page-title">统计概览</h1>
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
        style="width: 160px"
      >
        <el-option
          v-for="cls in classOptions"
          :key="cls"
          :label="cls"
          :value="cls"
        />
      </el-select>
      <el-select
        v-model="filterForm.subject"
        placeholder="选择科目"
        clearable
        style="width: 140px"
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
        style="width: 140px"
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

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-cards">
      <el-col
        v-for="(card, index) in statCards"
        :key="index"
        :xs="12"
        :sm="8"
        :md="4"
      >
        <div class="stat-card" :style="{ borderLeft: `4px solid ${card.color}` }">
          <div class="stat-card__icon" :style="{ color: card.color }">
            <el-icon :size="24">
              <component :is="card.icon" />
            </el-icon>
          </div>
          <div class="stat-card__content">
            <div class="stat-card__value">{{ card.format(card.value) }}</div>
            <div class="stat-card__label">{{ card.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="16" class="chart-section">
      <!-- 分数分布柱状图 -->
      <el-col :xs="24" :md="12">
        <div class="page-card">
          <BarChart
            title="分数分布"
            :xData="scoreDistributionData.xData"
            :yData="scoreDistributionData.yData"
            xLabel="分数段"
            yLabel="人数"
            color="#409EFF"
            :showValue="true"
            :height="300"
          />
        </div>
      </el-col>

      <!-- 成绩趋势折线图 -->
      <el-col :xs="24" :md="12">
        <div class="page-card">
          <LineChart
            title="成绩趋势"
            :xData="examTrendData.xData"
            :series="examTrendData.series"
            xLabel="考试类型"
            yLabel="分数"
            :smooth="true"
            :areaStyle="true"
            :height="300"
          />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-section">
      <!-- 科目占比饼图 -->
      <el-col :xs="24" :md="12">
        <div class="page-card">
          <PieChart
            title="科目平均分占比"
            :data="subjectPieData"
            :isRing="true"
            centerTitle="科目分布"
            :height="300"
          />
        </div>
      </el-col>

      <!-- 能力雷达图 -->
      <el-col :xs="24" :md="12">
        <div class="page-card">
          <RadarChart
            title="能力雷达图"
            :indicators="radarData.indicators"
            :series="radarData.series"
            :height="300"
          />
        </div>
      </el-col>
    </el-row>

    <!-- 排名表格 -->
    <div class="page-card">
      <div class="card-header">
        <h3 class="section-title">成绩排名（前10名）</h3>
      </div>
      <el-table
        :data="top10Rankings"
        border
        stripe
        :header-cell-style="{ background: 'var(--bg-color)', color: 'var(--text-color)' }"
      >
        <el-table-column type="index" label="排名" width="80" align="center">
          <template #default="{ $index }">
            <div class="rank-cell">
              <span
                v-if="$index < 3"
                class="rank-badge"
                :class="`rank-${$index + 1}`"
              >
                {{ $index + 1 }}
              </span>
              <span v-else>{{ $index + 1 }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="student_id" label="学号" width="120" align="center" />
        <el-table-column prop="student_name" label="姓名" width="120" align="center" />
        <el-table-column prop="score" label="分数" width="100" align="center">
          <template #default="{ row }">
            <span :style="{ color: getScoreColor(row.score), fontWeight: 'bold' }">
              {{ formatScore(row.score) }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Download, Search, RefreshRight } from '@element-plus/icons-vue'
import { useStatisticsOverview } from '@/composables/useStatistics'
import { formatScore, getScoreColor } from '@/utils/format'
import BarChart from '@/components/chart/BarChart.vue'
import LineChart from '@/components/chart/LineChart.vue'
import PieChart from '@/components/chart/PieChart.vue'
import RadarChart from '@/components/chart/RadarChart.vue'

const {
  filterForm,
  subjectOptions,
  examTypeOptions,
  classOptions,
  rankings,
  loading,
  statCards,
  scoreDistributionData,
  examTrendData,
  subjectPieData,
  radarData,
  handleSearch,
  handleReset,
  handleExport,
} = useStatisticsOverview()

/** 前10名排名数据 */
const top10Rankings = computed(() => rankings.value.slice(0, 10))
</script>

<style lang="scss" scoped>
.statistics-overview {
  animation: fadeIn 0.3s ease;

  .stat-cards {
    margin-bottom: 16px;
  }

  .stat-card {
    display: flex;
    align-items: center;
    padding: 20px;
    background: var(--surface-color);
    border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-color-light);
    box-shadow: var(--shadow-xs);
    margin-bottom: 16px;
    transition: all 0.25s ease;

    &:hover {
      box-shadow: var(--shadow-sm);
      transform: translateY(-2px);
    }

    &__icon {
      width: 48px;
      height: 48px;
      border-radius: 14px;
      background: var(--primary-light);
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
      color: var(--text-color);
      line-height: 1.2;
      letter-spacing: -0.02em;
    }

    &__label {
      font-size: 13px;
      color: var(--text-color-secondary);
      margin-top: 4px;
      font-weight: 500;
    }
  }

  .chart-section {
    margin-bottom: 16px;
  }

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-color);
    margin: 0;
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
  }

  .rank-cell {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .rank-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 700;
    color: #fff;

    &.rank-1 {
      background: linear-gradient(135deg, #ffd700, #ffed4e);
      color: #b8860b;
    }

    &.rank-2 {
      background: linear-gradient(135deg, #c0c0c0, #e8e8e8);
      color: #696969;
    }

    &.rank-3 {
      background: linear-gradient(135deg, #cd7f32, #daa520);
      color: #8b4513;
    }
  }
}

@media (max-width: 768px) {
  .statistics-overview {
    .stat-card {
      padding: 16px;

      &__value {
        font-size: 20px;
      }

      &__icon {
        width: 40px;
        height: 40px;
        margin-right: 12px;
      }
    }
  }
}
</style>
