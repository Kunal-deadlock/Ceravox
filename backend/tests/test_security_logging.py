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
        ("raw-token", "raw-password-hash"),
        None,
    )

    output = JsonFormatter().format(record)

    assert "raw-token" not in output
    assert "raw-password-hash" not in output
    assert redact({"cookie": "raw-cookie", "password_hash": "raw-hash"}) == {
        "cookie": "[REDACTED]",
        "password_hash": "[REDACTED]",
    }
