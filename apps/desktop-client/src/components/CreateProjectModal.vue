<script setup lang="ts">
import { ref, watch } from 'vue'
import { Close } from '@element-plus/icons-vue'
import { useProjectStore } from '@/stores/project'
import type { ProjectType } from '@/types'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'created'): void
}>()

const projectStore = useProjectStore()
const projectName = ref('')
const projectType = ref<ProjectType>('novel')
const loading = ref(false)

watch(() => props.visible, (val) => {
  if (val) {
    projectName.value = ''
    projectType.value = 'novel'
  }
})

async function handleCreate() {
  if (!projectName.value.trim()) return
  
  loading.value = true
  try {
    await projectStore.createProject({
      name: projectName.value.trim(),
      type: projectType.value,
    })
    emit('created')
    emit('close')
  } catch {
  } finally {
    loading.value = false
  }
}

const typeOptions = [
  { label: '小说', value: 'novel' as ProjectType },
  { label: '音乐', value: 'music' as ProjectType },
  { label: '短视频', value: 'short_video' as ProjectType },
  { label: '微电影', value: 'micro_film' as ProjectType },
]
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">创建新项目</h2>
          <button class="close-btn" @click="$emit('close')">
            <Close />
          </button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">项目名称</label>
            <input
              class="form-input"
              v-model="projectName"
              placeholder="请输入项目名称"
              :disabled="loading"
            />
          </div>

          <div class="form-group">
            <label class="form-label">项目类型</label>
            <div class="type-grid">
              <button
                v-for="option in typeOptions"
                :key="option.value"
                class="type-card"
                :class="{ active: projectType === option.value }"
                @click="projectType = option.value"
              >
                <span class="type-label">{{ option.label }}</span>
              </button>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="$emit('close')" :disabled="loading">
            取消
          </button>
          <button
            class="btn btn-primary"
            @click="handleCreate"
            :disabled="loading || !projectName.trim()"
          >
            创建项目
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  width: 90%;
  max-width: 500px;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background: #e2e8f0;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  font-size: 14px;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.form-input:disabled {
  background: #f8fafc;
}

.type-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.type-card {
  padding: 16px;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  background: #fff;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.type-card:hover {
  border-color: var(--primary-light);
}

.type-card.active {
  border-color: var(--primary-color);
  background: rgba(99, 102, 241, 0.1);
}

.type-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.type-card.active .type-label {
  color: var(--primary-color);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e2e8f0;
  background: #fafafa;
}

.btn {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--primary-color);
  color: #fff;
}

.btn-primary:hover {
  background: var(--primary-dark);
}

.btn-secondary {
  background: #f1f5f9;
  color: var(--text-secondary);
}

.btn-secondary:hover {
  background: #e2e8f0;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
