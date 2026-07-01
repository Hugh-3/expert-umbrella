from ai_engine import AIEngine, GenerationParams

from app.core.config import settings


_ai_engine: AIEngine | None = None


def get_ai_engine() -> AIEngine:
    global _ai_engine
    if _ai_engine is None:
        kwargs = {}
        if settings.ai_provider == "openai":
            kwargs = {
                "api_key": settings.ai_api_key,
                "base_url": settings.ai_base_url or "https://api.openai.com/v1",
                "model": settings.ai_model,
                "max_retries": settings.ai_max_retries,
                "timeout": float(settings.ai_timeout),
            }
        elif settings.ai_provider == "ollama":
            kwargs = {
                "base_url": settings.ollama_base_url,
                "model": settings.ollama_model,
                "max_retries": settings.ollama_max_retries,
                "timeout": float(settings.ollama_timeout),
            }
        _ai_engine = AIEngine.create(settings.ai_provider, **kwargs)
    return _ai_engine


def reset_ai_engine() -> None:
    global _ai_engine
    _ai_engine = None


def get_generation_params(custom_params: dict | None = None) -> GenerationParams:
    params = GenerationParams(
        temperature=settings.ai_temperature,
        max_tokens=settings.ai_max_tokens,
    )
    if custom_params:
        for key, value in custom_params.items():
            if hasattr(params, key):
                setattr(params, key, value)
    return params
