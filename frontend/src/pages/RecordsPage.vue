<template>
  <div class="p-6 space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-bold font-heading">跑步记录</h2>
      <button class="btn-primary" @click="openDrawer()">
        <Plus class="w-4 h-4 inline mr-1" />新增记录
      </button>
    </div>

    <div class="bg-white/90 rounded-card p-4 shadow-sm border border-black/5">
      <div class="flex items-center gap-3 flex-wrap">
        <div class="flex items-center gap-2">
          <label class="text-xs text-gray-500">日期</label>
          <input v-model="store.query.date_from" type="date" class="filter-input" />
          <span class="text-gray-400">~</span>
          <input v-model="store.query.date_to" type="date" class="filter-input" />
        </div>
        <div class="flex items-center gap-2">
          <label class="text-xs text-gray-500">距离</label>
          <input v-model.number="store.query.distance_min" type="number" step="0.1" placeholder="最小" class="filter-input w-20" />
          <span class="text-gray-400">~</span>
          <input v-model.number="store.query.distance_max" type="number" step="0.1" placeholder="最大" class="filter-input w-20" />
        </div>
        <div class="flex items-center gap-2">
          <label class="text-xs text-gray-500">地点</label>
          <input v-model="store.query.location" type="text" placeholder="搜索" class="filter-input w-28" />
        </div>
        <div class="flex items-center gap-2">
          <label class="text-xs text-gray-500">天气</label>
          <select v-model="store.query.weather" class="filter-input w-24">
            <option value="">全部</option>
            <option v-for="w in weatherList" :key="w" :value="w">{{ w }}</option>
          </select>
        </div>
        <button class="btn-primary text-xs px-3 py-1.5" @click="handleSearch">查询</button>
        <button class="btn-secondary text-xs px-3 py-1.5" @click="handleReset">重置</button>
      </div>
    </div>

    <div class="bg-white/90 rounded-card shadow-sm border border-black/5 overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-gray-50 text-gray-500">
            <th v-for="col in columns" :key="col.key" class="text-left px-4 py-3 font-medium cursor-pointer select-none hover:text-primary" @click="handleSort(col.key)">
              <span class="inline-flex items-center gap-1">
                {{ col.label }}
                <ArrowUpDown v-if="store.query.sort_by === col.key" class="w-3.5 h-3.5" :class="store.query.sort_order === 'asc' ? 'rotate-180' : ''" />
              </span>
            </th>
            <th class="text-right px-4 py-3 font-medium">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(r, i) in store.records" :key="r.id" class="border-t hover:bg-orange-50/50 transition-colors" :class="i % 2 === 0 ? '' : 'bg-gray-50/50'">
            <td class="px-4 py-3">{{ formatDate(r.date) }}</td>
            <td class="px-4 py-3">{{ formatDistance(r.distance) }}</td>
            <td class="px-4 py-3">{{ formatDuration(r.duration) }}</td>
            <td class="px-4 py-3 text-primary font-medium">{{ formatPace(r.avg_pace) }}</td>
            <td class="px-4 py-3">{{ r.avg_heart_rate ?? '-' }}</td>
            <td class="px-4 py-3 text-gray-500">{{ r.location || '-' }}</td>
            <td class="px-4 py-3 text-gray-500">{{ r.weather || '-' }}</td>
            <td class="px-4 py-3 text-gray-500">{{ r.feeling || '-' }}</td>
            <td class="px-4 py-3 text-right">
              <button class="text-primary hover:underline text-xs mr-3" @click="openDrawer(r)">编辑</button>
              <button class="text-red-500 hover:underline text-xs" @click="confirmDelete(r)">删除</button>
            </td>
          </tr>
          <tr v-if="store.records.length === 0">
            <td colspan="9" class="px-4 py-12 text-center text-gray-400">暂无跑步记录</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flex items-center justify-between">
      <span class="text-sm text-gray-500">共 {{ store.total }} 条记录</span>
      <div class="flex items-center gap-2">
        <button class="page-btn" :disabled="store.query.page! <= 1" @click="goPage((store.query.page ?? 1) - 1)">上一页</button>
        <span class="text-sm text-gray-600">{{ store.query.page ?? 1 }} / {{ totalPages }}</span>
        <button class="page-btn" :disabled="store.query.page! >= totalPages" @click="goPage((store.query.page ?? 1) + 1)">下一页</button>
      </div>
    </div>

    <RecordDrawer :visible="drawerVisible" :record="editingRecord" @close="drawerVisible = false" @saved="onSaved" />

    <Teleport to="body">
      <Transition name="fade">
        <div v-if="deleteTarget" class="fixed inset-0 z-50 flex items-center justify-center">
          <div class="absolute inset-0 bg-black/40" @click="deleteTarget = null" />
          <div class="relative bg-white rounded-card p-6 shadow-2xl max-w-sm w-full mx-4">
            <h3 class="text-lg font-bold font-heading mb-2">确认删除</h3>
            <p class="text-gray-500 text-sm mb-5">确定要删除 {{ formatDate(deleteTarget.date) }} 的跑步记录吗？此操作不可撤销。</p>
            <div class="flex gap-3 justify-end">
              <button class="btn-secondary" @click="deleteTarget = null">取消</button>
              <button class="px-5 py-2 bg-red-500 text-white rounded-btn text-sm font-medium hover:bg-red-600 transition-colors" @click="handleDelete">删除</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, ArrowUpDown } from 'lucide-vue-next'
