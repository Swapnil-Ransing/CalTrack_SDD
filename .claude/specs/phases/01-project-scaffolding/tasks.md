# Phase 01 — Project Scaffolding: Tasks

Numbered, small, independently testable. `/phase-build` implements and tests these one at a
time, in order (later tasks depend on earlier ones).

1. **Scaffold folders & package inits**
   Create `pages/`, `services/`, `models/`, `schemas/`, `core/`, `components/`, `tests/`,
   `docs/` with `__init__.py` where they're Python packages (`services/`, `models/`,
   `schemas/`, `core/`, `components/`). No logic yet.

2. **`requirements.txt`**
   Add pinned (major-version-floor) dependencies per `design.md` #9: `streamlit`,
   `sqlalchemy`, `psycopg[binary]`, `alembic`, `pydantic`, `ruff`, `mypy`, `pytest`,
   `pytest-cov`. Verify `pip install -r requirements.txt` succeeds in a clean venv.

3. **`.streamlit/config.toml` + `secrets.toml.example`**
   Theme block per `design.md` #10. `secrets.toml.example` lists `DATABASE_URL` (and a
   commented placeholder for `GEMINI_API_KEY`, added for real in phase 04) with dummy
   values. Confirm `.streamlit/secrets.toml` (the real, gitignored file) is listed in
   `.gitignore`.

4. **`core/config.py` — Settings resolver**
   Implement `get_settings()` per `design.md` #1 (Streamlit-secrets-first, env-var
   fallback, returns a Pydantic `Settings` model with `database_url`). Unit test: with a
   mocked/absent Streamlit context and `DATABASE_URL` env var set, `get_settings()` returns
   the expected value.

5. **`core/db.py` — engine/session factory**
   Implement `get_engine()` / `get_session()` per `design.md` #2, using
   `core.config.get_settings().database_url`.

6. **`models/__init__.py` — declarative Base**
   Add the empty `Base(DeclarativeBase)` per `design.md` #3.

7. **`docker-compose.yml`**
   Single `postgres:16` service per `design.md` #5. Manually verify `docker compose up -d`
   starts and is reachable (`psql` or a quick Python connect) — record the verification
   command used in the task's completion note, don't leave it untested.

8. **`app.py` — minimal landing page**
   Per `design.md` #6: page config, title, one-line description, themed. No DB calls.

9. **`tests/test_app_smoke.py`**
   `AppTest.from_file("app.py").run()`, assert no exception. This is the first automated
   test in the repo — confirms the harness itself works.

10. **`tests/test_db_connection.py`**
    Connects via `core/db.py` to whatever `DATABASE_URL` resolves to, runs `SELECT 1`.
    Requires Docker Compose Postgres (local) or the CI service container (CI) to be up —
    document this prerequisite at the top of the test file.

11. **Alembic init**
    `alembic init alembic`; edit `alembic.ini` (strip hardcoded URL) and `alembic/env.py`
    per `design.md` #4 (pull URL from `core.config.get_settings()`, import `models.Base`).
    Run `alembic upgrade head` against local Compose Postgres and confirm it succeeds
    (creates only `alembic_version`).

12. **`.github/workflows/ci.yml`**
    Per `design.md` #8: `pull_request` trigger, Postgres service container, `ruff check .`,
    `mypy .`, `pytest --cov`. Push the branch and confirm the workflow runs (even though
    the PR itself opens in `/phase-ship`, the workflow file can be validated via `act` or by
    eyeballing the YAML — note in the task's completion how it was validated).

13. **`docs/deployment.md` stub**
    Placeholder noting deployment is finalized in phase 09; not blocking for this phase.

14. **Full local verification pass**
    Run `ruff check .`, `mypy .`, `pytest --cov` locally end-to-end and confirm all green
    before declaring the phase build done — this is a dry run of what `/phase-verify` will
    check formally.
