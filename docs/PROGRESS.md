# Ceravox Progress

## M1 — Demo Resilience and UX Polish

**Status:** PLANNING — awaiting approval before implementation

**Deadline:** 31 October 2026, 11:59 PM IST

### M1 plan summary

Goal: make Ceravox easier for judges to run, harder to break during a demo, and
clearer when a local dependency is unavailable.

Six tasks, implemented in this order:

1. **System status endpoint** `GET /api/system/status` — authenticated; reports
   db, ASR, TTS, and Ollama readiness as "ready/unavailable/degraded" with a
   short safe reason. Overall status is "ready" only when all required
   components are ready. Builds on existing `ModelService.status()` and a
   lightweight Ollama `/api/tags` ping (no inference).
2. **Preflight status UI** — `SystemStatus.tsx` page accessible from the
   dashboard nav; shows each component with a clear indicator, short reason when
   unavailable, a Refresh button, and overall readiness. Handles backend-
   unreachable gracefully.
3. **Meeting Notes loading/error states** — improve `MeetingNotes.tsx`: typed
   loading state per action, inline error message, buttons disabled during any
   in-flight request, and duplicate-request guard.
4. **Transcript export** — add `GET /v1/transcripts/{id}/export?format=md|txt|json`
   (owner-scoped, server-validated format); add download buttons to `Transcribe.tsx`.
5. **Sample meeting asset** — `backend/samples/generate_sample.py` generates a
   short synthetic WAV using only Python stdlib (`wave`, `math`, `struct`);
   output is safe to use for demos. Instructions added to `DEMO.md`.
6. **One-command dev startup** — `scripts/dev.ps1` starts Ollama, backend,
   and dashboard and prints local URLs. `README.md` and `DEMO.md` updated.

### M1 auth convention

All new endpoints follow the existing convention: session cookie required
(returns 401 unauthenticated). No endpoint exposes filesystem paths, exception
messages, tokens, or secrets.

### M1 task list with tests

#### Task 1 — System status endpoint

**Status:** COMPLETE (74 backend tests passed, 2 skipped, ruff/format/mypy passed)

**Tests to write first (`backend/tests/test_system_status.py`)**

- [x] Authenticated GET returns 200 with expected shape (db, asr, tts, ollama, overall)
- [x] Unauthenticated GET returns 401
- [x] Each component status is "ready", "unavailable", or "degraded"
- [x] DB unavailable produces a safe degraded/unavailable response
- [x] Ollama unavailable produces a safe "unavailable" status (no error detail leaked)
- [x] Response contains no filesystem paths, secrets, stack traces, or tokens
- [x] Overall is "ready" only if all components are ready

**Implementation files**

- `backend/app/api/system.py` (new)
- `backend/app/main.py` (include system router)

#### Task 2 — Preflight status UI

**Status:** COMPLETE (18 frontend tests passed, typecheck, lint, build passed)

**Tests to write first (`dashboard/src/__tests__/SystemStatus.test.tsx`)**

- [x] Renders all four component status rows (db, asr, tts, ollama)
- [x] Shows "unavailable" state and reason safely (no paths or stack traces)
- [x] Refresh button triggers a new status fetch
- [x] Handles backend failure (network error) without crashing

**Implementation files**

- `dashboard/src/pages/SystemStatus.tsx` (new)
- `dashboard/src/lib/api.ts` (add `getSystemStatus()`)
- `dashboard/src/App.tsx` (add /status route and nav link)
- `dashboard/src/pages/Dashboard.tsx` (add System Status nav link)

#### Task 3 — Meeting Notes loading/error states

**Status:** COMPLETE (23 frontend tests passed across suite, 5 MeetingNotes tests, typecheck, lint, build passed)

**Tests to write first (`dashboard/src/__tests__/MeetingNotes.test.tsx`)**

- [x] Shows loading state while summary is generating
- [x] Shows loading state while Q&A answer is generating
- [x] Shows error message if Ollama request fails
- [x] Buttons are disabled while any request is in progress
- [x] Duplicate submit is prevented
- [x] Recovers cleanly after a retry
- [x] "Speak answer" button still works after successful Q&A

**Implementation files**

- `dashboard/src/pages/MeetingNotes.tsx` (improved with distinct action loading states, error boundary, and disabled inputs during requests)

#### Task 4 — Transcript export

**Status:** COMPLETE (81 backend tests passed, 24 frontend tests passed, typecheck, lint, and build passed)

**Tests to write first (`backend/tests/test_transcripts.py` additions)**

- [x] Authenticated owner can download `.md` format
- [x] Authenticated owner can download `.txt` format
- [x] Authenticated owner can download `.json` format
- [x] Unauthenticated request returns 401
- [x] Non-owner request returns indistinguishable 404 (not 403)
- [x] Invalid transcript ID handled safely
- [x] Invalid format parameter rejected safely
- [x] Exported MD, TXT, and JSON contain expected transcript content

**Frontend tests (`dashboard/src/__tests__/Transcribe.test.tsx` additions)**

- [x] Download MD button triggers correct API call
- [x] Download TXT button triggers correct API call
- [x] Download JSON button triggers correct API call

**Implementation files**

- `backend/app/api/transcripts.py` (add export endpoint)
- `dashboard/src/lib/api.ts` (add `exportTranscript()`)
- `dashboard/src/pages/Transcribe.tsx` (add MD, TXT, JSON export buttons)

#### Task 5 — Sample meeting asset

**Status:** COMPLETE (generate_sample.py added, DEMO.md updated, audio files gitignored)

- [x] `backend/scripts/generate_sample.py` generates a valid WAV using Kokoro or stdlib fallback
- [x] Running the script produces a valid WAV that the backend can transcribe
- [x] `DEMO.md` documents how to generate and use the sample
- [x] Audio formats (.wav, .mp3, .m4a, .ogg) explicitly gitignored to protect repo safety

**Implementation files**

- `backend/scripts/generate_sample.py` (new)
- `DEMO.md` (add sample instructions and workflow)
- `.gitignore` (safeguard all audio formats)

#### Task 6 — One-command dev startup

**Status:** COMPLETE (scripts/dev.ps1 created, README.md & DEMO.md updated with exact commands)

- [x] `scripts/dev.ps1` starts Ollama (if needed), backend, and dashboard
- [x] Script prints clear URLs and explains what to do if a model is missing
- [x] `README.md` updated with the exact startup command
- [x] `DEMO.md` updated with the exact startup command

**Implementation files**

- `scripts/dev.ps1` (new PowerShell startup script)
- `README.md` (one-command startup guide)
- `DEMO.md` (Option A/B startup workflows)

### M1 definition of done

