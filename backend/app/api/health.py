"""Liveness and readiness endpoints."""

import inspect
from collections.abc import Awaitable, Callable

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/health", tags=["health"])
ReadinessCheck = Callable[[], bool | Awaitable[bool]]


@router.get("/live")
async def live() -> dict[str, str]:
    """Report that the API process is running."""

    return {"status": "live"}


@router.get("/ready")
async def ready(request: Request) -> JSONResponse:
    """Report whether registered required dependencies are available.

    S0 has no mandatory external dependency, so the default check set is
    empty and this endpoint returns ready. Later services register checks on
    ``app.state.readiness_checks`` without changing the public contract.
    """

    checks: dict[str, ReadinessCheck] = getattr(request.app.state, "readiness_checks", {})
    dependencies: dict[str, str] = {}
    failed = False
    for name, check in checks.items():
        try:
            result = check()
            if inspect.isawaitable(result):
                result = await result
            available = bool(result)
        except Exception:
            available = False
        dependencies[name] = "available" if available else "unavailable"
        failed = failed or not available

    if failed:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "dependencies": dependencies},
        )
    return JSONResponse(content={"status": "ready", "dependencies": dependencies})
