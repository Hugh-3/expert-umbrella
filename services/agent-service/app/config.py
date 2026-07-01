from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    db_path: Path = Path("./agent_service.db")
    target_api_url: str = "http://localhost:8000"
    target_project_path: Optional[str] = None
    service_host: str = "0.0.0.0"
    service_port: int = 8001
    evaluation_timeout: int = 300
    api_request_timeout: int = 30
    
    class Config:
        env_file = ".env"
        env_prefix = "AGENT_"

settings = Settings()
