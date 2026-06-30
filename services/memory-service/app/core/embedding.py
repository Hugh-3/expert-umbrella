import json
from typing import List, Optional
import httpx

from app.core.config import settings


class EmbeddingService:
    """Service for generating text embeddings using various providers."""

    def __init__(self):
        self.provider = settings.embedding_provider
        self.batch_size = settings.embedding_batch_size

    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text."""
        embeddings = await self._generate([text])
        return embeddings[0] if embeddings else []

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts in batches."""
        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            batch_embeddings = await self._generate(batch)
            all_embeddings.extend(batch_embeddings)
        return all_embeddings

    async def _generate(self, texts: List[str]) -> List[List[float]]:
        """Internal method to generate embeddings based on provider."""
        if self.provider == "openai":
            return await self._openai_generate(texts)
        elif self.provider == "ollama":
            return await self._ollama_generate(texts)
        else:
            return self._mock_generate(texts)

    async def _openai_generate(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {settings.embedding_api_url}",
                    "Content-Type": "application/json",
                },
                json={
                    "input": texts,
                    "model": settings.embedding_model,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]

    async def _ollama_generate(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Ollama API."""
        embeddings = []
        async with httpx.AsyncClient() as client:
            for text in texts:
                try:
                    response = await client.post(
                        settings.embedding_api_url,
                        json={
                            "model": settings.embedding_model,
                            "prompt": text,
                        },
                        timeout=30.0,
                    )
                    response.raise_for_status()
                    data = response.json()
                    embeddings.append(data.get("embedding", []))
                except Exception:
                    embeddings.append(self._mock_vector())
        return embeddings

    def _mock_generate(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings for testing."""
        import hashlib
        import numpy as np

        vectors = []
        for text in texts:
            hash_value = int(hashlib.md5(text.encode()).hexdigest(), 16)
            np.random.seed(hash_value % (2**32))
            vector = np.random.randn(settings.qdrant_vector_size).astype(float)
            vector = vector / np.linalg.norm(vector)
            vectors.append(vector.tolist())
        return vectors


embedding_service = EmbeddingService()
