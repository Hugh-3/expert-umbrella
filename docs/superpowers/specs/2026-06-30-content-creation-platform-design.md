# 内容创作自动化平台 — 设计规格书

> 版本: v2.0
> 日期: 2026-06-30
> 状态: 待审核
> 首期交付: 小说创作模块 (v1.0)

---

## 1. 项目概述

### 1.1 定位

一款支持小说、音乐、短视频、微电影等多模态内容创作的自动化平台，覆盖从创意构思、内容生成、编辑优化到最终输出的全流程。采用核心引擎 + 插件扩展架构，按内容类型分期交付，内置反馈回路与自检机制，支持持续迭代优化。

### 1.2 核心设计原则

- **模块解耦**: 各创作服务独立运行，单一模块故障不级联
- **多线程并行**: 任务级并行执行，充分利用硬件资源
- **混合 AI**: 本地模型 + 云端 API 协同，兼顾成本与能力
- **全自托管**: 数据与服务完全自主可控
- **可迭代**: 反馈机制驱动提示词与模型策略持续优化

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│              Desktop Client (Tauri 2.0)                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │ Dashboard│ │ Timeline │ │  Editor  │ │  Settings │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └───────────┘  │
│       │             │            │                       │
│  SSE流式渲染     版本对比    冲突合并编辑器              │
└───────────────┬───────────────┼─────────────────────────┘
                │               │
┌───────────────▼───────────────▼─────────────────────────┐
│                  API Gateway (Nginx)                    │
│          负载均衡 / 路由 / 限流 / SSE 转发               │
└─────────────────────────┬───────────────────────────────┘
                          │
     ┌────────────────────┼────────────────────┐
     ▼                    ▼                    ▼
┌──────────┐        ┌──────────┐        ┌──────────┐
│ Novel Svc│        │ Memory   │        │  RAG Svc │
│ (小说服务)│        │ Service  │        │ (检索服务)│
└────┬─────┘        └────┬─────┘        └────┬─────┘
     │                   │                   │
     └───────────────────┼───────────────────┘
                         ▼
               ┌───────────────────┐
               │  Message Queue    │
               │  (NATS JetStream) │
               └───────────────────┘
                         │
     ┌───────────────────┼───────────────────┐
     ▼                   ▼                   ▼
┌──────────┐      ┌──────────┐      ┌──────────────┐
│  AI Mix  │      │  Vector  │      │  Object      │
│ (混合引擎)│      │  DB      │      │  Storage     │
│          │      │(PGVector) │      │  (MinIO)     │
└──────────┘      └──────────┘      └──────────────┘
     │
     └─ Local (Ollama)  +  Cloud (GPT-4o / 星火)
