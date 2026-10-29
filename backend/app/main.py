"""FastAPI application entry point."""

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.assistant import router as assistant_router
from app.api.audio import router as audio_router
from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.meetings import router as meetings_router
from app.api.models import router as models_router
from app.api.speech import router as speech_router
from app.api.system import router as system_router
from app.api.transcripts import router as transcripts_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.services.audio_storage import clean_abandoned
from app.services.models import ModelService


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Configure process infrastructure during application startup."""

    settings = get_settings()
    configure_logging(settings.log_level)
    clean_abandoned(settings.audio_storage_dir)
    application.state.voice_runtime = ModelService(settings)
    yield


def create_app() -> FastAPI:
    """Build the Ceravox FastAPI application."""

    settings = get_settings()
    application = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    application.state.readiness_checks = {}
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.dashboard_url],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-CSRF-Token"],
    )
    application.include_router(health_router)
    application.include_router(auth_router)
    application.include_router(audio_router)
    application.include_router(speech_router)
    application.include_router(transcripts_router)
    application.include_router(meetings_router)
    application.include_router(models_router)
    application.include_router(system_router)
    application.include_router(assistant_router)

    @application.middleware("http")
    async def private_cache(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        if request.url.path.startswith(
            ("/v1/audio", "/v1/transcripts", "/v1/models", "/api/system", "/v1/assistant")
        ):
            response.headers["Cache-Control"] = "no-store"
        return response

    @application.exception_handler(status.HTTP_404_NOT_FOUND)
    async def not_found(_: Request, __: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": {"code": "not_found", "message": "Route not found"}},
        )

    @application.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exception: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": {"code": "validation_error", "message": "Invalid request"}},
        )

    @application.exception_handler(HTTPException)
    async def http_error(_: Request, exception: HTTPException) -> JSONResponse:
        detail = exception.detail
        if isinstance(detail, dict) and "code" in detail and "message" in detail:
            error = detail
        else:
            error = {"code": "request_failed", "message": str(detail)}
        return JSONResponse(status_code=exception.status_code, content={"error": error})

    return application


app = create_app()
