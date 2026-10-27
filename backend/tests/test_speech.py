"""Local speech validation and output contracts."""

import io
import wave

import pytest


def test_speech_authentication_before_body(client):
    assert client.post("/v1/audio/speech", content=b"invalid").status_code == 401


def test_speech_csrf(voice_client):
    client, _, _ = voice_client
    assert client.post("/v1/audio/speech").status_code == 403
    assert client.post("/v1/audio/speech", headers={"X-CSRF-Token": "bad"}).status_code == 403


@pytest.mark.parametrize(
    "payload",
    [
        {"text": ""},
        {"text": "   "},
        {"text": "x" * 2001},
        {"text": "Hello", "response_format": "mp3"},
        {"text": "Hello", "voice": "../../secret"},
        {"text": "Hello", "voice": "unknown"},
    ],
)
def test_speech_validation(voice_client, payload):
    client, headers, _ = voice_client
    assert client.post("/v1/audio/speech", json=payload, headers=headers).status_code == 422


def test_speech_returns_wav_without_persistence(voice_client):
    client, headers, runtime = voice_client
    response = client.post("/v1/audio/speech", json={"text": "Hello"}, headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert response.headers["cache-control"] == "no-store"
    with wave.open(io.BytesIO(response.content)) as audio:
        assert audio.getframerate() == 24000
        assert audio.getnframes() > 0
    assert client.get("/v1/transcripts").json()["items"] == []
    assert not list(runtime.settings.audio_storage_dir.iterdir())


def test_tts_unavailable_and_output_limit(voice_client, monkeypatch):
    import numpy as np

    client, headers, runtime = voice_client
    adapter = runtime.tts
    runtime.tts = None
    assert (
        client.post("/v1/audio/speech", json={"text": "Hello"}, headers=headers).status_code == 503
    )
    runtime.tts = adapter
    runtime.settings.tts_max_audio_seconds = 1
    monkeypatch.setattr(adapter, "generate", lambda *_: iter([np.zeros(24001)]))
    assert (
        client.post("/v1/audio/speech", json={"text": "Hello"}, headers=headers).status_code == 422
    )
