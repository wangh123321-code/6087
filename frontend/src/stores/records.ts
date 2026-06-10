import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import type { RunRecord, RecordQuery, PaginatedResponse } from '@/types'
import * as api from '@/utils/api'

export const useRecordsStore = defineStore('records', () => {
  const records = ref<RunRecord[]>([])
  const total = ref(0)
  const loading = ref(false)
  const currentRecord = ref<RunRecord | null>(null)

  const query = reactive<RecordQuery>({
    page: 1,
    page_size: 10,
    date_from: '',
    date_to: '',
    distance_min: undefined,
    distance_max: undefined,
    location: '',
    weather: '',
    sort_by: 'date',
    sort_order: 'desc'
  })

  async function fetchRecords() {
    loading.value = true
    try {
      const res: PaginatedResponse<RunRecord> = await api.getRecords(query)
      records.value = res.items
      total.value = res.total
    } finally {
      loading.value = false
    }
  }

  async function fetchRecord(id: number) {
    const res = await api.getRecord(id)
    currentRecord.value = res
    return res
  }

  async function addRecord(record: Partial<RunRecord>) {
    const res = await api.createRecord(record)
    await fetchRecords()
    return res
  }

  async function editRecord(id: number, record: Partial<RunRecord>) {
    const res = await api.updateRecord(id, record)
    await fetchRecords()
    return res
  }

  async function removeRecord(id: number) {
    await api.deleteRecord(id)
    await fetchRecords()
  }

  function resetQuery() {
    query.page = 1
    query.date_from = ''
    query.date_to = ''
    query.distance_min = undefined
    query.distance_max = undefined
    query.location = ''
    query.weather = ''
    query.sort_by = 'date'
    query.sort_order = 'desc'
  }

  return {
    records, total, loading, currentRecord, query,
    fetchRecords, fetchRecord, addRecord, editRecord, removeRecord, resetQuery
  }
})
