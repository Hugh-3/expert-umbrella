import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { MemoryEntity, EntityType } from '@/types'
import { memoryApi } from '@/api/http'

export const useMemoryStore = defineStore('memory', () => {
  const entities = ref<MemoryEntity[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchEntities(projectId: string, entityType?: EntityType) {
    loading.value = true
    error.value = null
    try {
      entities.value = await memoryApi.list(projectId, entityType)
      return entities.value
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createEntity(projectId: string, data: Omit<MemoryEntity, 'id' | 'project_id' | 'created_at' | 'updated_at'>) {
    loading.value = true
    error.value = null
    try {
      const entity = await memoryApi.create(projectId, data)
      entities.value.push(entity)
      return entity
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateEntity(id: string, data: Partial<MemoryEntity>) {
    loading.value = true
    error.value = null
    try {
      const entity = await memoryApi.update(id, data)
      const index = entities.value.findIndex(e => e.id === id)
      if (index !== -1) {
        entities.value[index] = entity
      }
      return entity
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteEntity(id: string) {
    loading.value = true
    error.value = null
    try {
      await memoryApi.delete(id)
      entities.value = entities.value.filter(e => e.id !== id)
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function extractEntities(projectId: string, chapterId: string) {
    loading.value = true
    error.value = null
    try {
      const newEntities = await memoryApi.extract(projectId, chapterId)
      entities.value = [...new Set([...entities.value, ...newEntities])]
      return newEntities
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function searchEntities(projectId: string, query: string) {
    loading.value = true
    error.value = null
    try {
      return await memoryApi.search(projectId, query)
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    entities,
    loading,
    error,
    fetchEntities,
    createEntity,
    updateEntity,
    deleteEntity,
    extractEntities,
    searchEntities,
  }
})
