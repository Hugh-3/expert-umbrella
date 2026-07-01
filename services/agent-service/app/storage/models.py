from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid
import json

class FindingSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class FindingCategory(str, Enum):
    FUNCTIONALITY = "functionality"
    USABILITY = "usability"
    PERFORMANCE = "performance"
    SECURITY = "security"
    UI_DESIGN = "ui_design"

class OptimizationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"

@dataclass
class Finding:
    severity: FindingSeverity
    category: FindingCategory
    title: str
    description: str
    location: Optional[str] = None
    evidence: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "severity": self.severity.value,
            "category": self.category.value,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "evidence": self.evidence
        }

@dataclass
class EvaluationScores:
    functionality: float
    usability: float
    performance: float
    ui_design: float
    
    @property
    def overall(self) -> float:
        weights = {"functionality": 0.35, "usability": 0.25, "performance": 0.20, "ui_design": 0.20}
        return (
            self.functionality * weights["functionality"] +
            self.usability * weights["usability"] +
            self.performance * weights["performance"] +
            self.ui_design * weights["ui_design"]
        )
    
    def to_dict(self) -> dict:
        return {
            "functionality": self.functionality,
            "usability": self.usability,
            "performance": self.performance,
            "ui_design": self.ui_design,
            "overall": round(self.overall, 2)
        }

@dataclass
class EvaluationReport:
    id: str
    project_id: str
    target_project_path: Optional[str]
    target_api_url: str
    timestamp: datetime
    scores: EvaluationScores
    summary: str
    findings: List[Finding]
    suggestions: List[str]
    raw_metrics: Dict[str, Any]
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "target_project_path": self.target_project_path,
            "target_api_url": self.target_api_url,
            "timestamp": self.timestamp.isoformat(),
            "scores": self.scores.to_dict(),
            "summary": self.summary,
            "findings": [f.to_dict() for f in self.findings],
            "suggestions": self.suggestions,
            "raw_metrics": self.raw_metrics
        }

@dataclass
class Improvement:
    priority: int
    title: str
    description: str
    category: str
    target_area: str
    expected_impact: str
    
    def to_dict(self) -> dict:
        return {
            "priority": self.priority,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "target_area": self.target_area,
            "expected_impact": self.expected_impact
        }

@dataclass
class CodeSuggestion:
    file_path: str
    suggested_code: str
    rationale: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    
    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "suggested_code": self.suggested_code,
            "rationale": self.rationale,
            "line_start": self.line_start,
            "line_end": self.line_end
        }

@dataclass
class VerificationResult:
    before_scores: EvaluationScores
    after_scores: EvaluationScores
    improvement_metrics: Dict[str, float]
    status: str
    
    def to_dict(self) -> dict:
        return {
            "before_scores": self.before_scores.to_dict(),
            "after_scores": self.after_scores.to_dict(),
            "improvement_metrics": self.improvement_metrics,
            "status": self.status
        }

@dataclass
class OptimizationPlan:
    id: str
    evaluation_id: str
    status: OptimizationStatus
    improvements: List[Improvement]
    code_suggestions: List[CodeSuggestion]
    verification_result: Optional[VerificationResult]
    created_at: datetime
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "evaluation_id": self.evaluation_id,
            "status": self.status.value,
            "improvements": [i.to_dict() for i in self.improvements],
            "code_suggestions": [c.to_dict() for c in self.code_suggestions],
            "verification_result": self.verification_result.to_dict() if self.verification_result else None,
            "created_at": self.created_at.isoformat()
        }
