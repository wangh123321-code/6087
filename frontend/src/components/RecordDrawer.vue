<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="visible" class="fixed inset-0 z-50 flex justify-end">
        <div class="absolute inset-0 bg-black/40" @click="handleClose" />
        <div class="relative w-full max-w-lg bg-white shadow-2xl flex flex-col overflow-hidden">
          <div class="flex items-center justify-between px-6 py-4 border-b">
            <h3 class="text-lg font-bold font-heading">{{ isEdit ? '编辑记录' : '新增记录' }}</h3>
            <button class="p-1 hover:bg-gray-100 rounded" @click="handleClose">
              <X class="w-5 h-5 text-gray-500" />
            </button>
          </div>
          <div class="flex-1 overflow-auto px-6 py-4 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">日期</label>
              <input v-model="form.date" type="date" class="input-field" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">距离 (km)</label>
              <input v-model.number="form.distance" type="number" step="0.1" min="0" class="input-field" @input="calcPace" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">用时</label>
              <div class="flex gap-2">
                <input v-model.number="durationH" type="number" min="0" class="input-field" placeholder="时" @input="calcPace" />
                <input v-model.number="durationM" type="number" min="0" max="59" class="input-field" placeholder="分" @input="calcPace" />
                <input v-model.number="durationS" type="number" min="0" max="59" class="input-field" placeholder="秒" @input="calcPace" />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">平均配速</label>
              <div class="input-field bg-gray-50 text-gray-500">{{ paceDisplay }}</div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">平均心率</label>
              <input v-model.number="form.avg_heart_rate" type="number" min="0" max="250" class="input-field" placeholder="选填" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">地点</label>
              <input v-model="form.location" type="text" class="input-field" placeholder="选填" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">天气</label>
              <select v-model="form.weather" class="input-field">
                <option value="">请选择</option>
                <option v-for="w in weatherOptions" :key="w" :value="w">{{ w }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">感受</label>
              <select v-model="form.feeling" class="input-field">
                <option value="">请选择</option>
                <option v-for="f in feelingOptions" :key="f" :value="f">{{ f }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">训练类型</label>
              <select v-model="form.training_type" class="input-field">
                <option value="">请选择</option>
                <option v-for="t in trainingTypeOptions" :key="t" :value="t">{{ t }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">GPX 文件</label>
              <div
                class="border-2 border-dashed border-gray-300 rounded-btn p-6 text-center cursor-pointer hover:border-primary transition-colors"
                :class="isDragging ? 'border-primary bg-primary/5' : ''"
                @dragover.prevent="isDragging = true"
                @dragleave="isDragging = false"
                @drop.prevent="handleDrop"
                @click="fileInput?.click()"
              >
                <input ref="fileInput" type="file" accept=".gpx" class="hidden" @change="handleFileSelect" />
                <Upload class="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p class="text-sm text-gray-500">拖拽 GPX 文件到此处，或点击选择</p>
                <p v-if="gpxFile" class="text-sm text-primary mt-2">{{ gpxFile.name }}</p>
                <p v-if="gpxParsing" class="text-sm text-gray-400 mt-1">正在解析...</p>
                <p v-if="gpxParsed && !gpxParsing" class="text-sm text-success mt-1">解析成功，已自动填充距离、用时和配速</p>
                <p v-if="gpxError" class="text-sm text-red-500 mt-1">{{ gpxError }}</p>
              </div>
            </div>
          </div>
          <div class="px-6 py-4 border-t flex gap-3 justify-end">
            <button class="btn-secondary" @click="handleClose">取消</button>
            <button class="btn-primary" :disabled="submitting" @click="handleSubmit">
              {{ submitting ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { X, Upload } from 'lucide-vue-next'
import type { RunRecord } from '@/types'
import { formatPace } from '@/utils/format'
import { useRecordsStore } from '@/stores/records'
import { parseGpx } from '@/utils/api'

const props = defineProps<{
  visible: boolean
  record?: RunRecord | null
}>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const store = useRecordsStore()
const isDragging = ref(false)
const gpxFile = ref<File | null>(null)
const gpxParsing = ref(false)
const gpxParsed = ref(false)
const gpxError = ref('')
const fileInput = ref<HTMLInputElement | null>(null)
const submitting = ref(false)

const isEdit = computed(() => !!props.record?.id)

const weatherOptions = ['晴', '多云', '阴', '小雨', '大雨', '雪']
const feelingOptions = ['极好', '好', '一般', '差', '极差']
const trainingTypeOptions = ['恢复跑', '节奏跑', '间歇跑', '长距离']

const form = reactive({
  date: '',
  distance: 0,
  duration: 0,
  avg_pace: 0,
  avg_heart_rate: null as number | null,
  location: '',
  weather: '',
  feeling: '',
  training_type: '',
})

const durationH = ref(0)
const durationM = ref(0)
const durationS = ref(0)

const paceDisplay = computed(() => formatPace(form.avg_pace))

function calcPace() {
  const totalSeconds = (durationH.value || 0) * 3600 + (durationM.value || 0) * 60 + (durationS.value || 0)
  form.duration = totalSeconds
  if (form.distance > 0 && totalSeconds > 0) {
    form.avg_pace = totalSeconds / form.distance
  } else {
    form.avg_pace = 0
  }
}

function durationFromSeconds(s: number) {
  durationH.value = Math.floor(s / 3600)
  durationM.value = Math.floor((s % 3600) / 60)
  durationS.value = Math.round(s % 60)
}

watch(() => props.visible, (val) => {
  if (val && props.record) {
    form.date = props.record.date?.slice(0, 10) || ''
    form.distance = props.record.distance || 0
    form.duration = props.record.duration || 0
    form.avg_pace = props.record.avg_pace || 0
    form.avg_heart_rate = props.record.avg_heart_rate
    form.location = props.record.location || ''
    form.weather = props.record.weather || ''
    form.feeling = props.record.feeling || ''
    form.training_type = props.record.training_type || ''
    durationFromSeconds(props.record.duration || 0)
  } else if (val) {
    form.date = new Date().toISOString().slice(0, 10)
    form.distance = 0
    form.duration = 0
    form.avg_pace = 0
    form.avg_heart_rate = null
    form.location = ''
    form.weather = ''
    form.feeling = ''
    form.training_type = ''
    durationH.value = 0
    durationM.value = 0
    durationS.value = 0
  }
  gpxFile.value = null
  gpxParsed.value = false
  gpxError.value = ''
  gpxParsing.value = false
})

async function handleGpxFile(file: File) {
  gpxFile.value = file
  gpxParsed.value = false
  gpxError.value = ''
  gpxParsing.value = true
  try {
    const result = await parseGpx(file)
    form.distance = result.distance
    form.duration = result.duration
    form.avg_pace = result.avg_pace
    durationFromSeconds(result.duration)
    gpxParsed.value = true
  } catch (e: any) {
    gpxError.value = e?.response?.data?.detail || 'GPX解析失败'
  } finally {
    gpxParsing.value = false
  }
}

function handleDrop(e: DragEvent) {
  isDragging.value = false
  const file = e.dataTransfer?.files[0]
  if (file && file.name.endsWith('.gpx')) {
    handleGpxFile(file)
  }
}

function handleFileSelect(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files?.[0]) {
    handleGpxFile(target.files[0])
  }
}

function handleClose() {
  gpxFile.value = null
  gpxParsed.value = false
  gpxError.value = ''
  gpxParsing.value = false
  emit('close')
}

async function handleSubmit() {
  submitting.value = true
  try {
    if (isEdit.value && props.record?.id) {
      await store.editRecord(props.record.id, { ...form })
    } else {
      await store.addRecord({ ...form })
    }
    emit('saved')
    emit('close')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.input-field {
  @apply w-full px-3 py-2 border border-gray-200 rounded-btn text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary;
}
.btn-primary {
  @apply px-5 py-2 bg-primary text-white rounded-btn text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50;
}
.btn-secondary {
  @apply px-5 py-2 border border-gray-300 text-gray-600 rounded-btn text-sm font-medium hover:bg-gray-50 transition-colors;
}
.drawer-enter-active,
.drawer-leave-active {
  transition: transform 0.3s ease;
}
.drawer-enter-from,
.drawer-leave-to {
  transform: translateX(100%);
}
</style>
