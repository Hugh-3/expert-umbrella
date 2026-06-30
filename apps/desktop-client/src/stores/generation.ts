import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { GenerationTask, GenerateRequest, TaskType } from '@/types'
import { generateApi } from '@/api/http'
import { streamSSE } from '@/utils/sse'

export const useGenerationStore = defineStore('generation', () => {
  const currentTask = ref<GenerationTask | null>(null)
  const isGenerating = ref(false)
  const generatedContent = ref('')
  const progress = ref(0)
  const error = ref<string | null>(null)

  async function startGeneration(data: GenerateRequest, taskType: TaskType) {
    isGenerating.value = true
    generatedContent.value = ''
    progress.value = 0
    error.value = null

    try {
      let response: Response
      switch (taskType) {
        case 'chapter':
          response = await generateApi.chapter(data)
          break
        case 'rewrite':
          response = await generateApi.rewrite(data)
          break
        case 'polish':
          response = await generateApi.polish(data)
          break
        default:
          throw new Error(`Unsupported task type: ${taskType}`)
      }

      for await (const event of streamSSE(response)) {
        if (event.event === 'token') {
          generatedContent.value += event.data.content || ''
        } else if (event.event === 'progress') {
          progress.value = event.data.percent || 0
        } else if (event.event === 'done') {
          generatedContent.value = event.data.final_content || generatedContent.value
          progress.value = 100
          break
        } else if (event.event === 'error') {
          error.value = event.data.message || '生成失败'
          throw new Error(error.value)
        }
      }

      return generatedContent.value
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      isGenerating.value = false
    }
  }

  async function generateIdeas(data: GenerateRequest): Promise<GenerationTask> {
    isGenerating.value = true
    error.value = null
    try {
      const task = await generateApi.ideas(data)
      currentTask.value = task
      return task
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      isGenerating.value = false
    }
  }

  async function interruptTask(taskId: string): Promise<void> {
    try {
      await generateApi.interrupt(taskId)
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  async function getTaskStatus(taskId: string): Promise<GenerationTask> {
    try {
      const task = await generateApi.getStatus(taskId)
      currentTask.value = task
      return task
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  function resetState() {
    currentTask.value = null
    isGenerating.value = false
    generatedContent.value = ''
    progress.value = 0
    error.value = null
  }

  return {
    currentTask,
    isGenerating,
    generatedContent,
    progress,
    error,
    startGeneration,
    generateIdeas,
    interruptTask,
    getTaskStatus,
    resetState,
  }
})
