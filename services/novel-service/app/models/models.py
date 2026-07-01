import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, Integer, String, Text, Float, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProjectType(str, PyEnum):
    NOVEL = "novel"
    MUSIC = "music"
    SHORT_VIDEO = "short_video"
    MICRO_FILM = "micro_film"


class ProjectStatus(str, PyEnum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ChapterStatus(str, PyEnum):
    OUTLINE = "outline"
    DRAFT = "draft"
    EDITING = "editing"
    FINALIZED = "finalized"


class OperationType(str, PyEnum):
    AI_GENERATE = "ai_generate"
    USER_EDIT = "user_edit"
    MERGE = "merge"


class TaskType(str, PyEnum):
    OUTLINE = "outline"
    CHAPTER = "chapter"
    REWRITE = "rewrite"
    POLISH = "polish"
    IDEAS = "ideas"


class TaskStatus(str, PyEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class EntityType(str, PyEnum):
    CHARACTER = "character"
    LOCATION = "location"
    WORLD_RULE = "world_rule"
    EVENT = "event"
    ITEM = "item"


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(Enum(ProjectType), nullable=False, default=ProjectType.NOVEL)
    status = Column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.DRAFT)
    cover_image = Column(String(500), nullable=True)
    project_metadata = Column("metadata", JSON, nullable=True, default=lambda: {})
    owner_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    chapters = relationship("Chapter", back_populates="project", cascade="all, delete-orphan")
    memory_entities = relationship("MemoryEntity", back_populates="project", cascade="all, delete-orphan")


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)
    content = Column(Text, nullable=True, default="")
    word_count = Column(Integer, nullable=False, default=0)
    status = Column(Enum(ChapterStatus), nullable=False, default=ChapterStatus.OUTLINE)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="chapters")
    versions = relationship("VersionSnapshot", back_populates="chapter", cascade="all, delete-orphan")


class VersionSnapshot(Base):
    __tablename__ = "version_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    content = Column(Text, nullable=False)
    operation_type = Column(Enum(OperationType), nullable=False)
    operator = Column(String(100), nullable=True)
    diff_from_prev = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    chapter = relationship("Chapter", back_populates="versions")


class MemoryEntity(Base):
    __tablename__ = "memory_entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    entity_type = Column(Enum(EntityType), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    attributes = Column(JSON, nullable=True, default=dict)
    source_chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=True)
    confidence = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="memory_entities")


class GenerationTask(Base):
    __tablename__ = "generation_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=True)
    task_type = Column(Enum(TaskType), nullable=False)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.QUEUED)
    model = Column(String(100), nullable=False, default="mock-model")
    parameters = Column(JSON, nullable=True, default=dict)
    prompt = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    progress = Column(Float, nullable=False, default=0.0)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    feedbacks = relationship("Feedback", back_populates="task")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("generation_tasks.id"), nullable=False)
    overall_rating = Column(Integer, nullable=True)
    creativity_rating = Column(Integer, nullable=True)
    coherence_rating = Column(Integer, nullable=True)
    style_rating = Column(Integer, nullable=True)
    character_rating = Column(Integer, nullable=True)
    issues = Column(JSON, nullable=True, default=list)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    task = relationship("GenerationTask", back_populates="feedbacks")
