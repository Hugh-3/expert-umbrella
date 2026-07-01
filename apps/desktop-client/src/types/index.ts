export type ProjectType = 'novel' | 'music' | 'short_video' | 'micro_film'
export type ProjectStatus = 'draft' | 'in_progress' | 'completed' | 'archived'
export type ChapterStatus = 'outline' | 'draft' | 'editing' | 'finalized'
export type OperationType = 'ai_generate' | 'user_edit' | 'merge'
export type TaskType = 'outline' | 'chapter' | 'rewrite' | 'polish' | 'ideas'
export type TaskStatus = 'queued' | 'running' | 'completed' | 'failed' | 'interrupted'
export type EntityType = 'character' | 'location' | 'world_rule' | 'event' | 'item'

export interface Project {
  id: string
  name: string
  type: ProjectType
  status: ProjectStatus
  cover_image?: string
  metadata?: Record<string, unknown>
  owner_id?: string
  created_at: string
  updated_at: string
}

export interface ProjectListResponse {
  items: Project[]
  total: number
}

export interface Chapter {
  id: string
  project_id: string
  title: string
  order_index: number
  content: string
  word_count: number
  status: ChapterStatus
  version: number
  created_at: string
  updated_at: string
}

export interface VersionSnapshot {
  id: string
  chapter_id: string
  content: string
  operation_type: OperationType
  operator?: string
  diff_from_prev?: Record<string, unknown>
  created_at: string
}

export interface GenerationTask {
  id: string
  project_id: string
  chapter_id?: string
  task_type: TaskType
  status: TaskStatus
  model: string
  parameters?: Record<string, unknown>
  prompt?: string
  result?: string
  progress: number
  error?: string
  created_at: string
  completed_at?: string
}

export interface MemoryEntity {
  id: string
  project_id: string
  entity_type: EntityType
  name: string
  description?: string
  attributes?: Record<string, unknown>
  source_chapter_id?: string
  confidence: number
  created_at: string
  updated_at: string
}

export interface Feedback {
  id: string
  task_id: string
  overall_rating?: number
  creativity_rating?: number
  coherence_rating?: number
  style_rating?: number
  character_rating?: number
  issues?: string[]
  comment?: string
  created_at: string
}

export interface TimelineNode {
  stage: string
  status: 'completed' | 'in_progress' | 'pending'
  description: string
  completed_at?: string
}

export interface TimelineResponse {
  project_id: string
  stages: TimelineNode[]
}

export interface GenerateRequest {
  project_id: string
  chapter_id?: string
  task_type: TaskType
  model?: string
  parameters?: Record<string, unknown>
  prompt?: string
}

export interface GenerationEvent {
  event: 'start' | 'token' | 'sentence' | 'progress' | 'done' | 'error' | 'interrupted'
  data: GenerationEventData
}

export interface GenerationEventData {
  task_id: string
  content?: string
  position?: number
  sentence_id?: number
  percent?: number
  stage?: string
  final_content?: string
  word_count?: number
  error_code?: string
  message?: string
  partial_content?: string
  model?: string
  timestamp?: string
}

export interface SelfCheckItem {
  check_type: string
  passed: boolean
  details: string
}

export interface SelfCheckResponse {
  chapter_id: string
  overall_passed: boolean
  checks: SelfCheckItem[]
}

export interface LockStatus {
  resource: string
  locked: boolean
  holder?: string
  expires_at?: string
}
