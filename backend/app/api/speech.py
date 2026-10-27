"""Authenticated, CSRF-protected local speech endpoint."""

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Request, Response
from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool

from app.api.dependencies import get_current_user, get_voice_runtime
from app.api.voice_schemas import SpeechRequest, voice_error
from app.core.csrf import require_csrf
from app.core.upload_limits import bounded_stream
from app.db.models import User
from app.services.models import ModelService
from app.services.speech import synthesize

router = APIRouter(prefix="/v1/audio", tags=["speech"])
Owner = Annotated[User, Depends(get_current_user)]
Runtime = Annotated[ModelService, Depends(get_voice_runtime)]


@router.post("/speech")
async def speech(request: Request, owner: Owner, runtime: Runtime) -> Response:
    await require_csrf(request)
    body = bytearray()
    async for chunk in bounded_stream(request, runtime.settings.audio_max_request_bytes):
        body.extend(chunk)
    try:
        payload = SpeechRequest.model_validate_json(body)
    except ValidationError:
        raise voice_error(
            422, "invalid_speech_request", "Enter valid text, voice and WAV format"
        ) from None
    result = await run_in_threadpool(synthesize, payload, runtime)
    return Response(
        result,
        media_type="audio/wav",
        headers={
            "Cache-Control": "no-store",
            "Content-Disposition": f'attachment; filename="speech-{uuid4()}.wav"',
        },
    )
