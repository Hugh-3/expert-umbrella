import type { Project, ProjectListResponse, Chapter, VersionSnapshot, GenerationTask, MemoryEntity, Feedback, TimelineResponse, GenerateRequest, SelfCheckResponse, LockStatus, ProjectStatus } from '@/types'

const BASE_URL = '/api/v1'

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '请求失败' }))
    throw new Error(error.detail || '请求失败')
  }

  return response.json()
}

export const projectApi = {
  list: (status?: ProjectStatus): Promise<ProjectListResponse> =>
    request(`/projects${status ? `?status=${status}` : ''}`),

  create: (data: Omit<Project, 'id' | 'created_at' | 'updated_at'>): Promise<Project> =>
    request('/projects', { method: 'POST', body: JSON.stringify(data) }),

  get: (id: string): Promise<Project> =>
    request(`/projects/${id}`),

  update: (id: string, data: Partial<Project>): Promise<Project> =>
    request(`/projects/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  delete: (id: string): Promise<void> =>
    request(`/projects/${id}`, { method: 'DELETE' }),

  getTimeline: (id: string): Promise<TimelineResponse> =>
    request(`/projects/${id}/timeline`),
}

export const chapterApi = {
  list: (projectId: string): Promise<Chapter[]> =>
    request(`/projects/${projectId}/chapters`),

  create: (projectId: string, data: Omit<Chapter, 'id' | 'project_id' | 'word_count' | 'version' | 'created_at' | 'updated_at'>): Promise<Chapter> =>
    request(`/projects/${projectId}/chapters`, { method: 'POST', body: JSON.stringify(data) }),

  get: (id: string): Promise<Chapter> =>
    request(`/chapters/${id}`),

  update: (id: string, data: Partial<Chapter>): Promise<Chapter> =>
    request(`/chapters/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  getVersions: (id: string): Promise<VersionSnapshot[]> =>
    request(`/chapters/${id}/versions`),

  getDiff: (id: string, from: string, to: string): Promise<{ from_version: string; to_version: string; diff: string }> =>
    request(`/chapters/${id}/diff?from=${from}&to=${to}`),

  rollback: (id: string, versionId: string): Promise<Chapter> =>
    request(`/chapters/${id}/rollback`, { method: 'POST', body: JSON.stringify({ version_id: versionId }) }),
}

export const generateApi = {
  ideas: (data: GenerateRequest): Promise<GenerationTask> =>
    request('/generate/ideas', { method: 'POST', body: JSON.stringify(data) }),

  chapter: (data: GenerateRequest): Promise<Response> =>
    fetch(`${BASE_URL}/generate/chapter`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  rewrite: (data: GenerateRequest): Promise<Response> =>
    fetch(`${BASE_URL}/generate/rewrite`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  polish: (data: GenerateRequest): Promise<Response> =>
    fetch(`${BASE_URL}/generate/polish`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  interrupt: (taskId: string): Promise<void> =>
    request(`/generate/${taskId}/interrupt`, { method: 'POST' }),

  getStatus: (taskId: string): Promise<GenerationTask> =>
    request(`/generate/${taskId}/status`),
}

export const memoryApi = {
  list: (projectId: string, entityType?: string): Promise<MemoryEntity[]> =>
    request(`/memory/projects/${projectId}/entities${entityType ? `?entity_type=${entityType}` : ''}`),

  create: (projectId: string, data: Omit<MemoryEntity, 'id' | 'project_id' | 'created_at' | 'updated_at'>): Promise<MemoryEntity> =>
    request(`/memory/projects/${projectId}/entities`, { method: 'POST', body: JSON.stringify(data) }),

  update: (id: string, data: Partial<MemoryEntity>): Promise<MemoryEntity> =>
    request(`/memory/entities/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  delete: (id: string): Promise<void> =>
    request(`/memory/entities/${id}`, { method: 'DELETE' }),

  extract: (projectId: string, chapterId: string): Promise<MemoryEntity[]> =>
    request(`/memory/projects/${projectId}/extract`, { method: 'POST', body: JSON.stringify({ chapter_id: chapterId }) }),

  search: (projectId: string, query: string): Promise<MemoryEntity[]> =>
    request(`/memory/projects/${projectId}/search`, { method: 'POST', body: JSON.stringify({ query }) }),
}

export const feedbackApi = {
  create: (data: Omit<Feedback, 'id' | 'created_at'>): Promise<Feedback> =>
    request('/feedback', { method: 'POST', body: JSON.stringify(data) }),

  getByTask: (taskId: string): Promise<Feedback[]> =>
    request(`/feedback/task/${taskId}`),

  selfCheck: (chapterId: string): Promise<SelfCheckResponse> =>
    request(`/self-check/chapter/${chapterId}`, { method: 'POST' }),
}

export const lockApi = {
  acquire: (resource: string, holder: string, lockType: string = 'write', timeout: number = 1800): Promise<{ acquired: boolean }> =>
    request('/locks/acquire', { method: 'POST', body: JSON.stringify({ resource, holder, lock_type: lockType, timeout }) }),

  release: (resource: string, holder: string): Promise<{ released: boolean }> =>
    request('/locks/release', { method: 'POST', body: JSON.stringify({ resource, holder }) }),

  getStatus: (resource: string): Promise<LockStatus> =>
    request(`/locks/status?resource=${resource}`),
}

export interface ExportFormat {
  id: string
  name: string
  description: string
}

export const exportApi = {
  getFormats: (): Promise<{ formats: ExportFormat[] }> =>
    request('/export/formats'),

  exportEpub: async (projectId: string, chapterIds?: string[]): Promise<void> => {
    const body = chapterIds && chapterIds.length > 0 ? JSON.stringify({ chapter_ids: chapterIds }) : undefined
    const response = await fetch(`${BASE_URL}/export/${projectId}/epub`, {
      method: 'POST',
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body,
    })
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: '导出失败' }))
      throw new Error(error.detail || '导出失败')
    }
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const contentDisposition = response.headers.get('content-disposition')
    let filename = 'export.epub'
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?([^"]+)"?/)
      if (match) filename = match[1]
    }
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  },

  exportPdf: async (projectId: string, chapterIds?: string[]): Promise<void> => {
    const body = chapterIds && chapterIds.length > 0 ? JSON.stringify({ chapter_ids: chapterIds }) : undefined
    const response = await fetch(`${BASE_URL}/export/${projectId}/pdf`, {
      method: 'POST',
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body,
    })
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: '导出失败' }))
      throw new Error(error.detail || '导出失败')
    }
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const contentDisposition = response.headers.get('content-disposition')
    let filename = 'export.pdf'
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?([^"]+)"?/)
      if (match) filename = match[1]
    }
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  },
}
