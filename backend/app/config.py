from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./insureai.db"
    jwt_secret: str = "change-me-in-production"
    access_token_minutes: int = 120
    auto_approval_threshold: float = 35.0
    investigation_threshold: float = 65.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
