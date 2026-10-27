"""Shared isolated database and API fixtures for S1 tests."""

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from alembic.config import Config
from app.db.session import get_db
from app.main import app


def pytest_addoption(parser):
    parser.addoption("--run-local-voice", action="store_true", default=False)


@pytest.fixture(autouse=True)
def no_external_network(monkeypatch):
    import socket

    connect = socket.socket.connect

    def guarded(self, address):
        if isinstance(address, tuple) and address[0] not in {"127.0.0.1", "::1"}:
            raise AssertionError("External networking is forbidden in tests")
        return connect(self, address)

    monkeypatch.setattr(socket.socket, "connect", guarded)


@pytest.fixture
def db_session(tmp_path) -> Generator[Session, None, None]:
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")
    engine = create_engine(database_url, future=True)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with factory() as session:
        yield session
    engine.dispose()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def wav_bytes():
    import io
    import wave

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(16000)
        audio.writeframes(b"\x01\x00" * 1600)
    return buffer.getvalue()


@pytest.fixture
def voice_client(client, tmp_path):
    import numpy as np

    from app.adapters.faster_whisper import ASRResult, Segment
    from app.api.dependencies import get_voice_runtime
    from app.core.config import Settings
    from app.services.models import ModelService
    from tests.test_auth import csrf, login, setup_admin

    settings = Settings(
        audio_storage_dir=tmp_path / "audio",
        asr_model_dir=tmp_path / "asr",
        tts_model_dir=tmp_path / "tts",
        tts_voices_dir=tmp_path / "voices",
    )
    runtime = ModelService(settings)

    class FakeASR:
        def transcribe(self, samples):
            return ASRResult("A synthetic test sentence.", "en", [Segment(0, 100, "A sentence.")])

    class FakeTTS:
        def generate(self, text, voice):
            yield np.zeros(2400, dtype=np.float32)

    runtime.asr = FakeASR()
    runtime.tts = FakeTTS()
    app.dependency_overrides[get_voice_runtime] = lambda: runtime
    setup_admin(client)
    assert login(client).status_code == 200
    yield client, {"X-CSRF-Token": csrf(client)}, runtime
