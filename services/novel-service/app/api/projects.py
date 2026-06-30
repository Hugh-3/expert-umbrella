import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import ProjectStatus
from app.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    TimelineResponse,
)
from app.services import (
    get_projects,
    get_project,
    create_project,
    update_project,
    delete_project,
    get_project_timeline,
)

router = APIRouter()


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[ProjectStatus] = None,
    db: AsyncSession = Depends(get_db),
):
    projects, total = await get_projects(db, skip=skip, limit=limit, status=status)
    return ProjectListResponse(items=projects, total=total)


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_new_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    project = await create_project(db, project_in)
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_detail(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project_detail(
    project_id: uuid.UUID,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    project = await update_project(db, project_id, project_in)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project_by_id(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    deleted = await delete_project(db, project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="项目不存在")
    return None


@router.get("/{project_id}/timeline", response_model=TimelineResponse)
async def get_timeline(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    timeline = await get_project_timeline(db, project_id)
    return timeline
