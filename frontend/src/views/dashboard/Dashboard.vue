<template>
  <div class="dashboard">
    <div class="page-header">
      <h1 class="page-title">仪表盘</h1>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-cards">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-card--primary">
          <div class="stat-card__icon">
            <el-icon :size="40"><User /></el-icon>
          </div>
          <div class="stat-card__content">
            <div class="stat-card__value">{{ stats.totalStudents }}</div>
            <div class="stat-card__label">学生总数</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-card--success">
          <div class="stat-card__icon">
            <el-icon :size="40"><Document /></el-icon>
          </div>
          <div class="stat-card__content">
            <div class="stat-card__value">{{ stats.totalGrades }}</div>
            <div class="stat-card__label">成绩记录</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-card--warning">
          <div class="stat-card__icon">
            <el-icon :size="40"><TrendCharts /></el-icon>
          </div>
          <div class="stat-card__content">
            <div class="stat-card__value">{{ stats.averageScore }}</div>
            <div class="stat-card__label">平均分</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-card--danger">
          <div class="stat-card__icon">
            <el-icon :size="40"><DataAnalysis /></el-icon>
          </div>
          <div class="stat-card__content">
            <div class="stat-card__value">{{ stats.passRate }}</div>
            <div class="stat-card__label">及格率</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <div class="page-card">
      <h3 class="section-title">快捷操作</h3>
      <el-row :gutter="16">
        <el-col :xs="12" :sm="8" :md="6">
          <el-button class="quick-action" @click="router.push('/student/add')">
            <el-icon><UserPlus /></el-icon>
            <span>添加学生</span>
          </el-button>
        </el-col>
        <el-col :xs="12" :sm="8" :md="6">
          <el-button class="quick-action" @click="router.push('/grade/input')">
            <el-icon><Edit /></el-icon>
            <span>录入成绩</span>
          </el-button>
        </el-col>
        <el-col :xs="12" :sm="8" :md="6">
          <el-button class="quick-action" @click="router.push('/grade/import')">
            <el-icon><Upload /></el-icon>
            <span>导入成绩</span>
          </el-button>
        </el-col>
        <el-col :xs="12" :sm="8" :md="6">
          <el-button class="quick-action" @click="router.push('/statistics/overview')">
            <el-icon><DataAnalysis /></el-icon>
            <span>查看统计</span>
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 欢迎信息 -->
    <div class="page-card welcome-card">
      <h3>欢迎使用学生成绩管理系统</h3>
      <p>本系统提供学生成绩的录入、查询、统计分析等功能，帮助教师高效管理学生成绩数据。</p>
      <el-divider />
      <el-row :gutter="24">
        <el-col :span="8">
          <div class="feature-item">
            <el-icon :size="32" color="#409eff"><User /></el-icon>
            <h4>学生管理</h4>
            <p>管理学生基本信息，支持增删改查</p>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="feature-item">
            <el-icon :size="32" color="#67c23a"><Document /></el-icon>
            <h4>成绩管理</h4>
            <p>录入、导入、查询学生成绩</p>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="feature-item">
            <el-icon :size="32" color="#e6a23c"><DataAnalysis /></el-icon>
            <h4>统计分析</h4>
            <p>多维度统计分析，数据可视化</p>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

/** 统计数据（模拟数据，实际应从 API 获取） */
const stats = reactive({
  totalStudents: 128,
  totalGrades: 1024,
  averageScore: '78.5',
  passRate: '85.2%',
})
</script>

<style lang="scss" scoped>
.dashboard {
  .stat-cards {
    margin-bottom: 16px;
  }

  .stat-card {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 24px;
    background: #fff;
    border-radius: var(--border-radius-md);
    box-shadow: var(--shadow-sm);
    margin-bottom: 16px;
    transition: transform 0.3s, box-shadow 0.3s;

    &:hover {
      transform: translateY(-4px);
      box-shadow: var(--shadow-md);
    }

    &__icon {
      width: 64px;
      height: 64px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
    }

    &__content {
      flex: 1;
    }

    &__value {
      font-size: 28px;
      font-weight: 700;
      color: var(--text-color);
      line-height: 1.2;
    }

    &__label {
      font-size: 14px;
      color: var(--text-color-secondary);
      margin-top: 4px;
    }

    &--primary .stat-card__icon {
      background: linear-gradient(135deg, #409eff, #337ecc);
    }

    &--success .stat-card__icon {
      background: linear-gradient(135deg, #67c23a, #529b2e);
    }

    &--warning .stat-card__icon {
      background: linear-gradient(135deg, #e6a23c, #b88230);
    }

    &--danger .stat-card__icon {
      background: linear-gradient(135deg, #f56c6c, #c45656);
    }
  }

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-color);
    margin-bottom: 16px;
  }

  .quick-action {
    width: 100%;
    height: 80px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-bottom: 16px;

    .el-icon {
      font-size: 24px;
    }

    span {
      font-size: 14px;
    }
  }

  .welcome-card {
    h3 {
      font-size: 18px;
      color: var(--text-color);
      margin-bottom: 12px;
    }

    p {
      color: var(--text-color-secondary);
      line-height: 1.6;
    }

    .feature-item {
      text-align: center;
      padding: 16px;

      h4 {
        font-size: 16px;
        color: var(--text-color);
        margin: 12px 0 8px;
      }

      p {
        font-size: 13px;
      }
    }
  }
}
</style>
