# Ceravox

Ceravox is a local-first voice AI workstation for turning speech into useful
work: transcripts, meeting notes, action items, and spoken answers. S2 adds
authenticated local transcription, speech generation, persisted transcripts,
and safe model status reporting.

S0 provides the reproducible foundation: a FastAPI backend, React dashboard,
Docker Compose services, health checks, CI, and secret-safety guardrails.

## Cost and development workflow

Ceravox is free to build and run. It does not use paid AI APIs, hosting,
databases, model services, or dependencies that require a credit card. Runtime
inference uses local models and services: faster-whisper, Kokoro, Silero VAD,
and Ollama. Persistence uses SQLite, CI uses the GitHub Actions free tier, and
Ceravox remains offline-capable after local models are installed.

Wispr Flow Pro is used as the primary development interface for specifications,
user stories, architecture decisions, coding prompts, reviews, documentation,
bug reports, commit messages, demo scripts, and submission copy. Wispr Flow Pro
is not a Ceravox runtime dependency. Never enter passwords, session tokens,
private audio, transcripts, model weights, or secrets into Wispr Flow.

## Requirements

- Python 3.11+
- Node.js 20+
- Docker Desktop (optional, for Compose)

## S2 local models

Install models explicitly; Ceravox never downloads models at startup or during
requests. The supported S2 defaults are:

- faster-whisper base from `Systran/faster-whisper-base`, revision
  `ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66`, MIT license; CPU/int8.
- Kokoro-82M from `hexgrad/Kokoro-82M`, revision
  `f3ff3571791e39611d31c381e3a41a3af07b4987`, Apache-2.0 license; English
  `af_heart` voice and local `en_core_web_sm` English resources.

The model files are approximately 476 MB. Dependency downloads and temporary
installation space are larger. Run the explicit installer from `backend/` only
after reviewing the upstream licenses and pinned requirements:

```powershell
cd backend
..\.venv-bootstrap\Scripts\uv pip install --python .venv\Scripts\python.exe -r requirements.txt
..\.venv-bootstrap\Scripts\uv pip install --python .venv\Scripts\python.exe https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
.\.venv\Scripts\python scripts\install_models.py --download
```

Model directories are `backend/models/faster-whisper-base` and
`backend/models/kokoro`; they are ignored by Git. Configure locations, voices,
storage, and limits with the `CERAVOX_*` variables in `backend/.env.example`.
Do not put machine-specific absolute paths in committed documentation.

After installation, verify local-only operation:

```powershell
.\.venv\Scripts\python scripts\check_offline.py
.\.venv\Scripts\python scripts\check_offline.py --offline
```

S2 accepts WAV, MP3, M4A, and OGG uploads, normalizes them to 16 kHz mono PCM,
deletes temporary audio after processing, and persists only owner-scoped
transcript text/segments. Speech returns an in-memory WAV and does not persist
generated audio. The dashboard provides Transcribe, Speak, export, playback,
download, and model-status views.

## Run locally

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend is available at <http://127.0.0.1:8000>. OpenAPI docs are at
<http://127.0.0.1:8000/docs>.

### Dashboard

```powershell
cd dashboard
npm ci
npm run dev -- --host 127.0.0.1
```

The dashboard is available at <http://127.0.0.1:5173>.

### Docker Compose

```powershell
docker compose config -q
docker compose up --build
```

Compose starts the backend, dashboard, and local Ollama service. Services are
bound to localhost by default. In a second terminal, verify the running stack:

```powershell
curl.exe http://127.0.0.1:8000/health/live
curl.exe http://127.0.0.1:8000/health/ready
curl.exe http://127.0.0.1:5173
docker compose ps
docker compose logs --tail=50
docker compose down
```

## Checks

```powershell
cd backend
alembic upgrade head
python -m pytest
python -m ruff check .
python -m mypy app

cd ..\dashboard
npm run typecheck
npm run lint
npm test -- --run
npm run build
```

## Privacy and repository safety

Core Ceravox features are designed to run locally after model installation.
Do not commit secrets, recordings, transcripts, databases, backups, model
weights, or generated audio. The repository includes a pre-commit secret scan
and ignores common local data paths.

See [docs/CERAVOX_PLAN.md](docs/CERAVOX_PLAN.md),
[docs/PROGRESS.md](docs/PROGRESS.md), and [DEMO.md](DEMO.md) for the product
plan, current milestone, and demo instructions.
