import asyncio
import uuid
from datetime import datetime
from typing import AsyncGenerator, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    GenerationTask,
    TaskStatus,
    TaskType,
    Chapter,
    OperationType,
)
from app.schemas import GenerateRequest
from app.services.ai_service import get_ai_engine, get_generation_params
from app.services.chapter_service import create_version_snapshot, count_words
from ai_engine import Message, Role


_active_tasks: dict[uuid.UUID, bool] = {}


async def create_generation_task(
    db: AsyncSession,
    req: GenerateRequest,
) -> GenerationTask:
    from app.core.config import settings

    task = GenerationTask(
        project_id=req.project_id,
        chapter_id=req.chapter_id,
        task_type=req.task_type,
        status=TaskStatus.QUEUED,
        model=req.model or settings.ai_model,
        parameters=req.parameters or {},
        prompt=req.prompt,
        progress=0.0,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_generation_task(
    db: AsyncSession,
    task_id: uuid.UUID,
) -> Optional[GenerationTask]:
    result = await db.execute(
        select(GenerationTask).where(GenerationTask.id == task_id)
    )
    return result.scalar_one_or_none()


async def update_task_status(
    db: AsyncSession,
    task_id: uuid.UUID,
    status: TaskStatus,
    progress: float | None = None,
    result: str | None = None,
    error: str | None = None,
):
    task = await get_generation_task(db, task_id)
    if not task:
        return
    task.status = status
    if progress is not None:
        task.progress = progress
    if result is not None:
        task.result = result
    if error is not None:
        task.error = error
    if status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.INTERRUPTED):
        task.completed_at = datetime.utcnow()
    await db.commit()


def build_messages(task_type: TaskType, prompt: str, context: str = "") -> list[Message]:
    messages = []
    if task_type == TaskType.OUTLINE:
        messages.append(Message(
            role=Role.SYSTEM,
            content="你是一位专业的小说创作助手，擅长生成结构清晰、情节吸引人的故事大纲。",
        ))
    elif task_type == TaskType.CHAPTER:
        messages.append(Message(
            role=Role.SYSTEM,
            content="你是一位专业的小说作家，擅长撰写引人入胜的章节内容。请保持文风统一，人物形象鲜明。",
        ))
    elif task_type == TaskType.REWRITE:
        messages.append(Message(
            role=Role.SYSTEM,
            content="你是一位专业的编辑，擅长改写和优化文本内容。",
        ))
    elif task_type == TaskType.POLISH:
        messages.append(Message(
            role=Role.SYSTEM,
            content="你是一位文字润色专家，擅长优化语言表达，提升文字美感。",
        ))
    else:
        messages.append(Message(
            role=Role.SYSTEM,
            content="你是一位创意写作助手。",
        ))
    if context:
        messages.append(Message(role=Role.USER, content=f"上下文：\n{context}"))
    messages.append(Message(role=Role.USER, content=prompt))
    return messages


async def stream_generation(
    db: AsyncSession,
    task_id: uuid.UUID,
) -> AsyncGenerator[dict, None]:
    task = await get_generation_task(db, task_id)
    if not task:
        yield {"event": "error", "data": {"error_code": "NOT_FOUND", "message": "任务不存在"}}
        return
    if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.INTERRUPTED):
        yield {"event": "error", "data": {"error_code": "ALREADY_FINISHED", "message": "任务已结束"}}
        return

    _active_tasks[task.id] = True
    await update_task_status(db, task.id, TaskStatus.RUNNING, progress=0.0)

    ai_engine = get_ai_engine()
    params = get_generation_params(task.parameters)
    context = ""
    if task.chapter_id:
        result = await db.execute(select(Chapter).where(Chapter.id == task.chapter_id))
        chapter = result.scalar_one_or_none()
        if chapter:
            context = chapter.content

    messages = build_messages(task.task_type, task.prompt, context)
    full_content = ""

    yield {
        "event": "start",
        "data": {"task_id": str(task.id), "model": task.model, "timestamp": datetime.utcnow().isoformat()},
    }

    position = 0
    try:
        async for chunk in ai_engine.stream(messages, params, task.model):
            if not _active_tasks.get(task.id, False):
                await update_task_status(
                    db, task.id, TaskStatus.INTERRUPTED,
                    progress=1.0, result=full_content,
                )
                yield {
                    "event": "interrupted",
                    "data": {"task_id": str(task.id), "partial_content": full_content},
                }
                return
            if chunk.content:
                full_content += chunk.content
                position += len(chunk.content)
                yield {
                    "event": "token",
                    "data": {
                        "task_id": str(task.id),
                        "content": chunk.content,
                        "position": position,
                    },
                }
            if chunk.finish_reason == "stop":
                break

        await update_task_status(
            db, task.id, TaskStatus.COMPLETED,
            progress=1.0, result=full_content,
        )

        if task.chapter_id and task.task_type in (TaskType.CHAPTER, TaskType.REWRITE, TaskType.POLISH):
            chapter_result = await db.execute(
                select(Chapter).where(Chapter.id == task.chapter_id)
            )
            chapter = chapter_result.scalar_one_or_none()
            if chapter:
                if task.task_type == TaskType.CHAPTER:
                    chapter.content = (chapter.content or "") + full_content
                else:
                    chapter.content = full_content
                chapter.word_count = count_words(chapter.content)
                chapter.version += 1
                await db.commit()
                await create_version_snapshot(
                    db, chapter.id, chapter.content,
                    OperationType.AI_GENERATE, "ai",
                )

        yield {
            "event": "done",
            "data": {
                "task_id": str(task.id),
                "final_content": full_content,
                "word_count": count_words(full_content),
            },
        }
    except Exception as e:
        await update_task_status(
            db, task.id, TaskStatus.FAILED,
            progress=1.0, error=str(e),
        )
        yield {
            "event": "error",
            "data": {"task_id": str(task.id), "error_code": "GENERATION_ERROR", "message": str(e)},
        }
    finally:
        _active_tasks.pop(task.id, None)


async def interrupt_task(db: AsyncSession, task_id: uuid.UUID) -> bool:
    task = await get_generation_task(db, task_id)
    if not task:
        return False
    if task.status not in (TaskStatus.RUNNING, TaskStatus.QUEUED):
        return False
    _active_tasks[task.id] = False
    return True
