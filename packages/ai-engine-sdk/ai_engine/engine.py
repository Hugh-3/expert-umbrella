from typing import List, Optional

from ai_engine.providers import BaseProvider, MockProvider, OpenAIProvider, OllamaProvider
from ai_engine.types import Message, GenerationParams, GenerationResult, StreamChunk


class AIEngine:
    def __init__(self, provider: BaseProvider):
        self.provider = provider

    @classmethod
    def create(
        cls,
        provider_type: str = "mock",
        **kwargs,
    ) -> "AIEngine":
        if provider_type == "mock":
            provider = MockProvider(model=kwargs.get("model", "mock-model"))
        elif provider_type == "openai":
            provider = OpenAIProvider(
                api_key=kwargs.get("api_key", ""),
                base_url=kwargs.get("base_url", "https://api.openai.com/v1"),
                model=kwargs.get("model", "gpt-4o"),
                max_retries=kwargs.get("max_retries", 3),
                timeout=kwargs.get("timeout", 120.0),
            )
        elif provider_type == "ollama":
            provider = OllamaProvider(
                base_url=kwargs.get("base_url", "http://localhost:11434"),
                model=kwargs.get("model", "llama3"),
                max_retries=kwargs.get("max_retries", 3),
                timeout=kwargs.get("timeout", 300.0),
            )
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
        return cls(provider)

    async def generate(
        self,
        messages: List[Message],
        params: Optional[GenerationParams] = None,
        model: str = "",
    ) -> GenerationResult:
        params = params or GenerationParams()
        return await self.provider.generate(messages, params, model)

    async def stream(
        self,
        messages: List[Message],
        params: Optional[GenerationParams] = None,
        model: str = "",
    ):
        params = params or GenerationParams()
        async for chunk in self.provider.stream(messages, params, model):
            yield chunk
