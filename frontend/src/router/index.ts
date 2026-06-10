import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: () => import('@/pages/DashboardPage.vue')
  },
  {
    path: '/records',
    name: 'records',
    component: () => import('@/pages/RecordsPage.vue')
  },
  {
    path: '/stats',
    name: 'stats',
    component: () => import('@/pages/StatsPage.vue')
  },
  {
    path: '/goals',
    name: 'goals',
    component: () => import('@/pages/GoalsPage.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