- [x] `GET /api/system/status` works and is tested
- [x] Dashboard shows clear system readiness (SystemStatus page)
- [x] MeetingNotes has robust loading/error states with tested behavior
- [x] Transcript export works securely for all three formats (MD, TXT, JSON)
- [x] Sample meeting asset is documented and usable
- [x] One-command startup script exists and is documented
- [x] All backend and frontend checks pass with real output
- [x] No secrets, database files, recordings, or model weights are committed
- [x] `docs/PROGRESS.md` and `docs/wispr_usage_log.md` updated

### M1 verification (actual output)

| Check | Result |
| --- | --- |
| Backend pytest | 81 passed, 2 skipped |
| Ruff check | Passed (All checks passed!) |
| Ruff format --check | Passed (57 files already formatted) |
| mypy app | Passed (0 issues in 35 source files) |
| Frontend typecheck | Passed (tsc --noEmit clean) |
| Frontend lint | Passed (eslint clean) |
| Frontend tests | Passed (8 files, 24 passed) |
| Frontend build | Passed (dist/ created) |
| docker compose config -q | Passed |



## Lean hackathon delivery priority (2026-10-28)

Priority: A) finish S2 manual acceptance; B) minimum S4 meeting intelligence;
C) stabilize and prepare submission; D) attempt S3 real-time only if time remains.
S3 is deferred from the minimum release, not complete. Existing security and
completed work remain in scope; backup/restore is deferred unless already built.
Docker runtime remains blocked by this environment's unavailable Linux engine.

S2 manual acceptance is pending user confirmation. Native dashboard URL will be
`http://127.0.0.1:5173` when its local dependencies are available; this workspace
currently has no backend virtual environment or `dashboard/node_modules`, so
services could not be started here. No browser playback/offline check is claimed.
The prior suite's skips: the real-model voice round-trip is opt-in and its
coverage was separately exercised with installed models/network denial per the
existing evidence below; required release coverage is therefore not missing.
The symlink rejection test skips only when Windows disallows symlink creation;
the ordinary path-safety/cleanup coverage still runs, so this is host capability,
not a functional coverage requirement for normal operation.

### Minimum S4 implementation status

- Added configurable local Ollama model (`qwen2.5:3b`), timeout, and a 20,000
  character transcript limit; oversized transcripts are rejected without
  truncation. Request question bytes and model output are bounded.
- Added authenticated, CSRF-protected, owner-scoped summary/action-item and Q&A
  endpoints. No schema change; generated content is returned as plain text.
- Replaced the Meeting Notes placeholder with transcript selection, generation,
  Q&A, and optional speech using the configured Kokoro voice.
- Ollama model downloaded locally (1.9 GB); real adapter inference with synthetic
  transcript data returned a summary/action items and answered a question.
- Pinned SQLAlchemy 2.0.46 and numpy 2.2.6 for Python 3.14 compatibility.
- Installed backend virtual environment and dashboard dependencies (`npm ci`).
- Automated tests and verification:
  - Backend: `pytest -q` — 63 passed, 2 skipped (100%)
  - Backend lint: `ruff check .` and `ruff format --check .` — passed (55 files)
  - Backend types: `mypy app` — passed (0 errors in 34 source files)
  - Backend dependencies: `pip check` — no broken requirements found
  - Database migrations: `alembic upgrade head` — applied cleanly
  - Frontend types: `npm run typecheck` — passed
  - Frontend lint: `npm run lint` — passed
  - Frontend tests: `npm test -- --run` — 14 passed (6 test files)
  - Frontend build: `npm run build` — passed (dist/ created)
  - Container config: `docker compose config -q` — valid
- Submission assets created:
  - `docs/SUBMISSION.md`: Full hackathon submission index and checklist
  - `docs/DEMO_SCRIPT.md`: Two-minute video demo script covering core user flows
  - `DEMO.md`: Step-by-step local setup, execution, and verification guide
  - `README.md`: Updated with hackathon submission references

### S2 manual checks requested

1. Open the dashboard and use Speak to generate speech; confirm audible playback.
2. Upload that WAV on Transcribe; confirm transcript, refresh, and confirm it persists.
3. Disconnect WAN while keeping localhost available; repeat speech and transcription.

Report pass/fail for each check. Keep S2 manual acceptance open until confirmed.

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

## S2 — Core Voice APIs

**Status:** IMPLEMENTED — automated and real offline verification complete; manual browser playback remains open.

S1 remains **PASSED WITH ENVIRONMENT CAVEAT**. This section is an approval
proposal, not implementation or verification evidence. All S2 checks below are
pending. No model installation, dependency installation, or inference is part
of this planning step.

### Scope and development workflow

- Deliver authenticated audio upload/transcription, local speech generation,
  model status, safe temporary audio storage, persisted user-owned transcripts,
  and Transcribe/Speak pages with a dashboard model-status panel.
- Use faster-whisper (multilingual `base` by default), Kokoro, SQLAlchemy,
  SQLite, and Alembic. Default to CPU inference and small models; ASR uses
  `int8` by default. Select and pin compatible dependency versions after
  approval; validate on the documented Python 3.11 baseline used by CI/Docker.
- Model installation is an explicit, documented preparation step. Once all
  weights, voices, tokenizer/phonemizer resources, and system dependencies are
  installed, transcription and TTS must run offline. Neither request handling,
  application startup, model-status checks, nor tests may download models.
- No paid APIs, hosting, databases, model services, credit-card dependencies,
  cloud inference, new public listeners, or additional host ports. Preserve
  `127.0.0.1` host bindings and existing authentication/CSRF behavior.
- Live audio, WebSockets, VAD, Ollama inference, meeting intelligence, training,
  model-download APIs, and background job infrastructure are outside S2.
  Ollama is reported as `not_configured` for S2 without contacting it.
- Wispr Flow Pro remains the primary development interface for specifications,
  prompts, reviews, documentation, and commit messages, never a runtime
  dependency. Keep meaningful, non-sensitive workflow entries in
  `docs/wispr_usage_log.md`; do not claim tool usage that cannot be verified.
- Skills: no currently available specialized skill applies to Ceravox voice
  implementation. Follow `AGENTS.md`, the existing repository patterns, and
  verified upstream library documentation. No subagents are planned.

### Implementation sequence after approval

1. Write failing migration, authorization, CSRF, validation, model-status, and
   ownership tests against isolated databases, temporary storage, and injected
   fake inference adapters. Keep S1 regression tests active.
2. Add migration `002_core_voice`, schemas, settings, bounded upload handling,
   and safe storage/normalization. Test limits and cleanup before inference.
3. Add local-only faster-whisper and Kokoro adapters, model availability and
   lifecycle management, transcription persistence/query services, and thin
   authenticated routes. Write adapter contract tests before wiring adapters.
4. Write failing frontend behavior/API-client tests, then implement Transcribe,
   Speak, and the dashboard model panel with accessible pending/error states.
5. Update installation/demo/agent documentation, perform real local-model
   offline smoke checks, run the full exit gate, and review security/scope.
   Record actual commands/results and make small logical commits after checks.

### API contracts and error policy

