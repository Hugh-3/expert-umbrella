import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Chapter, VersionSnapshot } from '@/types'
import { chapterApi } from '@/api/http'

export const useChapterStore = defineStore('chapter', () => {
  const chapters = ref<Chapter[]>([])
  const currentChapter = ref<Chapter | null>(null)
  const versions = ref<VersionSnapshot[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchChapters(projectId: string) {
    loading.value = true
    error.value = null
    try {
      chapters.value = await chapterApi.list(projectId)
      return chapters.value
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createChapter(projectId: string, data: Omit<Chapter, 'id' | 'project_id' | 'word_count' | 'version' | 'created_at' | 'updated_at'>) {
    loading.value = true
    error.value = null
    try {
      const chapter = await chapterApi.create(projectId, data)
      chapters.value.push(chapter)
      chapters.value.sort((a, b) => a.order_index - b.order_index)
      return chapter
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchChapter(id: string) {
    loading.value = true
    error.value = null
    try {
      const chapter = await chapterApi.get(id)
      currentChapter.value = chapter
      return chapter
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateChapter(id: string, data: Partial<Chapter>) {
    loading.value = true
    error.value = null
    try {
      const chapter = await chapterApi.update(id, data)
      const index = chapters.value.findIndex(c => c.id === id)
      if (index !== -1) {
        chapters.value[index] = chapter
      }
      if (currentChapter.value?.id === id) {
        currentChapter.value = chapter
      }
      return chapter
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchVersions(chapterId: string) {
    loading.value = true
    error.value = null
    try {
      versions.value = await chapterApi.getVersions(chapterId)
      return versions.value
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function getDiff(chapterId: string, from: string, to: string) {
    loading.value = true
    error.value = null
    try {
      return await chapterApi.getDiff(chapterId, from, to)
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function rollback(chapterId: string, versionId: string) {
    loading.value = true
    error.value = null
    try {
      const chapter = await chapterApi.rollback(chapterId, versionId)
      const index = chapters.value.findIndex(c => c.id === chapterId)
      if (index !== -1) {
        chapters.value[index] = chapter
      }
      if (currentChapter.value?.id === chapterId) {
        currentChapter.value = chapter
      }
      return chapter
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  function setCurrentChapter(chapter: Chapter | null) {
    currentChapter.value = chapter
  }

  return {
    chapters,
    currentChapter,
    versions,
    loading,
    error,
    fetchChapters,
    createChapter,
    fetchChapter,
    updateChapter,
    fetchVersions,
    getDiff,
    rollback,
    setCurrentChapter,
  }
})
