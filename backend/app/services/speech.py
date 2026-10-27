"""Bounded WAV-only speech, never persisted."""

import io
import wave

import numpy as np
from fastapi import HTTPException

from app.api.voice_schemas import SpeechRequest, voice_error
from app.services.models import ModelService


def synthesize(payload: SpeechRequest, runtime: ModelService) -> bytes:
    text = payload.text.strip()
    voice = payload.voice or runtime.settings.tts_default_voice
    if not text or len(text) > runtime.settings.tts_max_text_chars:
        raise voice_error(422, "invalid_text", "Enter text within the character limit")
    if voice not in runtime.settings.tts_voices:
        raise voice_error(422, "invalid_voice", "Choose a configured voice")
    try:
        with runtime.slot(), io.BytesIO() as buffer:
            count = 0
            with wave.open(buffer, "wb") as output:
                output.setnchannels(1)
                output.setsampwidth(2)
                output.setframerate(24000)
                for samples in runtime.load_tts().generate(text, voice):
                    count += len(samples)
                    if count > runtime.settings.tts_max_audio_seconds * 24000:
                        raise voice_error(
                            422, "speech_too_long", "Generated speech exceeds duration limit"
                        )
                    if not np.isfinite(samples).all():
                        raise ValueError("Invalid samples")
                    output.writeframes((np.clip(samples, -1, 1) * 32767).astype("<i2").tobytes())
            if not count:
                raise voice_error(422, "empty_speech", "Text produced no speech")
            return buffer.getvalue()
    except HTTPException:
        raise
    except Exception:
        raise voice_error(500, "speech_failed", "Local speech generation failed") from None
