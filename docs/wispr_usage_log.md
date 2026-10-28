# Wispr Flow Usage Log

Record meaningful major product specifications, coding prompts, documentation,
commit messages, architecture decisions, reviews, debugging context, demo
scripts, and submission copy created through Wispr Flow Pro. Wispr Flow Pro is
development-only and is never a Ceravox runtime dependency. Keep private
credentials, passwords, session tokens, raw recordings, transcripts, model
weights, and secrets out of this file and out of Wispr Flow.

| Date | Area | Dictated item | Decision or result |
| --- | --- | --- | --- |
| 2026-10-26 | S0 | Initial foundation task and acceptance criteria | Build a reproducible local skeleton first |
| 2026-10-27 | S1 | Auth and app-shell implementation prompts, test criteria, and documentation updates | Use Alembic, Argon2id, hashed sessions, CSRF, and a protected local shell |
| 2026-10-27 | Workflow | Wispr Flow Pro and project cost policy | Use Flow Pro for the development workflow; keep Ceravox free, local, and offline-capable after model installation |
| 2026-10-27 | S1 implementation | Approved backend and frontend implementation prompt | Write failing tests first; add only local single-admin auth, CSRF, migrations, sessions, and the protected shell |
| 2026-10-27 | S1 review | Security and scope review notes | Confirm Argon2id, hashed sessions, generic errors, CSRF on mutations, restrictive CORS, no runtime voice features, and no sensitive logging |
| 2026-10-27 | Commit | `feat(auth): add Alembic auth persistence and session security`; `feat(shell): add protected Ceravox React app shell`; `docs: close out S1 auth and app-shell milestone` | Keep S1 split into backend, frontend, and documentation increments |
| 2026-10-27 | Review fix | `fix(security): satisfy secret scanning for auth fixtures` | Allowlist only deliberately synthetic auth-test values and preserve password-hash log redaction |
| 2026-10-27 | S2 planning | User-provided Core Voice APIs specification and approval-gated plan; Wispr capture method not independently verified | Document local faster-whisper/Kokoro, temporary audio deletion, owner-scoped transcripts, file/test inventory and exact exit gate; wait for approved before implementation |
| 2026-10-27 | S2 implementation | Approved implementation prompt and local-model installation approval | Install only pinned faster-whisper base, Kokoro-82M, af_heart, and English resources in the project environment; verify offline inference before the S2 gate |
| 2026-10-27 | S2 review | Backend/frontend tests, resource-boundary review, and Docker caveat handling | Keep mocked tests separate from real offline checks; preserve localhost bindings and never claim unavailable Compose runtime success |
| 2026-10-27 | S2 verification | Model installation, offline inference, migration, frontend, pre-commit and secret-scan results | Record only non-sensitive model revisions and command outcomes; leave manual browser playback and Docker runtime caveats explicit |
| 2026-10-28 | S4 Lean Hackathon | Priority pivot: upload audio -> transcript -> summary/action items -> Q&A -> TTS | Focus on lean hackathon delivery: defer S3 streaming, implement S4 meeting intelligence, stabilize stack |
| 2026-10-28 | S4 Implementation | Ollama qwen2.5:3b integration, meeting notes UI, Q&A, and TTS bridge | Local-first inference with strict input bounds, CSRF protection, and zero runtime cloud dependencies |
| 2026-10-28 | Verification & Docs | Full test suite execution, Python 3.14 wheel fixes, submission documentation | 63 backend tests, 14 frontend tests, mypy, ruff, SUBMISSION.md, DEMO_SCRIPT.md |
| 2026-10-28 | M1 Planning | Demo resilience and UX polish: system status endpoint, preflight UI, Meeting Notes error states, transcript export, sample asset, one-command startup | Six tasks planned in priority order; tests written first per TDD convention; awaiting approval before implementation |
| 2026-10-28 | M1 Task 1 | System status endpoint GET /api/system/status implementation and verification | 11 new tests in test_system_status.py, 74 passed total, ruff/format/mypy clean; safe component readiness reported |
| 2026-10-28 | M1 Task 2 | Preflight status UI page and integration | 4 new tests in SystemStatus.test.tsx, 18 passed total, typecheck/lint/build clean; System Status page added to nav |
| 2026-10-28 | M1 Task 3 | Meeting notes loading and error states | 5 new tests in MeetingNotes.test.tsx, 23 passed total; per-action loading indicators, input lockouts during generation, clean retry |
| 2026-10-28 | M1 Task 4 | Transcript export in Markdown, Plain text, and JSON | 7 new backend tests (81 passed), 1 new frontend test (24 passed), safe attachment downloads for owners only |
