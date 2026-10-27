"""Alembic migration contract tests."""

from pathlib import Path

from sqlalchemy import create_engine, inspect, text

from alembic import command
from alembic.config import Config
from app.db.models import SessionRecord, User


def alembic_config(database_url: str) -> Config:
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def test_fresh_database_upgrade_and_current_revision(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'migration.db'}"
    config = alembic_config(database_url)

    command.upgrade(config, "001_initial_auth")

    engine = create_engine(database_url)
    inspector = inspect(engine)
    assert {"users", "sessions", "alembic_version"}.issubset(inspector.get_table_names())
    with engine.connect() as connection:
        revision = connection.execute(text("select version_num from alembic_version")).scalar_one()
    assert revision == "001_initial_auth"
    engine.dispose()


def test_voice_constraints_and_cascade(db_session):
    import uuid

    import pytest
    from sqlalchemy.exc import IntegrityError

    from app.db.models import Transcript, TranscriptSegment

    db_session.add(
        TranscriptSegment(
            transcript_id=uuid.uuid4(), position=0, start_ms=0, end_ms=1, text="Synthetic"
        )
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
    user = User(email="schema@example.test", password_hash="synthetic")
    db_session.add(user)
    db_session.flush()
    transcript = Transcript(user_id=user.id, text="Synthetic", duration=1)
    transcript.segments = [TranscriptSegment(position=0, start_ms=0, end_ms=1000, text="Synthetic")]
    db_session.add(transcript)
    db_session.commit()
    segment_id = transcript.segments[0].id
    db_session.delete(transcript)
    db_session.commit()
    assert db_session.get(TranscriptSegment, segment_id) is None


def test_auth_migration_downgrades_to_base(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'migration.db'}"
    config = alembic_config(database_url)

    command.upgrade(config, "head")
    command.downgrade(config, "base")

    engine = create_engine(database_url)
    assert "users" not in inspect(engine).get_table_names()
    assert "sessions" not in inspect(engine).get_table_names()
    engine.dispose()


def test_auth_models_use_uuid_keys_and_utc_timestamps() -> None:
    assert User.id.type.as_uuid is True
    assert SessionRecord.id.type.as_uuid is True
    assert User.created_at.type.timezone is True
    assert User.created_at.default is not None
    assert SessionRecord.expires_at.type.timezone is True


def test_voice_migration_roundtrip_preserves_auth(tmp_path) -> None:
    import uuid

    url = f"sqlite:///{tmp_path / 'voice.db'}"
    config = alembic_config(url)
    command.upgrade(config, "001_initial_auth")
    engine = create_engine(url)
    identifier = uuid.uuid4().hex
    with engine.begin() as connection:
        connection.execute(
            text("INSERT INTO users VALUES (:id, 'owner@example.test', 'synthetic', 1, :now)"),
            {"id": identifier, "now": "2026-10-27 00:00:00"},
        )
    command.upgrade(config, "head")
    assert {"transcripts", "transcript_segments"} <= set(inspect(engine).get_table_names())
    with engine.connect() as connection:
        assert (
            connection.scalar(text("SELECT version_num FROM alembic_version")) == "002_core_voice"
        )
    command.downgrade(config, "001_initial_auth")
    assert "transcripts" not in inspect(engine).get_table_names()
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT id FROM users")) == identifier
    command.upgrade(config, "head")
    command.downgrade(config, "base")
    assert set(inspect(engine).get_table_names()) == {"alembic_version"}
    engine.dispose()
