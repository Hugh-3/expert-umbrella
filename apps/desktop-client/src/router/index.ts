import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
  },
  {
    path: '/project/:id',
    name: 'ProjectDetail',
    component: () => import('@/views/ProjectDetail.vue'),
    children: [
      {
        path: 'timeline',
        name: 'ProjectTimeline',
        component: () => import('@/views/ProjectTimeline.vue'),
      },
      {
        path: 'chapters',
        name: 'ProjectChapters',
        component: () => import('@/views/ProjectChapters.vue'),
      },
      {
        path: 'chapter/:chapterId',
        name: 'ChapterEditor',
        component: () => import('@/views/ChapterEditor.vue'),
      },
      {
        path: 'memory',
        name: 'ProjectMemory',
        component: () => import('@/views/ProjectMemory.vue'),
      },
    ],
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
