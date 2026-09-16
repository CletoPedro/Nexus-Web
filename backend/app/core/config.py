"""
Centralized configuration. No environment variable is read anywhere else
in the codebase — this is the single source of truth, per the Phase W1
architecture (section 4).
"""
from functools import lru_cache

from pydantic import model_validator
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

    # Auth (W12). SECRET_KEY MUST be overridden via env var in any real
    # deployment — the default here is an obvious, unusable placeholder,
    # never a real secret. See core/logging.py's startup warning.
    secret_key: str = "INSECURE-DEV-ONLY-CHANGE-VIA-SECRET_KEY-ENV-VAR"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    jwt_algorithm: str = "HS256"
    auth_cookie_name: str = "nexus_session"

    # Bootstrap admin (used only by the one-time migration data step that
    # creates the first user and backfills ownership of pre-existing
    # rows). Never has a real default — if unset, no admin is created and
    # the migration leaves existing rows unowned, documented in
    # PHASE_W12_REPORT.md.
    admin_email: str | None = None
    admin_initial_password: str | None = None

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        """Fail closed if production auth is not configured safely."""
        if self.environment != "development" and self.secret_key.startswith(
            "INSECURE-DEV-ONLY"
        ):
            raise ValueError(
                "SECRET_KEY must be explicitly configured in non-development environments."
            )
        return self

    @property
    def cookie_secure(self) -> bool:
        # Secure cookies require HTTPS. In local development (http://
        # localhost) a Secure cookie would silently not be sent at all,
        # breaking login — so this is only true outside development.
        return self.environment != "development"

    @property
    def cookie_samesite(self) -> str:
        # "none" is required for the deployed setup (frontend on Vercel,
        # backend on Railway — different origins) and requires Secure=True,
        # which is only set outside development. "lax" is fine for local
        # same-origin-ish dev over plain http.
        return "none" if self.environment != "development" else "lax"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance, injected via FastAPI's Depends()."""
    return Settings()
