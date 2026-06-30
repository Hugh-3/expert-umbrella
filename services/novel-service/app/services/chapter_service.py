import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Chapter, ChapterStatus, VersionSnapshot, OperationType
from app.schemas import ChapterCreate, ChapterUpdate


def count_words(text: str) -> int:
    if not text:
        return 0
    return len(text.replace(" ", "").replace("\n", ""))


async def get_chapters(
    db: AsyncSession,
    project_id: uuid.UUID,
) -> List[Chapter]:
    result = await db.execute(
        select(Chapter)
        .where(Chapter.project_id == project_id)
        .order_by(Chapter.order_index)
    )
    return list(result.scalars().all())


async def get_chapter(
    db: AsyncSession,
    chapter_id: uuid.UUID,
) -> Optional[Chapter]:
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    return result.scalar_one_or_none()


async def create_chapter(
    db: AsyncSession,
    project_id: uuid.UUID,
    chapter_in: ChapterCreate,
) -> Chapter:
    chapter = Chapter(
        project_id=project_id,
        title=chapter_in.title,
        order_index=chapter_in.order_index,
        content=chapter_in.content,
        word_count=count_words(chapter_in.content),
        status=chapter_in.status,
    )
    db.add(chapter)
    await db.commit()
    await db.refresh(chapter)
    await create_version_snapshot(db, chapter.id, chapter.content, OperationType.USER_EDIT, "system")
    return chapter


async def update_chapter(
    db: AsyncSession,
    chapter_id: uuid.UUID,
    chapter_in: ChapterUpdate,
    operator: str = "user",
    create_snapshot: bool = True,
) -> Optional[Chapter]:
    chapter = await get_chapter(db, chapter_id)
    if not chapter:
        return None
    old_content = chapter.content
    update_data = chapter_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(chapter, key, value)
    if "content" in update_data:
        chapter.word_count = count_words(chapter.content)
        chapter.version += 1
    await db.commit()
    await db.refresh(chapter)
    if create_snapshot and "content" in update_data:
        await create_version_snapshot(
            db, chapter.id, chapter.content, OperationType.USER_EDIT, operator
        )
    return chapter


async def create_version_snapshot(
    db: AsyncSession,
    chapter_id: uuid.UUID,
    content: str,
    operation_type: OperationType,
    operator: str,
) -> VersionSnapshot:
    snapshot = VersionSnapshot(
        chapter_id=chapter_id,
        content=content,
        operation_type=operation_type,
        operator=operator,
    )
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)
    return snapshot


async def get_version_snapshots(
    db: AsyncSession,
    chapter_id: uuid.UUID,
) -> List[VersionSnapshot]:
    result = await db.execute(
        select(VersionSnapshot)
        .where(VersionSnapshot.chapter_id == chapter_id)
        .order_by(VersionSnapshot.created_at.desc())
    )
    return list(result.scalars().all())


async def get_version_snapshot(
    db: AsyncSession,
    version_id: uuid.UUID,
) -> Optional[VersionSnapshot]:
    result = await db.execute(
        select(VersionSnapshot).where(VersionSnapshot.id == version_id)
    )
    return result.scalar_one_or_none()


async def rollback_chapter(
    db: AsyncSession,
    chapter_id: uuid.UUID,
    version_id: uuid.UUID,
) -> Optional[Chapter]:
    chapter = await get_chapter(db, chapter_id)
    snapshot = await get_version_snapshot(db, version_id)
    if not chapter or not snapshot or snapshot.chapter_id != chapter_id:
        return None
    chapter.content = snapshot.content
    chapter.word_count = count_words(snapshot.content)
    chapter.version += 1
    await db.commit()
    await db.refresh(chapter)
    await create_version_snapshot(
        db, chapter.id, chapter.content, OperationType.MERGE, "rollback"
    )
    return chapter
