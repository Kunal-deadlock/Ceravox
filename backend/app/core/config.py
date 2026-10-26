"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the local Ceravox API."""

    app_name: str = "Ceravox API"
    environment: str = "development"
    log_level: str = "INFO"
    backend_url: str = "http://127.0.0.1:8000"
    dashboard_url: str = "http://127.0.0.1:5173"
    ollama_url: str = "http://127.0.0.1:11434"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CERAVOX_",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return the cached process settings."""

    return Settings()
