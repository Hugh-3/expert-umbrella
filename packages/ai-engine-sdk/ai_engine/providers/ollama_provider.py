import json
from typing import List, AsyncGenerator

import httpx

from ai_engine.providers.base import BaseProvider
from ai_engine.providers.openai_provider import AIProviderError
from ai_engine.types import Message, GenerationParams, GenerationResult, StreamChunk


class OllamaProvider(BaseProvider):
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3",
        max_retries: int = 3,
        timeout: float = 300.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    def _build_options(self, params: GenerationParams) -> dict:
        options = {
            "temperature": params.temperature,
            "num_predict": params.max_tokens,
            "top_p": params.top_p,
        }
        if params.stop:
            options["stop"] = params.stop
        if params.frequency_penalty != 0.0:
            options["frequency_penalty"] = params.frequency_penalty
        if params.presence_penalty != 0.0:
            options["presence_penalty"] = params.presence_penalty
        return options

    async def _request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = await self._client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < self.max_retries - 1:
                    import asyncio
                    await asyncio.sleep(2 ** attempt)
                    last_exception = e
                    continue
                raise AIProviderError(f"Ollama API failed: {e.response.status_code} - {e.response.text}") from e
            except httpx.HTTPError as e:
                if attempt < self.max_retries - 1:
                    import asyncio
                    await asyncio.sleep(2 ** attempt)
                    last_exception = e
                    continue
                raise AIProviderError(f"Ollama network error: {str(e)}") from e
        if last_exception:
            raise AIProviderError(f"Max retries exceeded: {str(last_exception)}") from last_exception
        raise AIProviderError("Max retries exceeded")

    async def generate(
        self,
        messages: List[Message],
        params: GenerationParams,
        model: str = "",
    ) -> GenerationResult:
        model = model or self.model
        payload = {
            "model": model,
            "messages": [m.model_dump() for m in messages],
            "stream": False,
            "options": self._build_options(params),
        }
        response = await self._request_with_retry(
            "POST",
            f"{self.base_url}/api/chat",
            json=payload,
        )
        data = response.json()
        prompt_eval_count = data.get("prompt_eval_count", 0)
        eval_count = data.get("eval_count", 0)
        return GenerationResult(
            content=data["message"]["content"],
            model=data.get("model", model),
            prompt_tokens=prompt_eval_count,
            completion_tokens=eval_count,
            total_tokens=prompt_eval_count + eval_count,
            finish_reason="stop",
        )

    async def stream(
        self,
        messages: List[Message],
        params: GenerationParams,
        model: str = "",
    ) -> AsyncGenerator[StreamChunk, None]:
        model = model or self.model
        payload = {
            "model": model,
            "messages": [m.model_dump() for m in messages],
            "stream": True,
            "options": self._build_options(params),
        }
        async with self._client.stream(
            "POST",
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout,
        ) as response:
            if response.status_code >= 400:
                error_text = await response.aread()
                raise AIProviderError(f"Ollama API failed: {response.status_code} - {error_text}")
            async for line in response.aiter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if "error" in data:
                    raise AIProviderError(f"Ollama error: {data['error']}")
                content = data.get("message", {}).get("content", "")
                done = data.get("done", False)
                if done:
                    yield StreamChunk(
                        content=content,
                        model=data.get("model", model),
                        finish_reason="stop",
                    )
                    break
                if content:
                    yield StreamChunk(
                        content=content,
                        model=data.get("model", model),
                        finish_reason=None,
                    )
