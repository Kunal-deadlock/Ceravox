"""Cross-user isolation and export views for persisted transcripts."""

import uuid

import pytest


def test_anonymous_transcripts(client):
    assert client.get("/v1/transcripts").status_code == 401
    assert client.get(f"/v1/transcripts/{uuid.uuid4()}").status_code == 401
    assert client.get(f"/v1/transcripts/{uuid.uuid4()}/export?format=txt").status_code == 401


def test_cross_user_reads_are_hidden(voice_client, db_session):
    from app.db.models import Transcript, User

    client, _, _ = voice_client
    other = User(email="other@example.test", password_hash="synthetic")
    db_session.add(other)
    db_session.flush()
    transcript = Transcript(user_id=other.id, text="Private fixture", duration=1)
    db_session.add(transcript)
    db_session.commit()
    missing = client.get(f"/v1/transcripts/{uuid.uuid4()}")
    denied = client.get(f"/v1/transcripts/{transcript.id}")
    assert denied.status_code == missing.status_code == 404
    assert denied.json() == missing.json()
    assert client.get("/v1/transcripts").json()["items"] == []
    assert client.get("/v1/transcripts?limit=101").status_code == 422


@pytest.fixture
def user_transcript(voice_client, db_session):
    from sqlalchemy import select

    from app.db.models import Transcript, TranscriptSegment, User

    client, _, _ = voice_client
    user = db_session.scalar(select(User).where(User.email == "admin@example.test"))
    assert user is not None

    record = Transcript(
        user_id=user.id,
        storage_id=uuid.uuid4(),
        source_type="upload",
        text="Discussing quarterly roadmap milestones and deliverables.",
        language="en",
        duration=32.5,
    )
    db_session.add(record)
    db_session.flush()

    segment = TranscriptSegment(
        transcript_id=record.id,
        position=0,
        start_ms=0,
        end_ms=5000,
        text="Discussing quarterly roadmap milestones.",
    )
    db_session.add(segment)
    db_session.commit()
    return client, record


def test_export_unauthenticated_rejected(client):
    fake_id = uuid.uuid4()
    for fmt in ["md", "txt", "json"]:
        res = client.get(f"/v1/transcripts/{fake_id}/export?format={fmt}")
        assert res.status_code == 401


def test_export_markdown(user_transcript):
    client, record = user_transcript
    res = client.get(f"/v1/transcripts/{record.id}/export?format=md")
    assert res.status_code == 200
    assert "text/markdown" in res.headers["content-type"]
    assert f'filename="transcript-{record.id}.md"' in res.headers.get("content-disposition", "")
    assert res.headers["cache-control"] == "no-store"

    body = res.text
    assert f"# Transcript: {record.id}" in body
    assert "**Language:** en" in body
    assert "Discussing quarterly roadmap milestones and deliverables." in body
    assert "Discussing quarterly roadmap milestones." in body


def test_export_plaintext(user_transcript):
    client, record = user_transcript
    res = client.get(f"/v1/transcripts/{record.id}/export?format=txt")
    assert res.status_code == 200
    assert "text/plain" in res.headers["content-type"]
    assert f'filename="transcript-{record.id}.txt"' in res.headers.get("content-disposition", "")
    assert res.headers["cache-control"] == "no-store"

    body = res.text
    assert f"Transcript ID: {record.id}" in body
    assert "Discussing quarterly roadmap milestones and deliverables." in body
    assert "[0.00s - 5.00s]" in body
    assert "Discussing quarterly roadmap milestones." in body


def test_export_json(user_transcript):
    client, record = user_transcript
    res = client.get(f"/v1/transcripts/{record.id}/export?format=json")
    assert res.status_code == 200
    assert "application/json" in res.headers["content-type"]
    assert f'filename="transcript-{record.id}.json"' in res.headers.get("content-disposition", "")
    assert res.headers["cache-control"] == "no-store"

    data = res.json()
    assert data["id"] == str(record.id)
    assert data["language"] == "en"
    assert data["duration"] == 32.5
    assert data["text"] == "Discussing quarterly roadmap milestones and deliverables."
    assert len(data["segments"]) == 1
    assert data["segments"][0]["text"] == "Discussing quarterly roadmap milestones."


def test_export_non_owner_returns_404(voice_client, db_session):
    from app.db.models import Transcript, User

    client, _, _ = voice_client
    other = User(email="other2@example.test", password_hash="synthetic")
    db_session.add(other)
    db_session.flush()
    other_transcript = Transcript(user_id=other.id, text="Other secret audio", duration=5)
    db_session.add(other_transcript)
    db_session.commit()

    res = client.get(f"/v1/transcripts/{other_transcript.id}/export?format=txt")
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "not_found"


def test_export_invalid_id_returns_404(voice_client):
    client, _, _ = voice_client
    res = client.get(f"/v1/transcripts/{uuid.uuid4()}/export?format=md")
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "not_found"


def test_export_invalid_format_returns_422(user_transcript):
    client, record = user_transcript
    res = client.get(f"/v1/transcripts/{record.id}/export?format=pdf")
    assert res.status_code == 422
