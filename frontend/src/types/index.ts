export interface RunRecord {
  id: number
  date: string
  distance: number
  duration: number
  avg_pace: number
  avg_heart_rate: number | null
  location: string
  weather: string
  feeling: string
  training_type: string
  gpx_data: string | null
  created_at: string
  updated_at: string
}

export interface RecordQuery {
  page?: number
  page_size?: number
  date_from?: string
  date_to?: string
  distance_min?: number
  distance_max?: number
  location?: string
  weather?: string
  sort_by?: string
  sort_order?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface StatsSummary {
  total_distance: number
  total_runs: number
  avg_pace: number
  this_month_distance: number
}

export interface PeriodStats {
  period: string
  distance: number
  runs: number
  avg_pace: number
}

export interface PersonalBest {
  category: string
  best_time: number | null
  best_pace: number | null
  date: string | null
  record_id: number | null
}

export interface PersonalBestsResponse {
  personal_bests: PersonalBest[]
}

export interface Goal {
  id: number
  year: number
  target_distance: number
  created_at: string
  updated_at: string
}

export interface GpxParseResult {
  distance: number
  duration: number
  avg_pace: number
  points_count: number
}

export interface GoalProgress {
  target_distance: number
  current_distance: number
  percentage: number
  monthly_progress: { month: string; distance: number }[]
}

export interface TrainingTypeStatsItem {
  training_type: string
  runs: number
  distance: number
  avg_pace: number
}

export interface TrainingTypeStatsResponse {
  items: TrainingTypeStatsItem[]
}
