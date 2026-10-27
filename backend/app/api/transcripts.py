"""Owner-scoped persisted transcript views."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Response

from app.api.audio import Db, Owner
from app.api.voice_schemas import TranscriptList, TranscriptResponse, TranscriptSummary, voice_error
from app.services.transcripts import get_transcript, list_transcripts

router = APIRouter(prefix="/v1/transcripts", tags=["transcripts"])


@router.get("")
def listing(
    owner: Owner,
    db: Db,
    response: Response,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> TranscriptList:
    response.headers["Cache-Control"] = "no-store"
    return TranscriptList(
        items=[
            TranscriptSummary.model_validate(row)
            for row in list_transcripts(db, owner.id, limit, offset)
        ],
        limit=limit,
        offset=offset,
    )


@router.get("/{identifier}")
def detail(identifier: UUID, owner: Owner, db: Db, response: Response) -> TranscriptResponse:
    response.headers["Cache-Control"] = "no-store"
    record = get_transcript(db, owner.id, identifier)
    if record is None:
        raise voice_error(404, "not_found", "Transcript not found")
    return TranscriptResponse.model_validate(record)
