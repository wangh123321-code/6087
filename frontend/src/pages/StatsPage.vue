<template>
  <div class="p-6 space-y-4">
    <h2 class="text-2xl font-bold font-heading">统计分析</h2>

    <div class="flex items-center gap-4">
      <div class="flex gap-1 bg-gray-100 rounded-btn p-1">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="px-4 py-1.5 text-sm rounded-btn transition-colors font-medium"
          :class="activeTab === tab.key ? 'bg-primary text-white shadow-sm' : 'text-gray-500 hover:text-gray-700'"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>
      <div v-if="activeTab !== 'bests' && activeTab !== 'training'" class="ml-auto">
        <PeriodSelector v-model="period" :options="periodOptions" />
      </div>
    </div>

    <div v-if="activeTab === 'distance'" class="bg-white/90 rounded-card p-5 shadow-sm border border-black/5">
      <h3 class="text-sm font-medium text-gray-500 mb-4">跑量统计</h3>
      <v-chart :option="distanceChartOption" autoresize style="height: 360px; width: 100%;" />
    </div>

    <div v-if="activeTab === 'pace'" class="bg-white/90 rounded-card p-5 shadow-sm border border-black/5">
      <h3 class="text-sm font-medium text-gray-500 mb-4">配速趋势</h3>
      <v-chart :option="paceChartOption" autoresize style="height: 360px; width: 100%;" />
    </div>

    <div v-if="activeTab === 'training'" class="space-y-4">
      <div class="bg-white/90 rounded-card p-5 shadow-sm border border-black/5">
        <h3 class="text-sm font-medium text-gray-500 mb-4">训练类型占比</h3>
        <v-chart :option="trainingTypePieOption" autoresize style="height: 360px; width: 100%;" />
      </div>
      <div class="bg-white/90 rounded-card p-5 shadow-sm border border-black/5">
        <h3 class="text-sm font-medium text-gray-500 mb-4">训练类型里程分布</h3>
        <v-chart :option="trainingTypeBarOption" autoresize style="height: 360px; width: 100%;" />
      </div>
    </div>

    <div v-if="activeTab === 'bests'" class="grid grid-cols-4 gap-4">
      <div v-for="pb in pbCards" :key="pb.label" class="bg-white/90 rounded-card p-5 shadow-sm border border-black/5">
        <div class="text-xs text-gray-400 mb-1">{{ pb.label }}</div>
        <div v-if="pb.data && pb.data.best_time != null" class="space-y-2">
          <div class="text-2xl font-bold font-heading text-primary">{{ formatDuration(pb.data.best_time) }}</div>
          <div class="text-xs text-gray-500">{{ formatDate(pb.data.date!) }}</div>
          <div class="text-xs text-gray-500">{{ formatPace(pb.data.best_pace!) }}</div>
        </div>
        <div v-else class="text-sm text-gray-400 py-4">暂无记录</div>
      </div>
    </div>

    <div class="flex gap-3">
      <button class="btn-secondary" @click="handleExport('csv')">
        <Download class="w-4 h-4 inline mr-1" />导出 CSV
      </button>
      <button class="btn-secondary" @click="handleExport('json')">
        <Download class="w-4 h-4 inline mr-1" />导出 JSON
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { Download } from 'lucide-vue-next'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import PeriodSelector from '@/components/PeriodSelector.vue'
import { useStatsStore } from '@/stores/stats'
import { formatPace, formatDuration, formatDate } from '@/utils/format'
import * as api from '@/utils/api'

use([BarChart, LineChart, PieChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer])

const statsStore = useStatsStore()
const activeTab = ref('distance')
const period = ref('monthly')

const tabs = [
  { key: 'distance', label: '跑量统计' },
  { key: 'pace', label: '配速趋势' },
  { key: 'training', label: '训练类型' },
  { key: 'bests', label: '最佳成绩' },
]

const periodOptions = [
  { label: '周', value: 'weekly' },
  { label: '月', value: 'monthly' },
  { label: '年', value: 'yearly' },
]

const currentStats = computed(() => {
  if (period.value === 'weekly') return statsStore.weeklyStats
  if (period.value === 'yearly') return statsStore.yearlyStats
  return statsStore.monthlyStats
})

const pbCards = computed(() => {
  const bests = statsStore.personalBests?.personal_bests ?? []
  return [
    { label: '5K', data: bests.find(b => b.category === '5K') ?? null },
    { label: '10K', data: bests.find(b => b.category === '10K') ?? null },
    { label: '半马', data: bests.find(b => b.category === '半马') ?? null },
    { label: '全马', data: bests.find(b => b.category === '全马') ?? null },
  ]
})

