"""Structured logging with conservative sensitive-value redaction."""

import json
import logging
import re
import sys
from collections.abc import Mapping
from typing import Any

_SENSITIVE_KEY = re.compile(
    r"(password|passwd|secret|token|authorization|cookie|api[_-]?key|audio|transcript|speech|text|filename|path)",
    re.IGNORECASE,
)
_SENSITIVE_NAMES = (
    r"password(?:_hash)?|passwd|secret|token|authorization|cookie|"
    r"api[_-]?key|audio|transcript|speech|text|filename|path"
)
_SENSITIVE_ASSIGNMENT = re.compile(
    rf"(?i)({_SENSITIVE_NAMES})\s*[:=]\s*.*?"
    rf"(?=\s+(?:{_SENSITIVE_NAMES})\s*[:=]|\Z)"
)


def redact(value: Any) -> Any:
    """Redact sensitive mapping fields before they reach a log formatter."""

    if isinstance(value, Mapping):
        return {
            str(key): "[REDACTED]" if _SENSITIVE_KEY.search(str(key)) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list | tuple):
        return [redact(item) for item in value]
    if isinstance(value, str):
        return _SENSITIVE_ASSIGNMENT.sub(r"\1=[REDACTED]", value)
    return value


class JsonFormatter(logging.Formatter):
    """Emit one JSON object per log record."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": redact(record.getMessage()),
        }
        if record.exc_info:
            payload["exception"] = "[REDACTED]"
        return json.dumps(payload, ensure_ascii=True)


def configure_logging(level: str = "INFO") -> None:
    """Configure a single redacting JSON handler for the application."""

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
    for name in ("faster_whisper", "kokoro", "misaki", "httpx", "httpcore", "sqlalchemy.engine"):
        logger = logging.getLogger(name)
        logger.handlers = [logging.NullHandler()]
        logger.propagate = False
