# Memory Service - 向量检索与 RAG 管道

## 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                      Memory Service                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  FastAPI     │  │  RAG Pipeline │  │  Embedding Service   │   │
│  │  REST API    │  │  (检索增强)    │  │  (向量生成)           │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘   │
│         │                 │                     │               │
│  ┌──────▼─────────────────▼─────────────────────▼───────────┐   │
│  │                    Vector Store (Qdrant)                  │   │
│  │              向量数据库 - 存储 & 检索嵌入向量               │   │
│  └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    外部依赖服务                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │    Ollama    │  │    Redis     │  │     PostgreSQL       │   │
│  │  (嵌入模型)   │  │   (缓存)      │  │    (可选 - 主数据)    │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 核心功能

### 1. 向量检索 (Vector Search)
- 使用 Qdrant 作为向量数据库
- 支持余弦相似度、欧几里得距离、点积距离
- 可配置的向量维度 (默认 1536)
- 实时向量相似度搜索

### 2. RAG 管道 (RAG Pipeline)
- **检索 (Retrieval)**: 从向量库中检索相关记忆实体
- **上下文构建 (Context Building)**: 聚合检索结果
- **元数据丰富**: 添加相关性评分、类型分组等

### 3. 嵌入服务 (Embedding Service)
支持多种嵌入提供商:
- **Ollama**: 本地部署，支持 nomic-embed-text 等模型
- **OpenAI**: 使用 OpenAI Embeddings API
- **Mock**: 测试用随机向量

## API 端点

### 健康检查
```
GET /health
```

### 统计信息
```
GET /stats?project_id=xxx
```

### 实体管理
```
POST /entities                    # 创建实体 (自动生成向量)
POST /entities/batch              # 批量创建
DELETE /entities/{entity_id}      # 删除实体
DELETE /entities/project/{project_id}  # 删除项目所有实体
```

### 向量搜索
```
POST /search
{
  "query": "主角的成长经历",
  "project_id": "xxx",
  "entity_types": ["character", "event"],
  "limit": 5
}
```

### RAG 上下文
```
POST /rag/context
{
  "query": "故事中的主要冲突",
  "project_id": "xxx",
  "entity_types": ["event", "character"]
}
```

### RAG 摘要
```
POST /rag/summary
{
  "query": "世界观设定",
  "project_id": "xxx"
}
```

## 部署

### 快速启动
```bash
cd services/memory-service
cp .env.example .env

# 启动所有服务
docker compose up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f memory-service
```

### Ollama 模型准备
```bash
# 进入 Ollama 容器
docker exec -it memory-ollama ollama run nomic-embed-text

# 或者直接拉取模型
docker exec memory-ollama ollama pull nomic-embed-text
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| QDRANT_PORT | 6333 | Qdrant HTTP 端口 |
| QDRANT_GRPC_PORT | 6334 | Qdrant gRPC 端口 |
| MEMORY_SERVICE_PORT | 8001 | Memory Service 端口 |
| OLLAMA_PORT | 11434 | Ollama API 端口 |
| EMBEDDING_PROVIDER | ollama | 嵌入提供商: ollama/openai/mock |
| EMBEDDING_MODEL | nomic-embed-text | 嵌入模型名称 |
| EMBEDDING_VECTOR_SIZE | 768 | 向量维度 |
| RAG_TOP_K | 5 | 检索返回数量 |
| RAG_SCORE_THRESHOLD | 0.7 | 相似度阈值 |

## 与主服务集成

Memory Service 可以独立运行，也可以与 novel-service 集成:

1. **同步模式**: novel-service 写入 PostgreSQL，Memory Service 同步创建向量
2. **旁路模式**: Memory Service 作为独立向量检索服务，供 AI 生成时调用
3. **缓存模式**: 使用 Memory Service 的 Redis 缓存加速检索