```

### 2.2 架构风格

**微服务 + 事件驱动混合**

- 各创作服务（小说/音乐/视频）独立进程部署，通过 API 网关对外提供服务
- 服务间通过 NATS 消息队列异步通信，实现解耦
- 单服务内部采用多线程并行处理生成任务
- AI 调用层封装为各服务内部的公共 SDK 库（`ai-engine-sdk`），而非独立服务

### 2.3 服务职责边界

| 服务 | 职责 | 关键能力 |
|------|------|----------|
| Novel Service | 小说创作业务逻辑 | 大纲生成、章节撰写、改写润色、导出、版本管理 |
| Memory Service | 长期记忆管理 + RAG 检索 | 实体提取、记忆 CRUD、向量检索、混合检索管道 |
| *未来* Music Service | 音乐创作 | 旋律生成、编曲、混音（v1.5） |
| *未来* Video Service | 视频创作 | 脚本生成、剪辑、特效（v2.0） |

> **说明**：Memory Service 是首期第二个服务，负责长期记忆存储与 RAG 检索管道。AI 调用能力通过共享 SDK 提供给各创作服务，避免重复建设。

### 2.4 模块清单（首期）

| 模块 | 职责 | 技术栈 |
|------|------|--------|
| Desktop Client | 桌面端交互界面 | Tauri 2.0 + Vue 3 + TS |
| API Gateway | 路由、负载均衡、限流、SSE 转发 | Nginx |
| Novel Service | 小说创作核心业务逻辑 | Python + FastAPI |
| Memory Service | 长期记忆 + RAG 检索 | Python + FastAPI + LangChain |
| AI Engine SDK | 混合 AI 调用层（共享库） | Python |
| NATS | 消息队列 / 事件总线 | NATS JetStream |
| PostgreSQL | 关系数据库 + 向量扩展 | PGVector |
| Redis | 缓存 + 分布式锁 | Redis |
| MinIO | 对象存储（稿件、资产） | MinIO |

---

## 3. 首期交付：小说创作模块

### 3.1 功能范围

#### 3.1.1 智能创意生成

- 输入：主题关键词、类型标签、风格偏好、篇幅设定
- 输出：故事大纲（三幕式/五幕式）、人物设定卡、世界观概要、章节规划
- 支持：多方案生成（提供 N 个备选方案供选择）

#### 3.1.2 章节撰写

- 基于大纲逐章生成正文
- 支持续写（给定上下文继续）
- 支持改写（选定段落重写）
- 支持润色（风格调整、语气统一）
- **流式输出**：SSE 实时推送 token 到前端

#### 3.1.3 编辑优化

- 语法检查
- 风格一致性检测
- 逻辑连贯性自检
- 重复率检测
- 敏感词过滤

#### 3.1.4 多格式导出

- TXT（纯文本）
- Markdown
- EPUB（电子书格式）
- PDF

#### 3.1.5 项目管理

- 仪表盘：项目卡片展示（封面、名称、类型、进度、最近编辑）
- 时间线：创作阶段可视化（创意 → 大纲 → 章节 → 编辑 → 导出）
- 版本管理：每次 AI 生成自动保存版本，支持回滚与对比

---

## 4. 关键技术设计

### 4.1 流式输出 (Streaming)

#### 4.1.1 协议

- 主协议：SSE (Server-Sent Events)
- 备选：WebSocket（双向交互场景）
- 数据格式：`text/event-stream`

#### 4.1.2 事件类型

| 事件 | 说明 | 负载 |
|------|------|------|
| `start` | 生成开始 | `{ task_id, model, timestamp }` |
| `token` | 增量文本块 | `{ task_id, content, position }` |
| `sentence` | 完整句子 | `{ task_id, content, sentence_id }` |
| `progress` | 进度更新 | `{ task_id, percent, stage }` |
| `done` | 生成完成 | `{ task_id, final_content, word_count }` |
| `error` | 生成出错 | `{ task_id, error_code, message }` |
| `interrupted` | 被中断 | `{ task_id, partial_content }` |

#### 4.1.3 前端渲染策略

- **流式阶段**：纯文本追加渲染，不做 Markdown 解析（避免流式 Markdown 结构不稳定）
- **完成阶段**：`done` 事件触发后，统一进行 Markdown → HTML 渲染 + 安全清理
- 缓冲粒度：用户可配置（token 级 / 句子级 / 段级）

### 4.2 锁机制

#### 4.2.1 分布式读写锁

- 实现：基于 Redis Redlock
- 粒度：章节级 / 项目级
- 超时：默认 30 分钟，自动续期（心跳机制）

#### 4.2.2 锁类型

| 锁类型 | 场景 | 阻塞行为 |
|--------|------|----------|
| 写锁 | AI 生成章节、用户编辑 | 排他，阻塞其他写操作 |
| 读锁 | 预览、导出、只读查看 | 共享，允许多读 |

#### 4.2.3 冲突提示

获取写锁失败时，返回：
- 当前持有者信息（用户/任务 ID）
- 持有开始时间
- 预计剩余时间
- 操作建议（等待 / 只读查看 / 强制接管）

> **强制接管**：需二次确认，接管后原持有者收到通知，其未保存的变更将进入暂存区，避免数据丢失。

### 4.3 合并冲突提示

#### 4.3.1 冲突检测

- **段落级哈希**：每个段落计算哈希，检测变更范围
- **重叠检测**：AI 生成范围与用户编辑范围是否重叠
- **时间戳比对**：基于最后修改时间判断先后

#### 4.3.2 冲突处理策略

| 策略 | 触发条件 | 行为 |
|------|----------|------|
| 自动合并 | 双方变更段落无重叠 | 基于共同祖先，合并双方不同段落的修改 |
| 三向对比 | 存在重叠段落变更 | 展示原始 / AI版本 / 用户版本 三方 diff |
| 逐段解决 | 用户主动选择精细模式 | 按段落逐个确认保留哪一方或手动编辑 |
| 选择保留 | 快速处理，用户明确选择一方 | 整体保留某一方版本，另一方存为历史版本 |

#### 4.3.3 前端交互

- 类 Git diff 两侧对比视图
- 冲突段落高亮标注（颜色区分）
- 操作按钮：保留左 / 保留右 / 手动编辑 / 全部解决

### 4.4 长期记忆 / RAG 检索模块

#### 4.4.1 长期记忆 (Long-term Memory)

**存储内容**
- 世界观设定（地理、历史、规则体系）
- 人物档案（姓名、性格、外貌、关系网）
- 地点信息
- 关键事件时间线

**更新机制**
- 章节生成完成后，自动触发实体提取
- 提取结果经用户确认后入库
- 用户可手动编辑记忆条目

**存储结构**
- 向量空间：按项目独立划分
- 元数据：实体类型、来源章节、置信度
- 关系图谱：实体间关系（人物关系、地点从属等）

#### 4.4.2 RAG 检索

**检索策略**：混合检索
1. 向量相似度检索（语义匹配）
2. BM25 关键词检索（字面匹配）
3. 元数据过滤（按实体类型、章节范围）
4. 结果融合 + 重排序（Reranker）

**检索触发时机**
- 章节续写前：自动检索相关设定与前文摘要
- 人物/地点引用：自动召回背景信息
- 一致性自检：全文检索比对设定矛盾

**查询缓存**
- 相似查询结果缓存（余弦相似度 > 阈值直接返回）
- 缓存键：查询向量 + 过滤条件哈希
- TTL：可配置，默认 1 小时

#### 4.4.3 注意事项（来自历史经验）

- Prompt 模板中含变量的消息必须使用 `MessagePromptTemplate`，不能用字面量 `HumanMessage`，否则变量不会被渲染
- 流式输出与 Markdown 渲染需分层处理，避免 v-html 直接渲染流式内容带来的 XSS 和结构不稳定问题

---

## 5. 反馈与自检机制

### 5.1 反馈回路

```
用户评分/标注 → 反馈数据存储 → 分析面板 → 提示词优化 → 重新生成
     ↑                                                    │
     └──────────────── 长期记忆更新 ←───── RAG 检索 ↀ──────┘
