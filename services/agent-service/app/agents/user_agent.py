import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from app.agents.base import BaseAgent
from app.engine.evaluator import EvaluationEngine
from app.storage.models import EvaluationReport
from app.storage.database import Database

class UserAgent(BaseAgent):
    """用户智能体 - 从典型用户视角评估项目"""
    
    def __init__(self, config: Dict[str, Any], db: Database):
        super().__init__(config)
        self.db = db
        self.engine = EvaluationEngine(
            target_api_url=config.get("target_api_url", "http://localhost:8000"),
            target_project_path=config.get("target_project_path")
        )
    
    async def run(self, project_id: str, options: Optional[Dict] = None) -> EvaluationReport:
        options = options or {}
        
        report = await self.engine.run_evaluation(project_id)
        
        await self.db.save_evaluation(report.to_dict())
        await self._save_snapshots(report)
        
        return report
    
    async def _save_snapshots(self, report: EvaluationReport):
        scores = {
            "functionality": report.scores.functionality,
            "usability": report.scores.usability,
            "performance": report.scores.performance,
            "ui_design": report.scores.ui_design,
            "overall": report.scores.overall
        }
        
        for metric, score in scores.items():
            snapshot_id = str(uuid.uuid4())
            await self.db.save_snapshot(
                snapshot_id=snapshot_id,
                evaluation_id=report.id,
                metric_name=metric,
                score=score,
                recorded_at=datetime.now().isoformat()
            )
    
    def get_role_context(self) -> str:
        return """
你是一个典型用户，扮演以下角色：
- 有一定创作需求但非技术专家
- 希望快速上手、高效创作
- 关注功能可用性、响应速度、界面美观
- 对错误信息期望友好、清晰

评估要点：
1. 功能是否按预期工作
2. 操作流程是否顺畅
3. 错误提示是否友好
4. 响应时间是否可接受
5. 界面是否美观易用
"""
