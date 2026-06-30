from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import datetime
import uuid

from app.core.config import settings
from app.core.vector_store import vector_store, MemoryEntity
from app.core.embedding import embedding_service
from app.core.rag import rag_pipeline
from app.schemas import (
    MemoryEntityCreate,
    MemoryEntityUpdate,
    MemoryEntityResponse,
    SearchRequest,
    SearchResponse,
    RAGContextResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {settings.app_name}...")
    print(f"Qdrant: {settings.qdrant_host}:{settings.qdrant_port}")
    print(f"Embedding: {settings.embedding_provider}")
    yield
    print(f"Shutting down {settings.app_name}...")


app = FastAPI(
    title=settings.app_name,
    description="Memory Service with Vector Search and RAG Pipeline",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "qdrant_connected": True,
        "embedding_provider": settings.embedding_provider,
    }


@app.get("/stats")
async def get_stats(project_id: Optional[str] = None):
    """Get memory entity statistics."""
    count = vector_store.count(project_id)
    return {
        "total_entities": count,
        "project_id": project_id,
    }


@app.post("/entities", response_model=MemoryEntityResponse)
async def create_entity(entity_in: MemoryEntityCreate):
    """Create a new memory entity with vector embedding."""
    entity_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    text_for_embedding = f"{entity_in.name} {entity_in.description or ''}"
    vector = await embedding_service.get_embedding(text_for_embedding)
    
    entity = MemoryEntity(
        id=entity_id,
        project_id=entity_in.project_id,
        entity_type=entity_in.entity_type,
        name=entity_in.name,
        description=entity_in.description,
        attributes=entity_in.attributes or {},
        confidence=entity_in.confidence,
        chapter_id=entity_in.chapter_id,
        created_at=now,
        vector=vector,
    )
    
    vector_store.upsert_entity(entity, vector)
    
    return MemoryEntityResponse(
        id=entity_id,
        project_id=entity.project_id,
        entity_type=entity.entity_type,
        name=entity.name,
        description=entity.description,
        attributes=entity.attributes,
        confidence=entity.confidence,
        chapter_id=entity.chapter_id,
        created_at=now,
    )


@app.post("/entities/batch")
async def create_entities_batch(entities_in: List[MemoryEntityCreate]):
    """Create multiple memory entities in batch."""
    results = []
    now = datetime.utcnow()
    
    texts = [f"{e.name} {e.description or ''}" for e in entities_in]
    vectors = await embedding_service.get_embeddings(texts)
    
    for i, entity_in in enumerate(entities_in):
        entity_id = str(uuid.uuid4())
        
        entity = MemoryEntity(
            id=entity_id,
            project_id=entity_in.project_id,
            entity_type=entity_in.entity_type,
            name=entity_in.name,
            description=entity_in.description,
            attributes=entity_in.attributes or {},
            confidence=entity_in.confidence,
            chapter_id=entity_in.chapter_id,
            created_at=now,
            vector=vectors[i],
        )
        
        vector_store.upsert_entity(entity, vectors[i])
        results.append(entity_id)
    
    return {"created": len(results), "ids": results}


@app.delete("/entities/{entity_id}")
async def delete_entity(entity_id: str):
    """Delete a memory entity."""
    success = vector_store.delete_entity(entity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entity not found")
    return {"deleted": entity_id}


@app.delete("/entities/project/{project_id}")
async def delete_project_entities(project_id: str):
    """Delete all entities for a project."""
    count = vector_store.delete_project_entities(project_id)
    return {"deleted": count, "project_id": project_id}


@app.post("/search", response_model=SearchResponse)
async def search_entities(request: SearchRequest):
    """Vector similarity search for memory entities."""
    results = await rag_pipeline.retrieve(
        query=request.query,
        project_id=request.project_id,
        entity_types=request.entity_types,
        top_k=request.limit,
    )
    
    entities = [
        MemoryEntityResponse(
            id=e.id,
            project_id=e.project_id,
            entity_type=e.entity_type,
            name=e.name,
            description=e.description,
            attributes=e.attributes,
            confidence=e.confidence,
            chapter_id=e.chapter_id,
            created_at=e.created_at,
            score=e.score,
        )
        for e in results
    ]
    
    return SearchResponse(
        entities=entities,
        total=len(entities),
        query=request.query,
    )


@app.post("/rag/context", response_model=RAGContextResponse)
async def get_rag_context(request: SearchRequest):
    """Get full RAG context for generation."""
    context = await rag_pipeline.build_context(
        query=request.query,
        project_id=request.project_id,
        entity_types=request.entity_types,
    )
    
    return RAGContextResponse(
        entities=[
            MemoryEntityResponse(
                id=e.id,
                project_id=e.project_id,
                entity_type=e.entity_type,
                name=e.name,
                description=e.description,
                attributes=e.attributes,
                confidence=e.confidence,
                chapter_id=e.chapter_id,
                created_at=e.created_at,
                score=e.score,
            )
            for e in context.entities
        ],
        context_text=context.context_text,
        metadata=context.metadata,
    )


@app.post("/rag/summary")
async def get_rag_summary(request: SearchRequest):
    """Get a structured summary of search results."""
    summary = await rag_pipeline.search_and_summarize(
        query=request.query,
        project_id=request.project_id,
        entity_types=request.entity_types,
    )
    return summary


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
    )
