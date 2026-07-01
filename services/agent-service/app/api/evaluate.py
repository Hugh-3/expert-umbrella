from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import uuid

from app.schemas import EvaluateRequest, EvaluateResponse, EvaluationReportResponse
from app.agents.user_agent import UserAgent
from app.storage.database import Database, get_db

router = APIRouter(prefix="", tags=["evaluation"])

@router.post("/evaluate", response_model=EvaluateResponse)
async def run_evaluation(
    request: EvaluateRequest,
    db: Database = Depends(get_db)
):
    try:
        agent = UserAgent(
            config={
                "target_api_url": request.target_api_url or "http://localhost:8000",
                "target_project_path": request.target_project_path
            },
            db=db
        )
        
        report = await agent.run(request.project_id, request.options)
        
        return EvaluateResponse(
            evaluation_id=report.id,
            status="completed",
            report=EvaluationReportResponse(
                id=report.id,
                project_id=report.project_id,
                target_project_path=report.target_project_path,
                target_api_url=report.target_api_url,
                timestamp=report.timestamp.isoformat(),
                scores={
                    "functionality": report.scores.functionality,
                    "usability": report.scores.usability,
                    "performance": report.scores.performance,
                    "ui_design": report.scores.ui_design,
                    "overall": report.scores.overall
                },
                summary=report.summary,
                findings=[
                    {
                        "severity": f.severity.value,
                        "category": f.category.value,
                        "title": f.title,
                        "description": f.description,
                        "location": f.location,
                        "evidence": f.evidence
                    }
                    for f in report.findings
                ],
                suggestions=report.suggestions,
                raw_metrics=report.raw_metrics
            )
        )
    except Exception as e:
        return EvaluateResponse(
            evaluation_id=str(uuid.uuid4()),
            status="failed",
            error=str(e)
        )

@router.get("/evaluations")
async def list_evaluations(
    limit: int = 10,
    offset: int = 0,
    db: Database = Depends(get_db)
):
    evaluations = await db.list_evaluations(limit, offset)
    return {"evaluations": evaluations, "total": len(evaluations)}

@router.get("/evaluations/{evaluation_id}")
async def get_evaluation(evaluation_id: str, db: Database = Depends(get_db)):
    import json
    evaluation = await db.get_evaluation(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    if evaluation.get("findings") and isinstance(evaluation["findings"], str):
        evaluation["findings"] = json.loads(evaluation["findings"])
    if evaluation.get("suggestions") and isinstance(evaluation["suggestions"], str):
        evaluation["suggestions"] = json.loads(evaluation["suggestions"])
    if evaluation.get("raw_metrics") and isinstance(evaluation["raw_metrics"], str):
        evaluation["raw_metrics"] = json.loads(evaluation["raw_metrics"])
    return evaluation

@router.get("/evaluations/latest")
async def get_latest_evaluation(db: Database = Depends(get_db)):
    import json
    evaluation = await db.get_latest_evaluation()
    if not evaluation:
        raise HTTPException(status_code=404, detail="No evaluations found")
    if evaluation.get("findings") and isinstance(evaluation["findings"], str):
        evaluation["findings"] = json.loads(evaluation["findings"])
    return evaluation
