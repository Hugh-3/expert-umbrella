from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ============ Request Models ============

class EvaluateRequest(BaseModel):
    project_id: str = Field(..., description="项目标识")
    target_project_path: Optional[str] = Field(None, description="目标项目代码路径")
    target_api_url: Optional[str] = Field("http://localhost:8000", description="目标 API 地址")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)

class OptimizeRequest(BaseModel):
    evaluation_id: str = Field(..., description="评价报告 ID")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)

class UpdateOptimizationStatusRequest(BaseModel):
    status: str = Field(..., pattern="^(pending|in_progress|completed)$")

class VerifyOptimizationRequest(BaseModel):
    re_evaluate: bool = Field(True, description="是否重新评估")

# ============ Response Models ============

class EvaluationScoresResponse(BaseModel):
    functionality: float
    usability: float
    performance: float
    ui_design: float
    overall: float

class FindingResponse(BaseModel):
    severity: str
    category: str
    title: str
    description: str
    location: Optional[str] = None
    evidence: Optional[str] = None

class EvaluationReportResponse(BaseModel):
    id: str
    project_id: str
    target_project_path: Optional[str]
    target_api_url: str
    timestamp: str
    scores: EvaluationScoresResponse
    summary: str
    findings: List[FindingResponse]
    suggestions: List[str]
    raw_metrics: Dict[str, Any]

class EvaluateResponse(BaseModel):
    evaluation_id: str
    status: str
    report: Optional[EvaluationReportResponse] = None
    error: Optional[str] = None

class ImprovementResponse(BaseModel):
    priority: int
    title: str
    description: str
    category: str
    target_area: str
    expected_impact: str

class CodeSuggestionResponse(BaseModel):
    file_path: str
    suggested_code: str
    rationale: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None

class VerificationResultResponse(BaseModel):
    before_scores: EvaluationScoresResponse
    after_scores: EvaluationScoresResponse
    improvement_metrics: Dict[str, float]
    status: str

class OptimizationPlanResponse(BaseModel):
    id: str
    evaluation_id: str
    status: str
    improvements: List[ImprovementResponse]
    code_suggestions: List[CodeSuggestionResponse]
    verification_result: Optional[VerificationResultResponse]
    created_at: str

class OptimizeResponse(BaseModel):
    optimization_id: str
    status: str
    improvements: List[ImprovementResponse]
    code_suggestions: List[CodeSuggestionResponse]

class TrendDataPoint(BaseModel):
    metric: str
    score: float
    timestamp: str

class TrendResponse(BaseModel):
    metric: str
    data: List[TrendDataPoint]
