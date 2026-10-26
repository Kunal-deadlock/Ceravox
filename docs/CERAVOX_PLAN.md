# Ceravox Development Plan

Ceravox is a local-first voice AI runtime that turns speech into transcripts,
meeting notes, action items, and spoken answers. Core audio, transcript,
reasoning, and speech workflows remain local after the required models are
installed.

## Cost and workflow policy

Ceravox must remain free to build and run. The project does not use paid AI
APIs, paid hosting, paid databases, paid model services, or dependencies that
require a credit card. The approved runtime stack uses local/open-weight
faster-whisper, Kokoro, Silero VAD, and Ollama models/services, with SQLite for
persistence and the GitHub Actions free tier for CI.

Wispr Flow Pro is the primary development interface for specifications, user
stories, architecture decisions, coding prompts, code review notes,
documentation, bug reports, debugging context, commit messages, demo-video
scripts, and submission copy. It is development-only, not a Ceravox runtime
dependency. Meaningful usage is recorded in `docs/wispr_usage_log.md`.
Passwords, session tokens, private audio, transcripts, model weights, and
secrets must never be entered into Wispr Flow or committed to the repository.
Ceravox must remain offline-capable after local models are installed.

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
