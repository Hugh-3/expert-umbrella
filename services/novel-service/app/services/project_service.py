import uuid
from typing import List, Optional, Tuple

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project, ProjectStatus, ProjectType
from app.schemas import ProjectCreate, ProjectUpdate


async def get_projects(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    status: Optional[ProjectStatus] = None,
) -> Tuple[List[Project], int]:
    query = select(Project)
    if status:
        query = query.where(Project.status == status)
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    query = query.order_by(desc(Project.updated_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    projects = result.scalars().all()
    return list(projects), total or 0


async def get_project(db: AsyncSession, project_id: uuid.UUID) -> Optional[Project]:
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()


async def create_project(db: AsyncSession, project_in: ProjectCreate) -> Project:
    project = Project(
        name=project_in.name,
        type=project_in.type,
        cover_image=project_in.cover_image,
        project_metadata=project_in.metadata or {},
        status=ProjectStatus.DRAFT,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def update_project(
    db: AsyncSession,
    project_id: uuid.UUID,
    project_in: ProjectUpdate,
) -> Optional[Project]:
    project = await get_project(db, project_id)
    if not project:
        return None
    update_data = project_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project_id: uuid.UUID) -> bool:
    project = await get_project(db, project_id)
    if not project:
        return False
    await db.delete(project)
    await db.commit()
    return True
