<template>
  <div class="p-6 space-y-6">
    <h2 class="text-2xl font-bold font-heading">目标管理</h2>

    <div class="bg-white/90 rounded-card p-6 shadow-sm border border-black/5">
      <h3 class="text-sm font-medium text-gray-500 mb-4">{{ currentYear }} 年度目标</h3>
      <div class="flex items-center gap-4">
        <input
          v-model.number="targetDistance"
          type="number"
          step="1"
          min="1"
          class="w-40 px-4 py-3 border border-gray-200 rounded-btn text-xl font-heading font-bold text-center focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
          placeholder="目标公里数"
        />
        <span class="text-lg text-gray-400">km</span>
        <button class="btn-primary" @click="handleSaveGoal">保存目标</button>
      </div>
    </div>

    <div v-if="goalProgress" class="bg-white/90 rounded-card p-6 shadow-sm border border-black/5">
      <div class="flex items-center justify-between mb-2">
        <h3 class="text-sm font-medium text-gray-500">完成进度</h3>
        <span class="text-lg font-bold font-heading" :class="goalProgress.percentage >= 100 ? 'text-success' : 'text-primary'">
          {{ goalProgress.percentage.toFixed(1) }}%
        </span>
      </div>
      <div class="w-full h-5 bg-gray-100 rounded-full overflow-hidden">
        <div
          class="h-full rounded-full transition-all duration-700"
          :style="{
            width: Math.min(goalProgress.percentage, 100) + '%',
            background: 'linear-gradient(90deg, #FF6B35, #00E676)'
          }"
        />
      </div>
      <div class="flex justify-between mt-2 text-xs text-gray-400">
        <span>{{ formatDistance(goalProgress.current_distance) }}</span>
        <span>{{ formatDistance(goalProgress.target_distance) }}</span>
      </div>
    </div>

    <div class="bg-white/90 rounded-card p-5 shadow-sm border border-black/5">
      <h3 class="text-sm font-medium text-gray-500 mb-4">月度分解</h3>
      <v-chart :option="monthlyChartOption" autoresize style="height: 320px; width: 100%;" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useGoalsStore } from '@/stores/goals'
import { formatDistance } from '@/utils/format'

use([BarChart, TitleComponent, TooltipComponent, GridComponent, CanvasRenderer])

const goalsStore = useGoalsStore()
const currentYear = new Date().getFullYear()
const targetDistance = ref(1000)

const goalProgress = computed(() => goalsStore.progress)

const monthlyChartOption = computed(() => {
  const mp = goalProgress.value?.monthly_progress ?? []
  const months = mp.map(m => m.month)
  const distances = mp.map(m => Number(m.distance.toFixed(1)))
  const avgTarget = goalProgress.value ? Number((goalProgress.value.target_distance / 12).toFixed(1)) : 0
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
      data: months,
      axisLabel: { color: '#999', fontSize: 11 },
      axisLine: { lineStyle: { color: '#E5E7EB' } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#999', fontSize: 11, formatter: '{value} km' },
      splitLine: { lineStyle: { color: '#F3F4F6' } },
    },
    series: [
      {
        type: 'bar',
        data: distances,
        barWidth: '45%',
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
      },
      {
        type: 'bar',
        data: Array(12).fill(avgTarget),
        barWidth: '45%',
        itemStyle: { color: 'rgba(0,230,118,0.15)', borderRadius: [4, 4, 0, 0] },
        z: -1,
      }
    ]
  }
})

async function handleSaveGoal() {
  if (!targetDistance.value || targetDistance.value <= 0) return
  const existing = goalsStore.goals.find(g => g.year === currentYear)
  if (existing) {
    await goalsStore.editGoal(existing.id, { target_distance: targetDistance.value })
  } else {
    await goalsStore.addGoal({ year: currentYear, target_distance: targetDistance.value })
  }
  await goalsStore.fetchProgress(currentYear)
}

onMounted(async () => {
  await goalsStore.fetchGoals()
  await goalsStore.fetchProgress(currentYear)
  const existing = goalsStore.goals.find(g => g.year === currentYear)
  if (existing) {
    targetDistance.value = existing.target_distance
  }
})
</script>

<style scoped>
.btn-primary {
  @apply px-5 py-3 bg-primary text-white rounded-btn text-sm font-medium hover:bg-primary/90 transition-colors;
}
</style>
