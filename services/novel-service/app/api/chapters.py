import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas import (
    ChapterCreate,
    ChapterUpdate,
    ChapterResponse,
    VersionSnapshotResponse,
    RollbackRequest,
    DiffResponse,
)
from app.services import (
    get_project,
    get_chapters,
    get_chapter,
    create_chapter,
    update_chapter,
    get_version_snapshots,
    rollback_chapter,
    get_chapter_diff,
)

router = APIRouter()


@router.get("/projects/{project_id}/chapters", response_model=List[ChapterResponse])
async def list_chapters(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    chapters = await get_chapters(db, project_id)
    return chapters


@router.post("/projects/{project_id}/chapters", response_model=ChapterResponse, status_code=201)
async def create_new_chapter(
    project_id: uuid.UUID,
    chapter_in: ChapterCreate,
    db: AsyncSession = Depends(get_db),
):
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    chapter = await create_chapter(db, project_id, chapter_in)
    return chapter


@router.get("/chapters/{chapter_id}", response_model=ChapterResponse)
async def get_chapter_detail(
    chapter_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    chapter = await get_chapter(db, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    return chapter


@router.put("/chapters/{chapter_id}", response_model=ChapterResponse)
async def update_chapter_detail(
    chapter_id: uuid.UUID,
    chapter_in: ChapterUpdate,
    db: AsyncSession = Depends(get_db),
):
    chapter = await update_chapter(db, chapter_id, chapter_in)
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    return chapter


@router.get("/chapters/{chapter_id}/versions", response_model=List[VersionSnapshotResponse])
async def list_versions(
    chapter_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    chapter = await get_chapter(db, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    versions = await get_version_snapshots(db, chapter_id)
    return versions


@router.get("/chapters/{chapter_id}/diff", response_model=DiffResponse)
async def get_diff(
    chapter_id: uuid.UUID,
    from_version: uuid.UUID = Query(...),
    to_version: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    chapter = await get_chapter(db, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    diff_result = await get_chapter_diff(db, chapter_id, from_version, to_version)
    if not diff_result:
        raise HTTPException(status_code=404, detail="版本不存在")
    return diff_result


@router.post("/chapters/{chapter_id}/rollback", response_model=ChapterResponse)
async def rollback(
    chapter_id: uuid.UUID,
    req: RollbackRequest,
    db: AsyncSession = Depends(get_db),
):
    chapter = await rollback_chapter(db, chapter_id, req.version_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="章节或版本不存在")
    return chapter
