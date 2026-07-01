<script setup lang="ts">import { ref, watch } from 'vue';
import { Close, VideoPlay, Delete, Loading } from '@element-plus/icons-vue';
import { useGenerationStore } from '@/stores/generation';
import type { GenerateRequest, TaskType } from '@/types';
const props = defineProps<{
 visible: boolean;
 projectId: string;
 chapterId?: string;
}>();
const emit = defineEmits<{
 (e: 'close'): void;
 (e: 'complete', content: string): void;
}>();
const generationStore = useGenerationStore();
const taskType = ref<TaskType>('chapter');
const prompt = ref('');
const isGenerating = ref(false);
const generatedContent = ref('');
const progress = ref(0);
watch(() => props.visible, (val) => {
 if (!val) {
 generatedContent.value = '';
 progress.value = 0;
 isGenerating.value = false;
 generationStore.resetState();
 }
});
async function startGeneration() {
 isGenerating.value = true;
 generatedContent.value = '';
 progress.value = 0;
 try {
 const data: GenerateRequest = {
 project_id: props.projectId,
 chapter_id: props.chapterId,
 task_type: taskType.value,
 prompt: prompt.value || undefined,
 };
 const content = await generationStore.startGeneration(data, taskType.value);
 generatedContent.value = content;
 emit('complete', content);
 }
 catch {
 }
 finally {
 isGenerating.value = false;
 }
}
function handleInterrupt() {
 generationStore.interruptTask(generationStore.currentTask?.id || '');
 isGenerating.value = false;
}
function handleClose() {
 if (!isGenerating.value) {
 emit('close');
 }
}
const taskTypeOptions = [
 { label: '生成章节', value: 'chapter' as TaskType },
 { label: '改写', value: 'rewrite' as TaskType },
 { label: '润色', value: 'polish' as TaskType },
];
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="handleClose">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">AI 内容生成</h2>
          <button class="close-btn" @click="handleClose">
            <Close />
          </button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">任务类型</label>
            <div class="type-selector">
              <button
                v-for="option in taskTypeOptions"
                :key="option.value"
                class="type-btn"
                :class="{ active: taskType === option.value }"
                @click="taskType = option.value"
              >
                {{ option.label }}
              </button>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">提示词（可选）</label>
            <textarea
              class="prompt-textarea"
              v-model="prompt"
              placeholder="输入你想要生成的内容描述..."
              :disabled="isGenerating"
            ></textarea>
          </div>

          <div v-if="isGenerating" class="generation-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
            </div>
            <span class="progress-text">{{ Math.round(progress) }}%</span>
          </div>

          <div v-if="generatedContent" class="generation-result">
            <label class="form-label">生成结果</label>
            <div class="result-content">{{ generatedContent }}</div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="handleClose" :disabled="isGenerating">
            取消
          </button>
          <button v-if="!isGenerating" class="btn btn-primary" @click="startGeneration">
            <VideoPlay class="btn-icon" />
            开始生成
          </button>
          <button v-else class="btn btn-danger" @click="handleInterrupt">
            <Delete class="btn-icon" />
            中断
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
  max-width: 700px;
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
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.type-selector {
  display: flex;
  gap: 10px;
}

.type-btn {
  padding: 10px 20px;
  border-radius: 8px;
  border: 2px solid #e2e8f0;
  background: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.type-btn:hover {
  border-color: var(--primary-light);
}

.type-btn.active {
  border-color: var(--primary-color);
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary-color);
}

.prompt-textarea {
  width: 100%;
  height: 100px;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  resize: vertical;
  font-size: 14px;
  font-family: inherit;
}

.prompt-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
}

.prompt-textarea:disabled {
  background: #f8fafc;
}

.generation-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-color);
  border-radius: 4px;
  transition: width 0.3s;
}

.progress-text {
  font-size: 14px;
  color: var(--text-secondary);
  min-width: 50px;
  text-align: right;
}

.generation-result {
  margin-top: 20px;
}

.result-content {
  max-height: 300px;
  overflow-y: auto;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
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
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-icon {
  font-size: 14px;
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

.btn-danger {
  background: #ef4444;
  color: #fff;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