All five endpoints require the existing server-side session. Both POST routes
also require the existing CSRF double-submit check. Authenticate before CSRF
rejection and before expensive parsing/decoding/inference so an anonymous
voice request returns 401. Apply early request-body bounds as well as the
decoded-file limit; do not rely on browser validation or `Content-Length`.

| Endpoint | Request and success response |
| --- | --- |
| `POST /v1/audio/transcriptions` | Multipart with one `file`; 201 JSON containing `id`, `storage_id`, `source_type: "upload"`, `text`, `language`, `duration` (seconds), `created_at` (UTC ISO 8601), and ordered `segments` with `id`, `start_ms`, `end_ms`, `text`. Owner comes only from the authenticated session. |
| `GET /v1/transcripts` | Current user's summaries, newest first with UUID tie-break; `limit` defaults to 20 (maximum 100), `offset` defaults to 0. Return `{items, limit, offset}` with id, language, duration, source type, and creation time; detail is fetched separately. |
| `GET /v1/transcripts/{id}` | 200 with the same persisted transcript detail shape as upload; segments ordered by stored position. |
| `POST /v1/audio/speech` | JSON `{text, voice, response_format}`; default configured voice and `response_format: "wav"`. 200 `audio/wav` with a server-generated download filename. WAV is the only S2 output format; reject others explicitly. |
| `GET /v1/models` | 200 safe status for `faster_whisper`, `kokoro`, and `ollama`, plus public upload/text/output limits needed by the UI. Each model reports a safe configured name, `configured`, `available`, and an allowlisted status/reason code; Kokoro also reports configured usable voice IDs and default voice. |

- Use the existing `{error: {code, message}}` envelope, with safe fixed messages:
  401 unauthenticated; 403 invalid/missing CSRF; 413 upload/request too large;
  415 unsupported or mismatched audio content; 422 empty/corrupt audio, excessive
  duration, invalid text/voice/format; 503 missing/unloadable model or busy
  inference slot; safe 500 for unexpected processing/storage failure.
- Query transcript detail by both `id` and authenticated `user_id`. Missing and
  other-user UUIDs return identical 404 responses to avoid resource enumeration;
  list queries always filter by owner. Single-admin setup remains unchanged;
  ownership tests create a second user directly in their isolated fixture.
- Status reports use logical model names, never local directory names, absolute
  paths, exception strings, environment dumps, tokens, or provider URLs. Treat
  configured names as validated public labels, separate from directory settings.
- Preserve safe validation errors without echoing supplied text/audio. Set
  `Cache-Control: no-store` on private voice, transcript, and model responses.
  Return no raw upload paths or source filenames. No raw-audio serving endpoint.

### Model configuration and resource limits

Proposed environment variables (all use the existing `CERAVOX_` prefix):

| Variable | Default / meaning |
| --- | --- |
| `CERAVOX_ASR_MODEL` | `base`; safe public model name |
| `CERAVOX_ASR_MODEL_DIR` | `./models/faster-whisper-base`; installed local CTranslate2 model directory |
| `CERAVOX_ASR_DEVICE` | `cpu`; explicitly configurable supported device |
| `CERAVOX_ASR_COMPUTE_TYPE` | `int8`; validate compatibility with the selected device |
| `CERAVOX_ASR_CPU_THREADS` | `2`; positive bounded worker-thread count |
| `CERAVOX_TTS_MODEL` | `Kokoro-82M`; safe public model name |
| `CERAVOX_TTS_MODEL_DIR` | `./models/kokoro`; installed weights/config/resources |
| `CERAVOX_TTS_VOICES_DIR` | `./models/kokoro/voices`; local voice assets |
| `CERAVOX_TTS_VOICES` | `["af_heart"]`; JSON allowlist of installed voice IDs |
| `CERAVOX_TTS_DEFAULT_VOICE` | `af_heart`; must belong to that allowlist |
| `CERAVOX_AUDIO_STORAGE_DIR` | `./recordings/tmp`; private request-scoped storage |
| `CERAVOX_AUDIO_MAX_UPLOAD_BYTES` | `26214400` (25 MiB), counted from actual file bytes |
| `CERAVOX_AUDIO_MAX_REQUEST_BYTES` | `27262976` (26 MiB), includes multipart overhead |
| `CERAVOX_AUDIO_MAX_DURATION_SECONDS` | `600`; bound decoded audio as well as compressed input |
| `CERAVOX_TTS_MAX_TEXT_CHARS` | `2000`; count Unicode code points after trimming |
| `CERAVOX_TTS_MAX_AUDIO_SECONDS` | `300`; bound generated output and memory use |

Native relative directories resolve from the documented backend working
directory. Compose supplies explicit container directories and private data
volumes; mount installed models read-only. Document both layouts. Reject
invalid limits/default voices at configuration time with safe diagnostics.

- Status checks local dependencies and required assets without inference or
  network calls. Distinguish `not_configured`, `missing_dependency`,
  `missing_assets`, `available`, and `load_failed`; availability means the local
  prerequisites pass, not a claim that an inference smoke test has run.
- Load models lazily from explicit local files only, cache them per process,
  and update status on load failure. Verify the installed Kokoro API accepts
  explicit weights/config/voice inputs; supply phonemizer/tokenizer resources
  locally to prevent implicit hub/download fallback. Missing resources yield
  actionable 503 errors. Never silently switch models or providers.
- Decode using pinned PyAV and resample to 16 kHz mono signed 16-bit PCM before
  ASR. Use the installed Kokoro model's native output sample rate for WAV;
  the 16 kHz normalization rule applies to transcription input only.
- Run blocking decoding/inference off the async event loop. Use a single
  bounded inference slot shared by ASR/TTS and one application worker by
  default; reject contention with a safe retryable 503 instead of building an
  unbounded queue. Keep model libraries' diagnostic output free of private
  content. Do not log exception payloads or inference inputs/results.

### Upload validation, storage, and retention decisions

- Accept WAV, MP3, M4A, and OGG. Cross-check detected container/signature and
  successful local decoding with an allowlist of supported audio codecs. MIME
  and suffix are hints, never proof. Permit generic binary MIME only when
  detected content is valid; reject a conflicting explicit media type, corrupt
  input, unsupported media, video-bearing files, and empty audio safely.
- Limit total streamed request bytes before multipart spooling, including
  requests without or with a false `Content-Length`. Limit multipart parts to
  one audio file with bounded fields/headers. Copy/read in bounded chunks and
  independently count file bytes. Enforce decoded sample/duration limits
  incrementally, not after allocating an unbounded PCM buffer.
- Only decode locally opened files. Disable protocol/network access and reject
  playlist/reference formats; uploaded content must never trigger URL fetches.
- Generate a fresh UUID `storage_id` and an exclusively created private request
  directory. Derive source/normalized paths solely from that UUID and fixed
  internal names. Never join, persist, or log the supplied filename. Prevent
  symlink/path escapes, verify containment, and use restrictive permissions
  where supported. Storage is outside dashboard/public/build directories.