import { useRecordsStore } from '@/stores/records'
import { formatPace, formatDuration, formatDate, formatDistance } from '@/utils/format'
import RecordDrawer from '@/components/RecordDrawer.vue'
import type { RunRecord } from '@/types'

const store = useRecordsStore()
const drawerVisible = ref(false)
const editingRecord = ref<RunRecord | null>(null)
const deleteTarget = ref<RunRecord | null>(null)

const weatherList = ['晴', '多云', '阴', '小雨', '大雨', '雪']

const columns = [
  { key: 'date', label: '日期' },
  { key: 'distance', label: '距离' },
  { key: 'duration', label: '用时' },
  { key: 'avg_pace', label: '配速' },
  { key: 'avg_heart_rate', label: '心率' },
  { key: 'location', label: '地点' },
  { key: 'weather', label: '天气' },
  { key: 'feeling', label: '感受' },
]

const totalPages = computed(() => Math.max(1, Math.ceil(store.total / (store.query.page_size ?? 10))))

function openDrawer(record?: RunRecord) {
  editingRecord.value = record ?? null
  drawerVisible.value = true
}

function handleSort(key: string) {
  if (store.query.sort_by === key) {
    store.query.sort_order = store.query.sort_order === 'asc' ? 'desc' : 'asc'
  } else {
    store.query.sort_by = key
    store.query.sort_order = 'desc'
  }
  store.query.page = 1
  store.fetchRecords()
}

function handleSearch() {
  store.query.page = 1
  store.fetchRecords()
}

function handleReset() {
  store.resetQuery()
  store.fetchRecords()
}

function goPage(p: number) {
  store.query.page = p
  store.fetchRecords()
}

function onSaved() {
  store.fetchRecords()
}

function confirmDelete(record: RunRecord) {
  deleteTarget.value = record
}

async function handleDelete() {
  if (deleteTarget.value) {
    await store.removeRecord(deleteTarget.value.id)
    deleteTarget.value = null
  }
}

onMounted(() => {
  store.fetchRecords()
})
</script>

<style scoped>
.filter-input {
  @apply px-2.5 py-1.5 border border-gray-200 rounded-btn text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary;
}
.btn-primary {
  @apply px-4 py-2 bg-primary text-white rounded-btn text-sm font-medium hover:bg-primary/90 transition-colors;
}
.btn-secondary {
  @apply px-4 py-2 border border-gray-300 text-gray-600 rounded-btn text-sm font-medium hover:bg-gray-50 transition-colors;
}
.page-btn {
  @apply px-3 py-1.5 text-sm border border-gray-200 rounded-btn hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors;
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
