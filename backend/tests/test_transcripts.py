"""Cross-user isolation without adding multi-admin setup behavior."""

import uuid


def test_anonymous_transcripts(client):
    assert client.get("/v1/transcripts").status_code == 401
    assert client.get(f"/v1/transcripts/{uuid.uuid4()}").status_code == 401


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