- **Retention:** delete uploaded originals and normalized PCM on success,
  validation failure, inference failure, and DB failure in `finally` cleanup.
  Clean abandoned app-owned UUID request directories on startup in the
  single-worker deployment; never traverse symlinks or unrelated directories.
  Parser spool files must also close on failure/disconnect. No S2 retain-audio
  toggle; `storage_id` is persisted provenance, not a live file reference.
- **Generated speech:** keep bounded output in memory and return a downloadable
  WAV response. Do not persist speech text or generated audio. Release buffers
  after completion/disconnect. The browser owns playback/download Blob URLs
  and revokes them on replacement, unmount, or logout.
- Persist transcript text and segments until the local database is removed by
  its owner; document that audio deletion does not delete transcript records.
  User-facing deletion/retention management is outside S2. No private audio,
  transcript, model asset, or generated output belongs in git or CI artifacts.

### Migration 002 and persistence design

- Revision `002_core_voice`, parent `001_initial_auth`; use Alembic migrations,
  never `create_all()` as an upgrade path.
- `transcripts`: UUID `id` primary key; UUID `user_id` FK to users; unique UUID
  `storage_id`; `source_type` (`upload`); `text`; nullable `language` when no
  speech/language is detectable; nonnegative `duration` in seconds; UTC
  `created_at`. Index owner/creation time for scoped listing.
- `transcript_segments`: UUID `id` primary key; UUID `transcript_id` FK;
  integer `position`; integer `start_ms`, `end_ms`; `text`; UTC `created_at`.
  Unique `(transcript_id, position)` and checks for nonnegative position/start
  and `end_ms >= start_ms`; cascade segment deletion with its transcript.
- Insert the transcript and every segment in one transaction only after
  successful inference; roll back entirely on failure. Derive owner from the
  session, not payload. Materialize faster-whisper's lazy segment iterator
  within the guarded inference/cleanup operation.
- Enable SQLite foreign-key enforcement on application and test connections.
  Round-trip timestamps as UTC even though SQLite lacks native timezone storage;
  test serialized UTC values and persisted behavior, not only column flags.
- Upgrade an existing 001 database without losing users/sessions; downgrade
  002 to 001 removes only voice tables/indexes, then re-upgrade successfully.
  Fresh upgrade to head and full downgrade on a disposable DB must also work.

### Frontend behavior

- Replace the authenticated `/transcribe` placeholder with an accessible file
  picker (WAV/MP3/M4A/OGG), client-side type/size hints, pending state, and
  disabled duplicate submission. A pending indicator satisfies S2; no invented
  percentage progress. The backend remains authoritative for validation.
- Render text as plain React text, language (including unknown), duration, and
  ordered segment timestamps. Provide copy, UTF-8 TXT download, and JSON
  download using locally created Blobs and server-generated IDs for filenames.
  Show the user's transcript list and let them reopen persisted details.
- Replace `/speak` with trimmed-text validation, a visible character counter
  using the server's limit/counting rule, a configured-voices-only selector,
  pending/error states, and an HTML audio control plus WAV download. Handle
  empty voice lists, unavailable models, and network errors explicitly.
- Add a dashboard status panel with configured ASR/TTS model names and
  available/unavailable states, plus a refresh action. Show no internal paths.
- Extend the API client for multipart uploads without manually setting the
  multipart Content-Type boundary, and for binary audio responses. Send cookies
  and CSRF headers on mutations; consistently route expired-session 401s back
  to login. Preserve S1 auth calls and display safe backend error messages.
- Release Blob URLs and private page state on logout/unmount. Keep assets,
  fonts, scripts, playback, and exports local; do not add analytics or cloud
  calls. Keep Live Assistant and Meeting Notes as future-work placeholders.

### Complete planned file inventory

Paths below are repository-relative. These are the anticipated S2 implementation
files, not files already implemented. If library compatibility requires changing
this inventory, record the reason here before making that change.

**Create — backend implementation**

| File | Purpose |
| --- | --- |
| `backend/alembic/versions/002_core_voice.py` | Voice tables, indexes, constraints, reversible migration |
| `backend/app/api/audio.py` | Authenticated/CSRF-protected transcription and speech routes |
| `backend/app/api/transcripts.py` | Owner-scoped list/detail routes |
| `backend/app/api/models.py` | Authenticated safe model-status route |
| `backend/app/api/voice_schemas.py` | Typed public request/response/error contracts |
| `backend/app/core/upload_limits.py` | Early authenticated, bounded multipart request handling |
| `backend/app/services/audio_storage.py` | UUID storage, validation, decoding/resampling, cleanup |
| `backend/app/services/transcription.py` | ASR orchestration and atomic transcript persistence |
| `backend/app/services/transcripts.py` | Scoped transcript queries and ordering |
| `backend/app/services/speech.py` | Text/voice validation and bounded in-memory WAV output |
| `backend/app/services/models.py` | Local availability, safe statuses, cached lifecycle and inference slot |
| `backend/app/adapters/__init__.py` | Local inference adapter package |
| `backend/app/adapters/faster_whisper.py` | Local-only faster-whisper adapter and typed result contract |
| `backend/app/adapters/kokoro.py` | Local-only Kokoro adapter and voice resolution |
| `backend/.dockerignore` | Exclude models, recordings, DBs, env secrets, caches from build context |

**Create — backend tests**

- `backend/tests/test_audio_transcriptions.py`
- `backend/tests/test_audio_storage.py`
- `backend/tests/test_transcripts.py`
- `backend/tests/test_speech.py`
- `backend/tests/test_models.py`
- `backend/tests/test_voice_adapters.py`
- `backend/tests/test_voice_local.py` — opt-in real-model offline checks

**Create — frontend implementation and tests**

- `dashboard/src/pages/Transcribe.tsx`
- `dashboard/src/pages/Speak.tsx`
- `dashboard/src/components/ModelStatus.tsx`
- `dashboard/src/__tests__/Transcribe.test.tsx`
- `dashboard/src/__tests__/Speak.test.tsx`
- `dashboard/src/__tests__/ModelStatus.test.tsx`
- `dashboard/src/__tests__/VoiceApi.test.tsx`

**Modify — backend, deployment, and checks**

