import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import EntityType
from app.schemas import (
    MemoryEntityCreate,
    MemoryEntityUpdate,
    MemoryEntityResponse,
    MemorySearchRequest,
    MemoryExtractRequest,
)
from app.services import (
    get_project,
    get_entities,
    get_entity,
    create_entity,
    update_entity,
    delete_entity,
    search_entities,
    extract_entities_from_chapter,
)

router = APIRouter()


@router.get("/projects/{project_id}/entities", response_model=List[MemoryEntityResponse])
async def list_entities(
    project_id: uuid.UUID,
    entity_type: Optional[EntityType] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    entities, _ = await get_entities(db, project_id, entity_type=entity_type, skip=skip, limit=limit)
    return entities


@router.post("/projects/{project_id}/entities", response_model=MemoryEntityResponse, status_code=201)
async def create_new_entity(
    project_id: uuid.UUID,
    entity_in: MemoryEntityCreate,
    db: AsyncSession = Depends(get_db),
):
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    entity = await create_entity(db, project_id, entity_in)
    return entity


@router.put("/entities/{entity_id}", response_model=MemoryEntityResponse)
async def update_entity_detail(
    entity_id: uuid.UUID,
    entity_in: MemoryEntityUpdate,
    db: AsyncSession = Depends(get_db),
):
    entity = await update_entity(db, entity_id, entity_in)
    if not entity:
        raise HTTPException(status_code=404, detail="记忆实体不存在")
    return entity


@router.delete("/entities/{entity_id}", status_code=204)
async def delete_entity_by_id(
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    deleted = await delete_entity(db, entity_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="记忆实体不存在")
    return None


@router.post("/projects/{project_id}/search", response_model=List[MemoryEntityResponse])
async def search_memory(
    project_id: uuid.UUID,
    req: MemorySearchRequest,
    db: AsyncSession = Depends(get_db),
):
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    entities = await search_entities(
        db, project_id, req.query, entity_type=req.entity_type, limit=req.limit
    )
    return entities


@router.post("/projects/{project_id}/extract", response_model=List[MemoryEntityResponse])
async def extract_entities(
    project_id: uuid.UUID,
    req: MemoryExtractRequest,
    db: AsyncSession = Depends(get_db),
):
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    entities = await extract_entities_from_chapter(db, project_id, req.chapter_id)
    return entities
