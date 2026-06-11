<template>
  <div class="line-chart">
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
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  GraphicComponent,
  DatasetComponent,
  TransformComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  GraphicComponent,
  DatasetComponent,
  TransformComponent,
  CanvasRenderer,
])

/** 系列数据项 */
interface SeriesItem {
  /** 系列名称 */
  name: string
  /** 数据 */
  data: number[]
  /** 颜色 */
  color?: string
}

/** 折线图组件 Props */
interface LineChartProps {
  /** 图表标题 */
  title?: string
  /** X 轴数据 */
  xData: string[]
  /** 系列数据 */
  series: SeriesItem[]
  /** X 轴标签 */
  xLabel?: string
  /** Y 轴标签 */
  yLabel?: string
  /** 是否平滑曲线 */
  smooth?: boolean
  /** 是否显示填充区域 */
  areaStyle?: boolean
  /** 图表高度 */
  height?: number
  /** 是否显示工具提示 */
  showTooltip?: boolean
  /** 是否显示图例 */
  showLegend?: boolean
  /** 是否显示网格线 */
  showGrid?: boolean
}

const props = withDefaults(defineProps<LineChartProps>(), {
  title: '',
  xLabel: '',
  yLabel: '',
  smooth: false,
  areaStyle: false,
  height: 300,
  showTooltip: true,
  showLegend: true,
  showGrid: true,
})

/** 是否为空数据 */
const isEmpty = computed(() => {
  return !props.xData || props.xData.length === 0 ||
    !props.series || props.series.length === 0 ||
    props.series.every((s: SeriesItem) => !s.data || s.data.length === 0)
})

/** 默认颜色列表 */
const defaultColors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#8B5CF6', '#EC4899']

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

/** 是否全为零数据 */
const isAllZero = computed(() => {
  return props.series.every((s: SeriesItem) => s.data && s.data.length > 0 && s.data.every((v: number) => v === 0))
})

/** 更新图表配置 */
function updateChart() {
  if (!chart || isEmpty.value) return

  const seriesData = props.series.map((item: SeriesItem, index: number) => {
    const color = item.color || defaultColors[index % defaultColors.length]
    const allZero = item.data && item.data.length > 0 && item.data.every((v: number) => v === 0)
    return {
      name: item.name,
      type: 'line' as const,
      data: item.data,
      smooth: props.smooth,
      symbol: 'circle',
      symbolSize: allZero ? 0 : 8,
      itemStyle: {
        color: color,
      },
      lineStyle: {
        width: 2,
        color: color,
        type: allZero ? 'dashed' as const : 'solid' as const,
      },
      areaStyle: props.areaStyle && !allZero ? {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          {
            offset: 0,
            color: color + '80',
          },
          {
            offset: 1,
            color: color + '10',
          },
        ]),
      } : undefined,
      emphasis: {
        focus: 'series',
      },
    }
  })

  const option: echarts.EChartsCoreOption = {
    tooltip: props.showTooltip ? {
      trigger: 'axis',
      confine: true,
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985',
        },
      },
      textStyle: {
        fontSize: 13,
      },
    } : undefined,
    legend: props.showLegend && props.series.length > 1 ? {
      data: props.series.map((item: SeriesItem) => item.name),
      top: props.title ? 30 : 10,
      textStyle: {
        fontSize: 12,
        color: '#606266',
      },
      itemGap: 16,
    } : undefined,
    grid: props.showGrid ? {
      left: 50,
      right: 30,
      bottom: 50,
      top: props.title ? (props.showLegend && props.series.length > 1 ? 80 : 60) : (props.showLegend && props.series.length > 1 ? 60 : 40),
      containLabel: true,
    } : undefined,
    graphic: isAllZero.value ? [{
      type: 'text',
      left: 'center',
      top: 'middle',
      style: {
        text: '暂无数据',
        fontSize: 14,
        fontWeight: 'normal',
        fill: '#909399',
      },
    }] : undefined,
    xAxis: {
      type: 'category',
      data: props.xData,
      name: props.xLabel,
      nameTextStyle: {
        fontSize: 12,
        color: '#606266',
        padding: [8, 0, 0, 0],
      },
      boundaryGap: false,
      axisLabel: {
        rotate: props.xData.length > 6 ? 30 : 0,
        interval: 0,
        fontSize: 12,
        color: '#606266',
      },
      axisTick: {
        show: false,
      },
      axisLine: {
        lineStyle: {
          color: '#E8EAED',
        },
      },
    },
    yAxis: {
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
    series: seriesData,
  }

  chart.setOption(option, true)
}

/** 窗口大小变化时重绘图表 */
function handleResize() {
  chart?.resize()
}

/** 监听数据变化 */
watch(
  () => [props.xData, props.series],
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
.line-chart {
  width: 100%;

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
  }

  .chart-empty {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
</style>
