<template>
  <div class="bar-chart">
    <div class="chart-header" v-if="title">
      <h4 class="chart-title">{{ title }}</h4>
    </div>
    <div v-if="isEmpty" class="chart-empty" :style="{ height: height + 'px' }">
      <el-empty description="暂无数据" :image-size="80" />
    </div>
    <div v-else ref="chartRef" class="chart-container" :style="{ height: height + 'px' }"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  CanvasRenderer,
])

/** 柱状图组件 Props */
interface BarChartProps {
  /** 图表标题 */
  title?: string
  /** X 轴数据 */
  xData: string[]
  /** Y 轴数据 */
  yData: number[]
  /** X 轴标签 */
  xLabel?: string
  /** Y 轴标签 */
  yLabel?: string
  /** 柱状图颜色 */
  color?: string
  /** 是否显示数值 */
  showValue?: boolean
  /** 是否水平显示 */
  horizontal?: boolean
  /** 图表高度 */
  height?: number
  /** 是否显示工具提示 */
  showTooltip?: boolean
  /** 是否显示网格线 */
  showGrid?: boolean
}

const props = withDefaults(defineProps<BarChartProps>(), {
  title: '',
  xLabel: '',
  yLabel: '',
  color: '#409EFF',
  showValue: false,
  horizontal: false,
  height: 360,
  showTooltip: true,
  showGrid: true,
})

/** 是否为空数据 */
const isEmpty = computed(() => {
  return !props.xData || props.xData.length === 0 ||
    !props.yData || props.yData.length === 0
})

/** 图表引用 */
const chartRef = ref<HTMLElement>()

/** 图表实例 */
let chart: echarts.ECharts | null = null

/** 初始化图表 */
function initChart() {
  if (!chartRef.value || isEmpty.value) return

  chart = echarts.init(chartRef.value)
  updateChart()
}

/** 更新图表配置 */
function updateChart() {
  if (!chart || isEmpty.value) return

  const option: echarts.EChartsCoreOption = {
    tooltip: props.showTooltip ? {
      trigger: 'axis',
      confine: true,
      axisPointer: {
        type: 'shadow',
      },
      textStyle: {
        fontSize: 13,
      },
    } : undefined,
    grid: props.showGrid ? {
      left: 60,
      right: 40,
      bottom: 60,
      top: props.title ? 60 : 40,
      containLabel: true,
    } : undefined,
    xAxis: props.horizontal ? {
      type: 'value',
      name: props.xLabel,
      nameTextStyle: {
        fontSize: 12,
        color: '#606266',
        padding: [8, 0, 0, 0],
      },
      axisLabel: {
        formatter: '{value}',
        fontSize: 12,
        color: '#606266',
      },
      splitLine: {
        lineStyle: {
          color: '#F0F1F3',
        },
      },
    } : {
      type: 'category',
      data: props.xData,
      name: props.xLabel,
      nameTextStyle: {
        fontSize: 12,
        color: '#606266',
        padding: [8, 0, 0, 0],
      },
      axisLabel: {
        rotate: props.xData.length > 6 ? 30 : 0,
        interval: 0,
        fontSize: 12,
        color: '#606266',
      },
      axisTick: {
        show: false,
      },
    },
    yAxis: props.horizontal ? {
      type: 'category',
      data: props.xData,
      name: props.yLabel,
      nameTextStyle: {
        fontSize: 12,
        color: '#606266',
      },
      axisLabel: {
        fontSize: 12,
        color: '#606266',
      },
    } : {
      type: 'value',
      name: props.yLabel,
      nameTextStyle: {
        fontSize: 12,
        color: '#606266',
      },
      axisLabel: {
        formatter: '{value}',
        fontSize: 12,
        color: '#606266',
      },
      splitLine: {
        lineStyle: {
          color: '#F0F1F3',
          type: 'dashed',
        },
      },
    },
    series: [
      {
        name: props.yLabel || '数据',
        type: 'bar',
        data: props.yData,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(
            props.horizontal ? 0 : 0,
            props.horizontal ? 0 : 1,
            props.horizontal ? 1 : 0,
            0,
            [
              { offset: 0, color: props.color },
              { offset: 1, color: adjustColor(props.color, 30) },
            ]
          ),
          borderRadius: props.horizontal ? [0, 4, 4, 0] : [4, 4, 0, 0],
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(
              props.horizontal ? 0 : 0,
              props.horizontal ? 0 : 1,
              props.horizontal ? 1 : 0,
              0,
              [
                { offset: 0, color: adjustColor(props.color, -10) },
                { offset: 1, color: props.color },
              ]
            ),
          },
        },
        label: props.showValue ? {
          show: true,
          position: props.horizontal ? 'right' : 'top',
          formatter: '{c}',
          fontSize: 12,
          color: '#606266',
        } : undefined,
        barWidth: '50%',
      },
    ],
  }

  chart.setOption(option, true)
}

/** 调整颜色亮度 */
function adjustColor(color: string, amount: number): string {
  const hex = color.replace('#', '')
  const r = Math.max(0, Math.min(255, parseInt(hex.slice(0, 2), 16) + amount))
  const g = Math.max(0, Math.min(255, parseInt(hex.slice(2, 4), 16) + amount))
  const b = Math.max(0, Math.min(255, parseInt(hex.slice(4, 6), 16) + amount))
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
}

/** 窗口大小变化时重绘图表 */
function handleResize() {
  chart?.resize()
}

/** 监听数据变化 */
watch(
  () => [props.xData, props.yData],
  () => {
    nextTick(() => {
      if (isEmpty.value) {
        if (chart) {
          chart.dispose()
          chart = null
        }
      } else {
        if (!chart) {
          initChart()
        } else {
          updateChart()
        }
      }
    })
  },
  { deep: true }
)

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  chart?.dispose()
  chart = null
  window.removeEventListener('resize', handleResize)
})

/** 暴露方法供父组件调用 */
defineExpose({
  /** 获取图表实例 */
  getChart: () => chart,
  /** 手动刷新图表 */
  refresh: () => updateChart(),
  /** 导出图片 */
  exportImage: () => chart?.getDataURL({ type: 'png', pixelRatio: 2 }),
})
</script>

<style lang="scss" scoped>
.bar-chart {
  width: 100%;
  overflow: hidden;

  .chart-header {
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-color-light);

    .chart-title {
      font-size: 15px;
      font-weight: 600;
      color: var(--text-color);
      margin: 0;
      line-height: 1.4;
    }
  }

  .chart-container {
    width: 100%;
    overflow: hidden;
  }

  .chart-empty {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
</style>
