import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

from app.models import ProjectType, ProjectStatus, ChapterStatus, OperationType, TaskType, TaskStatus, EntityType


class ProjectBase(BaseModel):
    name: str
    type: ProjectType = ProjectType.NOVEL
    cover_image: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default=None, validation_alias="project_metadata")

    model_config = {"from_attributes": True, "populate_by_name": True}


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[ProjectStatus] = None
    cover_image: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ProjectResponse(ProjectBase):
    id: uuid.UUID
    status: ProjectStatus
    owner_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    items: List[ProjectResponse]
    total: int


class ChapterBase(BaseModel):
    title: str
    order_index: int = 0
    content: str = ""
    status: ChapterStatus = ChapterStatus.OUTLINE


class ChapterCreate(ChapterBase):
    pass


class ChapterUpdate(BaseModel):
    title: Optional[str] = None
    order_index: Optional[int] = None
    content: Optional[str] = None
    status: Optional[ChapterStatus] = None


class ChapterResponse(ChapterBase):
    id: uuid.UUID
    project_id: uuid.UUID
    word_count: int
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VersionSnapshotResponse(BaseModel):
    id: uuid.UUID
    chapter_id: uuid.UUID
    operation_type: OperationType
    operator: Optional[str] = None
    word_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class RollbackRequest(BaseModel):
    version_id: uuid.UUID


class DiffResponse(BaseModel):
    from_version: str
    to_version: str
    diff: str


class GenerateRequest(BaseModel):
    project_id: uuid.UUID
    chapter_id: Optional[uuid.UUID] = None
    task_type: TaskType
    prompt: str = ""
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class GenerateTaskResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    chapter_id: Optional[uuid.UUID] = None
    task_type: TaskType
    status: TaskStatus
    model: str
    progress: float
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MemoryEntityBase(BaseModel):
    entity_type: EntityType
    name: str
    description: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    source_chapter_id: Optional[uuid.UUID] = None
    confidence: float = 0.0


class MemoryEntityCreate(MemoryEntityBase):
    pass


class MemoryEntityUpdate(BaseModel):
    entity_type: Optional[EntityType] = None
    name: Optional[str] = None
    description: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None


class MemoryEntityResponse(MemoryEntityBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MemorySearchRequest(BaseModel):
    query: str
    entity_type: Optional[EntityType] = None
    limit: int = 10


class MemoryExtractRequest(BaseModel):
    chapter_id: uuid.UUID


class FeedbackCreate(BaseModel):
    task_id: uuid.UUID
    overall_rating: Optional[int] = Field(None, ge=1, le=5)
    creativity_rating: Optional[int] = Field(None, ge=1, le=5)
    coherence_rating: Optional[int] = Field(None, ge=1, le=5)
    style_rating: Optional[int] = Field(None, ge=1, le=5)
    character_rating: Optional[int] = Field(None, ge=1, le=5)
    issues: Optional[List[str]] = None
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    overall_rating: Optional[int] = None
    creativity_rating: Optional[int] = None
    coherence_rating: Optional[int] = None
    style_rating: Optional[int] = None
    character_rating: Optional[int] = None
    issues: Optional[List[str]] = None
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SelfCheckRequest(BaseModel):
    chapter_id: uuid.UUID


class SelfCheckItem(BaseModel):
    check_type: str
    passed: bool
    details: str


class SelfCheckResponse(BaseModel):
    chapter_id: uuid.UUID
    overall_passed: bool
    checks: List[SelfCheckItem]


class LockAcquireRequest(BaseModel):
    resource: str
    lock_type: str = "write"
    holder: str
    timeout: int = 1800


class LockReleaseRequest(BaseModel):
    resource: str
    holder: str


class LockStatusResponse(BaseModel):
    resource: str
    locked: bool
    holder: Optional[str] = None
    acquired_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class TimelineNode(BaseModel):
    stage: str
    status: str
    description: str
    completed_at: Optional[datetime] = None


class TimelineResponse(BaseModel):
    project_id: uuid.UUID
    stages: List[TimelineNode]
