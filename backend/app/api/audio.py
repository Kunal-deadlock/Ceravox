"""Authenticated, CSRF-protected local voice endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.api.dependencies import get_current_user, get_voice_runtime
from app.api.voice_schemas import TranscriptResponse
from app.core.csrf import require_csrf
from app.core.upload_limits import audio_upload
from app.db.models import User
from app.db.session import get_db
from app.services.models import ModelService
from app.services.transcription import transcribe

router = APIRouter(prefix="/v1/audio", tags=["audio"])
Owner = Annotated[User, Depends(get_current_user)]
Runtime = Annotated[ModelService, Depends(get_voice_runtime)]
Db = Annotated[Session, Depends(get_db)]


@router.post("/transcriptions", status_code=201)
async def transcription(
    request: Request, owner: Owner, db: Db, runtime: Runtime, response: Response
) -> TranscriptResponse:
    await require_csrf(request)
    response.headers["Cache-Control"] = "no-store"
    async with audio_upload(request, runtime.settings) as uploaded:
        return await run_in_threadpool(
            transcribe, db, owner.id, uploaded.file, uploaded.content_type, runtime
        )