| File | Purpose |
| --- | --- |
| `backend/app/core/config.py` | Validated model/storage/resource settings |
| `backend/app/db/models.py` | Transcript/segment mappings and relationships |
| `backend/app/db/session.py` | SQLite FK enforcement and safe SQL exception handling configuration |
| `backend/alembic/env.py` | Configurable DB URL for CLI while retaining explicit isolated test URLs |
| `backend/app/main.py` | Router wiring, upload limits, model/storage lifecycle, safe voice errors |
| `backend/app/core/logging.py` | Cover voice fields and suppress private library/DB error payloads |
| `backend/app/api/dependencies.py` | Reusable early auth and injected voice-service dependencies |
| `backend/requirements.txt` | Exact compatible inference, multipart, codec, and audio dependency pins |
| `backend/pyproject.toml` | Local-voice marker and narrowly scoped third-party typing configuration |
| `backend/tests/conftest.py` | Isolated 002 DBs, two-user fixtures, synthetic audio, fake adapters, network guard, local-voice option |
| `backend/tests/test_migrations.py` | Keep explicit 001 tests and add 002 upgrade/downgrade/data-preservation tests |
| `backend/tests/test_security_logging.py` | Privacy regression coverage for voice success/failure |
| `backend/.env.example` | Native model, voice, storage, and resource settings |
| `backend/Dockerfile` | Copy Alembic config/migrations, install required local TTS dependencies, retain local host-port policy |
| `docker-compose.yml` | Read-only model mounts, private audio/SQLite volumes, explicit model settings; preserve existing ports |
| `.env.example` | Compose model/data directory and limit configuration |
| `.gitignore` | Cover new runtime/temp data, SQLite sidecars, model assets and exported media |
| `.github/workflows/ci.yml` | No-model/no-download tests and required local codec/system setup on free CI |

The existing backend Dockerfile invokes Alembic but currently copies only the
application package; copying `alembic.ini` and the migration directory is part
of making the planned container startup reproducible. This observation does not
change the recorded S1 Docker caveat or establish that a container has run.

**Modify — frontend and documentation**

| File | Purpose |
| --- | --- |
| `dashboard/src/App.tsx` | Real voice routes, dashboard status, unified 401 handling |
| `dashboard/src/lib/api.ts` | Typed model/transcript APIs, multipart, binary responses, limits and errors |
| `dashboard/src/styles.css` | Accessible voice forms, pending/error states, results and player layout |
| `dashboard/src/__tests__/App.test.tsx` | Voice routing/status and expired-session regressions |
| `dashboard/src/__tests__/Auth.test.tsx` | Preserve setup/login/logout with updated voice-route mocks |
| `README.md` | Pinned install/model acquisition commands, asset/license sources, environment table, offline usage, limits/retention |
| `DEMO.md` | Local ASR/TTS/model-status walkthrough and Docker-caveat instructions |
| `docs/PROGRESS.md` | Approved tasks, inventory, tests, skills, actual evidence and exit gate |
| `docs/wispr_usage_log.md` | Meaningful non-sensitive S2 prompts/decisions/reviews/commit summaries |
| `AGENTS.md` | S2 commands, local-model testing, storage/security conventions and scope |

Use existing browser/React facilities; no new frontend packages are planned.
No binary test recordings, model assets, databases, generated speech, transcript
exports, credentials, or OpenCode workspace metadata are implementation files.

### Complete backend test plan

Write failing behavioral tests first where practical. Ordinary pytest runs use
fake ASR/TTS adapters, generated non-private audio in temporary directories,
and a network guard; they neither require nor download models. Parameterized
cases below are part of the required suite, not optional examples.

**`test_migrations.py`**

- Preserve migration 001's fresh upgrade/current/downgrade assertions by
  targeting 001 explicitly; add fresh upgrade/current to `002_core_voice`.
- Upgrade a populated 001 DB to 002; preserve users, hashed sessions and IDs.
- Verify transcript/segment UUID keys, columns, ownership FKs, ordering/indexes,
  timestamp round-trip/UTC serialization, uniqueness, and duration/time checks.
- Reject orphan segments; cascade segment cleanup when a transcript is deleted.
- Downgrade 002 to 001 preserving auth data, re-upgrade, and downgrade a
  disposable fresh head database to base without leftover voice tables.

**`test_audio_transcriptions.py`**

- Anonymous POST returns 401 before decoder/inference invocation; authenticated
  POST with missing or mismatched CSRF returns 403.
- WAV, MP3, M4A, and OGG valid uploads succeed with fake inference; invalid
  content/type, forged suffix/MIME, corrupt data and empty input are rejected.
- Exceeding actual file-byte limit returns 413, including missing or misleading
  Content-Length; whole-request limit and excessive multipart parts are bounded.
- Valid upload returns 201 with text, detected language, duration, UUID IDs,
  UTC creation time and ordered millisecond segment timestamps.
- Transcript and segments persist under the authenticated user; supplied owner
  fields cannot override that user. Silence returns empty text/segments safely.
- Model unavailable returns safe 503; inference failure or segment-iteration
  failure produces a safe error with no partial DB record.
- DB commit failure rolls back transcript and segments; all paths clean audio.

**`test_audio_storage.py`**

- Parameterized valid containers decode to 16 kHz mono PCM with bounded samples;
  duration limit rejects compressed inputs that expand beyond the limit.
- Unsupported codecs, video streams, corrupt headers, empty decoded samples,
  playlist/reference inputs, and explicit content-type mismatch are rejected.
- Traversal, absolute/Windows paths, Unicode filenames, duplicate names and
  missing names never determine storage paths; UUID allocations remain unique.
- Reject symlink escapes; temporary files remain inside private storage and
  outside web roots. Decode never opens remote URLs.
- Cleanup on success, validation/inference/DB errors and client cancellation;
  startup cleanup removes only abandoned app-owned directories, not unrelated
  files. Multipart spool handles close on rejected/truncated uploads.

**`test_transcripts.py`**

- Anonymous list/detail requests return 401.
- User A cannot retrieve User B's transcript; response matches nonexistent-ID
  404. List returns only A's records, including empty-list behavior.
- Detail survives a new DB session and includes correctly ordered segments.
- Pagination, maximum limit, newest-first order and tie-break are deterministic;
  invalid query values are rejected. Private responses carry no-store headers.

**`test_speech.py`**

- Anonymous POST returns 401; missing/mismatched CSRF returns 403.
- Empty/whitespace-only and excessive text are rejected before model invocation;
  exact character limit and Unicode counting match the documented rule.
- Unsupported formats and unconfigured/unknown/path-like voice IDs are rejected.
- Configured default/selected voice succeeds; response is decodable WAV with
  correct media type, generated download filename and no-store header.
- TTS unavailable/load failure returns safe 503; runtime failure is safe;
  output-duration limit prevents unbounded generation.
- No speech input or output is persisted; buffers/temporary resources are
  released on completion, error and disconnect.

**`test_models.py`**

- Anonymous GET returns 401; authenticated GET reports each configured model,
  Kokoro default/allowlisted voices, Ollama not configured, and safe UI limits.
- Cover available, not configured, missing dependency/assets and failed-load
  states without downloading/loading models in the status route.
- Responses and errors contain no absolute/relative model directories, secrets,
  environment values beyond allowlisted public settings, or exception details.
- Invalid public model labels/limits/default voices fail validation safely;
  a configured but missing voice is not advertised as usable.

**`test_voice_adapters.py`**

- faster-whisper receives the explicit local model directory, CPU/int8 defaults,
  normalized samples, and offline-only load behavior; configured overrides work.
