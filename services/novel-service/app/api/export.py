import os
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import export_project_to_epub, export_project_to_pdf

router = APIRouter()


@router.post("/{project_id}/epub")
async def export_epub(
    project_id: uuid.UUID,
    chapter_ids: Optional[List[uuid.UUID]] = None,
    db: AsyncSession = Depends(get_db),
):
    try:
        file_path = await export_project_to_epub(db, project_id, chapter_ids)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="导出失败")

    filename = os.path.basename(file_path)
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/epub+zip",
    )


@router.post("/{project_id}/pdf")
async def export_pdf(
    project_id: uuid.UUID,
    chapter_ids: Optional[List[uuid.UUID]] = None,
    db: AsyncSession = Depends(get_db),
):
    try:
        file_path = await export_project_to_pdf(db, project_id, chapter_ids)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="导出失败")

    filename = os.path.basename(file_path)
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf",
    )


@router.get("/formats")
async def get_export_formats():
    return {
        "formats": [
            {"id": "epub", "name": "EPUB", "description": "适用于电子书阅读器的EPUB格式"},
            {"id": "pdf", "name": "PDF", "description": "通用PDF文档格式"},
        ]
    }