```

**反馈维度**
- 整体质量评分（1-5 星）
- 维度评分（创意性 / 连贯性 / 风格匹配 / 人物塑造）
- 问题标注（逻辑错误 / 人设崩塌 / 重复 / 其他）
- 自由文本反馈

**优化机制**
- 低评分内容自动触发二次生成（调整温度/提示词）
- 反馈数据积累后，自动优化提示词模板
- 用户可保存自定义风格模板

### 5.2 自检模块

生成完成后自动运行以下检查：

| 检查项 | 方法 | 输出 |
|--------|------|------|
| 逻辑连贯性 | 前文摘要比对 + 设定一致性检索 | 冲突点列表 |
| 重复率 | 段落相似度矩阵 | 重复段落标注 |
| 敏感词 | 关键词匹配 + 模型审查 | 违规内容位置 |
| 人设一致性 | 人物档案 RAG 比对 | 矛盾行为标注 |
| 字数达标 | 简单计数 | 达标状态 |

自检报告随生成结果一同返回，用户可选择：
- 自动修复（可修复项）
- 手动修改
- 忽略通过

---

## 6. 项目管理界面

### 6.1 仪表盘视图

- 布局：卡片网格
- 每张卡片展示：
  - 项目封面（自动生成 / 自定义）
  - 项目名称 + 类型标签
  - 创作进度条
  - 最近编辑时间
  - 快捷操作（继续创作 / 查看 / 导出）

### 6.2 时间线视图

- 垂直时间线布局
- 每个节点代表一个创作阶段
- 阶段包括：
  1. 创意构思（生成大纲）
  2. 人物设定
  3. 章节规划
  4. 正文撰写（显示各章节完成状态）
  5. 编辑优化（自检 + 人工修改）
  6. 导出发布
- 点击阶段节点可快速跳转到对应编辑界面

### 6.3 版本管理

- 每次 AI 生成自动创建版本快照
- 版本列表：时间、操作类型、字数变化、操作者
- 支持：版本对比（diff）、回滚、标注版本标签（如 "v1.0 初稿"）

---

## 7. 技术选型详情

### 7.1 后端服务

| 组件 | 技术 | 版本 | 说明 |
|------|------|------|------|
| Web 框架 | FastAPI | 0.110+ | 异步高性能 |
| ORM | SQLAlchemy | 2.0+ | 异步支持 |
| 数据库 | PostgreSQL | 16+ | 关系型 + PGVector |
| 向量扩展 | PGVector | 0.7+ | 向量相似度检索 |
| 消息队列 | NATS JetStream | 2.10+ | 轻量、高性能 |
| 缓存/锁 | Redis | 7.0+ | 分布式锁、查询缓存 |
| 对象存储 | MinIO | latest | S3 兼容 |
| AI 框架 | LangChain | 0.3+ | RAG 管道 |
| 本地模型 | Ollama | latest | Llama3 系列 |

### 7.2 前端

| 组件 | 技术 | 说明 |
|------|------|------|
| 桌面框架 | Tauri 2.0 | Rust 后端 + WebView |
| UI 框架 | Vue 3 | Composition API |
| 语言 | TypeScript | 类型安全 |
| 构建工具 | Vite | 快速开发 |
| 状态管理 | Pinia | Vue 官方推荐 |
| UI 组件库 | Element Plus | 成熟稳定，组件丰富 |
| Markdown 渲染 | marked + DOMPurify | 安全渲染 |
| Diff 展示 | diff2html | 版本对比与冲突展示 |

### 7.3 部署

- 容器化：Docker + Docker Compose
- 反向代理：Nginx
- 进程管理：systemd / Docker restart policy

---

## 8. 数据模型（核心）

### 8.1 项目 (Project)

```
- id: UUID
- name: string
- type: enum (novel / music / short_video / micro_film)
- status: enum (draft / in_progress / completed / archived)
- cover_image: string (URL)
- metadata: JSON (类型特定配置)
- created_at: timestamp
- updated_at: timestamp
- owner_id: UUID
```

### 8.2 章节 (Chapter)

```
- id: UUID
- project_id: UUID (FK)
- title: string
- order_index: int
- content: text
- word_count: int
- status: enum (outline / draft / editing / finalized)
- version: int
- created_at: timestamp
- updated_at: timestamp
```

### 8.3 版本快照 (VersionSnapshot)

```
- id: UUID
- chapter_id: UUID (FK)
- content: text
- operation_type: enum (ai_generate / user_edit / merge)
- operator: string
- diff_from_prev: JSON
- created_at: timestamp
```

### 8.4 记忆实体 (MemoryEntity)

```
- id: UUID
- project_id: UUID (FK)
- entity_type: enum (character / location / world_rule / event / item)
- name: string
- description: text
- attributes: JSON
- embedding: vector
- source_chapter_id: UUID (FK, nullable)
- confidence: float
- created_at: timestamp
- updated_at: timestamp
```

### 8.5 生成任务 (GenerationTask)

```
- id: UUID
- project_id: UUID (FK)
- chapter_id: UUID (FK, nullable)
- task_type: enum (outline / chapter / rewrite / polish / ideas)
- status: enum (queued / running / completed / failed / interrupted)
- model: string
- parameters: JSON (温度、最大长度等)
- prompt: text
- result: text (nullable)
- progress: float
- error: string (nullable)
- created_at: timestamp
- completed_at: timestamp (nullable)
```

---

## 9. API 设计（核心接口）

### 9.1 项目管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/projects` | 获取项目列表 |
| POST | `/api/v1/projects` | 创建项目 |
| GET | `/api/v1/projects/{id}` | 获取项目详情 |
| PUT | `/api/v1/projects/{id}` | 更新项目 |
| DELETE | `/api/v1/projects/{id}` | 删除项目 |
| GET | `/api/v1/projects/{id}/timeline` | 获取项目时间线 |

