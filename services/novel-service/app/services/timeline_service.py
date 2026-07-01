import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project, Chapter, ChapterStatus
from app.schemas import TimelineResponse, TimelineNode


async def get_project_timeline(
    db: AsyncSession,
    project_id: uuid.UUID,
) -> TimelineResponse:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        return TimelineResponse(project_id=project_id, stages=[])

    chapters_result = await db.execute(
        select(Chapter)
        .where(Chapter.project_id == project_id)
        .order_by(Chapter.order_index)
    )
    chapters = chapters_result.scalars().all()

    stages = []

    stages.append(TimelineNode(
        stage="创意构思",
        status="completed" if chapters else "in_progress",
        description="生成故事大纲、人物设定、世界观",
        completed_at=project.created_at if chapters else None,
    ))

    has_chapters_outline = any(c.status == ChapterStatus.OUTLINE for c in chapters)
    stages.append(TimelineNode(
        stage="人物设定",
        status="completed" if has_chapters_outline else "pending",
        description="完善人物档案、关系网",
        completed_at=None,
    ))

    has_chapters = len(chapters) > 0
    stages.append(TimelineNode(
        stage="章节规划",
        status="completed" if has_chapters else "pending",
        description=f"共 {len(chapters)} 章",
        completed_at=chapters[0].created_at if chapters else None,
    ))

    drafted = sum(1 for c in chapters if c.status in (ChapterStatus.DRAFT, ChapterStatus.EDITING, ChapterStatus.FINALIZED))
    writing_status = "completed" if drafted == len(chapters) and drafted > 0 else ("in_progress" if drafted > 0 else "pending")
    stages.append(TimelineNode(
        stage="正文撰写",
        status=writing_status,
        description=f"已完成 {drafted}/{len(chapters)} 章",
        completed_at=None,
    ))

    finalized = sum(1 for c in chapters if c.status == ChapterStatus.FINALIZED)
    editing_status = "completed" if finalized == len(chapters) and finalized > 0 else ("in_progress" if finalized > 0 else "pending")
    stages.append(TimelineNode(
        stage="编辑优化",
        status=editing_status,
        description="自检与人工修改",
        completed_at=None,
    ))

    stages.append(TimelineNode(
        stage="导出发布",
        status="pending",
        description="多格式导出",
        completed_at=None,
    ))

    return TimelineResponse(project_id=project_id, stages=stages)
