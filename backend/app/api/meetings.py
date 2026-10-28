"""Owner-scoped summary and transcript Q&A endpoints."""

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from starlette.concurrency import run_in_threadpool

from app.api.audio import Db, Owner
from app.api.voice_schemas import voice_error
from app.core.config import get_settings
from app.core.csrf import require_csrf
from app.core.upload_limits import bounded_stream
from app.db.models import Transcript
from app.services.meeting_intelligence import (
    OllamaMalformedResponse,
    OllamaTimeout,
    OllamaUnavailable,
    generate,
    transcript_prompt,
)
from app.services.transcripts import get_transcript

router = APIRouter(prefix="/v1/transcripts", tags=["meeting-notes"])


class MeetingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str | None = Field(default=None, min_length=1, max_length=2000)


class MeetingResponse(BaseModel):
    transcript_id: UUID
    kind: Literal["summary", "answer"]
    text: str


async def _run(
    record: Transcript, task: str, kind: Literal["summary", "answer"]
) -> MeetingResponse:
    settings = get_settings()
    if len(record.text) > settings.meeting_max_transcript_chars:
        raise voice_error(
            413,
            "transcript_too_large",
            "This transcript exceeds the local meeting-notes limit. Choose a shorter transcript.",
        )
    try:
        result = await run_in_threadpool(generate, transcript_prompt(task, record.text), settings)
    except OllamaTimeout:
        raise voice_error(504, "ollama_timeout", "Local Ollama took too long to respond") from None
    except OllamaUnavailable:
        raise voice_error(
            503,
            "ollama_unavailable",
            f"Local Ollama or model '{settings.ollama_model}' is unavailable",
        ) from None
    except OllamaMalformedResponse:
        raise voice_error(
            502, "ollama_invalid_response", "Local Ollama returned an invalid response"
        ) from None
    return MeetingResponse(transcript_id=record.id, kind=kind, text=result)


async def _owned(identifier: UUID, owner: Owner, db: Db) -> Transcript:
    record = get_transcript(db, owner.id, identifier)
    if record is None:
        raise voice_error(404, "not_found", "Transcript not found")
    return record


async def _question_payload(request: Request) -> MeetingRequest:
    body = bytearray()
    async for chunk in bounded_stream(request, 4096):
        body.extend(chunk)
    try:
        return MeetingRequest.model_validate_json(body)
    except ValidationError:
        raise voice_error(
            422, "invalid_question", "Enter a question under 2000 characters"
        ) from None


@router.post("/{identifier}/summary", response_model=MeetingResponse)
async def summary(identifier: UUID, request: Request, owner: Owner, db: Db) -> MeetingResponse:
    await require_csrf(request)
    record = await _owned(identifier, owner, db)
    return await _run(
        record,
        "Create meeting notes with a short summary, decisions explicitly stated, and action items. "
        "For each action item include an owner or deadline only if stated; "
        "otherwise say unspecified.",
        "summary",
    )


@router.post("/{identifier}/questions", response_model=MeetingResponse)
async def question(identifier: UUID, request: Request, owner: Owner, db: Db) -> MeetingResponse:
    await require_csrf(request)
    payload = await _question_payload(request)
    if not payload.question or not payload.question.strip():
        raise voice_error(422, "invalid_question", "Enter a question")
    record = await _owned(identifier, owner, db)
    return await _run(record, f"Answer this question: {payload.question.strip()}", "answer")
