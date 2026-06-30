<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Clock, Reading, Folder, Setting } from '@element-plus/icons-vue'
import { useProjectStore } from '@/stores/project'
import Sidebar from '@/components/Sidebar.vue'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()

const tabs = [
  { name: '章节', icon: BookOpen, path: 'chapters' },
  { name: '时间线', icon: Clock, path: 'timeline' },
  { name: '记忆', icon: Database, path: 'memory' },
]

onMounted(async () => {
  const projectId = route.params.id as string
  await projectStore.fetchProject(projectId)
})

function navigateToTab(path: string) {
  router.push(`/project/${route.params.id}/${path}`)
}

function getCurrentTab() {
  const fullPath = route.fullPath
  return tabs.find(tab => fullPath.includes(tab.path))?.path || 'chapters'
}
</script>

<template>
  <div class="project-detail">
    <Sidebar />
    
    <main class="main-content">
      <header class="page-header">
        <div class="header-info">
          <h1 class="project-title">{{ projectStore.currentProject?.name }}</h1>
          <p class="project-type">{{ projectStore.currentProject?.type }}</p>
        </div>
      </header>

      <nav class="project-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.path"
          class="tab-item"
          :class="{ active: getCurrentTab() === tab.path }"
          @click="navigateToTab(tab.path)"
        >
          <component :is="tab.icon" class="tab-icon" />
          <span>{{ tab.name }}</span>
        </button>
      </nav>

      <div class="content-area">
        <router-view />
      </div>
    </main>
  </div>
</template>

<style scoped>
.project-detail {
  display: flex;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  margin-left: 260px;
  display: flex;
  flex-direction: column;
}

.page-header {
  padding: 20px 30px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.project-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.project-type {
  padding: 4px 12px;
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary-color);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.project-tabs {
  display: flex;
  gap: 4px;
  padding: 10px 30px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.tab-item:hover {
  background: #e2e8f0;
}

.tab-item.active {
  background: #fff;
  color: var(--primary-color);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.tab-icon {
  font-size: 16px;
}

.content-area {
  flex: 1;
  padding: 24px 30px;
  overflow-y: auto;
}
</style>
