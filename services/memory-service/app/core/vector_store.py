import uuid
from typing import List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    MatchAny,
    ScrollResult,
)
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import settings


class EntityType(str, Enum):
    CHARACTER = "character"
    LOCATION = "location"
    WORLD_RULE = "world_rule"
    EVENT = "event"
    ITEM = "item"


@dataclass
class MemoryEntity:
    id: str
    project_id: str
    entity_type: str
    name: str
    description: Optional[str]
    attributes: dict
    confidence: float
    chapter_id: Optional[str]
    created_at: datetime
    vector: Optional[List[float]] = None
    score: Optional[float] = None


class VectorStore:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            grpc_port=settings.qdrant_grpc_port,
        )
        self.collection_name = settings.qdrant_collection_name
        self._ensure_collection()

    def _ensure_collection(self):
        """Ensure the collection exists with proper configuration."""
        try:
            self.client.get_collection(self.collection_name)
        except (UnexpectedResponse, Exception):
            distance_map = {
                "Cosine": Distance.COSINE,
                "Euclidean": Distance.EUCLID,
                "Dot": Distance.DOT,
            }
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.qdrant_vector_size,
                    distance=distance_map.get(settings.qdrant_distance, Distance.COSINE),
                ),
            )

    def upsert_entity(self, entity: MemoryEntity, vector: List[float]) -> bool:
        """Upsert a memory entity with its embedding vector."""
        point = PointStruct(
            id=entity.id,
            vector=vector,
            payload={
                "project_id": entity.project_id,
                "entity_type": entity.entity_type,
                "name": entity.name,
                "description": entity.description or "",
                "attributes": entity.attributes,
                "confidence": entity.confidence,
                "chapter_id": entity.chapter_id or "",
                "created_at": entity.created_at.isoformat(),
            },
        )
        self.client.upsert(collection_name=self.collection_name, points=[point])
        return True

    def search(
        self,
        query_vector: List[float],
        project_id: str,
        entity_types: Optional[List[str]] = None,
        limit: int = 5,
        score_threshold: float = 0.0,
    ) -> List[MemoryEntity]:
        """Search for similar memory entities using vector similarity."""
        must_conditions = [
            FieldCondition(
                key="project_id",
                match=MatchValue(value=project_id),
            )
        ]
        if entity_types:
            must_conditions.append(
                FieldCondition(
                    key="entity_type",
                    match=MatchAny(any=entity_types),
                )
            )

        search_filter = Filter(must=must_conditions)

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=search_filter,
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True,
        )

        entities = []
        for result in results:
            payload = result.payload
            entities.append(
                MemoryEntity(
                    id=str(result.id),
                    project_id=payload["project_id"],
                    entity_type=payload["entity_type"],
                    name=payload["name"],
                    description=payload.get("description", ""),
                    attributes=payload.get("attributes", {}),
                    confidence=payload.get("confidence", 0.0),
                    chapter_id=payload.get("chapter_id") or None,
                    created_at=datetime.fromisoformat(payload["created_at"]),
                    score=result.score,
                )
            )
        return entities

    def delete_entity(self, entity_id: str) -> bool:
        """Delete a memory entity by ID."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=[entity_id],
        )
        return True

    def delete_project_entities(self, project_id: str) -> int:
        """Delete all entities for a project."""
        results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[FieldCondition(key="project_id", match=MatchValue(value=project_id))]
            ),
            limit=100,
            with_payload=False,
        )

        if results.points:
            ids = [p.id for p in results.points]
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=ids,
            )
            return len(ids)
        return 0

    def count(self, project_id: Optional[str] = None) -> int:
        """Count entities in the collection."""
        if project_id:
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[FieldCondition(key="project_id", match=MatchValue(value=project_id))]
                ),
                limit=0,
                with_payload=False,
            )
            return len(results.points)
        info = self.client.get_collection(self.collection_name)
        return info.vectors_count


vector_store = VectorStore()
