# Phase 01 — Project Scaffolding: Requirements

## Context
This phase has no end-user-facing feature. It builds the skeleton every later phase
(auth, meal logging, voice logging, etc.) will be implemented into: a runnable Streamlit
app, a local Postgres dev environment that mirrors production, Alembic migrations wired up,
and CI. "Users" here are the developer (Claude, in future phases) and the CI pipeline.

## User stories

### 1. Runnable app skeleton
**As a** developer starting phase 02+,
**I want** `streamlit run app.py` to boot a minimal, themed landing page with no errors,
**so that** every later phase adds to a working app instead of bootstrapping one.

**Acceptance criteria**
- Given a clean checkout with dependencies installed, when I run `streamlit run app.py`,
  then the app starts and renders a landing page (app name, one-line description, no
  crash) — no auth, no real feature yet.
- Given the app is running, when I inspect it in a browser, then the custom theme from
  `.streamlit/config.toml` is visibly applied (not Streamlit's default theme).
- Given `pytest` is run, when it collects `tests/test_app_smoke.py`, then an
  `AppTest`-based test confirms `app.py` runs without raising an exception.

### 2. Local dev database matches production engine
**As a** developer,
**I want** a one-command local Postgres instance via Docker Compose,
**so that** I develop against the same engine (Postgres) that Supabase runs in production,
with no SQLite-compatibility shims anywhere in the app.

**Acceptance criteria**
- Given Docker is installed, when I run `docker compose up -d`, then a Postgres container
  starts and is reachable on a documented local port.
- Given the container is running, when the app or a test connects using the local
  connection string, then the connection succeeds.
- Given `docker-compose.yml` is checked in, when a new developer clones the repo, then no
  further manual DB setup is needed to start developing locally.

### 3. Config & secrets access works both inside and outside Streamlit
**As a** developer,
**I want** a single config module that resolves secrets (DB URL, future API keys) the same
way whether the code runs inside `streamlit run` or from a standalone script (Alembic, CI,
pytest),
**so that** later phases don't reinvent secret-loading per module.

**Acceptance criteria**
- Given `.streamlit/secrets.toml` exists locally (gitignored), when the Streamlit app reads
  config via the shared module, then it gets values from `st.secrets`.
- Given no Streamlit runtime is active (e.g. Alembic CLI, CI), when the same shared module
  is used, then it resolves the same keys from environment variables instead, without the
  caller needing to know which context it's in.
- Given `.streamlit/secrets.toml.example` is checked in, when a new developer clones the
  repo, then they can see every required key name and a placeholder value.

### 4. Migrations are wired up and reproducible
**As a** developer,
**I want** Alembic initialized and pointed at the shared config module,
**so that** future phases can each ship a migration without re-solving "how does Alembic
find the DB URL."
**Acceptance criteria**
- Given the local Docker Postgres is running, when I run `alembic upgrade head` with zero
  migrations authored yet, then it succeeds (no-op) and creates Alembic's version table.
- Given `alembic revision --autogenerate` is run after a future phase adds a SQLAlchemy
  model, then it correctly detects the new table (verified in phase 02, not this phase —
  this phase only proves the wiring works end-to-end with zero app tables).

### 5. CI enforces the quality gate on every PR
**As a** developer,
**I want** a GitHub Actions workflow that runs lint, type-check, and the full test suite on
every PR,
**so that** the same checks `/phase-verify` runs locally are enforced remotely as a
backstop.

**Acceptance criteria**
- Given a PR is opened against `main`, when CI runs, then it executes `ruff` (lint), `mypy`
  (type-check), and `pytest` (full suite) against a Postgres service container.
- Given any of those three checks fail, when CI finishes, then the workflow run is marked
  failed.
- Given all three checks pass, when CI finishes, then the workflow run is marked green.

## Out of scope for this phase
- Any real app table (`users`, `nutrition_log`, `water_log`, `daily_summary`, `settings`) —
  those are added by the phases that need them, per `tech.md`'s additive-migrations rule.
- Auth, login, any page beyond the landing page.
- Deployment to Streamlit Community Cloud (phase 09).
- Branch protection configuration on GitHub (explicitly a human step per `tech.md`).
