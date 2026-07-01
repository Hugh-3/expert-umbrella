from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "memory-service"
    app_host: str = "0.0.0.0"
    app_port: int = 8001
    app_debug: bool = False

    # Qdrant Vector Database
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_grpc_port: int = 6334
    qdrant_collection_name: str = "memory_entities"
    qdrant_vector_size: int = 1536  # OpenAI embedding dimension
    qdrant_distance: str = "Cosine"

    # Embedding Service
    embedding_provider: str = "ollama"  # ollama, openai, mock
    embedding_api_url: str = "http://localhost:11434/api/embeddings"
    embedding_model: str = "nomic-embed-text"
    embedding_batch_size: int = 32

    # RAG Pipeline
    rag_top_k: int = 5
    rag_score_threshold: float = 0.7
    rag_context_window: int = 4096

    # Redis Cache (optional)
    redis_url: str = "redis://localhost:6379/1"
    enable_cache: bool = True
    cache_ttl: int = 3600


settings = Settings()
