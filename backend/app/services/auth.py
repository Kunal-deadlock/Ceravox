"""Authentication service for the local single-admin instance."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.rate_limit import LoginRateLimiter
from app.core.security import (
    generate_token,
    hash_password,
    hash_token,
    validate_password_strength,
    verify_password,
)
from app.db.models import SessionRecord, User


class AuthServiceError(Exception):
    """Expected, user-safe authentication failure."""

    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def normalize_email(email: str) -> str:
    normalized = email.strip().lower()
    if len(normalized) > 320 or normalized.count("@") != 1:
        raise AuthServiceError("invalid_email", "Enter a valid email address", 422)
    local, domain = normalized.split("@")
    if not local or not domain or "." not in domain:
        raise AuthServiceError("invalid_email", "Enter a valid email address", 422)
    return normalized


class AuthService:
    def __init__(self, settings: Settings, limiter: LoginRateLimiter) -> None:
        self.settings = settings
        self.limiter = limiter

    def setup_admin(self, db: Session, email: str, password: str) -> User:
        if db.scalar(select(User.id).where(User.is_admin.is_(True))) is not None:
            raise AuthServiceError("setup_unavailable", "Admin setup is unavailable", 409)
        normalized_email = normalize_email(email)
        if not validate_password_strength(password):
            raise AuthServiceError(
                "weak_password",
                "Password must be at least 12 characters and use three character classes",
                422,
            )
        if db.scalar(select(User.id).where(User.email == normalized_email)) is not None:
            raise AuthServiceError("setup_unavailable", "Admin setup is unavailable", 409)
        user = User(
            email=normalized_email,
            password_hash=hash_password(password),
            is_admin=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def register_user(self, db: Session, email: str, password: str) -> tuple[User, str]:
        normalized_email = normalize_email(email)
        if not validate_password_strength(password):
            raise AuthServiceError(
                "weak_password",
                "Password must be at least 12 characters and use three character classes",
                422,
            )
        if db.scalar(select(User.id).where(User.email == normalized_email)) is not None:
            raise AuthServiceError("email_taken", "An account with this email already exists", 409)
        is_first = db.scalar(select(User.id)) is None
        user = User(
            email=normalized_email,
            password_hash=hash_password(password),
            is_admin=is_first,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        raw_token = generate_token()
        now = datetime.now(UTC)
        db.add(
            SessionRecord(
                user_id=user.id,
                token_hash=hash_token(raw_token),
                expires_at=now + timedelta(seconds=self.settings.session_ttl_seconds),
                created_at=now,
            )
        )
        db.commit()
        return user, raw_token

    def login(self, db: Session, email: str, password: str) -> tuple[User, str]:
        normalized_email = email.strip().lower()
        key = normalized_email or "<empty>"
        if self.limiter.is_blocked(key):
            raise AuthServiceError("invalid_credentials", "Invalid email or password", 401)
        user = db.scalar(select(User).where(User.email == normalized_email))
        if user is None or not verify_password(password, user.password_hash):
            self.limiter.record_failure(
                key,
                self.settings.login_rate_limit_threshold,
                self.settings.login_rate_limit_window_seconds,
            )
            raise AuthServiceError("invalid_credentials", "Invalid email or password", 401)
        self.limiter.reset(key)
        raw_token = generate_token()
        now = datetime.now(UTC)
        db.add(
            SessionRecord(
                user_id=user.id,
                token_hash=hash_token(raw_token),
                expires_at=now + timedelta(seconds=self.settings.session_ttl_seconds),
                created_at=now,
            )
        )
        db.commit()
        return user, raw_token

    def logout(self, db: Session, raw_token: str | None) -> None:
        if raw_token:
            session = db.scalar(
                select(SessionRecord).where(SessionRecord.token_hash == hash_token(raw_token))
            )
            if session is not None:
                db.delete(session)
                db.commit()
