# Ceravox Progress

## S0 — Foundation

**Status:** PASSED WITH ENVIRONMENT CAVEAT

### Completed

- Repository structure and MIT license
- FastAPI application with JSON liveness, readiness, and unknown-route errors
- Pydantic settings and redacting JSON logging
- Backend pytest, Ruff, and mypy configuration
- Vite React TypeScript dashboard with backend health display
- Vitest smoke test and frontend lint/typecheck/build scripts
- Docker Compose services for backend, dashboard, and Ollama
- CI workflow for backend and frontend checks
- `.gitignore`, detect-secrets pre-commit configuration, and example env files
- README, demo instructions, development plan, and Wispr usage log

### Verification run

- `python -m ruff check .` — passed
- `python -m mypy app` — passed
- `python -m pytest -q` — 6 passed
- `npm run typecheck` — passed
- `npm run lint` — passed
- `npm test -- --run` — 1 passed
- `npm run build` — passed
- pre-commit detect-secrets, Ruff, and Ruff format — passed
- `docker compose config -q` — passed
- `docker compose up -d --build` — attempted and failed before build because
  Docker Desktop's Linux engine was not running in this workspace

### S0 files

Backend: `backend/app/`, `backend/tests/`, `backend/requirements.txt`.
Frontend: `dashboard/src/`, `dashboard/package.json`.
Operations: `docker-compose.yml`, Dockerfiles, `.github/workflows/ci.yml`.

### Exit gate

- [x] Fresh clone has exact documented commands in `README.md` and `DEMO.md`
- [x] `docker compose config -q` passes
- [ ] `docker compose up -d --build` starts backend, dashboard, and Ollama
- [ ] Container `/health/live`, `/health/ready`, and dashboard reachability
- [x] Backend and frontend checks pass
- [x] Secret scanning is configured and passes
- [x] No secrets, databases, recordings, or model weights are staged/tracked

### Docker smoke-test result

The Compose runtime smoke test is blocked by the local Docker Desktop engine.
The exact commands and results were:

- `docker desktop start` — timed out after 120 seconds.
- `docker info` — Docker client is available, but the server failed to connect
  to `npipe:////./pipe/dockerDesktopLinuxEngine` because the named pipe was not
  present.
- `docker compose config -q` — passed.
- `docker compose up -d --build` — failed before build for the same daemon
  connection error.
- `curl.exe http://127.0.0.1:8000/health/live` — connection refused because no
  container started.
- `curl.exe http://127.0.0.1:8000/health/ready` — connection refused because no
  container started.
- `curl.exe http://127.0.0.1:5173` — connection refused because no container
  started.
- `docker compose ps` and `docker compose logs --tail=50` — failed because the
  Docker API was unavailable.
- `docker compose down` — attempted; failed for the same unavailable Docker API.

Workaround: start Docker Desktop until `docker info` shows a Server section,
then rerun the commands in `DEMO.md`. The application-level backend and
frontend checks pass independently.

## Next task

S1: add Alembic-backed persistence, first-run admin setup, server-side
sessions, CSRF protection, and the protected application shell.
