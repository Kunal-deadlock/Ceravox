"""Run the approved real voice smoke check, optionally denying socket networking."""

import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    if args.offline:

        def deny_network(event: str, _: tuple[object, ...]) -> None:
            if event in {"socket.connect", "socket.getaddrinfo", "socket.sendto"}:
                raise RuntimeError("Network disabled for offline verification")

        sys.addaudithook(deny_network)

    from app.api.voice_schemas import SpeechRequest
    from app.core.config import Settings
    from app.core.logging import configure_logging
    from app.services.audio_storage import normalize, temporary_audio
    from app.services.models import ModelService
    from app.services.speech import synthesize

    configure_logging()
    with tempfile.TemporaryDirectory(prefix="ceravox-offline-") as temporary:
        runtime = ModelService(Settings(audio_storage_dir=Path(temporary)))
        status = runtime.status()
        assert status.faster_whisper.available, "ASR prerequisites unavailable"
        assert status.kokoro.available, "TTS prerequisites unavailable"
        audio = synthesize(
            SpeechRequest(text="Hello. This is a local voice test.", voice="af_heart"), runtime
        )
        import io

        with runtime.slot(), temporary_audio(Path(temporary)) as (_, directory):
            samples = normalize(io.BytesIO(audio), "audio/wav", directory, runtime.settings)
            result = runtime.load_asr().transcribe(samples)
        assert len(audio) > 44 and result.text and result.segments
        assert not list(Path(temporary).iterdir())
        print(
            f"PASS: Kokoro af_heart WAV {len(audio)} bytes; ASR base CPU/int8 "
            f"{len(result.segments)} segments, language={result.language}; "
            f"network={'denied by audit hook' if args.offline else 'available; local assets only'}"
        )


if __name__ == "__main__":
    main()
