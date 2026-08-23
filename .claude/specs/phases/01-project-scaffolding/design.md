# Phase 01 — Project Scaffolding: Design

## Goal
Stand up the full repo skeleton from `structure.md` with just enough working code to prove
every layer (app boot, theme, DB connection, migrations, CI) actually functions — without
building any real feature yet.

## Repo layout produced by this phase
```
/
├── .streamlit/
│   ├── config.toml            # theme
│   └── secrets.toml.example   # documents required secret keys
├── app.py                     # entrypoint / minimal landing page
├── pages/                     # empty; first real page arrives phase 02+
├── services/
│   └── __init__.py
├── models/
│   └── __init__.py            # SQLAlchemy declarative Base only, no tables yet
├── schemas/
│   └── __init__.py
├── core/
│   ├── __init__.py
│   ├── config.py              # secrets/env resolver (Settings)
│   └── db.py                  # SQLAlchemy engine/session factory
├── components/
│   └── __init__.py
├── alembic/
│   ├── env.py
│   └── versions/               # empty — first real migration arrives phase 02
├── alembic.ini
├── tests/
│   ├── test_app_smoke.py
│   └── test_db_connection.py
├── .github/workflows/ci.yml
├── requirements.txt
├── docker-compose.yml
└── docs/
    └── deployment.md           # stub, filled in phase 09
```

## Key design decisions

### 1. `core/config.py` — one Settings resolver, two contexts
Streamlit's `st.secrets` only works inside a Streamlit runtime. Alembic, pytest, and CI all
run standalone. `core/config.py` exposes a `get_settings()` function that:
- Tries `st.secrets["KEY"]` first (wrapped in try/except — raises `StreamlitSecretNotFoundError`
  outside a runtime, or the app has no `secrets.toml` in CI).
- Falls back to `os.environ["KEY"]`.
- Returns a small `Settings` Pydantic model (`gemini_api_key: str | None`,
  `database_url: str`) so downstream code never touches `st.secrets` or `os.environ`
  directly.

This means: locally, `.streamlit/secrets.toml` drives the app; in CI/Alembic/tests, plain
env vars (`DATABASE_URL`, set by the CI workflow / test fixture / developer's shell) drive
it. Same function, same call sites, in both contexts.

**Open question for human review:** should the local dev DB URL for Alembic/manual scripts
also come from `.streamlit/secrets.toml` (parsed with `tomllib` when no Streamlit runtime is
active), instead of requiring a separately-exported `DATABASE_URL` env var? This design
picks the env-var fallback because it's simpler and matches how CI already has to supply it
— but it means a local developer running `alembic upgrade head` by hand needs to `export
DATABASE_URL=...` once (documented in `docs/deployment.md` or a dev-setup note). Flagging in
case you'd rather have `core/config.py` also parse `secrets.toml` directly for full
consistency.

### 2. `core/db.py` — engine/session factory
A single `get_engine()` (cached) and `get_session()` using SQLAlchemy 2.0-style
`sessionmaker`. No models depend on it yet beyond Alembic's `env.py` importing
`models.Base.metadata` for autogenerate support in later phases.

### 3. `models/__init__.py` — empty declarative base
```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```
No table models yet — each phase adds its own model module (e.g. `models/user.py` in phase
02) and Alembic autogenerate picks it up because `env.py` imports `Base.metadata`.

### 4. Alembic wiring
- `alembic.ini` has no hardcoded `sqlalchemy.url`; `alembic/env.py` calls
  `core.config.get_settings().database_url` and sets it at runtime.
- `alembic/env.py` imports `models.Base` so `--autogenerate` works starting phase 02.
- This phase runs `alembic init alembic`, edits `env.py` per the above, and runs `alembic
  upgrade head` once against local Docker Postgres to prove the wiring (creates only
  Alembic's own `alembic_version` table — no app migration authored yet, matching the
  additive-schema convention in `tech.md`).

### 5. `docker-compose.yml`
Single `postgres:16` service, named volume for persistence, port `5432:5432` (documented),
env vars for a dev-only user/password/db name (not secret — local only). Local
`DATABASE_URL` for manual use: `postgresql+psycopg://healthtracker:healthtracker@localhost:5432/healthtracker`.

### 6. `app.py`
Minimal: `st.set_page_config(...)`, a title, one-line product description pulled loosely
from `product.md` intent ("voice-first health tracker"), no widgets that touch the DB yet.
Confirms the theme in `.streamlit/config.toml` (primary color + font) renders.

### 7. Testing
- `tests/test_app_smoke.py` — `streamlit.testing.v1.AppTest.from_file("app.py")`, `.run()`,
  assert `not at.exception`.
- `tests/test_db_connection.py` — connects to the Dockerized Postgres via `core/db.py`,
  runs `SELECT 1`. Requires the CI Postgres service container / local Docker Compose to be
  up; documented as a prerequisite. This is the only test in this phase that needs a live
  DB — everything else is pure Python.
- `pytest.ini` / `pyproject.toml` `[tool.pytest.ini_options]` sets `DATABASE_URL` default
  for local runs pointing at the Compose Postgres, overridable by CI.

### 8. CI (`.github/workflows/ci.yml`)
- Triggers on `pull_request` targeting `main`.
- Job: checkout → setup Python → `pip install -r requirements.txt` → spin up a `postgres:16`
  service container → `ruff check .` → `mypy .` → `pytest --cov`.
- `DATABASE_URL` env var for the job points at the service container
  (`postgresql+psycopg://postgres:postgres@localhost:5432/postgres`).
- No coverage gate enforced by CI itself in this phase (that's `/phase-verify`'s job
  locally per `tech.md`); CI just needs to run `pytest --cov` and report, matching the "CI
  is a backstop, not a separate bar" principle.

### 9. `requirements.txt` (pinned to major versions, not exact patch pins)
`streamlit`, `sqlalchemy>=2.0`, `psycopg[binary]`, `alembic`, `pydantic>=2.0`,
`google-genai` (unused until phase 04, but listed now per `tech.md`'s Gemini decision — or
deferred to phase 04's `design.md` to avoid an unused dependency; **picking deferred** — not
added in this phase), `ruff`, `mypy`, `pytest`, `pytest-cov`.

### 10. `.streamlit/config.toml`
A theme block (`[theme]`: `primaryColor`, `backgroundColor`, `secondaryBackgroundColor`,
`textColor`, `font`) with placeholder-but-considered values (not Streamlit defaults) —
phase 08 (UI polish) is where this gets real design attention; this phase just proves the
mechanism works and picks a non-default accent color so it's visibly themed.

## Integration with later phases
- Phase 02 (auth) adds `models/user.py`, its own Alembic revision, and a real `pages/`
  entry — all slot into this skeleton without restructuring it.
- Phase 04 (voice) adds `services/voice_parser.py` and the `google-genai` dependency.
- `core/config.py`'s `Settings` model grows fields per phase as new secrets are needed
  (documented in that phase's own `design.md`, per `tech.md`).

## Open questions for human review
1. Env-var vs. `secrets.toml`-parsing fallback for Alembic/local scripts (see decision #1
   above) — proceeding with env-var fallback unless you'd rather standardize on parsing
   `secrets.toml` everywhere.
2. `requirements.txt` version pinning strategy: major-version floors (as drafted) vs. exact
   pins with a lockfile (e.g. `pip-tools`)? Defaulting to major-version floors for now since
   no lockfile tooling has been decided in `tech.md`.
