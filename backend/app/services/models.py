"""Safe model availability and one bounded, local inference slot per process."""

import importlib.util
from collections.abc import Iterator
from contextlib import contextmanager
from threading import Lock
from typing import Protocol
from urllib.error import URLError
from urllib.request import urlopen

import numpy as np
from numpy.typing import NDArray

from app.adapters.faster_whisper import ASRResult, FasterWhisperAdapter
from app.adapters.kokoro import KokoroAdapter
from app.api.voice_schemas import ModelsResponse, ModelStatus, VoiceLimits, voice_error
from app.core.config import Settings
from app.services.audio_storage import prepare_storage


class ASR(Protocol):
    def transcribe(self, samples: NDArray[np.float32]) -> ASRResult: ...


class TTS(Protocol):
    def generate(self, text: str, voice: str) -> Iterator[NDArray[np.float32]]: ...


def _probe_ollama(settings: Settings) -> ModelStatus:
    """Probe the local Ollama daemon; never raises — returns a safe ModelStatus."""
    url = f"{settings.ollama_url.rstrip('/')}/api/tags"
    model = settings.ollama_model
    try:
        with urlopen(url, timeout=3):  # noqa: S310 — local loopback only
            return ModelStatus(
                model=model,
                configured=True,
                available=True,
                status="available",
            )
    except (URLError, TimeoutError, OSError):
        return ModelStatus(
            model=model,
            configured=True,
            available=False,
            status="missing_assets",
        )
    except Exception:  # noqa: BLE001
        return ModelStatus(
            model=model,
            configured=True,
            available=False,
            status="missing_assets",
        )


class ModelService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.asr: ASR | None = None
        self.tts: TTS | None = None
        self.failed: set[str] = set()
        self.lock = Lock()
        prepare_storage(settings.audio_storage_dir)

    def status(self) -> ModelsResponse:
        s = self.settings
        asr_assets = all(
            (s.asr_model_dir / name).is_file()
            for name in ("model.bin", "config.json", "tokenizer.json")
        )
        voices = [v for v in s.tts_voices if (s.tts_voices_dir / f"{v}.pt").is_file()]
        tts_assets = all(
            (s.tts_model_dir / name).is_file() for name in ("config.json", "kokoro-v1_0.pth")
        )

        def state(key: str, label: str, packages: list[str], assets: bool) -> ModelStatus:
            status: ModelStatus = ModelStatus(
                model=label, configured=True, available=False, status="missing_assets"
            )
            if key in self.failed:
                status.status = "load_failed"
            elif not all(importlib.util.find_spec(package) is not None for package in packages):
                status.status = "missing_dependency"
            elif assets:
                status.status = "available"
                status.available = True
            return status

        asr = state("asr", s.asr_model, ["faster_whisper", "ctranslate2"], asr_assets)
        tts = state(
            "tts",
            s.tts_model,
            ["kokoro", "en_core_web_sm", "espeakng_loader"],
            tts_assets and s.tts_default_voice in voices,
        )
        tts.voices = voices
        tts.default_voice = s.tts_default_voice if s.tts_default_voice in voices else None
        return ModelsResponse(
            faster_whisper=asr,
            kokoro=tts,
            ollama=_probe_ollama(s),
            limits=VoiceLimits(
                upload_bytes=s.audio_max_upload_bytes,
                text_chars=s.tts_max_text_chars,
                duration_seconds=s.audio_max_duration_seconds,
            ),
        )

    @contextmanager
    def slot(self) -> Iterator[None]:
        if not self.lock.acquire(blocking=False):
            raise voice_error(503, "inference_busy", "Local inference is busy; retry shortly")
        try:
            yield
        finally:
            self.lock.release()

    def load_asr(self) -> ASR:
        if self.asr is None:
            if not self.status().faster_whisper.available:
                raise voice_error(503, "asr_unavailable", "Install the configured local ASR model")
            try:
                self.asr = FasterWhisperAdapter(self.settings)
            except Exception:
                self.failed.add("asr")
                raise voice_error(
                    503, "asr_unavailable", "Local ASR model could not load"
                ) from None
        return self.asr

    def load_tts(self) -> TTS:
        if self.tts is None:
            if not self.status().kokoro.available:
                raise voice_error(
                    503, "tts_unavailable", "Install the local TTS model and English resources"
                )
            try:
                self.tts = KokoroAdapter(self.settings)
            except Exception:
                self.failed.add("tts")
                raise voice_error(
                    503, "tts_unavailable", "Local TTS model could not load"
                ) from None
        return self.tts
