from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from typing import Optional
import json
from datetime import datetime

from app.schemas import TrendResponse, TrendDataPoint
from app.storage.database import Database, get_db

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/trends", response_model=TrendResponse)
async def get_trend_data(
    metric: str = Query("overall", description="指标名称"),
    days: int = Query(30, description="统计天数"),
    project_id: Optional[str] = Query(None, description="项目筛选"),
    db: Database = Depends(get_db)
):
    data = await db.get_trend_data(metric, days)
    return TrendResponse(
        metric=metric,
        data=[TrendDataPoint(**d) for d in data]
    )

@router.get("/export")
async def export_markdown_report(
    evaluation_id: Optional[str] = Query(None),
    db: Database = Depends(get_db)
):
    if evaluation_id:
        evaluation = await db.get_evaluation(evaluation_id)
    else:
        evaluation = await db.get_latest_evaluation()
    
    if not evaluation:
        return Response(content="# 无评价报告\n\n暂无评价数据。", media_type="text/markdown")
    
    findings = json.loads(evaluation.get("findings", "[]"))
    suggestions = json.loads(evaluation.get("suggestions", "[]"))
    
    report = f"""# 评价报告 - {evaluation['project_id']}

**评估时间**: {evaluation['timestamp']}

## 综合评分

| 维度 | 评分 | 状态 |
|------|------|------|
| 功能完整性 | {evaluation['functionality_score']}/10 | {'✅ 良好' if evaluation['functionality_score'] >= 7 else '⚠️ 待改进'} |
| 易用性 | {evaluation['usability_score']}/10 | {'✅ 良好' if evaluation['usability_score'] >= 7 else '⚠️ 待改进'} |
| 性能 | {evaluation['performance_score']}/10 | {'✅ 良好' if evaluation['performance_score'] >= 7 else '⚠️ 待改进'} |
| 界面设计 | {evaluation['ui_design_score']}/10 | {'✅ 良好' if evaluation['ui_design_score'] >= 7 else '⚠️ 待改进'} |
| **综合评分** | **{evaluation['overall_score']}/10** | **{'优秀' if evaluation['overall_score'] >= 8 else '良好' if evaluation['overall_score'] >= 7 else '待改进'}** |

## 发现问题

"""
    
    severity_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
    for finding in findings:
        icon = severity_icons.get(finding.get("severity", "low"), "⚪")
        report += f"""### {icon} {finding.get('severity', 'unknown').upper()}

{finding.get('title', '发现问题')}

- **类别**: {finding.get('category', 'N/A')}
- **位置**: {finding.get('location', '未知')}
- **描述**: {finding.get('description', '无描述')}

"""
    
    report += """## 改进建议

"""
    for i, suggestion in enumerate(suggestions, 1):
        report += f"{i}. {suggestion}\n"
    
    report += f"""

---
*报告生成时间: {datetime.now().isoformat()}*
"""
    
    return Response(content=report, media_type="text/markdown")

@router.get("/summary")
async def get_summary(db: Database = Depends(get_db)):
    evaluations = await db.list_evaluations(limit=10)
    
    if not evaluations:
        return {
            "total_evaluations": 0,
            "latest_score": None,
            "average_scores": None
        }
    
    latest = evaluations[0]
    total = len(evaluations)
    
    avg_scores = {
        "functionality": round(sum(e.get("functionality_score", 0) for e in evaluations) / total, 2),
        "usability": round(sum(e.get("usability_score", 0) for e in evaluations) / total, 2),
        "performance": round(sum(e.get("performance_score", 0) for e in evaluations) / total, 2),
        "ui_design": round(sum(e.get("ui_design_score", 0) for e in evaluations) / total, 2)
    }
    
    return {
        "total_evaluations": total,
        "latest_score": {
            "overall": latest.get("overall_score", 0),
            "functionality": latest.get("functionality_score", 0),
            "usability": latest.get("usability_score", 0),
            "performance": latest.get("performance_score", 0),
            "ui_design": latest.get("ui_design_score", 0)
        },
        "average_scores": avg_scores
    }
