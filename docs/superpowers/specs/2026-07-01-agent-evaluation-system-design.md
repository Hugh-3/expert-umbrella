# 智能体评测与反馈系统 - 设计规格书

> 版本: v1.0
> 日期: 2026-07-01
> 状态: 已批准

---

## 1. 项目概述

### 1.1 定位

为内容创作自动化平台（Content Creation Platform）构建两个协同工作的智能体系统：
- **用户智能体**：从典型用户视角全面体验和评估平台功能
- **反馈智能体**：分析评价报告，制定并验证优化方案

两个智能体形成"体验-评价-优化-再体验"的闭环，持续提升项目质量和用户满意度。

### 1.2 设计原则

- **模块解耦**：两个智能体共享核心组件，但职责边界清晰
- **混合评估**：结合 API 实际调用和代码静态分析
- **量化验证**：通过评分指标和趋势数据量化改进效果
- **轻量部署**：使用 SQLite 存储，零外部依赖

---

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                   Agent Service (单体服务)                    │
│                                                              │
│  ┌─────────────────┐    ┌─────────────────┐                 │
│  │  User Agent     │    │ Feedback Agent  │                 │
│  │  (用户智能体)     │◄──►│ (反馈智能体)    │                 │
│  └────────┬────────┘    └────────┬────────┘                 │
│           │                        │                         │
│  ┌────────▼────────────────────────▼────────┐              │
│  │         Evaluation Engine (评估引擎)        │              │
│  │  - 功能完整性检查                            │              │
│  │  - 易用性评估                                │              │
│  │  - 性能分析                                  │              │
│  │  - 界面设计评估                              │              │
│  └─────────────────────┬─────────────────────┘              │
│                        │                                     │
│  ┌─────────────────────▼─────────────────────┐              │
│  │         Storage Layer (SQLite)            │              │
│  │  - 评价报告历史                            │              │
│  │  - 优化建议记录                            │              │
│  │  - 指标趋势数据                            │              │
│  └───────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
              │                    │
              ▼                    ▼
┌──────────────────┐    ┌──────────────────┐
│  Novel Service   │    │  Code Analysis   │
│  (HTTP API)      │    │  (AST Parser)    │
└──────────────────┘    └──────────────────┘
```

### 2.2 组件职责

| 组件 | 职责 |
|------|------|
| User Agent | 模拟用户行为，调用 API 体验功能，分析代码结构，生成评价报告 |
| Feedback Agent | 接收评价报告，制定优化方案，触发验证流程 |
| Evaluation Engine | 提供评估算法、评分模型、指标计算 |
| Storage Layer | SQLite 数据库，存储历史数据和趋势 |

### 2.3 与外部系统交互

- **Novel Service API**：通过 HTTP 调用创建项目、生成章节、导出内容等
- **Memory Service API**：测试记忆提取和检索功能
- **文件系统**：分析 `services/novel-service/` 和 `apps/desktop-client/` 目录下的代码

---

## 3. 数据模型

### 3.1 数据库 Schema

```sql
-- 评价报告表
CREATE TABLE evaluation_reports (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    target_project_path TEXT,
    target_api_url TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    functionality_score REAL,
    usability_score REAL,
    performance_score REAL,
    ui_design_score REAL,
    overall_score REAL,
    summary TEXT,
    findings TEXT,  -- JSON array
    suggestions TEXT,  -- JSON array
    raw_metrics TEXT,  -- JSON object
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 优化方案表
CREATE TABLE optimization_plans (
    id TEXT PRIMARY KEY,
    evaluation_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending, in_progress, completed, verified
    priority_summary TEXT,
    improvements TEXT,  -- JSON array
    code_suggestions TEXT,  -- JSON array
    verification_result TEXT,  -- JSON object
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_id) REFERENCES evaluation_reports(id)
);

-- 评估历史快照表（用于趋势分析）
CREATE TABLE evaluation_snapshots (
    id TEXT PRIMARY KEY,
    evaluation_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    score REAL NOT NULL,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_id) REFERENCES evaluation_reports(id)
);

-- 优化验证记录表
CREATE TABLE verification_records (
    id TEXT PRIMARY KEY,
    optimization_id TEXT NOT NULL,
    before_evaluation_id TEXT,
    after_evaluation_id TEXT,
    improvement_summary TEXT,  -- JSON object
    verified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (optimization_id) REFERENCES optimization_plans(id)
);
```

### 3.2 核心数据结构

```python
# 评价报告
@dataclass
class EvaluationReport:
    id: str
    project_id: str
    target_project_path: Optional[str]
    target_api_url: Optional[str]
    timestamp: datetime
    scores: EvaluationScores
    summary: str
    findings: List[Finding]
    suggestions: List[str]
    raw_metrics: Dict[str, Any]

