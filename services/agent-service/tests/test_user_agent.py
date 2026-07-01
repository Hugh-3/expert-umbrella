import pytest
from app.agents.user_agent import UserAgent
from app.storage.database import Database
from app.storage.models import EvaluationReport, EvaluationScores

@pytest.mark.asyncio
async def test_user_agent_initialization(test_db):
    agent = UserAgent(
        config={"target_api_url": "http://localhost:8000"},
        db=test_db
    )
    assert agent.config["target_api_url"] == "http://localhost:8000"
    assert agent.engine is not None

@pytest.mark.asyncio
async def test_user_agent_role_context(test_db):
    agent = UserAgent(config={}, db=test_db)
    context = agent.get_role_context()
    assert "典型用户" in context
    assert "功能可用性" in context

@pytest.mark.asyncio
async def test_user_agent_run_without_api(test_db):
    agent = UserAgent(
        config={"target_api_url": "http://localhost:9999"},
        db=test_db
    )
    report = await agent.run("test-project")
    assert report is not None
    assert report.scores is not None
    assert report.id is not None
    assert isinstance(report.scores, EvaluationScores)
    assert 0 <= report.scores.overall <= 10
