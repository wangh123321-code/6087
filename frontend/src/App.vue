<template>
  <div class="flex h-full">
    <aside class="w-60 flex-shrink-0 flex flex-col" style="background-color: #1A1A2E;">
      <div class="flex items-center gap-3 px-6 py-5 border-b border-white/10">
        <Activity class="w-7 h-7 text-primary" />
        <h1 class="text-xl font-bold text-white font-heading">RunTrack</h1>
      </div>
      <nav class="flex-1 py-4">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-6 py-3 text-sm transition-colors"
          :class="isActive(item.path) ? 'text-primary bg-white/5' : 'text-gray-400 hover:text-white hover:bg-white/5'"
        >
          <component :is="item.icon" class="w-5 h-5" />
          <span>{{ item.label }}</span>
        </router-link>
      </nav>
      <div class="px-6 py-4 border-t border-white/10 text-xs text-gray-500">
        RunTrack v1.0
      </div>
    </aside>
    <main class="flex-1 overflow-auto" style="background-color: #F5F5F7;">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { Activity, Footprints, BarChart3, Target } from 'lucide-vue-next'

const route = useRoute()

const navItems = [
  { path: '/', label: '仪表盘', icon: Activity },
  { path: '/records', label: '跑步记录', icon: Footprints },
  { path: '/stats', label: '统计分析', icon: BarChart3 },
  { path: '/goals', label: '目标管理', icon: Target },
]

function isActive(path: string): boolean {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>
