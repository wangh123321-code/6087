import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { StatsSummary, PeriodStats, PersonalBestsResponse, TrainingTypeStatsResponse } from '@/types'
import * as api from '@/utils/api'

export const useStatsStore = defineStore('stats', () => {
  const summary = ref<StatsSummary | null>(null)
  const monthlyStats = ref<PeriodStats[]>([])
  const weeklyStats = ref<PeriodStats[]>([])
  const yearlyStats = ref<PeriodStats[]>([])
  const paceTrend = ref<PeriodStats[]>([])
  const personalBests = ref<PersonalBestsResponse | null>(null)
  const trainingTypeStats = ref<TrainingTypeStatsResponse | null>(null)
  const loading = ref(false)

  async function fetchSummary() {
    loading.value = true
    try {
      summary.value = await api.getSummary()
    } finally {
      loading.value = false
    }
  }

  async function fetchMonthlyStats(year: number) {
    monthlyStats.value = await api.getMonthlyStats(year)
  }

  async function fetchWeeklyStats(year: number, month: number) {
    weeklyStats.value = await api.getWeeklyStats(year, month)
  }

  async function fetchYearlyStats() {
    yearlyStats.value = await api.getYearlyStats()
  }

  async function fetchPaceTrend(period: string = 'monthly') {
    paceTrend.value = await api.getPaceTrend(period)
  }

  async function fetchPersonalBests() {
    personalBests.value = await api.getPersonalBests()
  }

  async function fetchTrainingTypeStats() {
    trainingTypeStats.value = await api.getTrainingTypeStats()
  }

  return {
    summary, monthlyStats, weeklyStats, yearlyStats, paceTrend, personalBests, trainingTypeStats, loading,
    fetchSummary, fetchMonthlyStats, fetchWeeklyStats, fetchYearlyStats, fetchPaceTrend, fetchPersonalBests, fetchTrainingTypeStats
  }
})
