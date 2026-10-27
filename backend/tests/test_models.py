"""Model status exposes capabilities, never local paths."""


def test_models_requires_auth(client):
    assert client.get("/v1/models").status_code == 401


def test_models_safe_missing_assets(voice_client):
    client, _, runtime = voice_client
    response = client.get("/v1/models")
    assert response.status_code == 200
    result = response.json()
    assert result["faster_whisper"]["model"] == "base"
    assert result["kokoro"]["model"] == "Kokoro-82M"
    assert result["ollama"]["status"] == "not_configured"
    assert str(runtime.settings.asr_model_dir) not in response.text
    assert str(runtime.settings.tts_model_dir) not in response.text
    assert response.headers["cache-control"] == "no-store"
