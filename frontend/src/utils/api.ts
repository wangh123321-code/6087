import axios from 'axios'
import type { RunRecord, RecordQuery, PaginatedResponse, StatsSummary, PeriodStats, PersonalBestsResponse, GpxParseResult, Goal, GoalProgress, TrainingTypeStatsResponse } from '@/types'

const api = axios.create({ baseURL: '/api' })

export async function getRecords(params?: RecordQuery): Promise<PaginatedResponse<RunRecord>> {
  const { data } = await api.get('/records', { params })
  return data
}

export async function getRecord(id: number): Promise<RunRecord> {
  const { data } = await api.get(`/records/${id}`)
  return data
}

export async function createRecord(record: Partial<RunRecord>): Promise<RunRecord> {
  const { data } = await api.post('/records', record)
  return data
}

export async function updateRecord(id: number, record: Partial<RunRecord>): Promise<RunRecord> {
  const { data } = await api.put(`/records/${id}`, record)
  return data
}

export async function deleteRecord(id: number): Promise<void> {
  await api.delete(`/records/${id}`)
}

export async function parseGpx(file: File): Promise<GpxParseResult> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post('/records/gpx', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export async function getSummary(): Promise<StatsSummary> {
  const { data } = await api.get('/stats/summary')
  return data
}

export async function getMonthlyStats(year: number): Promise<PeriodStats[]> {
  const { data } = await api.get('/stats/monthly', { params: { year } })
  return data
}

export async function getWeeklyStats(year: number, month: number): Promise<PeriodStats[]> {
  const { data } = await api.get('/stats/weekly', { params: { year, month } })
  return data
}

export async function getYearlyStats(): Promise<PeriodStats[]> {
  const { data } = await api.get('/stats/yearly')
  return data
}

export async function getPaceTrend(period: string = 'monthly'): Promise<PeriodStats[]> {
  const { data } = await api.get('/stats/pace-trend', { params: { period } })
  return data
}

export async function getPersonalBests(): Promise<PersonalBestsResponse> {
  const { data } = await api.get('/stats/personal-bests')
  return data
}

export async function getGoals(): Promise<Goal[]> {
  const { data } = await api.get('/goals')
  return data
}

export async function createGoal(goal: Partial<Goal>): Promise<Goal> {
  const { data } = await api.post('/goals', goal)
  return data
}

export async function updateGoal(id: number, goal: Partial<Goal>): Promise<Goal> {
  const { data } = await api.put(`/goals/${id}`, goal)
  return data
}

export async function getGoalProgress(year: number): Promise<GoalProgress> {
  const { data } = await api.get(`/goals/year/${year}/progress`)
  return data
}

export async function exportCsv(): Promise<Blob> {
  const { data } = await api.get('/export/csv', { responseType: 'blob' })
  return data
}

export async function exportJson(): Promise<Blob> {
  const { data } = await api.get('/export/json', { responseType: 'blob' })
  return data
}

export async function getTrainingTypeStats(): Promise<TrainingTypeStatsResponse> {
  const { data } = await api.get('/stats/training-type')
  return data
}
