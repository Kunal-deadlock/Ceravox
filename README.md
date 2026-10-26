# Ceravox

Ceravox is a local-first voice AI workstation for turning speech into useful
work: transcripts, meeting notes, action items, and spoken answers.

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