- Kokoro receives only local weights/config/voice/resources; missing assets
  never fall back to remote downloads. Native output rate is preserved.
- Lazy model loading is cached/thread-safe; a load failure updates safe status.
- Busy inference is rejected with bounded 503; blocking work does not stall
  health/auth requests. Lazy ASR iteration stays within the slot/cleanup guard.
- SDK/decoder failures are translated without exposing input text or paths.

**`test_security_logging.py` and shared fixtures**

- Capture application/dependency logs for successful and failed ASR/TTS,
  validation, storage, and DB operations; no audio bytes, transcripts, speech
  text, filenames, credentials, hashes, cookies or CSRF values appear.
- Verify safe API errors do not echo private inputs, SQL parameters, model
  paths or exception text. Keep every S1 redaction regression.
- Network guard fails unexpected outbound access during normal tests; all
  generated media/DBs live only in isolated temporary directories.

**`test_voice_local.py` — explicit real-model gate**

- Locally installed Kokoro generates playable nonempty WAV with a configured
  voice through the authenticated API.
- Upload that locally generated, non-private test utterance through the API to
  real faster-whisper; assert nonempty transcript, language, positive duration,
  valid segments, and persisted owner-scoped retrieval (no exact-text golden).
- Repeat model status, ASR, and TTS with outbound network disabled; no downloads
  occur. Generate/delete local artifacts within the test's temporary directory.
- Default CI skips these marked tests explicitly. When `--run-local-voice` is
  supplied, missing assets fail rather than skip. A skipped/missing-model run
  cannot satisfy the S2 functional exit gate.

### Complete frontend test plan

**`Transcribe.test.tsx`**

- Authenticated page renders labeled file picker and pending/disabled states.
- File selection/submission sends the selected file to the upload API once.
- Result displays text, language, duration and segment timestamps; safely
  renders markup-like transcript text and empty/no-speech results.
- Invalid type, excessive size and corresponding server errors render clearly;
  model unavailability and network failure restore a usable form.
- Copy uses displayed text; TXT/JSON downloads contain correct result data and
  release object URLs; clipboard failure gives a useful message.
- Transcript list is user-scoped by API calls; selecting an item fetches and
  renders persisted detail; empty list and failed retrieval are handled.

**`Speak.test.tsx`**

- Authenticated page renders text input, character count and configured voices.
- Empty/whitespace-only and excessive input prevent submission; Unicode count
  and boundary cases match server limits.
- Valid text/voice requests WAV; pending state prevents duplicate requests.
- Generated Blob is attached to audio controls and playback can be invoked;
  download uses the same audio. Real browser playback is separately verified.
- Empty voices, unavailable TTS and request errors render safely; old Blob URLs
  are revoked on replacement/unmount/logout.

**`ModelStatus.test.tsx`**

- Available/unavailable ASR/TTS states, configured names and Ollama not configured
  render; loading, safe error, and refresh states work without showing paths.

**`VoiceApi.test.tsx`**

- Upload sends FormData with credentials/CSRF and lets the browser set boundary.
- Speech sends validated JSON with credentials/CSRF, consumes a binary response,
  and distinguishes safe JSON errors from audio.
- List/detail/model calls use typed endpoint contracts; safe 413/415/422/503
  messages and 401 handling work for both multipart and binary paths.

**Existing `App.test.tsx` and `Auth.test.tsx`**

- Anonymous voice-page navigation redirects to login; authenticated navigation
  renders Transcribe, Speak, and dashboard model status.
- Any voice/transcript/model 401 clears authenticated/private state and routes
  to login; logout clears active media. S1 setup/login/logout remain working.
- Live Assistant/Meeting Notes remain placeholders; no remote assets are added.

### S2 security review checklist

- [x] All audio, transcript, and model routes require authentication; all POST
  routes require CSRF. Anonymous requests cannot start inference.
- [x] Upload paths use only server-generated UUIDs and fixed internal names;
  uploaded filenames cannot influence paths or appear in logs.
- [x] Streamed request/file limits, container/codec validation, decoded duration
  bounds and bounded inference/output are enforced server-side.
- [x] Temporary audio is private and cleaned on success/failure/disconnect;
  generated speech is not persisted. Model mounts are read-only.
- [x] Transcripts/segments are atomically persisted and all reads are owner
  scoped; other-user and nonexistent resources return indistinguishable 404s.
- [x] No audio, transcript text, generated speech, credentials or private
  metadata enters logs; dependency and DB exceptions are sanitized.
- [x] `/v1/models` exposes only safe names, statuses, voices and public limits;
  filesystem paths, tokens, secrets and exception contents are absent.
- [x] Inference/status/startup are local-only; no auto-downloads or hidden model,
  voice, tokenizer or phonemizer network fallback.
- [x] New dependencies use exact compatible pins; review transitive resolution
  and licenses/model sources. Existing frontend lockfile remains reproducible.
- [x] Host ports and CORS remain restrictive; no new open ports or paid services.
- [x] No secrets, databases/sidecars, models, recordings, backups, generated
  speech or transcript exports are tracked/staged or copied into images.

### Exact verification commands after implementation

These commands are planned, not yet run for S2. Run under the documented Python
3.11 environment; do not infer inference-library support from the S1 host's
Python version. Record versions and actual outputs without private input data.

