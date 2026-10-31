"""Safe system readiness endpoint — no paths, secrets, or internal errors exposed."""

from typing import Literal
from urllib.error import URLError
from urllib.request import urlopen

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_voice_runtime
from app.core.config import get_settings
from app.db.models import User
from app.db.session import get_db
from app.services.models import ModelService

router = APIRouter(prefix="/api/system", tags=["system"])

ComponentStatus = Literal["ready", "unavailable", "degraded"]


class ComponentInfo(BaseModel):
    status: ComponentStatus
    reason: str


class SystemStatusResponse(BaseModel):
    overall: ComponentStatus
    components: dict[str, ComponentInfo]


def _check_db(db: Session) -> ComponentInfo:
    """Run a trivial query; report degraded if it fails."""
    try:
        db.execute(text("SELECT 1"))
        return ComponentInfo(status="ready", reason="")
    except SQLAlchemyError:
        return ComponentInfo(status="degraded", reason="Database query failed")
    except Exception:  # noqa: BLE001
        return ComponentInfo(status="degraded", reason="Database check failed")


def _check_ollama() -> ComponentInfo:
    """Probe Ollama /api/tags — lightweight, no inference, no model required."""
    settings = get_settings()
    url = f"{settings.ollama_url.rstrip('/')}/api/tags"
    try:
        with urlopen(url, timeout=3):  # noqa: S310 — local 127.0.0.1 only
            return ComponentInfo(status="ready", reason="")
    except URLError:
        if settings.environment == "production":
            reason = (
                "Local Ollama is not configured on this host "
                "(run Ceravox locally for LLM features)."
            )
        else:
            reason = (
                f"Local Ollama is not reachable. Start Ollama and pull {settings.ollama_model}."
            )
        return ComponentInfo(
            status="unavailable",
            reason=reason,
        )
    except TimeoutError:
        return ComponentInfo(
            status="unavailable",
            reason="Ollama did not respond in time.",
        )
    except Exception:  # noqa: BLE001
        return ComponentInfo(status="unavailable", reason="Ollama check failed.")


def _model_status_to_component(
    model_status_value: str, component_name: str = "model"
) -> ComponentInfo:
    """Map an existing ModelService status string to a safe ComponentInfo."""
    settings = get_settings()
    is_prod = settings.environment == "production"

    if model_status_value == "available":
        return ComponentInfo(status="ready", reason="")
    if model_status_value == "not_configured":
        return ComponentInfo(status="unavailable", reason="Model is not configured.")
    if model_status_value == "missing_dependency":
        reason = (
            (
                f"Local {component_name} engine is not installed on this host "
                "(run Ceravox locally for voice features)."
            )
            if is_prod
            else "A required Python package is not installed."
        )
        return ComponentInfo(status="unavailable", reason=reason)
    if model_status_value == "missing_assets":
        reason = (
            (
                f"Local {component_name} weights are not installed on this host "
                "(run Ceravox locally for voice features)."
            )
            if is_prod
            else "Model files are not installed. Run the model installer."
        )
        return ComponentInfo(status="unavailable", reason=reason)
    if model_status_value == "load_failed":
        return ComponentInfo(
            status="degraded",
            reason="Model files exist but could not be loaded.",
        )
    return ComponentInfo(status="unavailable", reason="Model is not available.")


def _overall(components: dict[str, ComponentInfo]) -> ComponentStatus:
    statuses = {c.status for c in components.values()}
    if statuses == {"ready"}:
        return "ready"
    if "degraded" in statuses:
        return "degraded"
    return "unavailable"


@router.get("/status", response_model=SystemStatusResponse)
def system_status(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
    runtime: ModelService = Depends(get_voice_runtime),
) -> SystemStatusResponse:
    """Return safe readiness for all local components. Requires authentication."""
    model_info = runtime.status()

    components: dict[str, ComponentInfo] = {
        "db": _check_db(db),
        "asr": _model_status_to_component(model_info.faster_whisper.status, "speech-to-text (ASR)"),
        "tts": _model_status_to_component(model_info.kokoro.status, "text-to-speech (TTS)"),
        "ollama": _check_ollama(),
    }

    return SystemStatusResponse(
        overall=_overall(components),
        components=components,
    )
