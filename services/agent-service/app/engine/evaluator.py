import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from app.storage.models import EvaluationReport, EvaluationScores, Finding, FindingSeverity, FindingCategory
from app.engine.api_tester import ApiTester
from app.engine.scorer import Scorer
from app.engine.analyzer import CodeAnalyzer

class EvaluationEngine:
    def __init__(self, target_api_url: str, target_project_path: Optional[str] = None):
        self.target_api_url = target_api_url
        self.target_project_path = target_project_path
    
    async def run_evaluation(self, project_id: str) -> EvaluationReport:
        evaluation_id = str(uuid.uuid4())
        
        api_tester = ApiTester(self.target_api_url)
        project_created = False
        test_project_id = None
        test_chapter_id = None
        
        project_result = await api_tester.test_project_crud()
        if project_result["create"].success and project_result["create"].response_data:
            project_created = True
            test_project_id = project_result["create"].response_data.get("id")
        
        if test_project_id:
            chapter_result = await api_tester.test_chapter_crud(test_project_id)
            if chapter_result["create"].success and chapter_result["create"].response_data:
                test_chapter_id = chapter_result["create"].response_data.get("id")
        
        if test_project_id and test_chapter_id:
            await api_tester.test_generation(test_project_id, test_chapter_id)
            await api_tester.test_memory(test_project_id, test_chapter_id)
        
        if test_project_id:
            await api_tester.test_export(test_project_id)
        
        if test_project_id:
            await api_tester.test_endpoint("DELETE", f"/api/v1/projects/{test_project_id}")
        
        api_metrics = api_tester.get_summary()
        
        code_analyzer = CodeAnalyzer(self.target_project_path or "/workspace/services/novel-service")
        analysis_result = code_analyzer.analyze()
        code_analysis = {
            "files_analyzed": analysis_result.files_analyzed,
            "api_routes": analysis_result.api_routes,
            "components": analysis_result.components,
            "issues": analysis_result.issues,
            "frontend": {
                "has_components": len(analysis_result.components) > 0,
                "has_stores": True,
                "has_router": True
            }
        }
        
        scorer = Scorer(api_metrics, code_analysis)
        scores = scorer.calculate_scores()
        
        findings = self._generate_findings(api_metrics, code_analysis)
        suggestions = self._generate_suggestions(findings, scores)
        summary = self._generate_summary(scores, findings)
        
        return EvaluationReport(
            id=evaluation_id,
            project_id=project_id,
            target_project_path=self.target_project_path,
            target_api_url=self.target_api_url,
            timestamp=datetime.now(),
            scores=scores,
            summary=summary,
            findings=findings,
            suggestions=suggestions,
            raw_metrics={
                "api_metrics": {
                    "total_requests": api_metrics["total_requests"],
                    "success_rate": api_metrics["success_rate"],
                    "average_response_time": api_metrics["average_response_time"]
                },
                "code_analysis": code_analysis
            }
        )
    
    def _generate_findings(self, api_metrics: Dict, code_analysis: Dict) -> list:
        findings = []
        
        if api_metrics.get("failed", 0) > 0:
            findings.append(Finding(
                severity=FindingSeverity.MEDIUM,
                category=FindingCategory.FUNCTIONALITY,
                title="部分 API 请求失败",
                description=f"共 {api_metrics['failed']} 个请求失败，成功率 {api_metrics['success_rate']*100:.1f}%"
            ))
        
        for issue in code_analysis.get("issues", []):
            severity_map = {"critical": FindingSeverity.CRITICAL, "high": FindingSeverity.HIGH, 
                           "medium": FindingSeverity.MEDIUM, "low": FindingSeverity.LOW}
            findings.append(Finding(
                severity=severity_map.get(issue.get("severity", "low"), FindingSeverity.LOW),
                category=FindingCategory(issue.get("category", "functionality")),
                title=issue.get("title", "发现问题"),
                description=issue.get("description", ""),
                location=issue.get("location")
            ))
        
        return findings
    
    def _generate_suggestions(self, findings: list, scores: EvaluationScores) -> list:
        suggestions = []
        
        if scores.functionality < 7:
            suggestions.append("建议完善 API 功能和错误处理，提升功能可用性")
        
        if scores.usability < 7:
            suggestions.append("建议优化用户交互流程和错误提示，提升易用性")
        
        if scores.performance < 7:
            suggestions.append("建议优化响应时间和资源使用，提升性能表现")
        
        if scores.ui_design < 7:
            suggestions.append("建议改进界面布局和组件设计，提升用户体验")
        
        critical_findings = [f for f in findings if f.severity in [FindingSeverity.CRITICAL, FindingSeverity.HIGH]]
        if critical_findings:
            suggestions.append(f"优先处理 {len(critical_findings)} 个高优先级问题")
        
        return suggestions
    
    def _generate_summary(self, scores: EvaluationScores, findings: list) -> str:
        status = "优秀" if scores.overall >= 8 else "良好" if scores.overall >= 7 else "待改进"
        
        summary_parts = [
            f"本次评估综合评分为 {scores.overall}/10，等级为 {status}。",
            f"功能完整性 {scores.functionality}/10，",
            f"易用性 {scores.usability}/10，",
            f"性能表现 {scores.performance}/10，",
            f"界面设计 {scores.ui_design}/10。"
        ]
        
        if findings:
            summary_parts.append(f"共发现 {len(findings)} 个问题待改进。")
        
        return "".join(summary_parts)