### 9.2 章节管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/projects/{id}/chapters` | 获取章节列表 |
| POST | `/api/v1/projects/{id}/chapters` | 新建章节 |
| GET | `/api/v1/chapters/{id}` | 获取章节详情 |
| PUT | `/api/v1/chapters/{id}` | 更新章节 |
| GET | `/api/v1/chapters/{id}/versions` | 获取版本列表 |
| GET | `/api/v1/chapters/{id}/diff?from=v1&to=v2` | 版本对比 |
| POST | `/api/v1/chapters/{id}/rollback` | 回滚到指定版本 |

### 9.3 AI 生成（流式）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/generate/ideas` | 生成创意大纲 |
| POST | `/api/v1/generate/chapter` | 生成章节 (SSE) |
| POST | `/api/v1/generate/rewrite` | 改写段落 (SSE) |
| POST | `/api/v1/generate/polish` | 润色 (SSE) |
| POST | `/api/v1/generate/{task_id}/interrupt` | 中断生成 |
| GET | `/api/v1/generate/{task_id}/status` | 查询任务状态 |

### 9.4 锁操作

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/locks/acquire` | 获取锁 |
| POST | `/api/v1/locks/release` | 释放锁 |
| GET | `/api/v1/locks/status?resource=xxx` | 查询锁状态 |

### 9.5 长期记忆

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/memory/projects/{id}/entities` | 获取项目记忆实体 |
| POST | `/api/v1/memory/projects/{id}/entities` | 新增记忆实体 |
| PUT | `/api/v1/memory/entities/{id}` | 更新记忆实体 |
| DELETE | `/api/v1/memory/entities/{id}` | 删除记忆实体 |
| POST | `/api/v1/memory/projects/{id}/extract` | 从章节提取实体 |
| POST | `/api/v1/memory/projects/{id}/search` | 语义检索记忆 |

