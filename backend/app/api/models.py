"""Public capability fields behind authentication."""

from fastapi import APIRouter, Response

from app.api.audio import Owner, Runtime
from app.api.voice_schemas import ModelsResponse

router = APIRouter(prefix="/v1/models", tags=["models"])


@router.get("")
def models(owner: Owner, runtime: Runtime, response: Response) -> ModelsResponse:
    response.headers["Cache-Control"] = "no-store"
    return runtime.status()
