# Ceravox Development Plan

Ceravox is a local-first voice AI runtime that turns speech into transcripts,
meeting notes, action items, and spoken answers. Core audio, transcript,
reasoning, and speech workflows remain local after the required models are
installed.

## Fixed stack

- React, TypeScript, and Vite dashboard
- FastAPI and Pydantic backend
- SQLite with SQLAlchemy and Alembic
- faster-whisper, Kokoro, Silero VAD, and Ollama local model adapters
- Docker Compose for reproducible local setup

## Milestones

1. **S0 Foundation:** repository, Compose, health checks, CI, documentation,
   and secret-safety guardrails.
2. **S1 Auth and app shell:** sessions, CSRF, first-run admin, and protected
   dashboard routes.
3. **S2 Core voice APIs:** validated audio upload, transcription, TTS, and
   model status.
4. **S3 Live voice pipeline:** WebSocket audio, VAD, local LLM, streaming TTS,
   and barge-in.
5. **S4 Meeting intelligence:** stored transcripts, summaries, decisions,
   action items, and transcript Q&A.
6. **S5 Reliability:** metrics, errors, backup/restore, and end-to-end tests.
7. **S6 Hardening:** offline test, security review, accessibility, and CPU
   performance checks.
8. **S7 Release:** clean-machine test, documentation, demo, and release freeze.

Security rules apply throughout: bind local services to localhost, never log
private audio or transcripts, validate uploads, use maintained cryptography,
and never commit secrets, databases, recordings, backups, or model weights.
