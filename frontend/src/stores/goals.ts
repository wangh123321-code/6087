import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Goal, GoalProgress } from '@/types'
import * as api from '@/utils/api'

export const useGoalsStore = defineStore('goals', () => {
  const goals = ref<Goal[]>([])
  const progress = ref<GoalProgress | null>(null)
  const loading = ref(false)

  async function fetchGoals() {
    loading.value = true
    try {
      goals.value = await api.getGoals()
    } finally {
      loading.value = false
    }
  }

  async function addGoal(goal: Partial<Goal>) {
    const res = await api.createGoal(goal)
    await fetchGoals()
    return res
  }

  async function editGoal(id: number, goal: Partial<Goal>) {
    const res = await api.updateGoal(id, goal)
    await fetchGoals()
    return res
  }

  async function fetchProgress(year: number) {
    loading.value = true
    try {
      progress.value = await api.getGoalProgress(year)
    } finally {
      loading.value = false
    }
  }

  return {
    goals, progress, loading,
    fetchGoals, addGoal, editGoal, fetchProgress
  }
})
