from typing import List, Optional

import httpx

from ai_engine.providers.base import BaseProvider
from ai_engine.types import Message, GenerationParams, GenerationResult, StreamChunk


class OpenAIProvider(BaseProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o",
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(timeout=60.0)

    async def generate(
        self,
        messages: List[Message],
        params: GenerationParams,
        model: str = "",
    ) -> GenerationResult:
        model = model or self.model
        response = await self._client.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [m.model_dump() for m in messages],
                "temperature": params.temperature,
                "max_tokens": params.max_tokens,
                "top_p": params.top_p,
                "frequency_penalty": params.frequency_penalty,
                "presence_penalty": params.presence_penalty,
                "stop": params.stop,
                "stream": False,
            },
        )
        response.raise_for_status()
        data = response.json()
        return GenerationResult(
            content=data["choices"][0]["message"]["content"],
            model=data["model"],
            prompt_tokens=data["usage"]["prompt_tokens"],
            completion_tokens=data["usage"]["completion_tokens"],
            total_tokens=data["usage"]["total_tokens"],
            finish_reason=data["choices"][0]["finish_reason"],
        )

    async def stream(
        self,
        messages: List[Message],
        params: GenerationParams,
        model: str = "",
    ):
        model = model or self.model
        async with self._client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [m.model_dump() for m in messages],
                "temperature": params.temperature,
                "max_tokens": params.max_tokens,
                "stream": True,
            },
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    import json
                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
                    delta = data["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield StreamChunk(
                            content=content,
                            model=data.get("model", model),
                            finish_reason=data["choices"][0].get("finish_reason"),
                        )
