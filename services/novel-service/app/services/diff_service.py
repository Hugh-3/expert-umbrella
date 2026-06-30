import difflib
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.chapter_service import get_version_snapshot, get_chapter


async def get_chapter_diff(
    db: AsyncSession,
    chapter_id: uuid.UUID,
    from_version_id: uuid.UUID,
    to_version_id: uuid.UUID,
) -> Optional[dict]:
    chapter = await get_chapter(db, chapter_id)
    if not chapter:
        return None
    from_snapshot = await get_version_snapshot(db, from_version_id)
    to_snapshot = await get_version_snapshot(db, to_version_id)
    if not from_snapshot or not to_snapshot:
        return None
    if from_snapshot.chapter_id != chapter_id or to_snapshot.chapter_id != chapter_id:
        return None
    from_lines = from_snapshot.content.splitlines(keepends=True)
    to_lines = to_snapshot.content.splitlines(keepends=True)
    diff = difflib.unified_diff(
        from_lines,
        to_lines,
        fromfile=str(from_version_id),
        tofile=str(to_version_id),
    )
    diff_text = "".join(diff)
    return {
        "from_version": str(from_version_id),
        "to_version": str(to_version_id),
        "diff": diff_text,
    }
