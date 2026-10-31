"""System status endpoint: safe readiness reporting for all local components."""

import re

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAFE_STATUSES = {"ready", "unavailable", "degraded"}
COMPONENT_KEYS = {"db", "asr", "tts", "ollama"}
SENSITIVE_PATTERNS = [
    # filesystem paths (Windows and Unix)
    re.compile(r"[A-Za-z]:\\"),
    re.compile(r"/home/"),
    re.compile(r"/root/"),
    re.compile(r"/tmp/"),
    re.compile(r"\\models\\"),
    re.compile(r"/models/"),
    # common secret/token indicators
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    # Python tracebacks
    re.compile(r"Traceback \(most recent call last\)"),
    re.compile(r"File \".*\", line \d+"),
]


def _no_sensitive(text: str) -> None:
    for pattern in SENSITIVE_PATTERNS:
        assert not pattern.search(text), f"Sensitive pattern found: {pattern.pattern!r}"


# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------


def test_system_status_requires_auth(client: TestClient) -> None:
    """Unauthenticated request must be rejected with 401."""
    response = client.get("/api/system/status")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Shape and safety
# ---------------------------------------------------------------------------


def test_system_status_shape(voice_client) -> None:
    """Authenticated GET returns 200 with the expected response shape."""
    client, _, _ = voice_client
    response = client.get("/api/system/status")
    assert response.status_code == 200

    body = response.json()
    # Top-level keys
    assert "overall" in body
    assert "components" in body

    # Overall status is a safe value
    assert body["overall"] in SAFE_STATUSES

    # All four expected components are present
    components = body["components"]
    assert COMPONENT_KEYS == set(components.keys())

    # Each component has the required fields with safe values
    for key, comp in components.items():
        assert "status" in comp, f"Component {key!r} missing 'status'"
        assert comp["status"] in SAFE_STATUSES, (
            f"Component {key!r} has unexpected status {comp['status']!r}"
        )
        assert "reason" in comp, f"Component {key!r} missing 'reason'"
        # Reason must be a string (possibly empty when status is "ready")
        assert isinstance(comp["reason"], str), f"Component {key!r} reason must be str"


def test_system_status_no_sensitive_data(voice_client) -> None:
    """Response must not contain filesystem paths, secrets, or tracebacks."""
    client, _, _ = voice_client
    response = client.get("/api/system/status")
    assert response.status_code == 200
    _no_sensitive(response.text)


def test_system_status_cache_control(voice_client) -> None:
    """Status endpoint carries no-store to prevent caching of private readiness info."""
    client, _, _ = voice_client
    response = client.get("/api/system/status")
    assert response.status_code == 200
    assert "no-store" in response.headers.get("cache-control", "")


# ---------------------------------------------------------------------------
# Overall readiness logic
# ---------------------------------------------------------------------------


def test_overall_ready_only_when_all_components_ready(voice_client, monkeypatch) -> None:
    """Overall is 'ready' only if every required component reports 'ready'."""
    client, _, runtime = voice_client

    # When Ollama is unavailable overall should NOT be 'ready'
    import urllib.error

    def fake_urlopen(req, **kwargs):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr("app.api.system.urlopen", fake_urlopen)

    response = client.get("/api/system/status")
    assert response.status_code == 200
    body = response.json()
    assert body["components"]["ollama"]["status"] == "unavailable"
    assert body["overall"] != "ready"


# ---------------------------------------------------------------------------
# DB component
# ---------------------------------------------------------------------------


def test_db_component_ready_when_database_accessible(voice_client) -> None:
    """DB component reports 'ready' when the database is reachable."""
    client, _, _ = voice_client
    response = client.get("/api/system/status")
    assert response.status_code == 200
    db_status = response.json()["components"]["db"]
    assert db_status["status"] == "ready"
    assert db_status["reason"] == ""


def test_db_component_degraded_when_query_fails(voice_client, monkeypatch) -> None:
    """DB component reports 'degraded' when a test query raises an exception."""
    client, _, _ = voice_client

    import app.api.system as system_module
    from app.api.system import ComponentInfo

    def broken_check_db(db: object) -> ComponentInfo:
        return ComponentInfo(status="degraded", reason="Database query failed")

    monkeypatch.setattr(system_module, "_check_db", broken_check_db)

    response = client.get("/api/system/status")
    assert response.status_code == 200
    body = response.json()
    db_comp = body["components"]["db"]
    assert db_comp["status"] in {"degraded", "unavailable"}
    assert db_comp["reason"]
    _no_sensitive(response.text)


# ---------------------------------------------------------------------------
# Ollama component
# ---------------------------------------------------------------------------


def test_ollama_unavailable_when_not_reachable(voice_client, monkeypatch) -> None:
    """Ollama component reports 'unavailable' when the server is not reachable."""
    import urllib.error

    client, _, _ = voice_client

    def fake_urlopen(req, **kwargs):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr("app.api.system.urlopen", fake_urlopen)

    response = client.get("/api/system/status")
    assert response.status_code == 200
    ollama = response.json()["components"]["ollama"]
    assert ollama["status"] == "unavailable"
    assert isinstance(ollama["reason"], str) and ollama["reason"]
    _no_sensitive(response.text)


def test_ollama_unavailable_monkeypatched(voice_client, monkeypatch) -> None:
    """Ollama unavailability is reflected in components and overall."""
    import urllib.error

    client, _, _ = voice_client

    def fake_urlopen(req, **kwargs):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr("app.api.system.urlopen", fake_urlopen)

    response = client.get("/api/system/status")
    assert response.status_code == 200
    body = response.json()
    assert body["components"]["ollama"]["status"] == "unavailable"
    assert body["overall"] != "ready"
    _no_sensitive(response.text)


# ---------------------------------------------------------------------------
# ASR / TTS components
# ---------------------------------------------------------------------------


def test_asr_component_present_with_safe_status(voice_client) -> None:
    """ASR component appears with a safe status string."""
    client, _, _ = voice_client
    response = client.get("/api/system/status")
    asr = response.json()["components"]["asr"]
    assert asr["status"] in SAFE_STATUSES


def test_tts_component_present_with_safe_status(voice_client) -> None:
    """TTS component appears with a safe status string."""
    client, _, _ = voice_client
    response = client.get("/api/system/status")
    tts = response.json()["components"]["tts"]
    assert tts["status"] in SAFE_STATUSES


def test_system_status_production_truthful_messages(voice_client, monkeypatch) -> None:
    """In production mode, unavailable services must explain local runtime requirement."""
    client, _, _ = voice_client
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "environment", "production")

    response = client.get("/api/system/status")
    assert response.status_code == 200
    body = response.json()

    # If ollama is unavailable, reason must cite running locally, not starting a local daemon
    ollama_info = body["components"]["ollama"]
    if ollama_info["status"] == "unavailable":
        assert "run Ceravox locally" in ollama_info["reason"]
        assert "Start Ollama and pull" not in ollama_info["reason"]
