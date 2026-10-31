"""Groq cloud AI adapter for zero-cost Whisper ASR and LLaMA meeting intelligence."""

from typing import Any

import httpx

from app.adapters.faster_whisper import ASRResult, Segment
from app.core.config import Settings
from app.services.meeting_intelligence import (
    OllamaMalformedResponse,
    OllamaTimeout,
    OllamaUnavailable,
)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class GroqAdapter:
    """Bounded, authenticated client for Groq's free cloud inference APIs."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.api_key = settings.groq_api_key.strip()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

    def transcribe_bytes(self, audio_bytes: bytes, filename: str = "audio.wav") -> ASRResult:
        """Transcribe audio bytes using Groq whisper-large-v3-turbo."""
        if not self.api_key:
            raise OllamaUnavailable("Groq API key is not configured")

        url = f"{GROQ_BASE_URL}/audio/transcriptions"
        files = {
            "file": (filename, audio_bytes, "audio/wav"),
        }
        data = {
            "model": self.settings.groq_asr_model,
            "response_format": "verbose_json",
            "timestamp_granularities[]": "segment",
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, headers=self.headers, files=files, data=data)
        except httpx.TimeoutException as exc:
            raise OllamaTimeout("Groq transcription timed out") from exc
        except httpx.RequestError as exc:
            raise OllamaUnavailable(f"Groq API connection error: {exc}") from exc

        if response.status_code == 401:
            raise OllamaUnavailable("Invalid Groq API key")
        if response.status_code != 200:
            raise OllamaUnavailable(f"Groq ASR failed with status {response.status_code}")

        try:
            body = response.json()
        except Exception as exc:
            raise OllamaMalformedResponse("Invalid JSON from Groq ASR") from exc

        raw_segments: list[dict[str, Any]] = body.get("segments") or []
        segments: list[Segment] = []
        for s in raw_segments:
            start_ms = round(float(s.get("start", 0)) * 1000)
            end_ms = round(float(s.get("end", 0)) * 1000)
            text = str(s.get("text", "")).strip()
            if text:
                segments.append(Segment(start_ms=start_ms, end_ms=end_ms, text=text))

        full_text = str(body.get("text", "")).strip()
        language = body.get("language")
        return ASRResult(text=full_text, language=language, segments=segments)

    def generate(self, prompt: str) -> str:
        """Generate text completion using Groq LLaMA model."""
        if not self.api_key:
            raise OllamaUnavailable("Groq API key is not configured")

        url = f"{GROQ_BASE_URL}/chat/completions"
        payload = {
            "model": self.settings.groq_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 1024,
        }

        try:
            with httpx.Client(timeout=self.settings.ollama_timeout_seconds) as client:
                response = client.post(url, headers=self.headers, json=payload)
        except httpx.TimeoutException as exc:
            raise OllamaTimeout("Groq LLM response timed out") from exc
        except httpx.RequestError as exc:
            raise OllamaUnavailable(f"Groq connection error: {exc}") from exc

        if response.status_code == 401:
            raise OllamaUnavailable("Invalid Groq API key")
        if response.status_code != 200:
            raise OllamaUnavailable(f"Groq LLM failed with status {response.status_code}")

        try:
            body = response.json()
            choices = body.get("choices")
            if not choices or not isinstance(choices, list):
                raise OllamaMalformedResponse("No choices in Groq response")
            reply = choices[0].get("message", {}).get("content", "")
            if not isinstance(reply, str) or not reply.strip() or len(reply) > 20000:
                raise OllamaMalformedResponse("Groq returned empty or out-of-bounds text")
            return reply.strip()
        except (OllamaMalformedResponse, OllamaTimeout, OllamaUnavailable):
            raise
        except Exception as exc:
            raise OllamaMalformedResponse("Failed to parse Groq response") from exc
