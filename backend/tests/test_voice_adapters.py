"""Adapters must receive local inputs, never model download identifiers."""

import sys
from types import SimpleNamespace

import numpy as np
import pytest
from fastapi import HTTPException

from app.adapters.faster_whisper import FasterWhisperAdapter
from app.core.config import Settings
from app.services.models import ModelService


def test_asr_local_load_and_lazy_materialization(monkeypatch, tmp_path):
    calls = {}

    class Model:
        def __init__(self, path, **kwargs):
            calls.update(path=path, **kwargs)

        def transcribe(self, samples, **kwargs):
            def segments():
                calls["iterated"] = True
                yield SimpleNamespace(start=0, end=1, text="Synthetic")

            return segments(), SimpleNamespace(language="en")

    monkeypatch.setitem(sys.modules, "faster_whisper", SimpleNamespace(WhisperModel=Model))
    settings = Settings(asr_model_dir=tmp_path)
    result = FasterWhisperAdapter(settings).transcribe(np.zeros(16000, dtype=np.float32))
    assert calls["path"] == str(tmp_path.resolve())
    assert calls["local_files_only"] is True
    assert calls["device"] == "cpu" and calls["compute_type"] == "int8"
    assert calls["iterated"] and result.segments[0].end_ms == 1000


def test_slot_contention_and_release(tmp_path):
    runtime = ModelService(Settings(audio_storage_dir=tmp_path))
    with runtime.slot():
        with pytest.raises(HTTPException) as error, runtime.slot():
            pass
        assert error.value.status_code == 503
    with runtime.slot():
        pass


def test_config_rejects_paths_as_public_labels():
    from pydantic import ValidationError

    for values in (
        {"asr_model": "C:/private"},
        {"tts_voices": ["../voice"]},
        {"asr_device": "cpu", "asr_compute_type": "float16"},
    ):
        with pytest.raises(ValidationError):
            Settings(**values)
