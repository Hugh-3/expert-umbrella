<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, VideoPlay, DocumentChecked, Edit, Download } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useChapterStore } from '@/stores/chapter'
import GenerationModal from '@/components/GenerationModal.vue'
import { exportApi } from '@/api/http'

const route = useRoute()
const router = useRouter()
const chapterStore = useChapterStore()
const showGenerationModal = ref(false)
const selectedChapterId = ref<string | undefined>(undefined)
const exporting = ref(false)

onMounted(async () => {
  const projectId = route.params.id as string
  await chapterStore.fetchChapters(projectId)
})

function handleAddChapter() {
  const projectId = route.params.id as string
  chapterStore.createChapter(projectId, {
    title: '新章节',
    order_index: chapterStore.chapters.length,
  }).then(() => {
    chapterStore.fetchChapters(projectId)
  })
}

function handleGenerate(chapterId?: string) {
  selectedChapterId.value = chapterId
  showGenerationModal.value = true
}

function handleGenerationComplete(content: string) {
  if (selectedChapterId.value) {
    chapterStore.updateChapter(selectedChapterId.value, { content })
  }
  showGenerationModal.value = false
}

async function handleExport(format: 'epub' | 'pdf') {
  const projectId = route.params.id as string
  if (chapterStore.chapters.length === 0) {
    ElMessage.warning('没有可导出的章节')
    return
  }
  try {
    exporting.value = true
    if (format === 'epub') {
      await exportApi.exportEpub(projectId)
    } else {
      await exportApi.exportPdf(projectId)
    }
    ElMessage.success(`导出${format.toUpperCase()}成功`)
  } catch (e: any) {
    ElMessage.error(e.message || '导出失败')
  } finally {
    exporting.value = false
  }
}

async function handleExportMenu() {
  try {
    const { value } = await ElMessageBox({
      title: '导出选项',
      message: '请选择导出格式',
      showCancelButton: true,
      confirmButtonText: 'EPUB',
      cancelButtonText: 'PDF',
      distinguishCancelAndClose: true,
    })
    if (value === 'confirm') {
      handleExport('epub')
    } else if (value === 'cancel') {
      handleExport('pdf')
    }
  } catch {
  }
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    outline: '大纲',
    draft: '草稿',
    editing: '编辑中',
    finalized: '已定稿',
  }
  return map[status] || status
}

function getStatusClass(status: string) {
  const map: Record<string, string> = {
    outline: 'status-outline',
    draft: 'status-draft',
    editing: 'status-editing',
    finalized: 'status-finalized',
  }
  return map[status] || 'status-outline'
}
</script>

<template>
  <div class="chapters-page">
    <div class="page-header">
      <h2 class="page-title">章节管理</h2>
      <div class="header-actions">
        <button class="export-btn" @click="handleExport('epub')" :disabled="exporting">
          <Download />
          导出EPUB
        </button>
        <button class="export-btn" @click="handleExport('pdf')" :disabled="exporting">
          <Download />
          导出PDF
        </button>
        <button class="add-btn" @click="handleAddChapter">
          <Plus />
          添加章节
        </button>
      </div>
    </div>

    <div v-if="chapterStore.loading" class="loading-state">
      加载中...
    </div>

    <div v-else-if="chapterStore.chapters.length === 0" class="empty-state">
      <div class="empty-icon">
        <Edit />
      </div>
      <h3 class="empty-title">还没有章节</h3>
      <p class="empty-desc">点击上方按钮添加章节</p>
    </div>

    <div v-else class="chapters-list">
      <div
        v-for="chapter in chapterStore.chapters"
        :key="chapter.id"
        class="chapter-item"
      >
        <div class="chapter-header">
          <div class="chapter-info">
            <span class="chapter-number">{{ chapter.order_index + 1 }}</span>
            <div class="chapter-title-wrap">
              <h3 class="chapter-title">{{ chapter.title }}</h3>
              <span class="chapter-status" :class="getStatusClass(chapter.status)">
                {{ getStatusText(chapter.status) }}
              </span>
            </div>
          </div>
          <span class="chapter-word-count">{{ chapter.word_count }} 字</span>
        </div>

        <p class="chapter-preview">
          {{ chapter.content.slice(0, 100) }}{{ chapter.content.length > 100 ? '...' : '' }}
        </p>

        <div class="chapter-actions">
          <button class="action-btn" @click="router.push(`/project/${route.params.id}/chapter/${chapter.id}`)">
            <Edit />
            编辑
          </button>
          <button class="action-btn" @click="handleGenerate(chapter.id)">
            <VideoPlay />
            AI生成
          </button>
        </div>
      </div>
    </div>

    <GenerationModal
      :visible="showGenerationModal"
      :project-id="route.params.id as string"
      :chapter-id="selectedChapterId"
      @close="showGenerationModal = false"
      @complete="handleGenerationComplete"
    />
  </div>
</template>

<style scoped>
.chapters-page {
  max-width: 800px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--primary-color);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.add-btn:hover {
  background: var(--primary-dark);
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: #fff;
  color: var(--text-primary);
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.export-btn:hover:not(:disabled) {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.export-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: var(--text-secondary);
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: var(--text-secondary);
}

.chapters-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chapter-item {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.chapter-info {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.chapter-number {
  width: 32px;
  height: 32px;
  background: var(--primary-color);
  color: #fff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.chapter-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chapter-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.chapter-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.status-outline {
  background: #f1f5f9;
  color: var(--text-secondary);
}

.status-draft {
  background: #fef3c7;
  color: #d97706;
}

.status-editing {
  background: #dbeafe;
  color: #2563eb;
}

.status-finalized {
  background: #dcfce7;
  color: #16a34a;
}

.chapter-word-count {
  font-size: 13px;
  color: var(--text-secondary);
}

.chapter-preview {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 16px;
  overflow: hidden;
}

.chapter-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.action-btn:nth-child(1) {
  background: #f1f5f9;
  color: var(--text-secondary);
}

.action-btn:nth-child(1):hover {
  background: #e2e8f0;
}

.action-btn:nth-child(2) {
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary-color);
}

.action-btn:nth-child(2):hover {
  background: rgba(99, 102, 241, 0.2);
}
</style>
