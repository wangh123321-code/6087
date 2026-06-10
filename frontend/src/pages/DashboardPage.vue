<template>
  <div class="p-6 space-y-6">
    <h2 class="text-2xl font-bold font-heading">仪表盘</h2>
    <div class="grid grid-cols-4 gap-4">
      <StatCard title="总跑量" :value="formatDistance(summary?.total_distance ?? 0)" :icon="MapPin" color="#FF6B35" />
      <StatCard title="总次数" :value="String(summary?.total_runs ?? 0)" :icon="Activity" color="#4F46E5" />
      <StatCard title="平均配速" :value="formatPace(summary?.avg_pace ?? 0)" :icon="Timer" color="#0891B2" />
      <StatCard title="本月跑量" :value="formatDistance(summary?.this_month_distance ?? 0)" :icon="Flame" color="#00E676" />
    </div>

    <div class="grid grid-cols-3 gap-4">
      <div class="col-span-1 bg-white/90 rounded-card p-5 shadow-sm border border-black/5">
        <h3 class="text-sm font-medium text-gray-500 mb-4">年度目标进度</h3>
        <div v-if="goalProgress" class="flex flex-col items-center">
          <v-chart :option="goalGaugeOption" autoresize style="height: 200px; width: 100%;" />
          <p class="text-sm text-gray-500 mt-2">
            {{ formatDistance(goalProgress.current_distance) }} / {{ formatDistance(goalProgress.target_distance) }}
          </p>
        </div>
        <div v-else class="text-center text-gray-400 py-8 text-sm">暂未设置年度目标</div>
      </div>
      <div class="col-span-2 bg-white/90 rounded-card p-5 shadow-sm border border-black/5">
        <h3 class="text-sm font-medium text-gray-500 mb-4">近12个月跑量趋势</h3>
        <v-chart :option="trendOption" autoresize style="height: 240px; width: 100%;" />
      </div>
    </div>

    <div class="bg-white/90 rounded-card p-5 shadow-sm border border-black/5">
      <h3 class="text-sm font-medium text-gray-500 mb-4">近期跑步记录</h3>
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b text-gray-500">
            <th class="text-left py-2 font-medium">日期</th>
            <th class="text-left py-2 font-medium">距离</th>
            <th class="text-left py-2 font-medium">用时</th>
            <th class="text-left py-2 font-medium">配速</th>
            <th class="text-left py-2 font-medium">地点</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in recentRecords" :key="r.id" class="border-b last:border-0 hover:bg-gray-50">
            <td class="py-2.5">{{ formatDate(r.date) }}</td>
            <td class="py-2.5">{{ formatDistance(r.distance) }}</td>
            <td class="py-2.5">{{ formatDuration(r.duration) }}</td>
            <td class="py-2.5">{{ formatPace(r.avg_pace) }}</td>
            <td class="py-2.5 text-gray-500">{{ r.location || '-' }}</td>
          </tr>
          <tr v-if="recentRecords.length === 0">
            <td colspan="5" class="py-8 text-center text-gray-400">暂无跑步记录</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { Activity, MapPin, Timer, Flame } from 'lucide-vue-next'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { GaugeChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import StatCard from '@/components/StatCard.vue'
import { useStatsStore } from '@/stores/stats'
import { useGoalsStore } from '@/stores/goals'
import { useRecordsStore } from '@/stores/records'
import { formatPace, formatDuration, formatDate, formatDistance } from '@/utils/format'

use([GaugeChart, BarChart, TitleComponent, TooltipComponent, GridComponent, CanvasRenderer])

const statsStore = useStatsStore()
const goalsStore = useGoalsStore()
const recordsStore = useRecordsStore()

const summary = computed(() => statsStore.summary)
const goalProgress = computed(() => goalsStore.progress)
const recentRecords = computed(() => (recordsStore.records ?? []).slice(0, 5))

const goalGaugeOption = computed(() => {
  const pct = goalProgress.value ? Math.min(goalProgress.value.percentage, 100) : 0
  return {
    series: [{
      type: 'gauge',
      startAngle: 200,
      endAngle: -20,
      min: 0,
      max: 100,
      splitNumber: 5,
      itemStyle: { color: '#FF6B35' },
      progress: { show: true, width: 18, roundCap: true },
      pointer: { show: false },
      axisLine: { lineStyle: { width: 18, color: [[1, '#E5E7EB']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      detail: {
        valueAnimation: true,
        formatter: '{value}%',
        fontSize: 28,
        fontFamily: 'Outfit',
        fontWeight: 'bold',
        color: '#FF6B35',
        offsetCenter: [0, '0%'],
      },
      data: [{ value: Math.round(pct) }],
    }]
  }
})

const trendOption = computed(() => {
  const stats = statsStore.monthlyStats
  const periods = stats.map(s => s.period)
  const distances = stats.map(s => Number(s.distance.toFixed(1)))
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1A1A2E',
      borderColor: '#1A1A2E',
      textStyle: { color: '#fff', fontSize: 12 },
      formatter: (params: any) => {
        const p = params[0]
        return `${p.name}<br/>跑量: ${p.value} km`
      }
    },
    grid: { left: 50, right: 20, top: 20, bottom: 30 },
    xAxis: {
      type: 'category',
      data: periods,
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
      data: distances,
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

onMounted(async () => {
  const currentYear = new Date().getFullYear()
  await Promise.all([
    statsStore.fetchSummary(),
    statsStore.fetchMonthlyStats(currentYear),
    recordsStore.fetchRecords(),
    goalsStore.fetchProgress(currentYear).catch(() => {}),
  ])
})
</script>
