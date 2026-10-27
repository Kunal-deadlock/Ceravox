"""Safe voice contracts and errors; no filesystem paths or private diagnostics."""

from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, field_validator


def voice_error(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(status, detail={"code": code, "message": message})


class SegmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    start_ms: int
    end_ms: int
    text: str


class TranscriptSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    storage_id: UUID
    source_type: str
    language: str | None
    duration: float
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def utc_timestamp(cls, value: datetime) -> datetime:
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


class TranscriptResponse(TranscriptSummary):
    text: str
    segments: list[SegmentResponse]


class TranscriptList(BaseModel):
    items: list[TranscriptSummary]
    limit: int
    offset: int


class SpeechRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str
    voice: str | None = None
    response_format: Literal["wav"] = "wav"


class ModelStatus(BaseModel):
    model: str | None
    configured: bool
    available: bool
    status: Literal[
        "available", "not_configured", "missing_dependency", "missing_assets", "load_failed"
    ]
    voices: list[str] = []
    default_voice: str | None = None


class VoiceLimits(BaseModel):
    upload_bytes: int
    text_chars: int
    duration_seconds: int
    response_formats: list[str] = ["wav"]


class ModelsResponse(BaseModel):
    faster_whisper: ModelStatus
    kokoro: ModelStatus
    ollama: ModelStatus
    limits: VoiceLimits