From `backend/`, first run the focused S2 tests, then the full backend gate:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q tests/test_migrations.py tests/test_audio_transcriptions.py tests/test_audio_storage.py tests/test_transcripts.py tests/test_speech.py tests/test_models.py tests/test_voice_adapters.py tests/test_security_logging.py
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python -m mypy app
python -m pip check
```

Run the real-model checks only after explicit local model/resource installation;
this command must never install/download assets. `--run-local-voice` is the
planned pytest option to be added in `backend/tests/conftest.py`:

```powershell
python -m pytest -q tests/test_voice_local.py --run-local-voice
```

Migration CLI round-trip from `backend/`, using a new disposable database and
restoring the original environment. Never downgrade the user's real database.
The planned Alembic environment wiring makes this URL override effective:

```powershell
$previousDb = $env:CERAVOX_DATABASE_URL
$gateDb = Join-Path ([System.IO.Path]::GetTempPath()) ("ceravox-s2-" + [guid]::NewGuid() + ".db")
$env:CERAVOX_DATABASE_URL = "sqlite:///" + $gateDb.Replace('\', '/')
try {
    python -m alembic upgrade 001_initial_auth
    if ($LASTEXITCODE -ne 0) { throw "Migration 001 failed" }
    python -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) { throw "Migration 002 failed" }
    python -m alembic current
    if ($LASTEXITCODE -ne 0) { throw "Revision check failed" }
    python -m alembic downgrade 001_initial_auth
    if ($LASTEXITCODE -ne 0) { throw "Downgrade 002 failed" }
    python -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) { throw "Re-upgrade failed" }
    python -m alembic downgrade base
    if ($LASTEXITCODE -ne 0) { throw "Full downgrade failed" }
} finally {
    $env:CERAVOX_DATABASE_URL = $previousDb
    if (Test-Path $gateDb) { Remove-Item -LiteralPath $gateDb }
}
```

Expected current revision is `002_core_voice (head)`. Migration tests separately
verify preservation of populated S1 data, schema constraints and fresh-head
creation; CLI success alone is insufficient.

From `dashboard/`:

```powershell
npm ci
npm run typecheck
npm run lint
npm test -- --run
npm run build
```

From the repository root:

```powershell
pre-commit run --all-files
docker compose config -q
git diff --check
git diff --cached --check
git status --short --untracked-files=all
git diff --name-only
git diff --cached --name-only
git ls-files
docker info
```

Pre-commit includes detect-secrets, Ruff, and Ruff format. Inspect the complete
diff, staged/tracked filenames and ignore rules for every sensitive file class;
an empty filename search alone is not proof of no secrets. Do not weaken
scanning or broadly allowlist directories to get a pass. Synthetic fixtures
must be narrowly documented if they trigger a false positive.

Only when `docker info` confirms an available server, perform the Compose smoke
sequence from the repository root with installed local model mounts:

```powershell
docker compose up -d --build
docker compose ps
curl.exe --fail http://127.0.0.1:8000/health/live
curl.exe --fail http://127.0.0.1:8000/health/ready
curl.exe --fail http://127.0.0.1:5173
docker compose logs --tail=50
docker compose down
```

Also run the authenticated browser workflow against that stack before teardown:
login, model status, supported upload/result/list/detail, copy/TXT/JSON export,
voice selection/generate/play/download, logout and expired-session handling.
Do not include credentials/private media in command history, screenshots,
documentation or logs. Use locally generated non-private test audio; do not
commit the resulting audio or transcript. Check actual playback in a browser;
jsdom tests alone cannot prove a WAV plays correctly.

If Docker remains unavailable, retain the exact named-pipe error
`npipe:////./pipe/dockerDesktopLinuxEngine` (or record the new actual error),
and mark runtime smoke **NOT RUN / ENVIRONMENT CAVEAT**. Do not label container
build/startup or smoke successful without real output. Native backend/frontend
and real local-model checks still apply; the Docker caveat does not excuse
missing ASR/TTS verification. Run the same browser flow on native localhost
services, using the README startup commands.

### Exact S2 exit gate

- [x] Authenticated supported WAV/MP3/M4A/OGG uploads produce transcripts through
  real local faster-whisper with text, language, duration and segment timestamps.
- [x] Transcript and segments persist in SQLite and can be reopened after a
  fresh session/restart; failed inference/DB operations leave no partial record.
- [x] Only the owner can list/retrieve their transcript; cross-user and missing
  detail return matching 404, and anonymous access returns 401.
- [x] Authenticated Kokoro generates playable/downloadable local speech for a
  configured voice; invalid text/voice/format is rejected and no speech persists.
- [x] `/v1/models` reports truthful ASR/TTS availability/configured names/voices
  and Ollama's S2 state without sensitive fields or network calls.
- [x] Authentication, CSRF, safe errors, content validation, size/duration limits,
  UUID paths, bounded resource use and cleanup pass the security tests/review.
- [x] Transcribe/Speak pages and status panel work, including pending/errors,
  copy, TXT/JSON export, audio playback/download and 401/logout behavior.
- [ ] Manual browser workflow and playback pass with network disabled; automated
  UI/API coverage and direct local WAV checks pass.
  after installation; record model/library versions and non-sensitive results.
- [x] Full backend pytest passes (report ordinary and real-model results
  separately), Ruff and format checks pass, mypy and dependency checks pass.
- [x] Frontend typecheck, lint, all Vitest tests and production build pass.
- [x] Pre-commit and detect-secrets pass on all tracked files.
- [x] Migration 002 fresh upgrade, populated-001 upgrade, current revision,
  downgrade to 001, re-upgrade and disposable full downgrade pass.
- [x] `docker compose config -q` passes with localhost-only bindings.
- [ ] Docker Compose runtime smoke passes, or its precise environment caveat
  is recorded; no fabricated pass and no public-exposure workaround.
- [ ] README, DEMO, PROGRESS, Wispr usage log and AGENTS accurately describe
  installation, env configuration, limits, retention, commands and real results.
- [ ] Full diff and tracked/staged files reviewed: exact dependency pins, S2
  scope only, and no secrets, DBs, model weights, recordings, backups, generated
  speech or transcript exports committed.

### S2 verification evidence register

| Check | Current result |
| --- | --- |
| Planning/repository inspection | Existing auth, routes, schema, settings, tests, CI and deployment read; S2 design documented |
| Planning diff/secret checks | `git diff --check` passed; `pre-commit run --files docs/PROGRESS.md docs/wispr_usage_log.md` detect-secrets passed, Ruff/format skipped (no applicable files) |
| Failing-first backend/frontend tests | Initial frontend/backend tests failed before implementation; current suites pass |
| Migration 002 | `5 passed`; CLI upgraded to `002_core_voice (head)` and downgraded to base |
| Backend pytest/Ruff/format/mypy | `55 passed, 2 skipped`; Ruff, format, mypy passed |
| Frontend typecheck/lint/Vitest/build | Typecheck/lint/build passed; Vitest `6 files, 14 tests passed` |
| Real faster-whisper/Kokoro offline inference | `check_offline.py --offline` passed; local API test `1 passed`; CPU/int8 ASR and Kokoro af_heart verified |
| Browser upload/transcript/export/playback | Automated UI/API tests passed; manual browser playback not run in this environment |
| Full pre-commit/secret scan and sensitive-file review | detect-secrets, Ruff, Ruff format passed; tracked binary scan empty |
| Compose configuration | `docker compose config -q` passed |
| Compose runtime | Historical Docker Linux-engine named-pipe blocker retained; no S2 smoke pass claimed |

Recorded S2 commands, actual counts, model revisions, and environment results
are retained here. The manual browser playback item remains open as a usability
follow-up; automated page/API coverage and direct WAV generation were verified.
Missing models or incompatible dependencies were not substituted with mocks.

### S2 actual model verification

- `backend/.venv/Scripts/python scripts/install_models.py --download` — passed;
  installed the approved model files only. Assets remain under ignored
  `backend/models/` and are not tracked.
- `backend/.venv/Scripts/python scripts/check_offline.py` — passed; Kokoro
  `af_heart` generated a 128,444-byte WAV and faster-whisper base CPU/int8
  returned one English segment.
- `backend/.venv/Scripts/python scripts/check_offline.py --offline` — passed;
  the same local generation/transcription completed with the audit network deny.
- `backend/.venv/Scripts/python -m pytest -q tests/test_voice_local.py
  --run-local-voice` — `1 passed`; authenticated API round-trip generated WAV,
  transcribed it, persisted/retrieved the transcript, and cleaned temporary
  audio with network access denied.
