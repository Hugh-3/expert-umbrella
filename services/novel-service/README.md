# Novel Service

小说创作服务，是内容创作自动化平台的核心服务之一。

## 功能特性

- 智能创意生成（大纲、人物设定、世界观）
- 章节撰写（续写、改写、润色）
- SSE 流式输出
- 版本管理与回滚
- 项目与章节管理

## 快速开始

```bash
cd services/novel-service
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload --port 8001
```

## 测试

```bash
pytest tests/ -v
```
