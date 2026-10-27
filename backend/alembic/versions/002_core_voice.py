"""Persist owner-scoped transcripts and ordered segments."""

import sqlalchemy as sa

from alembic import op

revision = "002_core_voice"
down_revision = "001_initial_auth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "transcripts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("storage_id", sa.Uuid(), nullable=False, unique=True),
        sa.Column("source_type", sa.String(16), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("language", sa.String(32)),
        sa.Column("duration", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("duration >= 0", name="ck_transcript_duration"),
        sa.CheckConstraint("source_type = 'upload'", name="ck_transcript_source"),
    )
    op.create_index("ix_transcripts_owner_created", "transcripts", ["user_id", "created_at"])
    op.create_table(
        "transcript_segments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "transcript_id",
            sa.Uuid(),
            sa.ForeignKey("transcripts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("start_ms", sa.Integer(), nullable=False),
        sa.Column("end_ms", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("transcript_id", "position"),
        sa.CheckConstraint(
            "position >= 0 AND start_ms >= 0 AND end_ms >= start_ms", name="ck_segment_times"
        ),
    )


def downgrade() -> None:
    op.drop_table("transcript_segments")
    op.drop_index("ix_transcripts_owner_created", table_name="transcripts")
    op.drop_table("transcripts")
