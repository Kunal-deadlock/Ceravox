"""Authentication persistence models."""

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    """Return an aware UTC timestamp for server-created records."""

    from datetime import UTC

    return datetime.now(UTC)


class User(Base):
    """Single-admin-capable local user record."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    is_admin: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    sessions: Mapped[list["SessionRecord"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class SessionRecord(Base):
    """Server-side session with only a hash of the browser token."""

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    user: Mapped[User] = relationship(back_populates="sessions")


class Transcript(Base):
    """A persisted transcript; storage_id is provenance, not a retained file."""

    __tablename__ = "transcripts"
    __table_args__ = (
        CheckConstraint("duration >= 0", name="ck_transcript_duration"),
        CheckConstraint("source_type = 'upload'", name="ck_transcript_source"),
        Index("ix_transcripts_owner_created", "user_id", "created_at"),
    )
    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    storage_id: Mapped[uuid.UUID] = mapped_column(Uuid(), unique=True, default=uuid.uuid4)
    source_type: Mapped[str] = mapped_column(String(16), default="upload")
    text: Mapped[str] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(String(32))
    duration: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    segments: Mapped[list["TranscriptSegment"]] = relationship(
        cascade="all, delete-orphan", order_by="TranscriptSegment.position"
    )


class TranscriptSegment(Base):
    """Ordered millisecond timestamps and text within a transcript."""

    __tablename__ = "transcript_segments"
    __table_args__ = (
        UniqueConstraint("transcript_id", "position"),
        CheckConstraint(
            "position >= 0 AND start_ms >= 0 AND end_ms >= start_ms", name="ck_segment_times"
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    transcript_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transcripts.id", ondelete="CASCADE")
    )
    position: Mapped[int]
    start_ms: Mapped[int]
    end_ms: Mapped[int]
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
