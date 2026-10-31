"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the local Ceravox API."""

    app_name: str = "Ceravox API"
    environment: str = "development"
    log_level: str = "INFO"
    backend_url: str = "http://127.0.0.1:8000"
    dashboard_url: str = "http://127.0.0.1:5173"
    database_url: str = "sqlite:///./ceravox.db"
    ollama_url: str = "http://127.0.0.1:11434"
    ollama_model: str = Field(default="qwen2.5:3b", min_length=1, max_length=128)
    ollama_timeout_seconds: float = Field(default=90.0, gt=0, le=300)
    meeting_max_transcript_chars: int = Field(default=20000, ge=1000, le=100000)
    session_ttl_seconds: int = 8 * 60 * 60
    cookie_secure: bool = False
    login_failure_delay_seconds: float = 0.1
    login_rate_limit_threshold: int = 5
    login_rate_limit_window_seconds: int = 30
    asr_model: str = Field(default="base", pattern=r"^[A-Za-z0-9_-]{1,64}$")
    asr_model_dir: Path = Path("models/faster-whisper-base")
    asr_device: Literal["cpu", "cuda"] = "cpu"
    asr_compute_type: Literal["int8", "float32", "float16"] = "int8"
    asr_cpu_threads: int = Field(default=2, ge=1, le=32)
    tts_model: str = Field(default="Kokoro-82M", pattern=r"^[A-Za-z0-9_-]{1,64}$")
    tts_model_dir: Path = Path("models/kokoro")
    tts_voices_dir: Path = Path("models/kokoro/voices")
    tts_voices: list[str] = Field(default_factory=lambda: ["af_heart"])
    tts_default_voice: str = "af_heart"
    audio_storage_dir: Path = Path("recordings/tmp")
    audio_max_upload_bytes: int = Field(default=26214400, ge=1, le=104857600)
    audio_max_request_bytes: int = Field(default=27262976, ge=1, le=105906176)
    audio_max_duration_seconds: int = Field(default=600, ge=1, le=3600)
    tts_max_text_chars: int = Field(default=2000, ge=1, le=10000)
    tts_max_audio_seconds: int = Field(default=300, ge=1, le=600)

    @model_validator(mode="after")
    def validate_database_url(self) -> Self:
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
        return self

    @model_validator(mode="after")
    def validate_voice_settings(self) -> Self:
        import re

        if self.tts_default_voice not in self.tts_voices or any(
            not re.fullmatch(r"[ab][fm]_[a-z]+", voice) for voice in self.tts_voices
        ):
            raise ValueError("Invalid configured English voices")
        if self.audio_max_request_bytes <= self.audio_max_upload_bytes:
            raise ValueError("Request limit must exceed upload limit")
        if self.asr_device == "cpu" and self.asr_compute_type == "float16":
            raise ValueError("CPU requires int8 or float32")
        return self

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
