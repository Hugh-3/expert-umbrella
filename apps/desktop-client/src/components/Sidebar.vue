<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import {
  HomeFilled,
  Reading,
  Clock,
  Folder,
  Setting,
  Plus,
} from '@element-plus/icons-vue'
import { useProjectStore } from '@/stores/project'

const router = useRouter()
const route = useRoute()
const projectStore = useProjectStore()

const menuItems = [
  { name: '仪表盘', icon: HomeFilled, path: '/' },
  { name: '设置', icon: Setting, path: '/settings' },
]

function navigateTo(path: string) {
  router.push(path)
}

function isActive(path: string) {
  return route.path === path
}
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="logo">
        <Reading class="logo-icon" />
        <span class="logo-text">Content Creator</span>
      </div>
    </div>

    <nav class="sidebar-nav">
      <div
        v-for="item in menuItems"
        :key="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
        @click="navigateTo(item.path)"
      >
        <component :is="item.icon" class="nav-icon" />
        <span>{{ item.name }}</span>
      </div>
    </nav>

    <div class="sidebar-divider"></div>

    <div class="sidebar-projects">
      <div class="projects-header">
        <span class="projects-title">我的项目</span>
        <Plus class="add-project" @click="$emit('create-project')" />
      </div>
      <div
        v-for="project in projectStore.projects.slice(0, 5)"
        :key="project.id"
        class="project-item"
        :class="{ active: route.params.id === project.id }"
        @click="router.push(`/project/${project.id}/chapters`)"
      >
        <div class="project-icon">
          <Reading />
        </div>
        <div class="project-info">
          <span class="project-name">{{ project.name }}</span>
          <span class="project-type">{{ project.type }}</span>
        </div>
      </div>
      <div
        v-if="projectStore.projects.length === 0"
        class="empty-projects"
      >
        暂无项目，点击上方按钮创建
      </div>
    </div>

    <div class="sidebar-footer">
      <span class="version">v1.0.0</span>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 260px;
  background-color: var(--sidebar-bg);
  color: #fff;
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #334155;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 24px;
  color: var(--primary-light);
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
}

.sidebar-nav {
  padding: 10px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.nav-item:hover {
  background-color: var(--sidebar-hover);
}

.nav-item.active {
  background-color: var(--primary-color);
}

.nav-icon {
  font-size: 18px;
}

.sidebar-divider {
  height: 1px;
  background-color: #334155;
  margin: 0 10px;
}

.sidebar-projects {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
}

.projects-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 5px;
  margin-bottom: 10px;
}

.projects-title {
  font-size: 12px;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.add-project {
  font-size: 16px;
  cursor: pointer;
  color: var(--primary-light);
  transition: color 0.2s;
}

.add-project:hover {
  color: var(--primary-color);
}

.project-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-bottom: 4px;
}

.project-item:hover {
  background-color: var(--sidebar-hover);
}

.project-item.active {
  background-color: rgba(99, 102, 241, 0.2);
  border-left: 3px solid var(--primary-color);
}

.project-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background-color: #334155;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.project-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.project-name {
  font-size: 13px;
  color: #f1f5f9;
}

.project-type {
  font-size: 11px;
  color: #64748b;
}

.empty-projects {
  padding: 20px;
  text-align: center;
  color: #64748b;
  font-size: 13px;
}

.sidebar-footer {
  padding: 15px 20px;
  border-top: 1px solid #334155;
}

.version {
  font-size: 11px;
  color: #64748b;
}
</style>