### 9.6 反馈与自检

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/feedback` | 提交反馈 |
| GET | `/api/v1/feedback/task/{task_id}` | 获取任务反馈 |
| POST | `/api/v1/self-check/chapter/{id}` | 触发章节自检 |
| GET | `/api/v1/self-check/{task_id}` | 获取自检报告 |

---

## 10. 非功能需求

### 10.1 性能

- 首 token 响应时间 < 3s（云端模型）
- 生成速度 > 30 tokens/s（本地模型，视硬件而定）
- 章节加载时间 < 1s（万字以内）
- 支持 10+ 并发生成任务

### 10.2 可靠性

- 单服务故障不影响其他服务
- 生成任务断点续传（网络中断后可恢复）
- 数据每日自动备份

### 10.3 安全性

- 用户认证（JWT）
- 项目数据隔离
- 敏感内容过滤
- 导出文件水印（可选）

### 10.4 可扩展性

- 插件化架构，新增内容类型只需新增服务
- 模型接入抽象层，支持新增 AI 供应商
- 水平扩展：无状态服务可多实例部署

---

## 11. 分期交付计划

| 阶段 | 内容 | 预估周期 |
|------|------|----------|
| v1.0 | 小说创作 + 核心引擎 + RAG + 反馈自检 | 首期 |
| v1.5 | 音乐创作模块 | 二期 |
| v2.0 | 短视频创作模块 | 三期 |
| v2.5 | 微电影创作模块 | 四期 |
| v3.0 | 多模态融合创作（图文音视频联动） | 远期 |

---

## 12. 风险与应对

| 风险 | 影响 | 应对策略 |
|------|------|----------|
| 本地模型质量不足 | 生成效果差 | 混合模式，关键环节走云端 |
| 向量检索准确率低 | RAG 召回不准 | 混合检索 + 重排序 + 用户反馈校准 |
| 合并冲突处理复杂 | 用户体验差 | 自动合并优先 + 渐进式手动介入 |
| 流式渲染不稳定 | 前端闪烁/错位 | 纯文本流式 + 完成后统一渲染 |
| 服务间依赖耦合 | 单点故障扩散 | 事件驱动 + 熔断降级 |
