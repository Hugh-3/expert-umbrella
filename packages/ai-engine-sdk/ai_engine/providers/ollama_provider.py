from typing import List, AsyncGenerator

import httpx

from ai_engine.providers.base import BaseProvider
from ai_engine.types import Message, GenerationParams, GenerationResult, StreamChunk


class OllamaProvider(BaseProvider):
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3",
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(timeout=120.0)

    async def generate(
        self,
        messages: List[Message],
        params: GenerationParams,
        model: str = "",
    ) -> GenerationResult:
        model = model or self.model
        response = await self._client.post(
            f"{self.base_url}/api/chat",
            json={
                "model": model,
                "messages": [m.model_dump() for m in messages],
                "stream": False,
                "options": {
                    "temperature": params.temperature,
                    "num_predict": params.max_tokens,
                    "top_p": params.top_p,
                },
            },
        )
        response.raise_for_status()
        data = response.json()
        return GenerationResult(
            content=data["message"]["content"],
            model=data.get("model", model),
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            finish_reason="stop",
        )

    async def stream(
        self,
        messages: List[Message],
        params: GenerationParams,
        model: str = "",
    ) -> AsyncGenerator[StreamChunk, None]:
        model = model or self.model
        async with self._client.stream(
            "POST",
            f"{self.base_url}/api/chat",
            json={
                "model": model,
                "messages": [m.model_dump() for m in messages],
                "stream": True,
                "options": {
                    "temperature": params.temperature,
                    "num_predict": params.max_tokens,
                    "top_p": params.top_p,
                },
            },
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                import json
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if data.get("done", False):
                    yield StreamChunk(
                        content="",
                        model=data.get("model", model),
                        finish_reason="stop",
                    )
                    break
                content = data.get("message", {}).get("content", "")
                if content:
                    yield StreamChunk(
                        content=content,
                        model=data.get("model", model),
                        finish_reason=None,
                    )
