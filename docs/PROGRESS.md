# Ceravox Progress

## Project constraints

- Ceravox remains free to build and run: no paid AI APIs, hosting, databases,
  model services, or credit-card-required dependencies.
- Runtime components remain local/open-weight: faster-whisper, Kokoro, Silero
  VAD, and Ollama. Persistence is SQLite and CI uses the GitHub Actions free
  tier.
- Wispr Flow Pro is the primary development interface for specifications,
  architecture, coding prompts, reviews, documentation, debugging, commits,
  demo scripts, and submission copy. It is not a runtime dependency.
- Meaningful Wispr usage is recorded in `docs/wispr_usage_log.md`; passwords,
  session tokens, private audio, transcripts, model weights, and secrets are
  excluded.
- Ceravox must work offline after local model installation, and services must
  remain local rather than being exposed publicly.

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

## S1 — Auth and App Shell

**Status:** IMPLEMENTED — verification complete; Docker caveat retained

### Scope boundary

S1 will implement authentication and the protected local single-admin shell
only. It will not implement ASR, TTS, VAD, Ollama, WebSocket, audio, or
meeting-intelligence features.

### Implementation sequence

1. **Database foundation:** add SQLAlchemy/Alembic dependencies, a SQLite
   session factory, declarative metadata, UTC timestamp helpers, and migration
   `001_initial_auth` for UUID-keyed `users` and `sessions` tables. Verify fresh
   upgrade, downgrade, and current-revision detection. Do not use
   `create_all()` for upgrades.
2. **Security primitives:** add Argon2id password hashing through a maintained
   library, SHA-256 session-token hashing, session expiration/invalidation,
   secure cookie settings, generic authentication errors, CSRF double-submit
   protection, and a small in-process failed-login delay/rate limiter.
3. **Auth API:** add public first-run status and CSRF-token endpoints; one-time
   admin setup; login; logout; `/me`; and a protected application status route.
   Enforce 401 for anonymous access, 403 only for insufficient permissions,
   generic login/setup errors, and no sensitive response or log fields.
4. **Frontend shell:** add login, first-run setup, authenticated dashboard,
   logout, `/me` display, protected navigation, 401 redirect handling, and
   accessible placeholders for Transcribe, Speak, Live Assistant, and Meeting
   Notes. Keep all UI assets local and offline-friendly.
5. **Documentation and verification:** update setup/demo instructions, record
   Wispr Flow work, run the security checklist, review the complete diff, and
   preserve the Docker environment caveat if the engine remains unavailable.

### Files to create

**Backend and database**

- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/script.py.mako`
- `backend/alembic/versions/001_initial_auth.py`
- `backend/app/db/__init__.py`
- `backend/app/db/base.py`
- `backend/app/db/models.py`
- `backend/app/db/session.py`
- `backend/app/core/security.py`
- `backend/app/core/csrf.py`
- `backend/app/core/rate_limit.py`
- `backend/app/api/auth.py`
- `backend/app/api/dependencies.py`
- `backend/app/services/__init__.py`
- `backend/app/services/auth.py`
- `backend/tests/conftest.py`
- `backend/tests/test_migrations.py`
- `backend/tests/test_auth.py`
- `backend/tests/test_csrf.py`
- `backend/tests/test_security_logging.py`

**Frontend**

- `dashboard/src/pages/Login.tsx`
- `dashboard/src/pages/Setup.tsx`
- `dashboard/src/pages/Dashboard.tsx`
- `dashboard/src/pages/Placeholder.tsx`
- `dashboard/src/__tests__/Auth.test.tsx`

### Files to modify

- `backend/requirements.txt` — pin SQLAlchemy, Alembic, and Argon2id library
  dependencies.
- `backend/pyproject.toml` — migration/test/type-check configuration.
- `backend/app/main.py` — database lifespan, auth router, protected-route
  dependencies, and exception handling.
- `backend/app/core/config.py` — database URL, session lifetime, cookie,
  CSRF, and rate-limit settings with localhost-safe defaults.
- `backend/app/core/logging.py` — preserve redaction for credentials, cookies,
  hashes, and session values.
- `backend/tests/test_health.py` — retain S0 health coverage with isolated
  database fixtures where needed.
- `dashboard/package.json` and `dashboard/package-lock.json` — pin the local
  router dependency and keep the lockfile reproducible.
- `dashboard/src/App.tsx` — route/authenticated-shell wiring.
- `dashboard/src/lib/api.ts` — cookies, CSRF header, typed auth calls, and 401
  handling.
- `dashboard/src/pages/Dashboard.tsx` — authenticated dashboard content/navigation.
- `dashboard/src/styles.css` — accessible auth and shell states.
- `dashboard/src/__tests__/App.test.tsx` — S1 shell and 401 behavior coverage.
- `README.md` — database migration, first-run admin, login, logout, and test
  commands.
- `DEMO.md` — first-run setup, login, protected shell, and logout demo steps.
- `docs/PROGRESS.md` — S1 implementation and verification evidence.
- `docs/wispr_usage_log.md` — dictated S1 prompts, docs, decisions, and commit
  message.
- `AGENTS.md` — S1 run commands, test commands, security conventions, and
  implementation boundaries.

### Tests to write before or alongside implementation

**Database and migration tests**

- Fresh temporary database accepts `alembic upgrade head`.
- `alembic current` identifies revision `001_initial_auth`.
- `alembic downgrade base` removes the auth schema cleanly.
- Users and sessions have UUID primary keys and UTC timestamps.

**Authentication and security tests**

- First-run setup creates exactly one admin with a strong password.
- A second setup attempt is rejected without revealing account state.
- Password storage is an Argon2id hash and never plaintext.
- Valid login sets an HttpOnly, SameSite=Lax/Strict session cookie.
- Invalid login returns a generic error and applies the local failure delay and
  rate limit.
- Session tokens are hashed in storage and never returned or logged.
- `/me` returns only safe authenticated profile data.
- `/me` and a protected route return 401 anonymously.
- Logout invalidates the session and subsequent access returns 401.
- CSRF-protected setup, login, logout, and future mutation requests reject
  missing or mismatched tokens.
- Authenticated users receive 403 only for an explicitly unauthorized action.
- Logs contain no passwords, hashes, cookies, session tokens, or raw CSRF
  values.

**Frontend tests**

- Login page renders.
- First-run setup page renders when no admin exists.
- Successful authentication renders the protected shell and safe user email or
  admin status.
- Logout clears client auth state and returns to login.
- A 401 API response redirects to login.
- Future-workflow navigation renders accessible placeholders.

### S1 security checklist

- [x] Passwords use maintained Argon2id; no plaintext storage or responses.
- [x] Session tokens are generated server-side and stored only as hashes.
- [x] Session cookies are HttpOnly, appropriately Secure, SameSite=Lax/Strict,
  and expiring.
- [x] CSRF covers every cookie-authenticated state-changing route.
- [x] Generic login/setup errors prevent account enumeration.
- [x] Failed login attempts are delayed or locally rate-limited.
- [x] No credentials, hashes, tokens, cookies, CSRF values, or private content
  appear in logs.
- [x] Protected backend routes enforce authorization independently of frontend
  route guards.
- [x] CORS is restrictive and never wildcard with credentials.
- [x] Local services remain bound to `127.0.0.1` by default.
- [x] No secrets, tokens, databases, model weights, recordings, backups, or
  transcripts are committed.

### Exact S1 exit gate

- [x] Fresh temporary database migration applies successfully.
- [x] Alembic reports the expected current revision and downgrade works.
- [x] Admin can be created exactly once with a strong password.
- [x] Anonymous protected-route access returns 401.
- [x] Valid login creates a usable session cookie.
- [x] Invalid login is generic and delayed/rate-limited.
- [x] `/me` returns safe authenticated user data only.
- [x] Logout invalidates the session.
- [x] CSRF rejects missing/invalid tokens and accepts a valid token.
- [x] Backend pytest suite passes.
- [x] Ruff passes.
- [x] mypy passes.
- [x] Frontend typecheck, lint, tests, and build pass.
- [x] Secret scanning passes.
- [x] No sensitive files or values are committed.
- [x] `docker compose config -q` still passes.
- [x] If Docker is available, Compose smoke test passes; otherwise the exact
  environment caveat is recorded without exposing services publicly.

### S1 verification evidence

- Backend tests: 18 passed.
- Ruff and Ruff format checks: passed.
- mypy: passed.
- Frontend typecheck, lint, Vitest, and build: passed.
- Pre-commit detect-secrets, Ruff, and Ruff format: passed.
- `docker compose config -q`: passed.
- Docker Compose runtime remains unverified because Docker Desktop's Linux
  engine is unavailable; the S0 environment caveat remains applicable.

### S1 security checklist result

- [x] Passwords use maintained Argon2id; no plaintext storage or responses.
- [x] Session tokens are generated server-side and stored only as hashes.
- [x] Session cookies are HttpOnly, locally appropriate Secure behavior,
  SameSite=Lax, and expiring.
- [x] CSRF covers every cookie-authenticated state-changing route.
- [x] Generic login/setup errors prevent account enumeration.
- [x] Failed login attempts receive a local delay and rate limit.
- [x] No credentials, hashes, tokens, cookies, CSRF values, or private content
  appear in logs.
- [x] Protected backend routes enforce authorization independently of frontend
  route guards.
- [x] CORS is restrictive and never wildcard with credentials.
- [x] Local services remain bound to `127.0.0.1` by default.
- [x] No secrets, tokens, databases, model weights, recordings, backups, or
  transcripts are committed.

### S1 exit-gate result

**PASSED WITH ENVIRONMENT CAVEAT** — all application-level S1 checks pass.
The Docker Compose smoke test is not claimed as passed because Docker Desktop's
Linux engine is unavailable. S2 has not started.
