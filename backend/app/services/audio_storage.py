"""Bounded content validation, normalization and request-only private storage."""

import re
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO
from uuid import UUID, uuid4

import av
import numpy as np
from numpy.typing import NDArray

from app.api.voice_schemas import voice_error
from app.core.config import Settings

OWNED = re.compile(r"cvx-[0-9a-f]{32}\Z")
MIMES = {
    "wav": {"audio/wav", "audio/x-wav", "audio/wave"},
    "mp3": {"audio/mpeg", "audio/mp3"},
    "mov": {"audio/mp4", "audio/m4a", "audio/x-m4a"},
    "ogg": {"audio/ogg", "application/ogg"},
}
CODECS = {
    "wav": {"pcm_s16le", "pcm_s24le", "pcm_s32le", "pcm_f32le", "pcm_u8"},
    "mp3": {"mp3", "mp3float"},
    "mov": {"aac", "alac"},
    "ogg": {"vorbis", "opus"},
}


def prepare_storage(root: Path) -> None:
    if any(p.is_symlink() for p in (root, *root.parents)):
        raise ValueError("Audio storage must not traverse links")
    webroot = Path(__file__).resolve().parents[3] / "dashboard"
    if root.resolve().is_relative_to(webroot):
        raise ValueError("Audio storage must be private")
    root.mkdir(parents=True, exist_ok=True, mode=0o700)


def remove_owned(directory: Path) -> None:
    if directory.is_symlink() or not OWNED.fullmatch(directory.name):
        return
    marker = directory / ".ceravox"
    if marker.is_symlink() or not marker.is_file():
        return
    for name in ("source", "normalized.pcm", ".ceravox"):
        (directory / name).unlink(missing_ok=True)
    directory.rmdir()


def clean_abandoned(root: Path) -> None:
    prepare_storage(root)
    for directory in root.iterdir():
        if directory.is_dir() and not directory.is_symlink() and OWNED.fullmatch(directory.name):
            # Leave unknown contents untouched; this directory is exclusively app-owned.
            if all(p.name in {"source", "normalized.pcm", ".ceravox"} for p in directory.iterdir()):
                remove_owned(directory)


@contextmanager
def temporary_audio(root: Path) -> Iterator[tuple[UUID, Path]]:
    prepare_storage(root)
    identifier = uuid4()
    directory = root / f"cvx-{identifier.hex}"
    directory.mkdir(mode=0o700)
    (directory / ".ceravox").touch(mode=0o600)
    try:
        yield identifier, directory
    finally:
        remove_owned(directory)


def container_type(header: bytes) -> str:
    if header[:4] == b"RIFF" and header[8:12] == b"WAVE":
        return "wav"
    if header.startswith(b"ID3") or (
        len(header) >= 2 and header[0] == 255 and header[1] & 224 == 224
    ):
        return "mp3"
    if header[4:8] == b"ftyp":
        return "mov"
    if header.startswith(b"OggS"):
        return "ogg"
    raise voice_error(415, "invalid_audio_type", "Choose WAV, MP3, M4A or OGG audio")


def normalize(
    source: BinaryIO, mime: str | None, directory: Path, settings: Settings
) -> NDArray[np.float32]:
    total = 0
    with (directory / "source").open("xb") as output:
        while chunk := source.read(65536):
            total += len(chunk)
            if total > settings.audio_max_upload_bytes:
                raise voice_error(413, "upload_too_large", "Audio exceeds the upload limit")
            output.write(chunk)
    if not total:
        raise voice_error(422, "empty_audio", "Audio is empty")
    with (directory / "source").open("rb") as media:
        kind = container_type(media.read(16))
        if mime not in (None, "", "application/octet-stream") and mime not in MIMES[kind]:
            raise voice_error(
                415, "invalid_audio_type", "Audio content does not match its media type"
            )
        media.seek(0)
        av.logging.set_level(av.logging.PANIC)
        count = 0
        try:
            with av.open(
                media, format=kind, options={"protocol_whitelist": "file,pipe"}
            ) as container:
                if len(container.streams.audio) != 1 or container.streams.video:
                    raise voice_error(
                        415, "invalid_audio_type", "Upload one audio stream without video"
                    )
                stream = container.streams.audio[0]
                if stream.codec_context.name not in CODECS[kind]:
                    raise voice_error(415, "invalid_audio_type", "Unsupported audio codec")
                resampler = av.AudioResampler(format="s16", layout="mono", rate=16000)
                with (directory / "normalized.pcm").open("xb") as pcm:
                    for frame in container.decode(stream):
                        for normalized in resampler.resample(frame):
                            count += normalized.samples
                            if count > settings.audio_max_duration_seconds * 16000:
                                raise voice_error(
                                    422, "audio_too_long", "Audio exceeds duration limit"
                                )
                            pcm.write(normalized.to_ndarray().tobytes())
                    for normalized in resampler.resample(None):
                        count += normalized.samples
                        if count > settings.audio_max_duration_seconds * 16000:
                            raise voice_error(422, "audio_too_long", "Audio exceeds duration limit")
                        pcm.write(normalized.to_ndarray().tobytes())
        except (av.FFmpegError, ValueError, EOFError):
            raise voice_error(422, "invalid_audio", "Audio could not be decoded") from None
    if not count:
        raise voice_error(422, "empty_audio", "Audio contains no samples")
    samples = np.fromfile(directory / "normalized.pcm", dtype="<i2").astype(np.float32)
    return samples / np.float32(32768)
