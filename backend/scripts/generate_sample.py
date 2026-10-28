"""Generate a legally safe local sample meeting audio file for testing and demos.

Uses the local Kokoro TTS model when available, or falls back to a synthesized
tone in a standard 16 kHz mono WAV container. Never commits real recordings.
"""

import argparse
import io
import math
import struct
import sys
import wave
from pathlib import Path

# Add backend root to path
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

SAMPLE_TEXT = (
    "Good morning team. In this sprint planning meeting, we decided to launch "
    "Ceravox offline voice runtime by Friday. Alice will finalize the export "
    "endpoints and Bob will review the documentation. Let us ensure all tests pass."
)


def generate_with_kokoro(output_path: Path) -> bool:
    """Attempt to generate high-quality speech with local Kokoro model."""
    try:
        from app.api.voice_schemas import SpeechRequest
        from app.core.config import Settings
        from app.services.models import ModelService
        from app.services.speech import synthesize

        settings = Settings()
        runtime = ModelService(settings)
        status = runtime.status()
        if not status.kokoro.available:
            return False

        wav_bytes = synthesize(
            SpeechRequest(text=SAMPLE_TEXT, voice="af_heart"),
            runtime,
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(wav_bytes)
        print(f"Generated realistic meeting speech ({len(wav_bytes):,} bytes) at {output_path}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"Kokoro synthesis skipped ({exc}); generating synthetic fallback WAV...")
        return False


def generate_synthetic_wav(output_path: Path, duration_seconds: float = 3.0) -> None:
    """Generate a clean 16 kHz mono PCM WAV file using Python standard library only."""
    sample_rate = 16000
    num_samples = int(sample_rate * duration_seconds)
    frequency = 440.0  # 440 Hz tone with fade in/out

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        frames = bytearray()
        for i in range(num_samples):
            t = float(i) / sample_rate
            # Add subtle envelope
            envelope = min(1.0, t * 4, (duration_seconds - t) * 4)
            sample = int(32767.0 * 0.3 * envelope * math.sin(2.0 * math.pi * frequency * t))
            frames.extend(struct.pack("<h", sample))

        wav_file.writeframes(frames)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(buffer.getvalue())
    print(f"Generated synthetic test audio ({output_path.stat().st_size:,} bytes) at {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("sample_meeting.wav"),
        help="Target output path for the WAV file (default: sample_meeting.wav)",
    )
    args = parser.parse_args()

    target = args.output.resolve()
    print(f"Generating sample meeting audio: {target}")

    success = generate_with_kokoro(target)
    if not success:
        generate_synthetic_wav(target)

    print("\nSample generation complete!")
    print(f"File: {target}")
    print("You can now upload this file on the Transcribe page to test the pipeline.")


if __name__ == "__main__":
    main()
