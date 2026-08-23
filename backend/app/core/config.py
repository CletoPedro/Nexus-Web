"""
Centralized configuration. No environment variable is read anywhere else
in the codebase — this is the single source of truth, per the Phase W1
architecture (section 4).
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "NEXUS"
    environment: str = "development"  # development | production
    debug: bool = True

    # API
    api_v1_prefix: str = "/api/v1"

    # CORS — explicit allow-list, never "*" in production (W1, section 9)
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3311",
    ]

    # Database (used starting Phase W4.5)
    database_url: str = (
        "postgresql+asyncpg://nexus:nexus@localhost:5432/nexus"
    )

    # Logging
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance, injected via FastAPI's Depends()."""
    return Settings()
