# Ceravox Demo

## S2 local voice demo

From `backend/`, with the approved local assets installed:

```powershell
.\.venv\Scripts\python scripts\check_offline.py --offline
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another terminal, start the dashboard with `npm run dev -- --host
127.0.0.1`, open <http://127.0.0.1:5173>, create the local admin on first run,
and log in. Confirm the model panel shows ASR/TTS states. On **Transcribe**,
upload a non-private WAV/MP3/M4A/OGG sample and confirm text, language,
duration, segments, copy, TXT/JSON export, and saved-detail reopening. On
**Speak**, enter short text, choose `af_heart`, generate WAV, play it, and
download it. Confirm logout removes access.

Do not record credentials, private audio, transcripts, model weights, or
generated media in screenshots, logs, documentation, or Git.

## S0/Compose smoke demo

From a fresh clone, run:

```powershell
docker compose config -q
docker compose up -d --build
curl.exe http://127.0.0.1:8000/health/live
curl.exe http://127.0.0.1:8000/health/ready
curl.exe http://127.0.0.1:5173
docker compose ps
docker compose logs --tail=50
docker compose down
```

Open <http://127.0.0.1:5173> and confirm that the dashboard reports the
backend as healthy. On the first visit, create the one-time local admin,
log in, inspect the protected navigation placeholders, and log out.

If Docker Desktop's Linux engine is unavailable, `docker compose config -q` may
still pass while runtime commands fail. Keep the exact environment error in
`docs/PROGRESS.md`; do not claim a Compose smoke test passed without real
container output. Live Assistant and Meeting Notes remain future milestones.
