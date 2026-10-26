"""Sensitive-value redaction tests."""

from app.core.logging import redact


def test_redact_removes_sensitive_mapping_values() -> None:
    value = redact({"token": "session-value", "message": "safe"})

    assert value == {"token": "[REDACTED]", "message": "safe"}


def test_redact_removes_sensitive_assignments_in_messages() -> None:
    value = redact("token=session-value transcript=private words")

    assert value == "token=[REDACTED] transcript=[REDACTED]"
