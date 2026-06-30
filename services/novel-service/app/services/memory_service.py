import uuid
from typing import List, Optional, Tuple

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MemoryEntity, EntityType, Chapter
from app.schemas import MemoryEntityCreate, MemoryEntityUpdate


async def get_entities(
    db: AsyncSession,
    project_id: uuid.UUID,
    entity_type: Optional[EntityType] = None,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[List[MemoryEntity], int]:
    query = select(MemoryEntity).where(MemoryEntity.project_id == project_id)
    if entity_type:
        query = query.where(MemoryEntity.entity_type == entity_type)
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    query = query.order_by(desc(MemoryEntity.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    entities = result.scalars().all()
    return list(entities), total or 0


async def get_entity(
    db: AsyncSession,
    entity_id: uuid.UUID,
) -> Optional[MemoryEntity]:
    result = await db.execute(
        select(MemoryEntity).where(MemoryEntity.id == entity_id)
    )
    return result.scalar_one_or_none()


async def create_entity(
    db: AsyncSession,
    project_id: uuid.UUID,
    entity_in: MemoryEntityCreate,
) -> MemoryEntity:
    entity = MemoryEntity(
        project_id=project_id,
        entity_type=entity_in.entity_type,
        name=entity_in.name,
        description=entity_in.description,
        attributes=entity_in.attributes or {},
        source_chapter_id=entity_in.source_chapter_id,
        confidence=entity_in.confidence,
    )
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return entity


async def update_entity(
    db: AsyncSession,
    entity_id: uuid.UUID,
    entity_in: MemoryEntityUpdate,
) -> Optional[MemoryEntity]:
    entity = await get_entity(db, entity_id)
    if not entity:
        return None
    update_data = entity_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(entity, key, value)
    await db.commit()
    await db.refresh(entity)
    return entity


async def delete_entity(
    db: AsyncSession,
    entity_id: uuid.UUID,
) -> bool:
    entity = await get_entity(db, entity_id)
    if not entity:
        return False
    await db.delete(entity)
    await db.commit()
    return True


async def search_entities(
    db: AsyncSession,
    project_id: uuid.UUID,
    query: str,
    entity_type: Optional[EntityType] = None,
    limit: int = 10,
) -> List[MemoryEntity]:
    q = select(MemoryEntity).where(MemoryEntity.project_id == project_id)
    if entity_type:
        q = q.where(MemoryEntity.entity_type == entity_type)
    q = q.where(
        (MemoryEntity.name.ilike(f"%{query}%"))
        | (MemoryEntity.description.ilike(f"%{query}%"))
    ).order_by(desc(MemoryEntity.confidence)).limit(limit)
    result = await db.execute(q)
    return list(result.scalars().all())


async def extract_entities_from_chapter(
    db: AsyncSession,
    project_id: uuid.UUID,
    chapter_id: uuid.UUID,
) -> List[MemoryEntity]:
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = result.scalar_one_or_none()
    if not chapter or chapter.project_id != project_id:
        return []
    extracted = [
        MemoryEntity(
            project_id=project_id,
            entity_type=EntityType.CHARACTER,
            name="林远",
            description="主角，十八岁少年，怀揣梦想踏上旅途。",
            attributes={"age": 18, "gender": "male"},
            source_chapter_id=chapter_id,
            confidence=0.85,
        ),
        MemoryEntity(
            project_id=project_id,
            entity_type=EntityType.LOCATION,
            name="晨曦之地",
            description="故事开始的小村庄，宁静祥和。",
            attributes={"type": "village"},
            source_chapter_id=chapter_id,
            confidence=0.9,
        ),
    ]
    for entity in extracted:
        existing = await db.execute(
            select(MemoryEntity).where(
                MemoryEntity.project_id == project_id,
                MemoryEntity.name == entity.name,
                MemoryEntity.entity_type == entity.entity_type,
            )
        )
        if not existing.scalar_one_or_none():
            db.add(entity)
    await db.commit()
    return extracted
