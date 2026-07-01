import json
from typing import List, Optional

import httpx

from ai_engine.providers.base import BaseProvider
from ai_engine.types import Message, GenerationParams, GenerationResult, StreamChunk


class AIProviderError(Exception):
    pass


class OpenAIProvider(BaseProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o",
        max_retries: int = 3,
        timeout: float = 120.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    def _get_headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _build_payload(
        self,
        messages: List[Message],
        params: GenerationParams,
        model: str,
        stream: bool = False,
    ) -> dict:
        payload = {
            "model": model,
            "messages": [m.model_dump() for m in messages],
            "temperature": params.temperature,
            "max_tokens": params.max_tokens,
            "top_p": params.top_p,
            "stream": stream,
        }
        if params.frequency_penalty != 0.0:
            payload["frequency_penalty"] = params.frequency_penalty
        if params.presence_penalty != 0.0:
            payload["presence_penalty"] = params.presence_penalty
        if params.stop:
            payload["stop"] = params.stop
        return payload

    async def _request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = await self._client.request(method, url, **kwargs)
                if response.status_code == 429:
                    retry_after = float(response.headers.get("retry-after", 2 ** attempt))
                    import asyncio
                    await asyncio.sleep(retry_after)
                    continue
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < self.max_retries - 1:
                    import asyncio
                    await asyncio.sleep(2 ** attempt)
                    last_exception = e
                    continue
                raise AIProviderError(f"API request failed: {e.response.status_code} - {e.response.text}") from e
            except httpx.HTTPError as e:
                if attempt < self.max_retries - 1:
                    import asyncio
                    await asyncio.sleep(2 ** attempt)
                    last_exception = e
                    continue
                raise AIProviderError(f"Network error: {str(e)}") from e
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
        payload = self._build_payload(messages, params, model, stream=False)
        response = await self._request_with_retry(
            "POST",
            f"{self.base_url}/chat/completions",
            headers=self._get_headers(),
            json=payload,
        )
        data = response.json()
        usage = data.get("usage", {})
        return GenerationResult(
            content=data["choices"][0]["message"]["content"],
            model=data.get("model", model),
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            finish_reason=data["choices"][0].get("finish_reason", "stop"),
        )

    async def stream(
        self,
        messages: List[Message],
        params: GenerationParams,
        model: str = "",
    ):
        model = model or self.model
        payload = self._build_payload(messages, params, model, stream=True)
        async with self._client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            headers=self._get_headers(),
            json=payload,
            timeout=self.timeout,
        ) as response:
            if response.status_code >= 400:
                error_text = await response.aread()
                raise AIProviderError(f"API request failed: {response.status_code} - {error_text}")
            async for line in response.aiter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    data_str = line[6:]
                else:
                    data_str = line
                if data_str == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    continue
                if "error" in data:
                    raise AIProviderError(f"API error: {data['error']}")
                choices = data.get("choices", [])
                if not choices:
                    continue
                delta = choices[0].get("delta", {})
                content = delta.get("content", "")
                finish_reason = choices[0].get("finish_reason")
                if content or finish_reason:
                    yield StreamChunk(
                        content=content,
                        model=data.get("model", model),
                        finish_reason=finish_reason,
                    )
