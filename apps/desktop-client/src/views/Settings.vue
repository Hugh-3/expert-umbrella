<script setup lang="ts">
import { ref } from 'vue'
import { Check, Reading, Cpu, Lock } from '@element-plus/icons-vue'
import Sidebar from '@/components/Sidebar.vue'

const aiProvider = ref('mock')
const apiKey = ref('')
const baseUrl = ref('')
const model = ref('gpt-4o')
const temperature = ref(0.7)
const maxTokens = ref(4096)
const language = ref('zh')

const aiProviders = [
  { label: 'Mock (测试)', value: 'mock' },
  { label: 'OpenAI', value: 'openai' },
  { label: 'Ollama (本地)', value: 'ollama' },
]

const languages = [
  { label: '中文', value: 'zh' },
  { label: 'English', value: 'en' },
  { label: '日本語', value: 'ja' },
]

function handleSave() {
}
</script>

<template>
  <div class="settings-page">
    <Sidebar />
    
    <main class="main-content">
      <header class="page-header">
        <h1 class="page-title">设置</h1>
      </header>

      <div class="settings-container">
        <section class="settings-section">
          <div class="section-header">
            <Cpu class="section-icon" />
            <h2 class="section-title">AI 配置</h2>
          </div>

          <div class="form-group">
            <label class="form-label">AI Provider</label>
            <div class="provider-selector">
              <button
                v-for="provider in aiProviders"
                :key="provider.value"
                class="provider-btn"
                :class="{ active: aiProvider === provider.value }"
                @click="aiProvider = provider.value"
              >
                {{ provider.label }}
              </button>
            </div>
          </div>

          <div v-if="aiProvider === 'openai'" class="form-group">
            <label class="form-label">API Key</label>
            <input
              class="form-input"
              v-model="apiKey"
              type="password"
              placeholder="sk-..."
            />
          </div>

          <div v-if="aiProvider !== 'mock'" class="form-group">
            <label class="form-label">Base URL</label>
            <input
              class="form-input"
              v-model="baseUrl"
              :placeholder="aiProvider === 'openai' ? 'https://api.openai.com/v1' : 'http://localhost:11434'"
            />
          </div>

          <div class="form-group">
            <label class="form-label">模型</label>
            <input
              class="form-input"
              v-model="model"
              placeholder="gpt-4o"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">温度 (Temperature)</label>
              <input
                class="form-input"
                v-model.number="temperature"
                type="range"
                min="0"
                max="2"
                step="0.1"
              />
              <span class="range-value">{{ temperature }}</span>
            </div>
            <div class="form-group">
              <label class="form-label">最大 Token 数</label>
              <input
                class="form-input"
                v-model.number="maxTokens"
                type="number"
                min="512"
                max="16384"
              />
            </div>
          </div>
        </section>

        <section class="settings-section">
          <div class="section-header">
            <Reading class="section-icon" />
            <h2 class="section-title">语言设置</h2>
          </div>

          <div class="form-group">
            <label class="form-label">界面语言</label>
            <div class="language-selector">
              <button
                v-for="lang in languages"
                :key="lang.value"
                class="language-btn"
                :class="{ active: language === lang.value }"
                @click="language = lang.value"
              >
                {{ lang.label }}
              </button>
            </div>
          </div>
        </section>

        <section class="settings-section">
          <div class="section-header">
            <Lock class="section-icon" />
            <h2 class="section-title">安全设置</h2>
          </div>

          <div class="form-group">
            <label class="form-label">敏感内容过滤</label>
            <div class="toggle-switch">
              <input type="checkbox" id="safe-filter" checked />
              <label for="safe-filter"></label>
              <span>启用敏感内容自动过滤</span>
            </div>
          </div>
        </section>

        <div class="save-section">
          <button class="save-btn" @click="handleSave">
            <Check />
            保存设置
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.settings-page {
  display: flex;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  margin-left: 260px;
  padding: 30px;
}

.page-header {
  margin-bottom: 30px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.settings-container {
  max-width: 700px;
}

.settings-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.section-icon {
  font-size: 20px;
  color: var(--primary-color);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
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

.provider-selector, .language-selector {
  display: flex;
  gap: 10px;
}

.provider-btn, .language-btn {
  flex: 1;
  padding: 12px 16px;
  border-radius: 8px;
  border: 2px solid #e2e8f0;
  background: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.provider-btn:hover, .language-btn:hover {
  border-color: var(--primary-light);
}

.provider-btn.active, .language-btn.active {
  border-color: var(--primary-color);
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary-color);
}

.range-value {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 8px;
}

.toggle-switch {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-switch input {
  display: none;
}

.toggle-switch label {
  width: 48px;
  height: 24px;
  background: #e2e8f0;
  border-radius: 12px;
  position: relative;
  cursor: pointer;
  transition: background-color 0.2s;
}

.toggle-switch label::before {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 50%;
  top: 2px;
  left: 2px;
  transition: transform 0.2s;
}

.toggle-switch input:checked + label {
  background: var(--primary-color);
}

.toggle-switch input:checked + label::before {
  transform: translateX(24px);
}

.toggle-switch span {
  font-size: 14px;
  color: var(--text-primary);
}

.save-section {
  display: flex;
  justify-content: flex-end;
  padding-top: 20px;
}

.save-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 28px;
  background: var(--primary-color);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.save-btn:hover {
  background: var(--primary-dark);
}
</style>
