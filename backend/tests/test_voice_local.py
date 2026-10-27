"""Explicit opt-in API verification with real local models and network denial."""

import pytest


def test_real_offline_voice_roundtrip(voice_client, request, monkeypatch):
    if not request.config.getoption("--run-local-voice"):
        pytest.skip("Requires explicitly installed local models; use --run-local-voice")
    import socket

    from app.core.config import Settings

    client, headers, runtime = voice_client
    settings = Settings()
    runtime.settings.asr_model_dir = settings.asr_model_dir
    runtime.settings.tts_model_dir = settings.tts_model_dir
    runtime.settings.tts_voices_dir = settings.tts_voices_dir
    runtime.asr = runtime.tts = None

    def deny(*args, **kwargs):
        raise AssertionError("Network denied")

    monkeypatch.setattr(socket, "getaddrinfo", deny)
    assert runtime.status().faster_whisper.available
    assert runtime.status().kokoro.available
    speech = client.post(
        "/v1/audio/speech",
        headers=headers,
        json={"text": "Hello. This is a local voice test.", "voice": "af_heart"},
    )
    assert speech.status_code == 200, speech.text[:100] if speech.status_code != 200 else ""
    response = client.post(
        "/v1/audio/transcriptions",
        headers=headers,
        files={"file": ("sample.wav", speech.content, "audio/wav")},
    )
    assert response.status_code == 201
    result = response.json()
    assert result["text"] and result["language"] == "en" and result["duration"] > 0
    assert result["segments"]
    assert client.get(f"/v1/transcripts/{result['id']}").json() == result
    assert not list(runtime.settings.audio_storage_dir.iterdir())
