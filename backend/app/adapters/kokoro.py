"""Kokoro with explicit local weights/voices and preinstalled English resources."""

from collections.abc import Iterator
from typing import Any

import numpy as np
from numpy.typing import NDArray

from app.core.config import Settings


class KokoroAdapter:
    def __init__(self, settings: Settings) -> None:
        import os

        # Must precede importing hub/transformers; explicit files remain authoritative.
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        from loguru import logger

        logger.disable("kokoro")
        logger.disable("misaki")
        import spacy
        from misaki import espeak

        if not spacy.util.is_package("en_core_web_sm"):
            raise RuntimeError("English resources unavailable")
        # Ensure fallback exists BEFORE KPipeline; otherwise Misaki can request a model.
        espeak.EspeakFallback(british=False)
        from kokoro import KModel, KPipeline

        self.settings = settings
        self.model = (
            KModel(
                repo_id="hexgrad/Kokoro-82M",
                config=str(settings.tts_model_dir / "config.json"),
                model=str(settings.tts_model_dir / "kokoro-v1_0.pth"),
            )
            .to("cpu")
            .eval()
        )
        self.pipelines: dict[str, Any] = {}
        for language in {voice[0] for voice in settings.tts_voices}:
            self.pipelines[language] = KPipeline(
                lang_code=language, model=self.model, repo_id="hexgrad/Kokoro-82M", device="cpu"
            )

    def generate(self, text: str, voice: str) -> Iterator[NDArray[np.float32]]:
        import torch

        # A tensor avoids KPipeline's voice-name download branch entirely.
        pack = torch.load(
            self.settings.tts_voices_dir / f"{voice}.pt", map_location="cpu", weights_only=True
        )
        for result in self.pipelines[voice[0]](text, voice=pack):
            if result.audio is not None:
                yield np.asarray(result.audio.numpy(), dtype=np.float32)
