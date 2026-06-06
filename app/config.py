"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./lexiflow.db"
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    APP_NAME: str = "LexiFlow Legal Suite"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    SECRET_KEY: str = "change-me-to-a-random-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()