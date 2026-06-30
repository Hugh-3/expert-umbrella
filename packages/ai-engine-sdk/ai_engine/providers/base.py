from abc import ABC, abstractmethod
from typing import AsyncGenerator, List

from ai_engine.types import Message, GenerationParams, GenerationResult, StreamChunk


class BaseProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        params: GenerationParams,
        model: str = "",
    ) -> GenerationResult:
        pass

    @abstractmethod
    async def stream(
        self,
        messages: List[Message],
        params: GenerationParams,
        model: str = "",
    ) -> AsyncGenerator[StreamChunk, None]:
        pass
