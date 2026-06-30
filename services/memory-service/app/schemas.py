from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class MemoryEntityCreate(BaseModel):
    project_id: str
    entity_type: str
    name: str
    description: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    chapter_id: Optional[str] = None


class MemoryEntityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class MemoryEntityResponse(BaseModel):
    id: str
    project_id: str
    entity_type: str
    name: str
    description: Optional[str] = None
    attributes: Dict[str, Any] = {}
    confidence: float = 0.0
    chapter_id: Optional[str] = None
    created_at: datetime
    score: Optional[float] = None


class SearchRequest(BaseModel):
    query: str
    project_id: str
    entity_types: Optional[List[str]] = None
    limit: int = Field(default=5, ge=1, le=50)


class SearchResponse(BaseModel):
    entities: List[MemoryEntityResponse]
    total: int
    query: str


class RAGContextResponse(BaseModel):
    entities: List[MemoryEntityResponse]
    context_text: str
    metadata: Dict[str, Any]


class BatchCreateResponse(BaseModel):
    created: int
    ids: List[str]
