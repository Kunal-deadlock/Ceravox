"""Small in-process failed-login limiter for a single local admin."""

import time
from dataclasses import dataclass


@dataclass
class _Attempt:
    failures: int = 0
    blocked_until: float = 0.0


class LoginRateLimiter:
    def __init__(self) -> None:
        self._attempts: dict[str, _Attempt] = {}

    def is_blocked(self, key: str) -> bool:
        attempt = self._attempts.get(key)
        return bool(attempt and attempt.blocked_until > time.monotonic())

    def record_failure(self, key: str, threshold: int, window_seconds: int) -> None:
        attempt = self._attempts.setdefault(key, _Attempt())
        attempt.failures += 1
        if attempt.failures >= threshold:
            attempt.blocked_until = time.monotonic() + window_seconds

    def reset(self, key: str) -> None:
        self._attempts.pop(key, None)


login_limiter = LoginRateLimiter()
