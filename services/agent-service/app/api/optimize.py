from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import json

from app.schemas import (
    OptimizeRequest, OptimizeResponse,
    OptimizationPlanResponse, UpdateOptimizationStatusRequest
)
from app.agents.feedback_agent import FeedbackAgent
from app.agents.user_agent import UserAgent
from app.storage.database import Database, get_db

router = APIRouter(prefix="", tags=["optimization"])

@router.post("/optimize", response_model=OptimizeResponse)
async def create_optimization_plan(
    request: OptimizeRequest,
    db: Database = Depends(get_db)
):
    try:
        agent = FeedbackAgent(config={}, db=db)
        plan = await agent.analyze_and_plan(request.evaluation_id, request.options)
        
        return OptimizeResponse(
            optimization_id=plan.id,
            status=plan.status.value,
            improvements=[
                {
                    "priority": i.priority,
                    "title": i.title,
                    "description": i.description,
                    "category": i.category,
                    "target_area": i.target_area,
                    "expected_impact": i.expected_impact
                }
                for i in plan.improvements
            ],
            code_suggestions=[
                {
                    "file_path": c.file_path,
                    "suggested_code": c.suggested_code,
                    "rationale": c.rationale,
                    "line_start": c.line_start,
                    "line_end": c.line_end
                }
                for c in plan.code_suggestions
            ]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/optimizations")
async def list_optimizations(
    limit: int = 10,
    offset: int = 0,
    db: Database = Depends(get_db)
):
    return {"optimizations": [], "total": 0}

@router.get("/optimizations/{optimization_id}")
async def get_optimization(optimization_id: str, db: Database = Depends(get_db)):
    plan = await db.get_optimization(optimization_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Optimization not found")
    
    plan["improvements"] = json.loads(plan.get("improvements", "[]"))
    plan["code_suggestions"] = json.loads(plan.get("code_suggestions", "[]"))
    if plan.get("verification_result"):
        plan["verification_result"] = json.loads(plan["verification_result"])
    
    return plan

@router.patch("/optimizations/{optimization_id}/status")
async def update_optimization_status(
    optimization_id: str,
    request: UpdateOptimizationStatusRequest,
    db: Database = Depends(get_db)
):
    await db.update_optimization_status(optimization_id, request.status)
    return {"optimization_id": optimization_id, "status": request.status}

@router.post("/optimizations/{optimization_id}/verify")
async def verify_optimization(
    optimization_id: str,
    db: Database = Depends(get_db)
):
    try:
        plan_data = await db.get_optimization(optimization_id)
        if not plan_data:
            raise HTTPException(status_code=404, detail="Optimization not found")
        
        feedback_agent = FeedbackAgent(config={}, db=db)
        user_agent = UserAgent(
            config={"target_api_url": "http://localhost:8000"},
            db=db
        )
        
        result = await feedback_agent.verify_improvement(optimization_id, user_agent)
        
        return {
            "optimization_id": optimization_id,
            "verification_result": result.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
