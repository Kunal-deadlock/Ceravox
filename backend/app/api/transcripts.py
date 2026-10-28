"""Owner-scoped persisted transcript views and exports."""

import json
from typing import Annotated, Literal
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


@router.get("/{identifier}/export")
def export(
    identifier: UUID,
    owner: Owner,
    db: Db,
    format: Literal["md", "txt", "json"] = Query(default="txt"),
) -> Response:
    """Export an owned transcript as Markdown, Plain text, or JSON attachment."""
    record = get_transcript(db, owner.id, identifier)
    if record is None:
        raise voice_error(404, "not_found", "Transcript not found")

    filename = f"transcript-{record.id}.{format}"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Cache-Control": "no-store",
    }

    if format == "json":
        data = TranscriptResponse.model_validate(record).model_dump(mode="json")
        content = json.dumps(data, indent=2)
        return Response(content=content, media_type="application/json", headers=headers)

    if format == "txt":
        lines = [
            f"Transcript ID: {record.id}",
            f"Created At: {record.created_at.isoformat()}",
            f"Language: {record.language or 'unknown'}",
            f"Duration: {record.duration:.2f}s",
            "",
            "Full Text:",
            record.text or "(No speech detected)",
            "",
            "Segments:",
        ]
        for seg in record.segments:
            start = seg.start_ms / 1000.0
            end = seg.end_ms / 1000.0
            lines.append(f"[{start:.2f}s - {end:.2f}s] {seg.text}")
        content = "\n".join(lines) + "\n"
        return Response(
            content=content,
            media_type="text/plain; charset=utf-8",
            headers=headers,
        )

    # format == "md"
    lines = [
        f"# Transcript: {record.id}",
        "",
        f"- **Date:** {record.created_at.isoformat()}",
        f"- **Language:** {record.language or 'unknown'}",
        f"- **Duration:** {record.duration:.2f}s",
        "",
        "## Full Text",
        "",
        record.text or "*(No speech detected)*",
        "",
        "## Segments",
        "",
    ]
    for seg in record.segments:
        start = seg.start_ms / 1000.0
        end = seg.end_ms / 1000.0
        lines.append(f"- **[{start:.2f}s - {end:.2f}s]**: {seg.text}")
    content = "\n".join(lines) + "\n"
    return Response(
        content=content,
        media_type="text/markdown; charset=utf-8",
        headers=headers,
    )
