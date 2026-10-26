# Ceravox Demo

## S0 smoke demo

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
backend as healthy.

The transcription, speech, live assistant, and meeting intelligence flows are
planned for the later S2–S4 milestones.
