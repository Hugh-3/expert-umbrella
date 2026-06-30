<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { Plus, Search, Delete, Edit } from '@element-plus/icons-vue'
import { useMemoryStore } from '@/stores/memory'
import type { EntityType } from '@/types'

const route = useRoute()
const memoryStore = useMemoryStore()
const searchQuery = ref('')
const selectedType = ref<EntityType | ''>('')

onMounted(async () => {
  const projectId = route.params.id as string
  await memoryStore.fetchEntities(projectId)
})

function getEntityTypeText(type: string) {
  const map: Record<string, string> = {
    character: '人物',
    location: '地点',
    world_rule: '世界观规则',
    event: '事件',
    item: '物品',
  }
  return map[type] || type
}

function getEntityTypeColor(type: string) {
  const map: Record<string, string> = {
    character: 'bg-blue-100 text-blue-600',
    location: 'bg-green-100 text-green-600',
    world_rule: 'bg-purple-100 text-purple-600',
    event: 'bg-orange-100 text-orange-600',
    item: 'bg-gray-100 text-gray-600',
  }
  return map[type] || 'bg-gray-100 text-gray-600'
}

const filteredEntities = computed(() => {
  let entities = memoryStore.entities
  if (selectedType.value) {
    entities = entities.filter(e => e.entity_type === selectedType.value)
  }
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    entities = entities.filter(e => 
      e.name.toLowerCase().includes(query) || 
      (e.description && e.description.toLowerCase().includes(query))
    )
  }
  return entities
})

</script>

<template>
  <div class="memory-page">
    <div class="page-header">
      <h2 class="page-title">记忆实体</h2>
      <button class="add-btn">
        <Plus />
        添加实体
      </button>
    </div>

    <div class="filter-bar">
      <div class="search-box">
        <Search class="search-icon" />
        <input
          class="search-input"
          v-model="searchQuery"
          placeholder="搜索记忆实体..."
        />
      </div>
      <div class="type-filter">
        <select class="type-select" v-model="selectedType">
          <option value="">全部类型</option>
          <option value="character">人物</option>
          <option value="location">地点</option>
          <option value="world_rule">世界观规则</option>
          <option value="event">事件</option>
          <option value="item">物品</option>
        </select>
      </div>
    </div>

    <div v-if="memoryStore.loading" class="loading-state">
      加载中...
    </div>

    <div v-else-if="filteredEntities.length === 0" class="empty-state">
      <div class="empty-icon">
        <Search />
      </div>
      <h3 class="empty-title">暂无记忆实体</h3>
      <p class="empty-desc">添加或搜索相关的人物、地点、事件等</p>
    </div>

    <div v-else class="entities-grid">
      <div
        v-for="entity in filteredEntities"
        :key="entity.id"
        class="entity-card"
      >
        <div class="entity-header">
          <span class="entity-type" :class="getEntityTypeColor(entity.entity_type)">
            {{ getEntityTypeText(entity.entity_type) }}
          </span>
          <div class="entity-actions">
            <button class="action-btn"><Edit /></button>
            <button class="action-btn delete"><Delete /></button>
          </div>
        </div>
        <h3 class="entity-name">{{ entity.name }}</h3>
        <p class="entity-desc">{{ entity.description || '暂无描述' }}</p>
        <div class="entity-meta">
          <span class="confidence">置信度: {{ Math.round(entity.confidence * 100) }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.memory-page {
  max-width: 900px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--primary-color);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.add-btn:hover {
  background: var(--primary-dark);
}

.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 8px;
  padding: 0 16px;
  border: 1px solid #e2e8f0;
}

.search-icon {
  font-size: 16px;
  color: var(--text-secondary);
  margin-right: 12px;
}

.search-input {
  flex: 1;
  padding: 12px 0;
  border: none;
  font-size: 14px;
}

.search-input:focus {
  outline: none;
}

.type-select {
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  font-size: 14px;
  background: #fff;
  cursor: pointer;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: var(--text-secondary);
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: var(--text-secondary);
}

.entities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.entity-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.entity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.entity-type {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.entity-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: none;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.action-btn:hover {
  background: #e2e8f0;
}

.action-btn.delete:hover {
  background: #fee2e2;
  color: #ef4444;
}

.entity-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.entity-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.entity-meta {
  display: flex;
  justify-content: space-between;
}

.confidence {
  font-size: 12px;
  color: var(--text-secondary);
}
</style>