@dataclass
class EvaluationScores:
    functionality: float  # 0-10
    usability: float       # 0-10
    performance: float     # 0-10
    ui_design: float       # 0-10
    overall: float         # 加权平均

@dataclass
class Finding:
    severity: str  # critical, high, medium, low
    category: str   # functionality, usability, performance, security
    title: str
    description: str
    location: Optional[str]  # 文件路径或 API 端点
    evidence: Optional[str]

# 优化方案
@dataclass
class OptimizationPlan:
    id: str
    evaluation_id: str
    status: str
    improvements: List[Improvement]
    code_suggestions: List[CodeSuggestion]
    verification_result: Optional[VerificationResult]

@dataclass
class Improvement:
    priority: int  # 1-5, 1 是最高
    category: str
    title: str
    description: str
    target_area: str
    expected_impact: str

@dataclass
class CodeSuggestion:
    file_path: str
    line_start: Optional[int]
    line_end: Optional[int]
    current_code: Optional[str]
    suggested_code: str
    rationale: str

@dataclass
class VerificationResult:
    before_scores: EvaluationScores
    after_scores: EvaluationScores
    improvement_metrics: Dict[str, float]  # 改进百分比
    status: str  # improved, unchanged, regressed
```

---

## 4. 用户智能体设计

### 4.1 角色定义

用户智能体扮演"典型用户"角色：
- 有一定创作需求但非技术专家
- 希望快速上手、高效创作
- 关注功能可用性、响应速度、界面美观

### 4.2 功能探索流程

```
1. 初始化
   ├── 加载项目配置
   │   ├── API 端点 (默认: http://localhost:8000)
   │   ├── 目标项目路径 (可选)
   │   └── 测试用户标识
   ├── 清理历史测试数据
   └── 准备评估上下文

2. 功能体验 (API 层面)
   ├── 项目管理
   │   ├── 创建新项目 (POST /projects)
   │   ├── 查询项目列表 (GET /projects)
   │   ├── 获取项目详情 (GET /projects/{id})
   │   └── 删除项目 (DELETE /projects/{id})
   │
   ├── 章节管理
   │   ├── 创建章节 (POST /projects/{id}/chapters)
   │   ├── 更新章节内容 (PUT /chapters/{id})
   │   ├── 获取章节列表 (GET /projects/{id}/chapters)
   │   └── 获取章节详情 (GET /chapters/{id})
   │
   ├── 内容生成
   │   ├── 生成创意 (POST /generate/ideas)
   │   ├── 生成章节 (POST /generate/chapter)
   │   ├── 改写内容 (POST /generate/rewrite)
   │   ├── 润色内容 (POST /generate/polish)
   │   └── 中断生成 (POST /generate/{id}/interrupt)
   │
   ├── 记忆系统
   │   ├── 提取记忆实体 (POST /memory/projects/{id}/extract)
   │   ├── 搜索记忆 (POST /memory/projects/{id}/search)
   │   └── 管理记忆实体 (CRUD /memory/entities)
   │
   ├── 版本控制
   │   ├── 获取版本历史 (GET /chapters/{id}/versions)
   │   ├── 对比版本 (GET /chapters/{id}/diff)
   │   └── 回滚版本 (POST /chapters/{id}/rollback)
   │
   └── 导出功能
       ├── 导出 EPUB (POST /export/{id}/epub)
       └── 导出 PDF (POST /export/{id}/pdf)

3. 代码分析 (静态层面)
   ├── API 路由分析
   │   ├── 扫描 routes 定义
   │   ├── 检查请求/响应模型
   │   └── 验证参数校验
   │
   ├── 服务层分析
   │   ├── 检查业务逻辑完整性
   │   ├── 评估错误处理
   │   └── 分析依赖注入
   │
   ├── 前端组件分析
   │   ├── 检查组件结构
   │   ├── 评估状态管理
   │   └── 分析 API 调用模式
   │
   └── 安全检查
       ├── 敏感信息暴露
       ├── SQL 注入风险
       └── CORS 配置

4. 指标计算
   ├── 功能完整性 = (成功操作数 / 总操作数) × 10
   ├── 易用性 = 10 - (错误次数 × 2) - (平均响应时间 > 3s ? 1 : 0)
   ├── 性能 = 10 - (P95响应时间 > 5s ? 3 : 0) - (超时次数 × 2)
   └── UI设计 = 基于代码分析的结构化评分

5. 报告生成
   ├── 汇总评分
   ├── 列出发现 (按严重程度排序)
   ├── 生成改进建议
   └── 存储报告到数据库
```

### 4.3 评估维度

| 维度 | 权重 | 评估指标 |
|------|------|----------|
| 功能完整性 | 35% | API 覆盖率、CRUD 完整性、核心流程走通率 |
| 易用性 | 25% | 错误率、响应时间、操作步骤数 |
| 性能 | 20% | API 响应时间、加载速度、资源消耗 |
| 界面设计 | 20% | 组件结构、状态管理、响应式设计 |

---

## 5. 反馈智能体设计

### 5.1 工作流程

```
1. 报告分析
   ├── 读取最新评价报告
   ├── 识别低分项 (< 7.0)
   ├── 汇总发现列表
   └── 按严重程度初步排序

2. 根因分析
   ├── 关联发现与代码位置
   ├── 判断问题类别
   │   ├── 功能缺陷：功能未实现或行为异常
   │   ├── 体验问题：交互不顺畅或提示不清晰
   │   ├── 性能瓶颈：响应慢或资源浪费
   │   └── 代码问题：结构混乱或维护性差
   └── 评估影响范围和修复难度

3. 方案制定
   ├── 高优先级 (P1)
   │   └── 功能缺失/Bug 影响核心流程
   ├── 中优先级 (P2)
   │   └── 体验优化/性能改进
   └── 低优先级 (P3)
       └── 代码重构/样式调整

4. 方案输出
   ├── Markdown 优化文档
   │   ├── 问题描述
   │   ├── 根本原因
   │   ├── 解决方案
   │   └── 预期效果
   │
   ├── JSON 结构化建议
   │   ├── 每个改进点
   │   ├── 目标文件
   │   └── 代码片段
   │
   └── 可执行代码变更
       └── 生成 patch 文件

5. 验证执行
   ├── 等待人工确认 (可选模式)
   ├── 记录优化措施
   ├── 触发用户智能体重新评估
   ├── 对比改进前后指标
   └── 更新验证结果
```

### 5.2 优化建议生成规则

| 问题类别 | 建议类型 | 输出格式 |
|----------|----------|----------|
| 功能缺失 | 实现方案 | 代码示例 + 步骤说明 |
| API 错误 | 修复建议 | 修改点 + 正确代码 |
| 性能问题 | 优化方案 | 原因分析 + 优化策略 |
| 体验问题 | UI改进 | 设计建议 + Mock示意 |
| 代码问题 | 重构建议 | 重构前后对比 |

---

## 6. API 端点规范

### 6.1 评估相关

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /evaluate | 触发用户智能体评估 |
| GET | /evaluations | 查询评估历史 (支持分页、筛选) |
| GET | /evaluations/{id} | 获取特定评估报告 |
| GET | /evaluations/latest | 获取最新评估报告 |

**POST /evaluate 请求体**:
```json
{
    "project_id": "test-project-001",
    "target_project_path": "/workspace/services/novel-service",
    "target_api_url": "http://localhost:8000",
    "options": {
        "include_code_analysis": true,
        "include_performance_test": true,
        "timeout_seconds": 300
    }
}
```

**POST /evaluate 响应体**:
```json
{
    "evaluation_id": "uuid",
    "status": "completed",
    "report": {
        "scores": {
            "functionality": 8.5,
            "usability": 7.2,
            "performance": 8.0,
            "ui_design": 7.8,
            "overall": 7.9
        },
        "findings": [...],
        "suggestions": [...],
        "summary": "..."
    }
}
```

### 6.2 优化相关

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /optimize | 基于评价报告生成优化方案 |
| GET | /optimizations | 查询优化方案历史 |
| GET | /optimizations/{id} | 获取特定优化方案 |
| PATCH | /optimizations/{id}/status | 更新优化状态 |
| POST | /optimizations/{id}/verify | 触发重新评估验证 |
| POST | /optimizations/{id}/confirm | 人工确认优化方案 |

**POST /optimize 请求体**:
```json
{
    "evaluation_id": "uuid",
    "options": {
        "priority_threshold": 3,
        "include_code_suggestions": true
    }
}
```

**POST /optimize 响应体**:
```json
{
    "optimization_id": "uuid",
    "status": "pending",
    "improvements": [
        {
            "priority": 1,
            "title": "导出功能错误处理不完善",
            "description": "...",
            "target_area": "services/novel-service/app/services/export_service.py",
            "expected_impact": "提升易用性评分约 0.5 分"
        }
    ],
    "code_suggestions": [
        {
            "file_path": "...",
            "suggested_code": "..."
        }
    ]
}
```

### 6.3 报告相关

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /reports/trends | 获取评分趋势数据 |
| GET | /reports/export | 导出 Markdown 报告 |
| GET | /reports/summary | 获取综合摘要 |

**GET /reports/trends 查询参数**:
- `metric`: functionality | usability | performance | ui_design | overall
- `days`: 统计天数 (默认 30)
- `project_id`: 可选的项目筛选

---

## 7. 输出格式

### 7.1 JSON API 响应

所有 API 返回统一 JSON 格式：
```json
{
    "success": true,
    "data": {...},
    "meta": {
        "timestamp": "2026-07-01T10:00:00Z",
        "request_id": "uuid"
    }
}
```

错误响应：
```json
{
    "success": false,
    "error": {
        "code": "EVALUATION_NOT_FOUND",
        "message": "评价报告不存在",
        "details": {...}
    }
}
```

### 7.2 Markdown 报告模板

```markdown
# 评价报告 - {project_name}

**评估时间**: {timestamp}
**评估版本**: {version}

## 综合评分

| 维度 | 评分 | 状态 |
|------|------|------|
| 功能完整性 | 8.5/10 | ✅ 良好 |
| 易用性 | 7.2/10 | ⚠️ 待改进 |
| 性能 | 8.0/10 | ✅ 良好 |
| 界面设计 | 7.8/10 | ⚠️ 待改进 |
| **综合评分** | **7.9/10** | **良好** |

## 发现问题

### 🔴 高优先级

1. **[功能缺陷] 导出 EPUB 失败**
   - 位置: `export_service.py:45`
   - 描述: 当章节数为空时抛出未处理异常
   - 影响: 用户无法导出作品

### 🟡 中优先级

...

## 改进建议

1. 增强错误处理，添加参数校验
2. 优化大章节列表的查询性能
3. 改进导出进度提示

## 附录

- 原始指标数据: [链接]
- API 测试日志: [链接]
```

---

## 8. 技术实现

### 8.1 项目结构

```
services/
└── agent-service/
    ├── app/
    │   ├── main.py              # FastAPI 入口
    │   ├── config.py            # 配置管理
    │   ├── agents/
    │   │   ├── __init__.py
    │   │   ├── user_agent.py     # 用户智能体
    │   │   └── feedback_agent.py # 反馈智能体
    │   ├── engine/
    │   │   ├── __init__.py
    │   │   ├── evaluator.py     # 评估引擎
    │   │   ├── scorer.py         # 评分计算
    │   │   └── analyzer.py       # 代码分析
    │   ├── api/
    │   │   ├── __init__.py
    │   │   ├── evaluate.py       # 评估 API
    │   │   ├── optimize.py       # 优化 API
    │   │   └── reports.py        # 报告 API
    │   ├── storage/
    │   │   ├── __init__.py
    │   │   ├── database.py      # 数据库连接
    │   │   └── models.py         # ORM 模型
    │   └── schemas.py            # Pydantic 模型
    ├── tests/
    │   ├── test_user_agent.py
    │   └── test_feedback_agent.py
    ├── pyproject.toml
    └── README.md
```

### 8.2 依赖项

```
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
httpx>=0.24.0
aiosqlite>=0.19.0
python-dotenv>=1.0.0
```

---

## 9. 部署方式

### 9.1 Docker 部署

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install -e .
COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 9.2 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| AGENT_SERVICE_DB_PATH | SQLite 数据库路径 | ./agent_service.db |
| TARGET_API_URL | 被评估的 API 端点 | http://localhost:8000 |
| TARGET_PROJECT_PATH | 被分析的代码路径 | /workspace/services/novel-service |
| LOG_LEVEL | 日志级别 | INFO |

---

## 10. 成功标准

- [ ] 用户智能体能够完整执行功能体验流程
- [ ] 代码分析能够识别主要文件和潜在问题
- [ ] 评价报告包含量化评分和详细发现
- [ ] 反馈智能体能够生成可执行的优化建议
- [ ] 验证流程能够对比改进前后的评分变化
- [ ] API 端点响应正常，支持 CRUD 操作
- [ ] Markdown 报告格式正确、可读性强
- [ ] SQLite 数据库正确存储历史数据
