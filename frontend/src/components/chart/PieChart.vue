<template>
  <div class="pie-chart">
    <div class="chart-header" v-if="title">
      <h4 class="chart-title">{{ title }}</h4>
    </div>
    <div ref="chartRef" class="chart-container" :style="{ height: height + 'px' }"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

/** 饼图数据项 */
interface PieDataItem {
  /** 名称 */
  name: string
  /** 数值 */
  value: number
  /** 颜色（可选） */
  color?: string
}

/** 饼图组件 Props */
interface PieChartProps {
  /** 图表标题 */
  title?: string
  /** 数据 */
  data: PieDataItem[]
  /** 饼图半径 */
  radius?: string[]
  /** 是否显示标签 */
  showLabel?: boolean
  /** 是否显示图例 */
  showLegend?: boolean
  /** 图表高度 */
  height?: number
  /** 是否显示工具提示 */
  showTooltip?: boolean
  /** 是否为环形图 */
  isRing?: boolean
  /** 中心标题 */
  centerTitle?: string
  /** 中心副标题 */
  centerSubtitle?: string
}

const props = withDefaults(defineProps<PieChartProps>(), {
  title: '',
  radius: () => ['40%', '70%'],
  showLabel: true,
  showLegend: true,
  height: 300,
  showTooltip: true,
  isRing: false,
  centerTitle: '',
  centerSubtitle: '',
})

/** 默认颜色列表 */
const defaultColors = [
  '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399',
  '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16', '#F97316',
]

/** 图表引用 */
const chartRef = ref<HTMLElement>()

/** 图表实例 */
let chart: echarts.ECharts | null = null

/** 初始化图表 */
function initChart() {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)
  updateChart()
}

/** 更新图表配置 */
function updateChart() {
  if (!chart) return

  const processedData = props.data.map((item, index) => ({
    ...item,
    itemStyle: {
      color: item.color || defaultColors[index % defaultColors.length],
    },
  }))

  const option: echarts.EChartsOption = {
    tooltip: props.showTooltip ? {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)',
    } : undefined,
    legend: props.showLegend ? {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: {
        fontSize: 12,
      },
    } : undefined,
    graphic: props.centerTitle ? [
      {
        type: 'group',
        left: 'center',
        top: 'center',
        children: [
          {
            type: 'text',
            style: {
              text: props.centerTitle,
              textAlign: 'center',
              fill: '#303133',
              fontSize: 18,
              fontWeight: 'bold',
            },
            left: 'center',
            top: 'middle',
          },
          {
            type: 'text',
            style: {
              text: props.centerSubtitle,
              textAlign: 'center',
              fill: '#909399',
              fontSize: 12,
            },
            left: 'center',
            top: 'center',
            y: 25,
          },
        ],
      },
    ] : undefined,
    series: [
      {
        name: props.title || '数据',
        type: 'pie',
        radius: props.isRing ? ['50%', '70%'] : props.radius,
        center: ['40%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: props.showLabel ? {
          show: true,
          formatter: '{b}\n{d}%',
          fontSize: 12,
        } : {
          show: false,
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.2)',
          },
        },
        data: processedData,
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
  () => props.data,
  () => {
    nextTick(() => {
      updateChart()
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
.pie-chart {
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
}
</style>
