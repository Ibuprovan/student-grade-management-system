<template>
  <div class="radar-chart">
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
import * as echarts from 'echarts'

/** 雷达图指标 */
interface RadarIndicator {
  /** 指标名称 */
  name: string
  /** 最大值 */
  max: number
}

/** 雷达图系列数据 */
interface RadarSeriesItem {
  /** 系列名称 */
  name: string
  /** 数据 */
  data: number[]
  /** 颜色（可选） */
  color?: string
}

/** 雷达图组件 Props */
interface RadarChartProps {
  /** 图表标题 */
  title?: string
  /** 指标定义 */
  indicators: RadarIndicator[]
  /** 系列数据 */
  series: RadarSeriesItem[]
  /** 是否显示图例 */
  showLegend?: boolean
  /** 图表高度 */
  height?: number
  /** 是否显示工具提示 */
  showTooltip?: boolean
  /** 形状（circle/polygon） */
  shape?: 'circle' | 'polygon'
}

const props = withDefaults(defineProps<RadarChartProps>(), {
  title: '',
  showLegend: true,
  height: 300,
  showTooltip: true,
  shape: 'polygon',
})

/** 默认颜色列表 */
const defaultColors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#8B5CF6']

/** 是否为空数据 */
const isEmpty = computed(() => {
  return !props.indicators || props.indicators.length === 0 ||
    !props.series || props.series.length === 0 ||
    props.series.every(s => !s.data || s.data.length === 0)
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

  const seriesData = props.series.map((item, index) => ({
    name: item.name,
    value: item.data,
    symbol: 'circle',
    symbolSize: 6,
    lineStyle: {
      width: 2,
      color: item.color || defaultColors[index % defaultColors.length],
    },
    itemStyle: {
      color: item.color || defaultColors[index % defaultColors.length],
    },
    areaStyle: {
      color: (item.color || defaultColors[index % defaultColors.length]) + '30',
    },
  }))

  const option: echarts.EChartsOption = {
    tooltip: props.showTooltip ? {
      trigger: 'item',
    } : undefined,
    legend: props.showLegend && props.series.length > 1 ? {
      data: props.series.map((item) => item.name),
      bottom: '5%',
      textStyle: {
        fontSize: 12,
      },
    } : undefined,
    radar: {
      shape: props.shape,
      indicator: props.indicators,
      center: ['50%', props.showLegend && props.series.length > 1 ? '45%' : '50%'],
      radius: '65%',
      axisName: {
        color: '#606266',
        fontSize: 12,
      },
      splitArea: {
        areaStyle: {
          color: ['#fff', '#f5f7fa', '#fff', '#f5f7fa', '#fff'],
        },
      },
      splitLine: {
        lineStyle: {
          color: '#e4e7ed',
        },
      },
      axisLine: {
        lineStyle: {
          color: '#dcdfe6',
        },
      },
    },
    series: [
      {
        type: 'radar',
        data: seriesData,
      },
    ],
  }

  chart.setOption(option, true)
}

/** 窗口大小变化时重绘图表 */
function handleResize() {
  chart?.resize()
}

/** 监听数据变化 */
watch(
  () => [props.indicators, props.series],
  () => {
    nextTick(() => {
      if (isEmpty.value) {
        // 数据变空时销毁图表
        if (chart) {
          chart.dispose()
          chart = null
        }
      } else {
        // 数据非空时初始化或更新图表
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
.radar-chart {
  width: 100%;

  .chart-header {
    margin-bottom: 12px;

    .chart-title {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-color);
      margin: 0;
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
