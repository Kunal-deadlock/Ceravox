"""Logging must not expose authentication material."""

import logging

from app.core.logging import JsonFormatter, redact


def test_authentication_values_are_redacted_from_structured_logs() -> None:
    record = logging.LogRecord(
        "test",
        logging.INFO,
        __file__,
        1,
        "token=%s password_hash=%s",
        ("raw-token", "raw-password-hash"),  # pragma: allowlist secret
        None,
    )

    output = JsonFormatter().format(record)

    assert "raw-token" not in output
    assert "raw-password-hash" not in output
    values = {
        "cookie": "raw-cookie",
        "password_hash": "raw-hash",  # pragma: allowlist secret
    }
    assert redact(values) == {
        "cookie": "[REDACTED]",
        "password_hash": "[REDACTED]",
    }


def test_exception_details_are_not_formatted():
    import sys

    try:
        raise RuntimeError("private model path and transcript fixture")
    except RuntimeError:
        record = logging.LogRecord(
            "test", logging.ERROR, __file__, 1, "Processing failed", (), sys.exc_info()
        )
    assert "private model" not in JsonFormatter().format(record)


def test_voice_content_not_logged(voice_client, wav_bytes, monkeypatch):
    import io

    client, headers, runtime = voice_client
    buffer = io.StringIO()
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(JsonFormatter())
    logging.getLogger().addHandler(handler)
    try:
        response = client.post(
            "/v1/audio/transcriptions",
            headers=headers,
            files={"file": ("private-filename.wav", wav_bytes, "audio/wav")},
        )
        assert response.status_code == 201

        def fail(_):
            raise RuntimeError("private-exception-transcript")

        monkeypatch.setattr(runtime.asr, "transcribe", fail)
        response = client.post(
            "/v1/audio/transcriptions",
            headers=headers,
            files={"file": ("private-filename.wav", wav_bytes, "audio/wav")},
        )
        assert response.status_code == 500
    finally:
        logging.getLogger().removeHandler(handler)
    output = buffer.getvalue()
    for value in ("private-filename", "A synthetic test sentence.", "private-exception-transcript"):
        assert value not in output
