"""Database engine and request-scoped session dependency."""

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def _engine_kwargs(database_url: str) -> dict[str, object]:
    if database_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {}


settings = get_settings()


@event.listens_for(Engine, "connect")
def enable_foreign_keys(connection: Any, _: Any) -> None:
    if connection.__class__.__module__.startswith("sqlite3"):
        connection.execute("PRAGMA foreign_keys=ON")


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
    hide_parameters=True,
    **_engine_kwargs(settings.database_url),
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """Yield one database session per request."""

    with SessionLocal() as session:
        yield session
