from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "novel-service"
    app_env: str = "development"
    app_debug: bool = True

    database_url: str = "sqlite+aiosqlite:///./novel_service.db"

    redis_url: str = "redis://localhost:6379/0"
    nats_url: str = "nats://localhost:4222"

    ai_provider: str = "mock"
    ai_api_key: str = ""
    ai_base_url: str = ""
    ai_model: str = "gpt-4o"
    ai_max_tokens: int = 4096
    ai_temperature: float = 0.7
    ai_max_retries: int = 3
    ai_timeout: int = 120

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    ollama_max_retries: int = 3
    ollama_timeout: int = 300

    export_temp_dir: str = "./temp/exports"


settings = Settings()
