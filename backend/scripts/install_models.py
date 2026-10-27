"""Explicit installation only; runtime code never calls this script."""

import argparse
import hashlib
import subprocess
import urllib.request
from pathlib import Path

ASR_REVISION = "ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66"  # pragma: allowlist secret
TTS_REVISION = "f3ff3571791e39611d31c381e3a41a3af07b4987"  # pragma: allowlist secret
FILES = [
    (
        "Systran/faster-whisper-base",
        ASR_REVISION,
        "model.bin",
        "faster-whisper-base/model.bin",
        "d01c3014881c9c6f3133c182f3d2887e"  # pragma: allowlist secret
        "b6ca1c789a7538c5c007196857a0a6a9",  # pragma: allowlist secret
    ),
    (
        "Systran/faster-whisper-base",
        ASR_REVISION,
        "config.json",
        "faster-whisper-base/config.json",
        None,
    ),
    (
        "Systran/faster-whisper-base",
        ASR_REVISION,
        "tokenizer.json",
        "faster-whisper-base/tokenizer.json",
        None,
    ),
    (
        "Systran/faster-whisper-base",
        ASR_REVISION,
        "vocabulary.txt",
        "faster-whisper-base/vocabulary.txt",
        None,
    ),
    (
        "hexgrad/Kokoro-82M",
        TTS_REVISION,
        "kokoro-v1_0.pth",
        "kokoro/kokoro-v1_0.pth",
        "496dba118d1a58f5f3db2efc88dbdc21"  # pragma: allowlist secret
        "6e0483fc89fe6e47ee1f2c53f18ad1e4",  # pragma: allowlist secret
    ),
    ("hexgrad/Kokoro-82M", TTS_REVISION, "config.json", "kokoro/config.json", None),
    (
        "hexgrad/Kokoro-82M",
        TTS_REVISION,
        "voices/af_heart.pt",
        "kokoro/voices/af_heart.pt",
        "0ab5709b8ffab19bfd849cd11d98f75b"  # pragma: allowlist secret
        "60af7733253ad0d67b12382a102cb4ff",  # pragma: allowlist secret
    ),
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", required=True)
    parser.parse_args()
    backend = Path(__file__).resolve().parents[1]
    root = backend / "models"
    for repository, revision, name, target, expected in FILES:
        destination = root / target
        subprocess.run(
            ["git", "check-ignore", "--quiet", str(destination)], cwd=backend, check=True
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and expected:
            if hashlib.sha256(destination.read_bytes()).hexdigest() == expected:
                print(f"Verified {target}")
                continue
        partial = destination.with_suffix(destination.suffix + ".partial")
        digest = hashlib.sha256()
        try:
            url = f"https://huggingface.co/{repository}/resolve/{revision}/{name}"
            with urllib.request.urlopen(url, timeout=120) as response, partial.open("wb") as output:
                while data := response.read(1024 * 1024):
                    digest.update(data)
                    output.write(data)
            if expected and digest.hexdigest() != expected:
                raise RuntimeError("Upstream model checksum mismatch")
            partial.replace(destination)
            print(f"Installed {target}: {destination.stat().st_size} bytes")
        finally:
            partial.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
