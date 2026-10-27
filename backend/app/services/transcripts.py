"""Owner-scoped transcript queries; never query details by ID alone."""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Transcript


def list_transcripts(db: Session, owner: UUID, limit: int, offset: int) -> Sequence[Transcript]:
    return db.scalars(
        select(Transcript)
        .where(Transcript.user_id == owner)
        .order_by(Transcript.created_at.desc(), Transcript.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()


def get_transcript(db: Session, owner: UUID, identifier: UUID) -> Transcript | None:
    return db.scalar(
        select(Transcript)
        .where(Transcript.user_id == owner, Transcript.id == identifier)
        .options(selectinload(Transcript.segments))
    )
