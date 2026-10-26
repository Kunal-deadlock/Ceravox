"""Reusable authentication dependencies."""

from datetime import UTC, datetime

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.security import hash_token
from app.db.models import SessionRecord, User
from app.db.session import get_db

SESSION_COOKIE = "ceravox_session"
UNAUTHORIZED = {"code": "unauthorized", "message": "Authentication required"}


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    raw_token = request.cookies.get(SESSION_COOKIE)
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED)
    session = db.scalar(
        select(SessionRecord).where(
            SessionRecord.token_hash == hash_token(raw_token),
            SessionRecord.expires_at > datetime.now(UTC),
        )
    )
    if session is None:
        db.execute(delete(SessionRecord).where(SessionRecord.token_hash == hash_token(raw_token)))
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED)
    user = db.get(User, session.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED)
    return user
