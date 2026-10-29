"""Conversational Live Assistant router powered by local Ollama."""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool

from app.api.dependencies import get_current_user
from app.api.voice_schemas import voice_error
from app.core.config import get_settings
from app.core.csrf import require_csrf
from app.db.models import User
from app.services.meeting_intelligence import (
    OllamaMalformedResponse,
    OllamaTimeout,
    OllamaUnavailable,
    generate,
)

router = APIRouter(prefix="/v1/assistant", tags=["assistant"])


class AssistantChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str = Field(min_length=1, max_length=1000)


class AssistantChatResponse(BaseModel):
    reply: str


ASSISTANT_SYSTEM_PROMPT = (
    "You are Ceravox, a helpful, direct, and conversational local voice AI assistant. "
    "Keep your answers concise, natural, friendly, and under 3 sentences so they can be spoken "
    "clearly."
)


def assistant_prompt(user_message: str) -> str:
    return f"{ASSISTANT_SYSTEM_PROMPT}\n\nUser: {user_message.strip()}\nCeravox:"


@router.post("/chat", response_model=AssistantChatResponse)
async def chat(
    payload: AssistantChatRequest,
    request: Request,
    owner: User = Depends(get_current_user),
) -> AssistantChatResponse:
    await require_csrf(request)
    settings = get_settings()
    prompt = assistant_prompt(payload.message)
    try:
        reply = await run_in_threadpool(generate, prompt, settings)
    except OllamaTimeout:
        raise voice_error(504, "ollama_timeout", "Local Ollama took too long to respond") from None
    except OllamaUnavailable:
        raise voice_error(
            503,
            "ollama_unavailable",
            f"Local Ollama or model '{settings.ollama_model}' is unavailable",
        ) from None
    except OllamaMalformedResponse:
        raise voice_error(
            502, "ollama_invalid_response", "Local Ollama returned an invalid response"
        ) from None
    return AssistantChatResponse(reply=reply)
