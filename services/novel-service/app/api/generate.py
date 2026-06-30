import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas import GenerateRequest, GenerateTaskResponse
from app.services import (
    create_generation_task,
    get_generation_task,
    stream_generation,
    interrupt_task,
)

router = APIRouter()


@router.post("/ideas", response_model=GenerateTaskResponse, status_code=201)
async def generate_ideas(
    req: GenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    from app.models import TaskType
    req.task_type = TaskType.IDEAS
    task = await create_generation_task(db, req)
    return task


@router.post("/chapter")
async def generate_chapter_stream(
    req: GenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    from app.models import TaskType
    req.task_type = TaskType.CHAPTER
    task = await create_generation_task(db, req)

    async def event_generator():
        async for event in stream_generation(db, task.id):
            yield f"event: {event['event']}\n"
            yield f"data: {json.dumps(event['data'], ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/rewrite")
async def generate_rewrite_stream(
    req: GenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    from app.models import TaskType
    req.task_type = TaskType.REWRITE
    task = await create_generation_task(db, req)

    async def event_generator():
        async for event in stream_generation(db, task.id):
            yield f"event: {event['event']}\n"
            yield f"data: {json.dumps(event['data'], ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/polish")
async def generate_polish_stream(
    req: GenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    from app.models import TaskType
    req.task_type = TaskType.POLISH
    task = await create_generation_task(db, req)

    async def event_generator():
        async for event in stream_generation(db, task.id):
            yield f"event: {event['event']}\n"
            yield f"data: {json.dumps(event['data'], ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{task_id}/interrupt")
async def interrupt_generation(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    success = await interrupt_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在或无法中断")
    return {"status": "interrupting", "task_id": str(task_id)}


@router.get("/{task_id}/status", response_model=GenerateTaskResponse)
async def get_task_status(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    task = await get_generation_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task
