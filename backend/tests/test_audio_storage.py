"""Real codec decoding and path/retention boundary tests."""

import io

import av
import numpy as np
import pytest

from app.core.config import Settings
from app.services.audio_storage import clean_abandoned, normalize, temporary_audio


@pytest.mark.parametrize(
    "container,codec,mime",
    [
        ("wav", "pcm_s16le", "audio/wav"),
        ("mp3", "libmp3lame", "audio/mpeg"),
        ("ipod", "aac", "audio/mp4"),
        ("ogg", "libopus", "audio/ogg"),
    ],
)
def test_supported_formats_normalize_to_pcm(tmp_path, container, codec, mime):
    buffer = io.BytesIO()
    with av.open(buffer, mode="w", format=container) as output:
        stream = output.add_stream(codec, rate=48000)
        stream.layout = "mono"
        frame = av.AudioFrame.from_ndarray(
            np.zeros((1, 4800), dtype=np.float32), format="flt", layout="mono"
        )
        frame.sample_rate = 48000
        for packet in stream.encode(frame):
            output.mux(packet)
        for packet in stream.encode(None):
            output.mux(packet)
    buffer.seek(0)
    settings = Settings(audio_storage_dir=tmp_path)
    with temporary_audio(tmp_path) as (_, directory):
        samples = normalize(buffer, mime, directory, settings)
        assert samples.dtype == np.float32
        assert 1000 <= len(samples) <= 2500
        assert (directory / "normalized.pcm").stat().st_size == len(samples) * 2
    assert list(tmp_path.iterdir()) == []


def test_storage_cleanup_is_owned_and_exception_safe(tmp_path):
    unrelated = tmp_path / "keep"
    unrelated.write_text("unrelated")
    with pytest.raises(RuntimeError), temporary_audio(tmp_path) as (_, directory):
        (directory / "source").write_bytes(b"synthetic")
        raise RuntimeError("cancelled")
    clean_abandoned(tmp_path)
    assert list(tmp_path.iterdir()) == [unrelated]


def test_symlink_storage_rejected(tmp_path):
    from app.services.audio_storage import prepare_storage

    destination = tmp_path / "real"
    destination.mkdir()
    link = tmp_path / "link"
    try:
        link.symlink_to(destination, target_is_directory=True)
    except OSError:
        pytest.skip("Host does not permit symlink creation")
    with pytest.raises(ValueError):
        prepare_storage(link)
