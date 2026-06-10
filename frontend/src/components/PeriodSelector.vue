<template>
  <div class="flex gap-1 bg-gray-100 rounded-btn p-1">
    <button
      v-for="option in options"
      :key="option.value"
      class="px-4 py-1.5 text-sm rounded-btn transition-colors font-medium"
      :class="modelValue === option.value ? 'bg-primary text-white shadow-sm' : 'text-gray-500 hover:text-gray-700'"
      @click="$emit('update:modelValue', option.value)"
    >
      {{ option.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  options: { label: string; value: string }[]
  modelValue: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>
