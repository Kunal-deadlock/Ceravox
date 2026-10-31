"""Thin authentication and protected-shell routes."""

import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import SESSION_COOKIE, get_current_user
from app.core.config import get_settings
from app.core.csrf import CSRF_COOKIE, new_csrf_token, require_csrf, set_csrf_cookie
from app.core.rate_limit import login_limiter
from app.db.models import User
from app.db.session import get_db
from app.services.auth import AuthService, AuthServiceError

router = APIRouter(prefix="/v1", tags=["auth"])
Db = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


class Credentials(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    is_admin: bool


def safe_user(user: User) -> UserResponse:
    return UserResponse(id=str(user.id), email=user.email, is_admin=user.is_admin)


def service() -> AuthService:
    return AuthService(get_settings(), login_limiter)


def auth_error(error: AuthServiceError) -> HTTPException:
    return HTTPException(
        status_code=error.status_code,
        detail={"code": error.code, "message": error.message},
    )


@router.get("/auth/status")
def auth_status(db: Db) -> dict[str, bool]:
    return {"setup_required": db.scalar(select(User.id).where(User.is_admin.is_(True))) is None}


@router.get("/auth/csrf")
def csrf_token(response: Response) -> dict[str, str]:
    token = new_csrf_token()
    set_csrf_cookie(response, token)
    return {"csrf_token": token}


@router.post(
    "/auth/setup",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_csrf)],
)
def setup(payload: Credentials, db: Db) -> UserResponse:
    try:
        return safe_user(service().setup_admin(db, payload.email, payload.password))
    except AuthServiceError as error:
        raise auth_error(error) from error
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={"code": "setup_unavailable", "message": "Admin setup is unavailable"},
        ) from error


@router.post(
    "/auth/register",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_csrf)],
)
async def register(payload: Credentials, db: Db, response: Response) -> UserResponse:
    try:
        user, raw_token = service().register_user(db, payload.email, payload.password)
    except AuthServiceError as error:
        raise auth_error(error) from error
    settings = get_settings()
    response.set_cookie(
        SESSION_COOKIE,
        raw_token,
        max_age=settings.session_ttl_seconds,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
    return safe_user(user)


@router.post("/auth/login", dependencies=[Depends(require_csrf)])
async def login(payload: Credentials, db: Db, response: Response) -> UserResponse:
    try:
        user, raw_token = service().login(db, payload.email, payload.password)
    except AuthServiceError as error:
        if error.code == "invalid_credentials":
            await asyncio.sleep(get_settings().login_failure_delay_seconds)
        raise auth_error(error) from error
    settings = get_settings()
    response.set_cookie(
        SESSION_COOKIE,
        raw_token,
        max_age=settings.session_ttl_seconds,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
    return safe_user(user)


@router.post(
    "/auth/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_csrf)],
)
def logout(request: Request, response: Response, db: Db, _: CurrentUser) -> None:
    service().logout(db, request.cookies.get(SESSION_COOKIE))
    response.delete_cookie(SESSION_COOKIE, path="/")
    response.delete_cookie(CSRF_COOKIE, path="/")


@router.get("/auth/me")
def me(user: CurrentUser) -> UserResponse:
    return safe_user(user)


@router.get("/app/status")
def app_status(user: CurrentUser) -> dict[str, object]:
    return {"status": "authenticated", "is_admin": user.is_admin}
