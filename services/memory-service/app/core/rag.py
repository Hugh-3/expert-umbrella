from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from app.core.config import settings
from app.core.vector_store import vector_store, MemoryEntity
from app.core.embedding import embedding_service


@dataclass
class RAGContext:
    """RAG retrieval context with source information."""
    entities: List[MemoryEntity]
    context_text: str
    metadata: Dict[str, Any]


class RAGPipeline:
    """
    RAG (Retrieval-Augmented Generation) Pipeline for Memory Service.
    
    Workflow:
    1. Query Understanding - Parse and enhance the user query
    2. Retrieval - Search for relevant memory entities
    3. Context Building - Build context from retrieved entities
    4. (Future) Generation - Generate response with context
    """

    def __init__(self):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.top_k = settings.rag_top_k
        self.score_threshold = settings.rag_score_threshold
        self.context_window = settings.rag_context_window

    async def retrieve(
        self,
        query: str,
        project_id: str,
        entity_types: Optional[List[str]] = None,
        top_k: Optional[int] = None,
    ) -> List[MemoryEntity]:
        """
        Retrieve relevant memory entities for a query.
        
        Args:
            query: The search/query text
            project_id: Project context for the search
            entity_types: Optional filter by entity types
            top_k: Number of results to return (overrides default)
            
        Returns:
            List of relevant MemoryEntity objects with similarity scores
        """
        query_vector = await self.embedding_service.get_embedding(query)
        
        results = self.vector_store.search(
            query_vector=query_vector,
            project_id=project_id,
            entity_types=entity_types,
            limit=top_k or self.top_k,
            score_threshold=self.score_threshold,
        )
        
        return results

    async def build_context(
        self,
        query: str,
        project_id: str,
        entity_types: Optional[List[str]] = None,
        include_attributes: bool = True,
    ) -> RAGContext:
        """
        Build a complete RAG context for generation.
        
        Args:
            query: The search/query text
            project_id: Project context
            entity_types: Optional filter by entity types
            include_attributes: Include entity attributes in context
            
        Returns:
            RAGContext with entities and formatted context text
        """
        entities = await self.retrieve(query, project_id, entity_types)
        
        context_parts = []
        entity_map = {}
        
        for i, entity in enumerate(entities):
            entity_map[entity.entity_type] = entity_map.get(entity.entity_type, [])
            entity_map[entity.entity_type].append(entity)
            
            part = f"[{i+1}] {entity.entity_type.upper()}: {entity.name}"
            if entity.description:
                part += f"\n   描述: {entity.description}"
            if include_attributes and entity.attributes:
                attrs_str = ", ".join(f"{k}={v}" for k, v in entity.attributes.items())
                part += f"\n   属性: {attrs_str}"
            if entity.score:
                part += f"\n   相关度: {entity.score:.2f}"
            context_parts.append(part)
        
        context_text = "\n\n".join(context_parts)
        
        summary_parts = []
        for etype, ents in entity_map.items():
            names = ", ".join(e.name for e in ents)
            summary_parts.append(f"{etype}({len(ents)}): {names}")
        
        metadata = {
            "query": query,
            "entity_count": len(entities),
            "entity_types": list(entity_map.keys()),
            "entity_summary": "; ".join(summary_parts),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        return RAGContext(
            entities=entities,
            context_text=context_text,
            metadata=metadata,
        )

    async def search_and_summarize(
        self,
        query: str,
        project_id: str,
        entity_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Search and return a structured summary of results.
        
        Returns:
            Dict with entities grouped by type and summary
        """
        entities = await self.retrieve(query, project_id, entity_types)
        
        grouped = {}
        for entity in entities:
            etype = entity.entity_type
            if etype not in grouped:
                grouped[etype] = []
            grouped[etype].append({
                "id": entity.id,
                "name": entity.name,
                "description": entity.description,
                "confidence": entity.confidence,
                "score": entity.score,
            })
        
        return {
            "query": query,
            "total_found": len(entities),
            "grouped_by_type": grouped,
            "context": "\n".join(
                f"- {e.name}: {e.description or '无描述'}"
                for e in entities
            ),
        }


rag_pipeline = RAGPipeline()