const distanceChartOption = computed(() => {
  const stats = currentStats.value
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1A1A2E',
      borderColor: '#1A1A2E',
      textStyle: { color: '#fff', fontSize: 12 },
    },
    grid: { left: 60, right: 20, top: 20, bottom: 30 },
    xAxis: {
      type: 'category',
      data: stats.map(s => s.period),
      axisLabel: { color: '#999', fontSize: 11 },
      axisLine: { lineStyle: { color: '#E5E7EB' } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#999', fontSize: 11, formatter: '{value} km' },
      splitLine: { lineStyle: { color: '#F3F4F6' } },
    },
    series: [{
      type: 'bar',
      data: stats.map(s => Number(s.distance.toFixed(1))),
      barWidth: '50%',
      itemStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#FF6B35' },
            { offset: 1, color: '#FF9A6C' }
          ]
        },
        borderRadius: [4, 4, 0, 0],
      }
    }]
  }
})

const paceChartOption = computed(() => {
  const stats = statsStore.paceTrend
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1A1A2E',
      borderColor: '#1A1A2E',
      textStyle: { color: '#fff', fontSize: 12 },
      formatter: (params: any) => {
        const p = params[0]
        return `${p.name}<br/>配速: ${formatPace(p.value)}`
      }
    },
    grid: { left: 60, right: 20, top: 20, bottom: 30 },
    xAxis: {
      type: 'category',
      data: stats.map(s => s.period),
      axisLabel: { color: '#999', fontSize: 11 },
      axisLine: { lineStyle: { color: '#E5E7EB' } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#999', fontSize: 11,
        formatter: (v: number) => formatPace(v),
      },
      splitLine: { lineStyle: { color: '#F3F4F6' } },
    },
    series: [{
      type: 'line',
      data: stats.map(s => Number(s.avg_pace.toFixed(0))),
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color: '#FF6B35', width: 2 },
      itemStyle: { color: '#FF6B35' },
      areaStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(255,107,53,0.3)' },
            { offset: 1, color: 'rgba(255,107,53,0.02)' }
          ]
        }
      }
    }]
  }
})

const TRAINING_TYPE_COLORS: Record<string, string> = {
  '恢复跑': '#4CAF50',
  '节奏跑': '#FF9800',
  '间歇跑': '#F44336',
  '长距离': '#2196F3',
  '未标注': '#9E9E9E',
}

const trainingTypePieOption = computed(() => {
  const items = statsStore.trainingTypeStats?.items ?? []
  const pieData = items.map(item => ({
    name: item.training_type,
    value: item.runs,
    itemStyle: { color: TRAINING_TYPE_COLORS[item.training_type] || '#9E9E9E' }
  }))
  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1A1A2E',
      borderColor: '#1A1A2E',
      textStyle: { color: '#fff', fontSize: 12 },
      formatter: (params: any) => `${params.name}<br/>次数: ${params.value} (${params.percent}%)`
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: { fontSize: 12, color: '#666' }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['40%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}\n{d}%', fontSize: 12 },
      data: pieData
    }]
  }
})

const trainingTypeBarOption = computed(() => {
  const items = statsStore.trainingTypeStats?.items ?? []
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1A1A2E',
      borderColor: '#1A1A2E',
      textStyle: { color: '#fff', fontSize: 12 },
      formatter: (params: any) => {
        const p = params[0]
        const item = items[p.dataIndex]
        return `${p.name}<br/>里程: ${p.value} km<br/>次数: ${item.runs}<br/>平均配速: ${formatPace(item.avg_pace)}`
      }
    },
    grid: { left: 60, right: 20, top: 20, bottom: 30 },
    xAxis: {
      type: 'category',
      data: items.map(i => i.training_type),
      axisLabel: { color: '#999', fontSize: 11 },
      axisLine: { lineStyle: { color: '#E5E7EB' } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#999', fontSize: 11, formatter: '{value} km' },
      splitLine: { lineStyle: { color: '#F3F4F6' } },
    },
    series: [{
      type: 'bar',
      data: items.map(i => ({
        value: Number(i.distance.toFixed(1)),
        itemStyle: { color: TRAINING_TYPE_COLORS[i.training_type] || '#9E9E9E', borderRadius: [4, 4, 0, 0] }
      })),
      barWidth: '50%',
    }]
  }
})

watch(period, () => {
  const year = new Date().getFullYear()
  const month = new Date().getMonth() + 1
  if (period.value === 'weekly') {
    statsStore.fetchWeeklyStats(year, month)
  } else if (period.value === 'yearly') {
    statsStore.fetchYearlyStats()
  } else {
    statsStore.fetchMonthlyStats(year)
  }
  statsStore.fetchPaceTrend(period.value)
})

async function handleExport(type: 'csv' | 'json') {
  try {
    const blob = type === 'csv' ? await api.exportCsv() : await api.exportJson()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `runtrack_export.${type}`
    a.click()
    URL.revokeObjectURL(url)
  } catch {}
}

onMounted(async () => {
  const year = new Date().getFullYear()
  await Promise.all([
    statsStore.fetchMonthlyStats(year),
    statsStore.fetchPaceTrend('monthly'),
    statsStore.fetchPersonalBests(),
    statsStore.fetchTrainingTypeStats(),
  ])
})
</script>

<style scoped>
.btn-secondary {
  @apply px-4 py-2 border border-gray-300 text-gray-600 rounded-btn text-sm font-medium hover:bg-gray-50 transition-colors;
}
</style>
