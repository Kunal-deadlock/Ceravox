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
