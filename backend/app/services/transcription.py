"""Atomic transcription with immediate cleanup on every exit path."""

from typing import BinaryIO
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.voice_schemas import TranscriptResponse, voice_error
from app.db.models import Transcript, TranscriptSegment
from app.services.audio_storage import normalize, temporary_audio
from app.services.models import ModelService


def transcribe(
    db: Session, owner: UUID, file: BinaryIO, mime: str | None, runtime: ModelService
) -> TranscriptResponse:
    try:
        with (
            runtime.slot(),
            temporary_audio(runtime.settings.audio_storage_dir) as (identifier, path),
        ):
            samples = normalize(file, mime, path, runtime.settings)
            result = runtime.load_asr().transcribe(samples)
            record = Transcript(
                user_id=owner,
                storage_id=identifier,
                text=result.text,
                language=result.language,
                duration=len(samples) / 16000,
            )
            record.segments = [
                TranscriptSegment(position=index, start_ms=s.start_ms, end_ms=s.end_ms, text=s.text)
                for index, s in enumerate(result.segments)
            ]
            db.add(record)
            db.flush()
            response = TranscriptResponse.model_validate(record)
            db.commit()
            return response
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise voice_error(500, "transcription_failed", "Local transcription failed") from None
