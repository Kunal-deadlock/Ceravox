# Ceravox Agent Conventions

## Workflow and cost constraints

- Wispr Flow Pro is the primary development interface for product
  specifications, user stories, architecture decisions, coding prompts, code
  review notes, README/API/DEMO/AGENTS documentation, commit messages, bug
  reports, debugging context, demo-video scripts, and submission copy.
- Continue maintaining `docs/wispr_usage_log.md` with meaningful major prompts,
  documents, decisions, and commit messages.
- Never put passwords, session tokens, private audio, transcripts, model
  weights, credentials, or other secrets into Wispr Flow or repository
  documentation.
- Wispr Flow Pro is development-only and must never become a Ceravox runtime
  dependency.
- Ceravox must remain free to build and run: no paid AI APIs, hosting,
  databases, model services, or credit-card-required dependencies.
- Runtime inference uses local/open-weight components: faster-whisper, Kokoro,
  Silero VAD, and Ollama. Persistence remains SQLite; CI uses the free GitHub
  Actions tier.
- After local models are installed, advertised Ceravox workflows must work
  offline. Do not expose services publicly to work around local limitations.

## S2 commands

Run backend commands from `backend/`:

```powershell
python -m pip install -r requirements.txt
alembic upgrade head
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python -m mypy app
python -m pip check
python scripts/check_offline.py --offline  # after explicit local model install
```

Run dashboard commands from `dashboard/`:

```powershell
npm ci
npm run typecheck
npm run lint
npm test -- --run
npm run build
```

Validate the local stack from the repository root with
`docker compose config -q`. Services must remain bound to `127.0.0.1` on the
host.

## S2 conventions

- Use Alembic for schema changes; never use `create_all()` as an upgrade path.
- Keep routes thin: authenticate, validate, call a service, and return a safe
  response.
- Store Argon2id password hashes and hashed opaque session tokens only.
- Protect every cookie-authenticated mutation with the CSRF double-submit
  check.
- Never log passwords, password hashes, cookies, session tokens, CSRF values,
  audio, transcript text, generated speech, filenames, paths, or private user
  content.
- Require authentication on every voice/model/transcript route and CSRF on every
  voice mutation. Keep transcripts owner-scoped and return indistinguishable
  404s for missing/other-user details.
- Store only UUID provenance for temporary uploads; never use user filenames as
  paths. Delete source/normalized audio in all request paths and never persist
  generated speech.
- Load faster-whisper and Kokoro only from configured local assets. No model,
  voice, tokenizer, phonemizer, cloud, or Ollama download/fallback at runtime.
- Keep audio decoding, inference, request bytes, text, duration, and output
  bounded; use Alembic for schema changes and never `create_all()` for upgrades.
- S2 excludes WebSockets, VAD, live assistant, meeting intelligence, cloud APIs,
  public exposure, and new host ports. S3 requires an approved S2 report.
