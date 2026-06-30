import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Project, ProjectStatus, TimelineResponse } from '@/types'
import { projectApi } from '@/api/http'

export const useProjectStore = defineStore('project', () => {
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const timeline = ref<TimelineResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const filteredProjects = computed(() => {
    return projects.value
  })

  const draftProjects = computed(() =>
    projects.value.filter(p => p.status === 'draft')
  )

  const inProgressProjects = computed(() =>
    projects.value.filter(p => p.status === 'in_progress')
  )

  async function fetchProjects(status?: ProjectStatus) {
    loading.value = true
    error.value = null
    try {
      const response = await projectApi.list(status)
      projects.value = response.items
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function createProject(data: Omit<Project, 'id' | 'created_at' | 'updated_at'>) {
    loading.value = true
    error.value = null
    try {
      const project = await projectApi.create(data)
      projects.value.unshift(project)
      return project
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchProject(id: string) {
    loading.value = true
    error.value = null
    try {
      const project = await projectApi.get(id)
      currentProject.value = project
      return project
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateProject(id: string, data: Partial<Project>) {
    loading.value = true
    error.value = null
    try {
      const project = await projectApi.update(id, data)
      const index = projects.value.findIndex(p => p.id === id)
      if (index !== -1) {
        projects.value[index] = project
      }
      if (currentProject.value?.id === id) {
        currentProject.value = project
      }
      return project
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteProject(id: string) {
    loading.value = true
    error.value = null
    try {
      await projectApi.delete(id)
      projects.value = projects.value.filter(p => p.id !== id)
      if (currentProject.value?.id === id) {
        currentProject.value = null
      }
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchTimeline(id: string) {
    loading.value = true
    error.value = null
    try {
      const result = await projectApi.getTimeline(id)
      timeline.value = result
      return result
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  function setCurrentProject(project: Project | null) {
    currentProject.value = project
  }

  return {
    projects,
    currentProject,
    timeline,
    loading,
    error,
    filteredProjects,
    draftProjects,
    inProgressProjects,
    fetchProjects,
    createProject,
    fetchProject,
    updateProject,
    deleteProject,
    fetchTimeline,
    setCurrentProject,
  }
})
