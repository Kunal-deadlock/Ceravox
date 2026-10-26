"""Password and opaque-token security helpers."""

import hashlib
import secrets
import string

from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()
_DUMMY_PASSWORD_HASH = password_hasher.hash("ceravox-invalid-password")


def validate_password_strength(password: str) -> bool:
    """Require a long password with at least three character classes."""

    classes = sum(
        (
            any(character.islower() for character in password),
            any(character.isupper() for character in password),
            any(character.isdigit() for character in password),
            any(character in string.punctuation for character in password),
        )
    )
    return len(password) >= 12 and classes >= 3


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    """Verify against a dummy hash when the user does not exist."""

    try:
        return password_hasher.verify(password, password_hash or _DUMMY_PASSWORD_HASH)
    except (ValueError, TypeError):
        return False


def generate_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return f"sha256${digest}"
