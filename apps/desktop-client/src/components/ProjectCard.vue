<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Reading, Edit, DocumentChecked, Download, More } from '@element-plus/icons-vue'
import type { Project } from '@/types'

const props = defineProps<{
  project: Project
}>()

const router = useRouter()

const statusText = computed(() => {
  const map: Record<string, string> = {
    draft: '草稿',
    in_progress: '进行中',
    completed: '已完成',
    archived: '已归档',
  }
  return map[props.project.status] || props.project.status
})

const statusColor = computed(() => {
  const map: Record<string, string> = {
    draft: 'text-gray-400',
    in_progress: 'text-blue-400',
    completed: 'text-green-400',
    archived: 'text-gray-500',
  }
  return map[props.project.status] || 'text-gray-400'
})

const typeText = computed(() => {
  const map: Record<string, string> = {
    novel: '小说',
    music: '音乐',
    short_video: '短视频',
    micro_film: '微电影',
  }
  return map[props.project.type] || props.project.type
})

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
  })
}

function handleContinue() {
  router.push(`/project/${props.project.id}/chapters`)
}

function handleView() {
  router.push(`/project/${props.project.id}/chapters`)
}

function handleExport() {
}
</script>

<template>
  <div class="project-card">
    <div class="card-header">
      <div class="cover-wrapper">
        <div class="cover-placeholder">
          <Reading class="cover-icon" />
        </div>
        <span class="type-badge">{{ typeText }}</span>
      </div>
    </div>

    <div class="card-body">
      <h3 class="project-name">{{ project.name }}</h3>
      <p class="project-status" :class="statusColor">{{ statusText }}</p>
      <p class="last-edited">最近编辑：{{ formatDate(project.updated_at) }}</p>
    </div>

    <div class="card-actions">
      <button class="action-btn primary" @click="handleContinue">
        <Edit class="action-icon" />
        <span>继续创作</span>
      </button>
      <div class="action-group">
        <button class="action-btn secondary" @click="handleView">
          <DocumentChecked class="action-icon" />
        </button>
        <button class="action-btn secondary" @click="handleExport">
          <Download class="action-icon" />
        </button>
        <button class="action-btn secondary">
          <More class="action-icon" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.project-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
}

.card-header {
  position: relative;
}

.cover-wrapper {
  height: 120px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-placeholder {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-icon {
  font-size: 32px;
  color: #fff;
}

.type-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(4px);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  color: #fff;
}

.card-body {
  padding: 16px;
}

.project-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.project-status {
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 8px;
}

.last-edited {
  font-size: 12px;
  color: var(--text-secondary);
}

.card-actions {
  padding: 0 16px 16px;
  display: flex;
  gap: 10px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.action-btn.primary {
  flex: 1;
  background: var(--primary-color);
  color: #fff;
}

.action-btn.primary:hover {
  background: var(--primary-dark);
}

.action-btn.secondary {
  background: #f1f5f9;
  color: var(--text-secondary);
  padding: 8px;
}

.action-btn.secondary:hover {
  background: #e2e8f0;
}

.action-icon {
  font-size: 14px;
}

.action-group {
  display: flex;
  gap: 4px;
}
</style>
