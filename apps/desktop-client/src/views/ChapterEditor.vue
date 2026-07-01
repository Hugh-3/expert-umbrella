<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Check, VideoPlay, CircleCheck } from '@element-plus/icons-vue'
import { useChapterStore } from '@/stores/chapter'
import GenerationModal from '@/components/GenerationModal.vue'

const route = useRoute()
const router = useRouter()
const chapterStore = useChapterStore()

const content = ref('')
const showGenerationModal = ref(false)
const isSaving = ref(false)
const saveSuccess = ref(false)

onMounted(async () => {
  const chapterId = route.params.chapterId as string
  const chapter = await chapterStore.fetchChapter(chapterId)
  if (chapter) {
    content.value = chapter.content
  }
})

async function handleSave() {
  isSaving.value = true
  try {
    const chapterId = route.params.chapterId as string
    await chapterStore.updateChapter(chapterId, { content: content.value })
    saveSuccess.value = true
    setTimeout(() => {
      saveSuccess.value = false
    }, 2000)
  } catch {
  } finally {
    isSaving.value = false
  }
}

function handleGenerate() {
  showGenerationModal.value = true
}

function handleGenerationComplete(newContent: string) {
  content.value = newContent
  showGenerationModal.value = false
  handleSave()
}

function goBack() {
  router.push(`/project/${route.params.id}/chapters`)
}

function countWords() {
  return content.value.replace(/\s/g, '').length
}
</script>

<template>
  <div class="chapter-editor">
    <div class="editor-header">
      <div class="header-left">
        <button class="back-btn" @click="goBack">
          <ArrowLeft />
        </button>
        <div class="header-info">
          <h2 class="editor-title">{{ chapterStore.currentChapter?.title }}</h2>
          <span class="editor-subtitle">第 {{ chapterStore.currentChapter?.order_index + 1 }} 章</span>
        </div>
      </div>
      <div class="header-right">
        <span class="word-count">{{ countWords() }} 字</span>
        <button class="action-btn" @click="handleGenerate">
          <VideoPlay />
          AI生成
        </button>
        <button class="action-btn primary" @click="handleSave" :disabled="isSaving">
          <CircleCheck v-if="saveSuccess" />
          <Check v-else />
          {{ isSaving ? '保存中...' : (saveSuccess ? '已保存' : '保存') }}
        </button>
      </div>
    </div>

    <div class="editor-content">
      <textarea
        class="content-editor"
        v-model="content"
        placeholder="开始编写你的章节内容..."
      ></textarea>
    </div>

    <GenerationModal
      :visible="showGenerationModal"
      :project-id="route.params.id as string"
      :chapter-id="route.params.chapterId as string"
      @close="showGenerationModal = false"
      @complete="handleGenerationComplete"
    />
  </div>
</template>

<style scoped>
.chapter-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-radius: 12px 12px 0 0;
  border-bottom: 1px solid #e2e8f0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: none;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.back-btn:hover {
  background: #e2e8f0;
}

.header-info {
  display: flex;
  flex-direction: column;
}

.editor-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.editor-subtitle {
  font-size: 13px;
  color: var(--text-secondary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.word-count {
  font-size: 13px;
  color: var(--text-secondary);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.action-btn:not(.primary) {
  background: #f1f5f9;
  color: var(--text-secondary);
}

.action-btn:not(.primary):hover {
  background: #e2e8f0;
}

.action-btn.primary {
  background: var(--primary-color);
  color: #fff;
}

.action-btn.primary:hover {
  background: var(--primary-dark);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.editor-content {
  flex: 1;
  background: #fff;
  border-radius: 0 0 12px 12px;
  overflow: hidden;
}

.content-editor {
  width: 100%;
  height: 100%;
  padding: 24px;
  border: none;
  resize: none;
  font-size: 16px;
  line-height: 1.8;
  font-family: inherit;
  color: var(--text-primary);
}

.content-editor:focus {
  outline: none;
}

.content-editor::placeholder {
  color: var(--text-secondary);
}
</style>
