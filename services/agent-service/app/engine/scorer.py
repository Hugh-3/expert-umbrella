from typing import Dict, List, Any
from app.storage.models import EvaluationScores, Finding, FindingSeverity, FindingCategory

class Scorer:
    def __init__(self, api_metrics: Dict[str, Any], code_analysis: Dict[str, Any]):
        self.api_metrics = api_metrics
        self.code_analysis = code_analysis
    
    def calculate_functionality_score(self) -> float:
        if not self.api_metrics.get("total_requests"):
            return 5.0
        
        success_rate = self.api_metrics.get("success_rate", 0)
        base_score = success_rate * 10
        
        deductions = 0
        results = self.api_metrics.get("results", [])
        endpoints_tested = set(r.endpoint for r in results)
        
        critical_endpoints = [
            "/api/v1/projects",
            "/api/v1/chapters",
        ]
        for endpoint in critical_endpoints:
            if not any(endpoint in e for e in endpoints_tested):
                deductions += 0.5
        
        return max(0, min(10, base_score - deductions))
    
    def calculate_usability_score(self) -> float:
        base_score = 10.0
        deductions = 0
        
        if self.api_metrics.get("failed", 0) > 0:
            failure_rate = self.api_metrics.get("failed", 0) / max(1, self.api_metrics.get("total_requests", 1))
            deductions += failure_rate * 5
        
        avg_time = self.api_metrics.get("average_response_time", 0)
        if avg_time > 3:
            deductions += 1
        if avg_time > 5:
            deductions += 1
        
        code_issues = self.code_analysis.get("issues", [])
        usability_issues = [i for i in code_issues if i.get("category") == FindingCategory.USABILITY.value]
        deductions += len(usability_issues) * 0.3
        
        return max(0, min(10, base_score - deductions))
    
    def calculate_performance_score(self) -> float:
        base_score = 10.0
        deductions = 0
        
        p95 = self.api_metrics.get("p95_response_time", 0)
        if p95 > 2:
            deductions += 1
        if p95 > 5:
            deductions += 2
        
        results = self.api_metrics.get("results", [])
        timeout_count = sum(1 for r in results if r.error and "timeout" in str(r.error).lower())
        deductions += timeout_count * 0.5
        
        code_issues = self.code_analysis.get("issues", [])
        perf_issues = [i for i in code_issues if i.get("category") == FindingCategory.PERFORMANCE.value]
        deductions += len(perf_issues) * 0.5
        
        return max(0, min(10, base_score - deductions))
    
    def calculate_ui_design_score(self) -> float:
        base_score = 7.0
        additions = 0
        
        frontend = self.code_analysis.get("frontend", {})
        if frontend.get("has_components"):
            additions += 0.5
        if frontend.get("has_stores"):
            additions += 0.5
        if frontend.get("has_router"):
            additions += 0.5
        
        code_issues = self.code_analysis.get("issues", [])
        ui_issues = [i for i in code_issues if i.get("category") == FindingCategory.UI_DESIGN.value]
        deductions = len(ui_issues) * 0.3
        
        return max(0, min(10, base_score + additions - deductions))
    
    def calculate_scores(self) -> EvaluationScores:
        return EvaluationScores(
            functionality=round(self.calculate_functionality_score(), 2),
            usability=round(self.calculate_usability_score(), 2),
            performance=round(self.calculate_performance_score(), 2),
            ui_design=round(self.calculate_ui_design_score(), 2)
        )
