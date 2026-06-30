<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { CircleCheck, Clock, CircleClose, VideoPlay } from '@element-plus/icons-vue'
import { useProjectStore } from '@/stores/project'

const route = useRoute()
const projectStore = useProjectStore()

onMounted(async () => {
  const projectId = route.params.id as string
  await projectStore.fetchTimeline(projectId)
})

function getStatusIcon(status: string) {
  switch (status) {
    case 'completed':
      return CircleCheck
    case 'in_progress':
      return VideoPlay
    default:
      return CircleClose
  }
}

function getStatusColor(status: string) {
  switch (status) {
    case 'completed':
      return 'text-green-500'
    case 'in_progress':
      return 'text-blue-500'
    default:
      return 'text-gray-400'
  }
}

function getLineColor(status: string, isLast: boolean) {
  if (isLast) return 'bg-gray-200'
  switch (status) {
    case 'completed':
      return 'bg-green-500'
    case 'in_progress':
      return 'bg-blue-500'
    default:
      return 'bg-gray-200'
  }
}
</script>

<template>
  <div class="timeline-page">
    <h2 class="page-title">创作时间线</h2>

    <div v-if="projectStore.loading" class="loading-state">
      加载中...
    </div>

    <div v-else class="timeline-container">
      <div class="timeline">
        <div
          v-for="(stage, index) in projectStore.timeline?.stages"
          :key="stage.stage"
          class="timeline-item"
        >
          <div class="timeline-line" :class="getLineColor(stage.status, index === (projectStore.timeline?.stages.length || 0) - 1)"></div>
          <div class="timeline-content">
            <div class="timeline-icon" :class="getStatusColor(stage.status)">
              <component :is="getStatusIcon(stage.status)" />
            </div>
            <div class="timeline-info">
              <h3 class="timeline-stage">{{ stage.stage }}</h3>
              <p class="timeline-desc">{{ stage.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.timeline-page {
  max-width: 600px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 24px;
}

.loading-state {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
}

.timeline-container {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
}

.timeline {
  position: relative;
}

.timeline-item {
  position: relative;
  padding-bottom: 32px;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-line {
  position: absolute;
  left: 15px;
  top: 32px;
  width: 2px;
  height: calc(100% - 32px);
}

.timeline-content {
  display: flex;
  gap: 16px;
}

.timeline-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.timeline-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.timeline-stage {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.timeline-desc {
  font-size: 13px;
  color: var(--text-secondary);
}
</style>
