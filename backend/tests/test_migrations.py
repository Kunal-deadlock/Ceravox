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

    command.upgrade(config, "head")

    engine = create_engine(database_url)
    inspector = inspect(engine)
    assert {"users", "sessions", "alembic_version"}.issubset(inspector.get_table_names())
    with engine.connect() as connection:
        revision = connection.execute(text("select version_num from alembic_version")).scalar_one()
    assert revision == "001_initial_auth"
    engine.dispose()


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
