import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas import (
    FeedbackCreate,
    FeedbackResponse,
    SelfCheckResponse,
)
from app.services import (
    create_feedback,
    get_feedbacks_by_task,
    run_self_check,
    get_generation_task,
    get_chapter,
)

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(
    feedback_in: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
):
    task = await get_generation_task(db, feedback_in.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    feedback = await create_feedback(db, feedback_in)
    return feedback


@router.get("/feedback/task/{task_id}", response_model=List[FeedbackResponse])
async def get_task_feedbacks(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    task = await get_generation_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    feedbacks = await get_feedbacks_by_task(db, task_id)
    return feedbacks


@router.post("/self-check/chapter/{chapter_id}", response_model=SelfCheckResponse)
async def self_check_chapter(
    chapter_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    chapter = await get_chapter(db, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    result = await run_self_check(db, chapter_id)
    return result
