import uuid
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.agents.base import BaseAgent
from app.storage.models import (
    OptimizationPlan, Improvement, CodeSuggestion, VerificationResult,
    FindingSeverity, OptimizationStatus, EvaluationScores
)
from app.storage.database import Database

class FeedbackAgent(BaseAgent):
    """反馈智能体 - 分析评价报告并制定优化方案"""
    
    def __init__(self, config: Dict[str, Any], db: Database):
        super().__init__(config)
        self.db = db
    
    async def analyze_and_plan(self, evaluation_id: str, options: Optional[Dict] = None) -> OptimizationPlan:
        options = options or {}
        priority_threshold = options.get("priority_threshold", 3)
        
        report_data = await self.db.get_evaluation(evaluation_id)
        if not report_data:
            raise ValueError(f"Evaluation report not found: {evaluation_id}")
        
        findings = report_data.get("findings", "[]")
        if isinstance(findings, str):
            findings = json.loads(findings)
        
        improvements = self._generate_improvements(findings, report_data, priority_threshold)
        code_suggestions = self._generate_code_suggestions(findings, report_data)
        
        plan = OptimizationPlan(
            id=str(uuid.uuid4()),
            evaluation_id=evaluation_id,
            status=OptimizationStatus.PENDING,
            improvements=improvements,
            code_suggestions=code_suggestions,
            verification_result=None,
            created_at=datetime.now()
        )
        
        await self.db.save_optimization(plan.to_dict())
        
        return plan
    
    def _generate_improvements(self, findings: List, report_data: Dict, threshold: int) -> List[Improvement]:
        improvements = []
        
        severity_order = {"critical": 1, "high": 2, "medium": 3, "low": 4}
        sorted_findings = sorted(
            findings,
            key=lambda f: severity_order.get(f.get("severity", "low"), 5)
        )
        
        for i, finding in enumerate(sorted_findings):
            priority = i + 1
            if priority > threshold:
                break
            
            category = finding.get("category", "functionality")
            
            if category == "functionality":
                title = f"改进: {finding.get('title', '功能问题')}"
                expected_impact = "提升功能完整性评分"
            elif category == "usability":
                title = f"优化: {finding.get('title', '易用性问题')}"
                expected_impact = "提升易用性评分"
            elif category == "performance":
                title = f"优化: {finding.get('title', '性能问题')}"
                expected_impact = "提升性能评分"
            elif category == "security":
                title = f"修复: {finding.get('title', '安全问题')}"
                expected_impact = "提升安全性"
            else:
                title = f"改进: {finding.get('title', '一般问题')}"
                expected_impact = "整体质量提升"
            
            improvements.append(Improvement(
                priority=priority,
                title=title,
                description=finding.get("description", ""),
                category=category,
                target_area=finding.get("location", "未知位置"),
                expected_impact=expected_impact
            ))
        
        return improvements
    
    def _generate_code_suggestions(self, findings: List, report_data: Dict) -> List[CodeSuggestion]:
        suggestions = []
        
        for finding in findings:
            location = finding.get("location", "")
            category = finding.get("category", "")
            
            if not location or "services" not in location:
                continue
            
            if category == "security":
                suggestions.append(CodeSuggestion(
                    file_path=location,
                    suggested_code="""import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")
""",
                    rationale="使用环境变量替代硬编码，提高安全性"
                ))
            elif category == "performance":
                suggestions.append(CodeSuggestion(
                    file_path=location,
                    suggested_code="""from functools import lru_cache

@lru_cache(maxsize=128)
async def cached_operation(param):
    pass
""",
                    rationale="添加缓存减少重复计算，提升性能"
                ))
            elif category == "usability":
                suggestions.append(CodeSuggestion(
                    file_path=location,
                    suggested_code="""try:
    await operation()
except ValueError as e:
    raise HTTPException(status_code=400, detail="输入数据格式不正确，请检查后重试")
except Exception as e:
    raise HTTPException(status_code=500, detail="操作失败，请稍后重试")
""",
                    rationale="改进错误处理，提供友好的错误信息"
                ))
        
        return suggestions
    
    async def verify_improvement(self, optimization_id: str, user_agent) -> VerificationResult:
        plan_data = await self.db.get_optimization(optimization_id)
        if not plan_data:
            raise ValueError(f"Optimization plan not found: {optimization_id}")
        
        before_eval = await self.db.get_evaluation(plan_data["evaluation_id"])
        
        await self.db.update_optimization_status(optimization_id, "in_progress")
        
        new_report = await user_agent.run(f"re-eval-{optimization_id}")
        
        before_scores_obj = EvaluationScores(
            functionality=float(before_eval.get("functionality_score", 0)),
            usability=float(before_eval.get("usability_score", 0)),
            performance=float(before_eval.get("performance_score", 0)),
            ui_design=float(before_eval.get("ui_design_score", 0))
        )
        
        improvement_metrics = {
            "functionality_change": round(new_report.scores.functionality - before_scores_obj.functionality, 2),
            "usability_change": round(new_report.scores.usability - before_scores_obj.usability, 2),
            "performance_change": round(new_report.scores.performance - before_scores_obj.performance, 2),
            "ui_design_change": round(new_report.scores.ui_design - before_scores_obj.ui_design, 2)
        }
        
        total_improvement = sum(improvement_metrics.values())
        if total_improvement > 0:
            status = "improved"
        elif total_improvement < 0:
            status = "regressed"
        else:
            status = "unchanged"
        
        await self.db.update_optimization_status(optimization_id, "verified")
        
        return VerificationResult(
            before_scores=before_scores_obj,
            after_scores=new_report.scores,
            improvement_metrics=improvement_metrics,
            status=status
        )
