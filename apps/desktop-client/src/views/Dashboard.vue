<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Reading, Trophy } from '@element-plus/icons-vue'
import { useProjectStore } from '@/stores/project'
import Sidebar from '@/components/Sidebar.vue'
import ProjectCard from '@/components/ProjectCard.vue'
import CreateProjectModal from '@/components/CreateProjectModal.vue'

const projectStore = useProjectStore()
const showCreateModal = ref(false)

onMounted(async () => {
  await projectStore.fetchProjects()
})

function handleRefresh() {
  projectStore.fetchProjects()
}

function handleCreated() {
  projectStore.fetchProjects()
}
</script>

<template>
  <div class="dashboard">
    <Sidebar @create-project="showCreateModal = true" />
    
    <main class="main-content">
      <header class="page-header">
        <div class="header-left">
          <h1 class="page-title">欢迎回来</h1>
          <p class="page-subtitle">开始你的创作之旅</p>
        </div>
        <button class="create-btn" @click="showCreateModal = true">
          <Plus class="btn-icon" />
          <span>新建项目</span>
        </button>
      </header>

      <div class="stats-section">
        <div class="stat-card">
          <div class="stat-icon blue">
            <BookOpen />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ projectStore.projects.length }}</span>
            <span class="stat-label">项目总数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon green">
            <Trophy />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ projectStore.inProgressProjects.length }}</span>
            <span class="stat-label">进行中</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon purple">
            <BookOpen />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ projectStore.draftProjects.length }}</span>
            <span class="stat-label">草稿</span>
          </div>
        </div>
      </div>

      <section class="projects-section">
        <div class="section-header">
          <h2 class="section-title">我的项目</h2>
          <button class="refresh-btn" @click="handleRefresh">
            刷新
          </button>
        </div>

        <div v-if="projectStore.loading" class="loading-state">
          加载中...
        </div>

        <div v-else-if="projectStore.projects.length === 0" class="empty-state">
          <div class="empty-icon">
            <BookOpen />
          </div>
          <h3 class="empty-title">还没有项目</h3>
          <p class="empty-desc">点击上方按钮创建你的第一个项目</p>
          <button class="empty-action" @click="showCreateModal = true">
            <Plus />
            创建项目
          </button>
        </div>

        <div v-else class="projects-grid">
          <ProjectCard
            v-for="project in projectStore.projects"
            :key="project.id"
            :project="project"
          />
        </div>
      </section>
    </main>

    <CreateProjectModal
      :visible="showCreateModal"
      @close="showCreateModal = false"
      @created="handleCreated"
    />
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  margin-left: 260px;
  padding: 30px;
  overflow-y: auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
}

.create-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--primary-color);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.create-btn:hover {
  background: var(--primary-dark);
}

.btn-icon {
  font-size: 16px;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #fff;
}

.stat-icon.blue {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.stat-icon.green {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

.stat-icon.purple {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.projects-section {
  margin-top: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.refresh-btn {
  padding: 8px 16px;
  background: #f1f5f9;
  color: var(--text-secondary);
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.refresh-btn:hover {
  background: #e2e8f0;
}

.loading-state {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: var(--text-secondary);
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.empty-action {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--primary-color);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
</style>
