# Ceravox — Setup and Demo

## Requirements

- **Python 3.11+** (Python 3.14 confirmed working with pinned dependencies)
- **Node.js 20+**
- **Ollama** with `qwen2.5:3b` pulled (`ollama pull qwen2.5:3b`, ~1.9 GB)
- faster-whisper base and Kokoro-82M with af_heart voice (~476 MB, installed via
  `backend/scripts/install_models.py`)
- Docker Desktop (optional, for Compose)
- ~4–6 GB free storage total for models and temporary audio

---

## Environment setup (first time)

```powershell
# From repository root
cd backend
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt

# Install local AI models (downloads ~476 MB; approve before running)
.venv\Scripts\python.exe scripts\install_models.py --download

# Apply database migrations
.venv\Scripts\python.exe -m alembic upgrade head
```

For Ollama (separate install at https://ollama.com):

```powershell
ollama pull qwen2.5:3b
```

---

## Start services (native, without Docker)

```powershell
# Terminal 1 — backend
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal 2 — dashboard
cd dashboard
npm ci
npm run dev -- --host 127.0.0.1
```

Dashboard URL: **http://127.0.0.1:5173**

---

## First-run admin setup

1. Open http://127.0.0.1:5173.
2. On the first visit, a setup page appears. Enter an email and strong password.
3. Log in with those credentials.

---

## Core workflow demo

### Speak (TTS)

1. Navigate to **Speak**.
2. Type any text (up to 2000 characters).
3. Click **Generate speech**.
4. Play the audio control and download the WAV file.

### Transcribe (ASR)

1. Navigate to **Transcribe**.
2. Click **Choose audio file** and select a WAV/MP3/M4A/OGG file.
3. Click **Transcribe** and wait for faster-whisper to process it locally.
4. View text, language, duration, and segments.
5. Use **Copy**, **Download TXT**, or **Download JSON**.
6. Reload the page and confirm the transcript appears in the saved list.

### Meeting Notes (S4)

1. Navigate to **Meeting Notes**.
2. Select a saved transcript from the dropdown.
3. Click **Generate summary and action items** (uses local Ollama, may take
   20–60 seconds on CPU).
4. Type a question (e.g. "What decisions were made?") and click **Ask locally**.
5. Click **Speak answer** to hear the answer through Kokoro TTS.

---

## Offline operation

All core workflows operate offline once models are installed:

1. Run the backend and dashboard startup commands above.
2. Disconnect your WAN connection (keep localhost available).
3. Reload the dashboard and repeat: Speak, Transcribe, Meeting Notes.

The models are loaded from local files only. No network calls are made during
inference.

---

## Verify offline readiness

```powershell
cd backend
.venv\Scripts\python.exe scripts\check_offline.py --offline
```

---

## Run automated checks

```powershell
# From backend/
.venv\Scripts\python.exe -m pytest -q          # 63 passed, 2 skipped
.venv\Scripts\python.exe -m ruff check .       # passed
.venv\Scripts\python.exe -m mypy app          # passed

# From dashboard/
npm run typecheck   # passed
npm run lint        # passed
npm test -- --run   # 14 passed
npm run build       # passed
```

---

## Docker caveat

`docker compose config -q` passes. The Compose runtime smoke test is blocked
on this machine by Docker Desktop's Linux engine not being available
(`npipe:////./pipe/dockerDesktopLinuxEngine`). Native localhost startup works
correctly. Once Docker Desktop is running (`docker info` shows a server), run:

```powershell
docker compose up -d --build
curl.exe http://127.0.0.1:8000/health/live
curl.exe http://127.0.0.1:5173
docker compose down
```

---

## Security notes

- Services bind to 127.0.0.1 only. Do not expose publicly.
- No credentials, audio, transcripts, or model weights are committed.
- Generated speech is not persisted. Temporary audio is cleaned after each request. Live Assistant and Meeting Notes remain future milestones.
