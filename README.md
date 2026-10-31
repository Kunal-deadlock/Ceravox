# Ceravox

**🔴 Live Demo:** [https://ceravox-nova.vercel.app](https://ceravox-nova.vercel.app)

Ceravox is a local-first voice AI workstation for turning speech into useful work: transcripts, meeting notes, action items, and spoken answers. Built with privacy and accessibility in mind, all audio decoding, speech-to-text, reasoning, and speech synthesis are executed on your local machine.

---

## Architecture

Ceravox is designed as a modular, local-only workstation. The web dashboard communicates with a local FastAPI backend over authenticated HTTP, with speech models and Ollama running directly on host hardware.

```text
Browser Dashboard (React / TypeScript / Vite on 127.0.0.1:5173)
      │
      │ HTTP (Argon2id Session Cookie + CSRF Double-Submit)
      ▼
FastAPI Backend (Python on 127.0.0.1:8000)
      ├─► SQLite Database (Owner-scoped user accounts and transcripts)
      ├─► faster-whisper (Local ASR via CPU int8, Systran/faster-whisper-base)
      ├─► Kokoro-82M (Local TTS synthesis, hexgrad/Kokoro-82M af_heart)
      └─► Ollama Service (Local LLM inference via qwen2.5:3b on 127.0.0.1:11434)
```

- **Frontend:** React 19, TypeScript, and Vite single-page dashboard with zero external font/CSS CDN calls.
- **Backend:** FastAPI with asynchronous endpoints, SQLAlchemy ORM, and Alembic database migrations.
- **Audio & Storage:** PyAV for stream decoding and 16 kHz mono PCM normalization; ephemeral request-scoped directories.
- **Local AI Engines:** faster-whisper (CTranslate2 CPU int8), Kokoro-82M TTS, and Ollama for meeting notes and contextual Q&A.

---

## Features

- **Speech-to-Text (ASR):** Upload WAV, MP3, M4A, or OGG audio. Audio is validated, normalized to 16 kHz mono PCM, and transcribed locally with timestamped segments using faster-whisper.
- **Text-to-Speech (TTS):** Convert text inputs (up to 2000 characters) into natural speech using Kokoro-82M (`af_heart` voice). Audio plays directly in the browser and can be downloaded as standard WAV.
- **Live Voice Assistant:** Offline conversational voice AI combining faster-whisper speech recognition, Qwen2.5 local reasoning, and Kokoro auto-spoken answers, with Wispr Flow hands-free dictation support.
- **Meeting Notes & Action Items:** Analyze transcripts locally with Ollama (`qwen2.5:3b`) to produce executive summaries, key decisions, and prioritized action items.
- **Interactive Transcript Q&A:** Ask questions about any recorded meeting. The local LLM answers using the transcript as context, with a one-click "Speak Answer" option to hear the response read aloud.
- **Transcript Management & Multi-Format Export:** Saved transcripts are stored with ownership isolation and can be exported at any time in Markdown (`.md`), Plain Text (`.txt`), or structured JSON (`.json`).
- **System Status Preflight:** A live diagnostics page reports real-time readiness for the database, faster-whisper ASR, Kokoro TTS, and Ollama LLM services before starting work.
- **Local Authentication & Multi-Account Registration:** Argon2id password hashing, CSRF double-submit protection, and owner-scoped data isolation with tabbed sign-in and account registration.
- **Synthetic Sample Generator:** Includes `scripts/generate_sample.py` to create synthetic meeting audio for testing without needing microphone recordings.

---

## Cost and development workflow

Ceravox is free to build and run. It does not use paid AI APIs, hosting, databases, model services, or dependencies that require a credit card. Persistence uses local SQLite, CI uses the GitHub Actions free tier, and runtime inference uses local models and services.

[Wispr Flow Pro](https://flow.wispr.ai) is used as the primary development interface for specifications, user stories, architecture decisions, coding prompts, reviews, documentation, bug reports, commit messages, demo scripts, and submission copy. Wispr Flow Pro is a development-time tool only and is not a runtime dependency. Development notes and prompts are maintained in [docs/wispr_usage_log.md](docs/wispr_usage_log.md). Never enter passwords, session tokens, private audio, transcripts, model weights, or secrets into Wispr Flow.

---

## Requirements

- **Python:** 3.11+
- **Node.js:** 20+ (Node 22 recommended)
- **Ollama:** Installed locally with model `qwen2.5:3b` pulled (`ollama pull qwen2.5:3b`)
- **Docker Desktop:** Optional (for Compose)
- **Hardware:** 16 GB RAM recommended; works on CPU or local GPU (RTX 3050+).

---

## Local models setup

Ceravox never downloads models at server startup or during client requests. Local models are installed explicitly:

- **faster-whisper base:** `Systran/faster-whisper-base` (revision `ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66`, MIT license; CPU int8).
- **Kokoro-82M:** `hexgrad/Kokoro-82M` (revision `f3ff3571791e39611d31c381e3a41a3af07b4987`, Apache-2.0 license; English `af_heart` voice and `en_core_web_sm`).

The model weights total approximately 476 MB. To install:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
python scripts/install_models.py --download
```

Model files are placed in `backend/models/faster-whisper-base` and `backend/models/kokoro` (gitignored). After installation, verify offline capability:

```powershell
python scripts/check_offline.py
python scripts/check_offline.py --offline
```

---

## Deployment Modes: Hosted Companion vs. Local AI Runtime

Ceravox operates in two modes:

### 1. Hosted Companion Console (Public)
- **Frontend:** [https://ceravox-nova.vercel.app](https://ceravox-nova.vercel.app) (Vercel)
- **Backend API & Database:** [https://ceravox-api.onrender.com](https://ceravox-api.onrender.com) (Render Web + PostgreSQL)
- **Supported in Cloud:** User accounts, Argon2id session authentication, CSRF double-submit protection, persistent transcript storage, transcript viewing, and multi-format export (Markdown, Plain Text, JSON).
- **Cloud Limitations:** Free zero-cost cloud containers cannot run heavy local inference weights. Voice transcription (faster-whisper), speech generation (Kokoro), and local LLM reasoning (Ollama) remain offline local capabilities and require the local runtime below.

### 2. Full Local Workstation (Complete Offline AI)
Running Ceravox locally executes all speech recognition, synthesis, and LLM reasoning on your machine's hardware with no cloud calls or external dependencies.

---

## Run locally

### Option 1: One-command local startup (Windows PowerShell)

From the repository root:

```powershell
.\scripts\dev.ps1
```

This verifies prerequisites, starts Ollama (if installed), launches the FastAPI backend on `127.0.0.1:8000`, and opens the Vite dashboard on `127.0.0.1:5173`.

### Option 2: Manual startup

#### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend is available at <http://127.0.0.1:8000>. Interactive OpenAPI docs are at <http://127.0.0.1:8000/docs>.

#### Dashboard

```powershell
cd dashboard
npm ci
npm run dev -- --host 127.0.0.1
```

The dashboard is available at <http://127.0.0.1:5173>.

### Option 3: Docker Compose

```powershell
docker compose config -q
docker compose up --build
```

Compose starts the backend, dashboard, and local Ollama service bound to `127.0.0.1`. In a second terminal:

```powershell
curl.exe http://127.0.0.1:8000/health/live
curl.exe http://127.0.0.1:8000/health/ready
curl.exe http://127.0.0.1:5173
docker compose ps
docker compose logs --tail=50
docker compose down
```

---

## Verification checks

Run the full automated test and linting suite:

```powershell
# Backend
cd backend
python -m alembic upgrade head
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python -m mypy app

# Dashboard
cd ..\dashboard
npm run typecheck
npm run lint
npm test -- --run
npm run build
```

---

## Privacy and security

- **Local Runtime Boundary:** No cloud inference and no external network calls during core runtime operation once local models are installed. Initial model downloads and optional Ollama model pulls require an internet connection during setup.
- **Audio Handling:** Uploaded audio is processed locally and is not sent to external services. Temporary audio files created during decoding and normalization are managed in request-scoped directories and cleaned up on both success and failure exit paths.
- **Generated Speech:** Synthesized speech is returned in-memory as an audio WAV stream and is never persisted to disk.
- **Authentication & Authorization:** Passwords are encrypted with Argon2id. Sessions use opaque, hashed tokens stored in HTTP-only cookies. All state-mutating requests are protected with CSRF double-submit validation.
- **Owner Isolation:** Transcripts are strictly scoped to the authenticated owner. Requests for transcripts owned by other users return indistinguishable 404 responses to prevent ID enumeration.
- **Host Binding:** By default, services bind exclusively to `127.0.0.1` on the local machine.

---

## Project roadmap

| Phase | Milestone | Scope & Deliverables | Status |
|---|---|---|---|
| **S0** | **Foundation** | Repository layout, Docker Compose, CI workflow, secret scanning baseline | ✅ Complete |
| **S1** | **Auth & Shell** | Argon2id passwords, session tokens, CSRF double-submit, first-run admin, protected UI routes | ✅ Complete |
| **S2** | **Core Voice APIs** | Bounded multipart upload, faster-whisper ASR, Kokoro-82M TTS, model health probes | ✅ Complete |
| **S4** | **Meeting Intelligence** | Owner-scoped transcripts, Ollama `qwen2.5:3b` summaries & action items, contextual Q&A, Speak Answer | ✅ Complete |
| **M1** | **Usability & Polish** | Preflight System Status view, multi-format export (MD/TXT/JSON), synthetic sample audio generator, dev startup script | ✅ Complete |
| **S3** | **Live Voice Pipeline** | Real-time WebSocket audio streaming, live Silero VAD, barge-in, interactive voice assistant | ⏸️ Deferred (Post-MVP) |
| **S5** | **Reliability & Ops** | Automated backup/restore CLI, operational metrics, extended end-to-end integration suite | 🔮 Future Roadmap |
| **S6** | **Hardening** | Multi-speaker diarization, custom voice profiles, accessibility audits | 🔮 Future Roadmap |

---

## Hackathon submission

Ceravox was built and submitted for **No Hands: The Wispr Challenge**.

- **Submission Index:** [docs/SUBMISSION.md](docs/SUBMISSION.md)
- **Judge Setup & Demo Guide:** [DEMO.md](DEMO.md)
- **Demo Recording Script:** [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)
- **Wispr Flow Usage Log:** [docs/wispr_usage_log.md](docs/wispr_usage_log.md)
- **Development Plan:** [docs/CERAVOX_PLAN.md](docs/CERAVOX_PLAN.md)
- **Progress & Verification Evidence:** [docs/PROGRESS.md](docs/PROGRESS.md)
