# Agent Service

智能体评测与反馈系统。

## 功能

- **用户智能体**：从用户视角评估项目功能
  - API 功能测试（项目 CRUD、章节 CRUD、生成、导出、记忆）
  - 代码静态分析（安全检查、错误处理、性能问题）
  - 量化评分计算（功能完整性、易用性、性能、界面设计）
  - 结构化报告生成（JSON + Markdown）

- **反馈智能体**：分析评价报告并制定优化方案
  - 根因分析与优先级排序
  - 代码修改建议生成
  - 改进效果验证（前后对比）

- **评估引擎**：提供评分算法和代码分析
  - API 测试器
  - 评分计算器
  - 代码分析器

- **SQLite 存储**：历史记录和趋势数据
  - 评价报告存储
  - 优化方案记录
  - 趋势分析数据

## 快速开始

```bash
cd services/agent-service
pip install -e ".[dev]"

# 启动服务
uvicorn app.main:app --reload --port 8001
```

## API 文档

启动服务后访问 http://localhost:8001/docs 查看完整的 Swagger API 文档。

### 主要端点

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /evaluate | 触发用户智能体评估 |
| GET | /evaluations | 查询评估历史 |
| GET | /evaluations/{id} | 获取特定评估报告 |
| POST | /optimize | 基于评价报告生成优化方案 |
| GET | /optimizations/{id} | 获取特定优化方案 |
| POST | /optimizations/{id}/verify | 触发重新评估验证 |
| GET | /reports/trends | 获取评分趋势数据 |
| GET | /reports/export | 导出 Markdown 报告 |
| GET | /reports/summary | 获取综合摘要 |

### 使用示例

```bash
# 1. 运行评估
curl -X POST http://localhost:8001/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "my-project",
    "target_api_url": "http://localhost:8000",
    "target_project_path": "/workspace/services/novel-service"
  }'

# 2. 查看评估历史
curl http://localhost:8001/evaluations

# 3. 生成优化方案
curl -X POST http://localhost:8001/optimize \
  -H "Content-Type: application/json" \
  -d '{"evaluation_id": "<evaluation_id>"}'

# 4. 导出 Markdown 报告
curl http://localhost:8001/reports/export > report.md

# 5. 查看趋势数据
curl "http://localhost:8001/reports/trends?metric=overall&days=30"
```

## 项目结构

```
services/agent-service/
├── app/
│   ├── main.py            # FastAPI 入口
│   ├── config.py          # 配置管理
│   ├── schemas.py         # Pydantic 模型
│   ├── agents/
│   │   ├── base.py        # 智能体基类
│   │   ├── user_agent.py  # 用户智能体
│   │   └── feedback_agent.py  # 反馈智能体
│   ├── engine/
│   │   ├── evaluator.py   # 评估引擎
│   │   ├── scorer.py      # 评分计算
│   │   ├── analyzer.py    # 代码分析
│   │   └── api_tester.py  # API 测试器
│   ├── storage/
│   │   ├── database.py    # SQLite 数据库
│   │   └── models.py      # 数据模型
│   └── api/
│       ├── evaluate.py    # 评估 API
│       ├── optimize.py    # 优化 API
│       └── reports.py     # 报告 API
├── tests/
│   ├── conftest.py
│   ├── test_user_agent.py
│   └── test_api.py
├── pyproject.toml
└── README.md
```

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_api.py -v

# 查看覆盖率
pytest --cov=app tests/
```

## 配置

通过环境变量或 `.env` 文件配置：

```env
AGENT_DB_PATH=./agent_service.db
AGENT_TARGET_API_URL=http://localhost:8000
AGENT_TARGET_PROJECT_PATH=/workspace/services/novel-service
AGENT_SERVICE_PORT=8001
```
