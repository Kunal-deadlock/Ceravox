"""Tests for the local live voice assistant chat endpoint."""

from app.services import meeting_intelligence as ollama
from tests.test_auth import csrf


def test_assistant_chat_requires_auth(client):
    response = client.post("/v1/assistant/chat", json={"message": "Hello"})
    assert response.status_code == 401


def test_assistant_chat_requires_csrf(voice_client):
    client, _, _ = voice_client
    response = client.post("/v1/assistant/chat", json={"message": "Hello"})
    assert response.status_code == 403


def test_assistant_chat_success(voice_client, monkeypatch):
    client, _, _ = voice_client
    monkeypatch.setattr(
        "app.api.assistant.generate",
        lambda prompt, settings: "Hello! I am Ceravox, your offline voice workstation.",
    )
    headers = {"X-CSRF-Token": csrf(client)}
    response = client.post("/v1/assistant/chat", json={"message": "Who are you?"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["reply"] == "Hello! I am Ceravox, your offline voice workstation."


def test_assistant_chat_rejects_empty_or_oversized_message(voice_client):
    client, _, _ = voice_client
    headers = {"X-CSRF-Token": csrf(client)}
    # Empty message
    response = client.post("/v1/assistant/chat", json={"message": ""}, headers=headers)
    assert response.status_code == 422

    # Oversized message (>1000 chars)
    response = client.post("/v1/assistant/chat", json={"message": "a" * 1001}, headers=headers)
    assert response.status_code == 422


def test_assistant_chat_handles_ollama_unavailable(voice_client, monkeypatch):
    client, _, _ = voice_client
    monkeypatch.setattr(
        "app.api.assistant.generate",
        lambda *_: (_ for _ in ()).throw(ollama.OllamaUnavailable()),
    )
    headers = {"X-CSRF-Token": csrf(client)}
    response = client.post("/v1/assistant/chat", json={"message": "Hello"}, headers=headers)
    assert response.status_code == 503
    assert "unavailable" in response.json()["error"]["message"]


def test_assistant_chat_handles_ollama_timeout(voice_client, monkeypatch):
    client, _, _ = voice_client
    monkeypatch.setattr(
        "app.api.assistant.generate",
        lambda *_: (_ for _ in ()).throw(ollama.OllamaTimeout()),
    )
    headers = {"X-CSRF-Token": csrf(client)}
    response = client.post("/v1/assistant/chat", json={"message": "Hello"}, headers=headers)
    assert response.status_code == 504
    assert "Local Ollama took too long" in response.json()["error"]["message"]
