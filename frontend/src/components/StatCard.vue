<template>
  <div class="bg-white/90 rounded-card p-5 shadow-sm border border-black/5">
    <div class="flex items-center justify-between mb-3">
      <span class="text-sm text-gray-500">{{ title }}</span>
      <div class="w-9 h-9 rounded-lg flex items-center justify-center" :style="{ backgroundColor: color + '20' }">
        <component :is="icon" class="w-5 h-5" :style="{ color }" />
      </div>
    </div>
    <div class="text-2xl font-bold font-heading" :style="{ color }">{{ value }}</div>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  title: string
  value: string | number
  icon: Component
  color: string
}>()
</script>
