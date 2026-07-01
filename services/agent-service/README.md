# Agent Service

智能体评测与反馈系统。

## 功能

- 用户智能体：从用户视角评估项目功能
- 反馈智能体：分析评价报告并制定优化方案
- 评估引擎：提供评分算法和代码分析
- SQLite 存储：历史记录和趋势数据

## 快速开始

```bash
cd services/agent-service
pip install -e .
uvicorn app.main:app --reload --port 8001
```

## API 文档

访问 http://localhost:8001/docs 查看 API 文档。
