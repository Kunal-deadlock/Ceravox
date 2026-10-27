"""Local-only faster-whisper, with materialized segments inside inference scope."""

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from app.core.config import Settings


@dataclass
class Segment:
    start_ms: int
    end_ms: int
    text: str


@dataclass
class ASRResult:
    text: str
    language: str | None
    segments: list[Segment]


class FasterWhisperAdapter:
    def __init__(self, settings: Settings) -> None:
        from faster_whisper import WhisperModel

        self.model: Any = WhisperModel(
            str(settings.asr_model_dir.resolve()),
            device=settings.asr_device,
            compute_type=settings.asr_compute_type,
            cpu_threads=settings.asr_cpu_threads,
            local_files_only=True,
            num_workers=1,
        )

    def transcribe(self, samples: NDArray[np.float32]) -> ASRResult:
        segments, info = self.model.transcribe(samples, beam_size=1, vad_filter=False)
        result = [
            Segment(round(item.start * 1000), round(item.end * 1000), item.text)
            for item in segments
        ]
        return ASRResult(
            "".join(item.text for item in result).strip(), info.language if result else None, result
        )