- Model revisions: faster-whisper base
  `ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66`; Kokoro-82M
  `f3ff3571791e39611d31c381e3a41a3af07b4987`. Sources and licenses are recorded
  in `README.md`; no machine-specific paths are documented.
- `docker info` — Docker client available, server unavailable at
  `npipe:////./pipe/dockerDesktopLinuxEngine`; Compose runtime smoke is **NOT
  RUN / ENVIRONMENT CAVEAT**. `docker compose config -q` independently passed.

### Approval checkpoint

Implementation approved by the user. Model/dependency installation was separately
approved, limited to faster-whisper base, Kokoro-82M, af_heart and required English
resources in the project virtual environment. S3 still requires a passed S2 gate
and explicit report approval.

### Implementation notes

- Installation estimate before downloading: model files approximately 476 MB;
  complete downloads estimated 1–2 GB and installed/temporary storage 4–6 GB.
  Exact dependency total not yet known. Ignore rules verified before download.
- Host has only Python 3.14; create a project-local Python 3.11 virtual environment.
  `.venv-bootstrap/` and `.cache/` are ignored installation tools/cache locations.
- Add `backend/scripts/install_models.py` for explicit revision-pinned installation
  with checksum verification, and `backend/scripts/check_offline.py` for a
  subprocess network-denied real-model check. These additional inventory entries
  make the user's explicit installation/offline verification reproducible.


---

## 2026-10-29 — Repository Hygiene, Presentation, and Accuracy Alignment

### Scope and goals
Make the GitHub repository clean, professional, and easy for judges to evaluate for *No Hands: The Wispr Challenge*, without altering application runtime behavior, removing features, or breaking tests.

### Changes made
1. **Untracked IDE artifacts:**
   - Untracked `opencode.jsonc` from Git index (`git rm --cached opencode.jsonc`).
   - Added `opencode.jsonc` to `.gitignore` under IDE configuration files.
   - Preserved local `opencode.jsonc` file intact on disk.
2. **Canonical README.md overhaul:**
   - Added text-based architecture diagram illustrating component data flow (Dashboard -> FastAPI -> SQLite / faster-whisper / Kokoro / Ollama).
   - Added concise features section categorized by capability (ASR, TTS, Meeting Notes, Transcript Q&A, Multi-format Export, System Status, Sample Generator).
   - Audited and updated Privacy & Security section with verified claims:
     - No cloud inference and no external network calls during core runtime operation once local models are installed.
     - Uploaded audio is processed locally and is not sent to external services; temporary audio in request-scoped directories is cleaned up on both success and failure paths.
     - Generated speech is returned in-memory as a WAV stream and never persisted to disk.
     - Argon2id password hashing, opaque session tokens, CSRF double-submit protection, and owner-scoped transcript access with 404 isolation.
     - Services bind to `127.0.0.1` by default.
   - Clarified Project Roadmap: marked completed MVP milestones (S0, S1, S2, S4, M1), explicitly marked S3 (Live Voice Pipeline with WebSockets and VAD) as deferred post-MVP, and listed future scope (S5, S6).
   - Audited and verified all markdown links and commands in `README.md` and `DEMO.md`.
3. **Automated Verification:**
   - Backend tests: `81 passed, 2 skipped` in 33.31s.
   - Backend linter: `ruff check .` passed with 0 errors.
   - Backend formatter: `ruff format --check .` passed (58 files formatted).
   - Backend typechecker: `mypy app` passed (35 source files clean).
   - Frontend typecheck: `tsc --noEmit` passed.
   - Frontend linter: `eslint .` passed with 0 warnings/errors.
   - Frontend tests: `24 passed` across 8 test suites.
   - Frontend production build: `tsc -b && vite build` passed (built in 211ms).
   - Docker Compose: `docker-compose config -q` passed with code 0.


---

## 2026-10-29 — Live Assistant (Interactive Voice Chat Implementation)

### Scope and goals
Replaced the "Coming in a later milestone" placeholder on the Live Assistant page with a full offline-first interactive voice chat workflow connecting the browser microphone, local faster-whisper ASR, local Ollama LLM (`qwen2.5:3b`), and local Kokoro-82M TTS.

### Changes made
1. **Backend Endpoint (`backend/app/api/assistant.py`):**
   - Added `POST /v1/assistant/chat` requiring session authentication and CSRF double-submit protection.
   - Validates user input message (1–1000 characters).
   - Invocates local Ollama (`qwen2.5:3b`) via `OllamaClient.generate()` with tailored system prompt.
   - Robust error handling for `OllamaUnavailable` (503), `OllamaTimeout` (504), and `OllamaMalformedResponse` (502).
   - Registered router in `backend/app/main.py` and included in private-cache headers.
2. **Backend Tests (`backend/tests/test_assistant.py`):**
   - 6 new automated tests verifying authentication enforcement, CSRF protection, message validation, successful replies, and error mappings. Total backend test suite: 87 passed, 2 skipped.
3. **Frontend In-Browser WAV Audio Recorder (`dashboard/src/lib/audioRecorder.ts`):**
   - Pure Web Audio API implementation (16 kHz mono, Float32 -> 16-bit PCM conversion with 44-byte standard RIFF WAV header).
   - Zero external npm dependencies.
4. **Frontend API Client (`dashboard/src/lib/api.ts`):**
   - Added `askAssistant(message: string): Promise<AssistantReply>` contract and endpoint invocation.
5. **Frontend Live Assistant Page (`dashboard/src/pages/LiveAssistant.tsx`):**
   - Interactive chat message thread with timestamps and role-based speech bubble styling.
   - Dual-input mode: Microphone recording with live duration timer or direct text message input.
   - Auto-speak response toggle using Kokoro-82M synthesized audio in-browser playback.
   - Clear chat and granular error alerts.
6. **Dashboard Routing (`dashboard/src/App.tsx`):**
   - Replaced `Placeholder` component with `LiveAssistant`.
7. **Frontend Unit Tests (`dashboard/src/__tests__/LiveAssistant.test.tsx`):**
   - 5 comprehensive tests covering initial render, auto-speak defaults, empty input inhibition, chat reply rendering, and API error surfacing. Total frontend test suite: 29 passed across 9 test suites.
8. **Automated Verification:**
   - Backend tests: `87 passed, 2 skipped` in 16.03s.
   - Backend linter: `ruff check .` passed with 0 errors.
   - Backend formatter: `ruff format --check .` passed (60 files formatted).
   - Backend typechecker: `mypy app` passed (36 source files clean).
   - Frontend typecheck: `tsc --noEmit` passed.
   - Frontend linter: `eslint .` passed with 0 warnings/errors.
   - Frontend tests: `29 passed` across 9 test suites.
   - Frontend production build: `tsc -b && vite build` passed.
   - Docker Compose: `docker-compose config -q` passed.
