"""Voice API contracts; inference is injected, decoding and persistence are real."""

import uuid

import pytest


@pytest.mark.parametrize("route", ["transcriptions"])
def test_voice_requires_auth_before_body_validation(client, route):
    assert client.post(f"/v1/audio/{route}", content=b"invalid").status_code == 401


@pytest.mark.parametrize("route", ["transcriptions"])
def test_voice_requires_csrf(voice_client, route):
    client, _, _ = voice_client
    assert client.post(f"/v1/audio/{route}").status_code == 403
    assert client.post(f"/v1/audio/{route}", headers={"X-CSRF-Token": "bad"}).status_code == 403


def test_transcription_persists_and_deletes_audio(voice_client, wav_bytes, db_session):
    from app.db.models import Transcript

    client, headers, runtime = voice_client
    response = client.post(
        "/v1/audio/transcriptions",
        headers=headers,
        files={"file": ("../../private.wav", wav_bytes, "audio/wav")},
    )
    assert response.status_code == 201, response.text
    result = response.json()
    uuid.UUID(result["storage_id"])
    assert result["text"] == "A synthetic test sentence."
    assert result["language"] == "en"
    assert result["duration"] == pytest.approx(0.1)
    assert result["segments"][0]["start_ms"] == 0
    assert result["segments"][0]["end_ms"] == 100
    assert result["created_at"].endswith("Z")
    stored = db_session.get(Transcript, uuid.UUID(result["id"]))
    assert str(stored.user_id) == client.get("/v1/auth/me").json()["id"]
    assert not list(runtime.settings.audio_storage_dir.iterdir())
    assert client.get(f"/v1/transcripts/{result['id']}").json() == result
    assert client.get("/v1/transcripts").json()["items"][0]["id"] == result["id"]


@pytest.mark.parametrize(
    "data,mime,expected",
    [
        (b"not audio", "audio/wav", 415),
        (b"#EXTM3U\nhttps://example.test/private", "audio/ogg", 415),
        (b"", "audio/wav", 422),
        (b"RIFF\x00\x00\x00\x00WAVE", "audio/wav", 422),
    ],
)
def test_invalid_audio(voice_client, data, mime, expected):
    client, headers, runtime = voice_client
    response = client.post(
        "/v1/audio/transcriptions", headers=headers, files={"file": ("valid.wav", data, mime)}
    )
    assert response.status_code == expected
    assert not list(runtime.settings.audio_storage_dir.iterdir())


def test_mime_mismatch_and_size(voice_client, wav_bytes):
    client, headers, runtime = voice_client
    response = client.post(
        "/v1/audio/transcriptions",
        headers=headers,
        files={"file": ("fake.mp3", wav_bytes, "audio/mpeg")},
    )
    assert response.status_code == 415
    runtime.settings.audio_max_upload_bytes = 20
    response = client.post(
        "/v1/audio/transcriptions",
        headers=headers,
        files={"file": ("test.wav", wav_bytes, "audio/wav")},
    )
    assert response.status_code == 413
    assert not list(runtime.settings.audio_storage_dir.iterdir())


def test_model_failure_leaves_no_transcript_or_audio(voice_client, wav_bytes, monkeypatch):
    client, headers, runtime = voice_client

    def fail(_):
        raise RuntimeError("private input must not escape")

    monkeypatch.setattr(runtime.asr, "transcribe", fail)
    response = client.post(
        "/v1/audio/transcriptions",
        headers=headers,
        files={"file": ("test.wav", wav_bytes, "audio/wav")},
    )
    assert response.status_code == 500
    assert "private input" not in response.text
    assert client.get("/v1/transcripts").json()["items"] == []
    assert not list(runtime.settings.audio_storage_dir.iterdir())


def test_request_stream_limit_and_multiple_files(voice_client, wav_bytes):
    client, headers, runtime = voice_client
    runtime.settings.audio_max_request_bytes = 100
    response = client.post(
        "/v1/audio/transcriptions",
        headers=headers,
        files={"file": ("a.wav", wav_bytes, "audio/wav")},
    )
    assert response.status_code == 413
    runtime.settings.audio_max_request_bytes = 100000
    response = client.post(
        "/v1/audio/transcriptions",
        headers=headers,
        files=[
            ("file", ("a.wav", wav_bytes, "audio/wav")),
            ("file", ("b.wav", wav_bytes, "audio/wav")),
        ],
    )
    assert response.status_code == 422


def test_missing_model_and_commit_failure_cleanup(voice_client, wav_bytes, db_session, monkeypatch):
    client, headers, runtime = voice_client
    adapter = runtime.asr
    runtime.asr = None
    response = client.post(
        "/v1/audio/transcriptions",
        headers=headers,
        files={"file": ("a.wav", wav_bytes, "audio/wav")},
    )
    assert response.status_code == 503
    runtime.asr = adapter

    def fail():
        raise RuntimeError("private SQL parameters")

    with monkeypatch.context() as patch:
        patch.setattr(db_session, "commit", fail)
        response = client.post(
            "/v1/audio/transcriptions",
            headers=headers,
            files={"file": ("a.wav", wav_bytes, "audio/wav")},
        )
    assert response.status_code == 500
    assert "private" not in response.text
    assert client.get("/v1/transcripts").json()["items"] == []
    assert not list(runtime.settings.audio_storage_dir.iterdir())
