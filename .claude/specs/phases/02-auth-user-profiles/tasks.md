# Phase 02 — Tasks: Auth & User Profiles

Each task is small and independently testable. `/phase-build` implements and tests them one
at a time, in order (later tasks depend on earlier ones).

1. [x] **Dependencies** — add `bcrypt`, `itsdangerous`, `extra-streamlit-components` to
   `requirements.txt`. Install and confirm imports work.

2. [x] **Config: `AUTH_SECRET_KEY`** — add to `.streamlit/secrets.toml.example` (placeholder +
   generation comment). Extend `core/config.Settings` with `auth_secret_key: str`, resolved
   like `database_url` (required, `RuntimeError` if missing). Test: extend
   `tests/test_config.py` with a case asserting the same missing/present behavior for
   `AUTH_SECRET_KEY` as already exists for `DATABASE_URL`.

3. [x] **Model: `models/user.py`** — `Sex`, `ActivityLevel`, `Goal` Python enums; `User(Base)`
   mapped class with all columns from `design.md`. Register in `models/__init__.py`. No DB
   test yet — this task is just the mapped class compiling and `Base.metadata` including it
   (assert `"users" in Base.metadata.tables` in a quick unit test).

4. [x] **Migration** — new Alembic revision: enable `pgcrypto`, create the three enum types and
   the `users` table with a unique index on `email`. Run `alembic upgrade head` against
   local Docker Postgres and confirm the table + indexes exist. Run `alembic downgrade -1`
   to confirm the migration is reversible, then upgrade again.

5. [x] **Schemas: `schemas/user.py`** — `UserSignup`, `UserLogin`, `UserProfileUpdate`,
   `UserOut` per `design.md`, with the password-length and password-match validators on
   `UserSignup`. Unit tests: valid payload passes; short password rejected; mismatched
   confirm rejected; invalid email format rejected.

6. [x] **Password hashing — `services/auth_service.py`** — `hash_password`, `verify_password`.
   Unit tests: correct password verifies true; wrong password verifies false; two hashes of
   the same password differ (salted).

7. [x] **Session tokens — `services/auth_service.py`** — `create_session_token`,
   `verify_session_token`, using `AUTH_SECRET_KEY` from `core.config.get_settings()`. Unit
   tests: valid token round-trips to the right user id; tampered token returns `None`;
   expired token returns `None` (patch/freeze time rather than sleeping).

8. [x] **`services/user_service.py`** — `create_user`, `authenticate_user`, `get_user_by_id`,
   `get_user_by_email`, `update_profile`, plus `EmailAlreadyRegisteredError`. Integration
   tests against the Dockerized Postgres test DB (pattern from
   `tests/test_db_connection.py`): create succeeds; duplicate email raises; authenticate
   succeeds/fails correctly; update_profile succeeds and rejects a conflicting email. Clean
   up rows created by each test.

9. [x] **`core/auth.py`** — `get_current_user`, `login_user`, `logout_user`, `require_auth`,
   wired to `CookieManager` + `st.session_state` per `design.md`, including the
   first-run-`None` handling note. This module needs a live Streamlit script context to
   fully exercise the cookie path — cover what's testable in isolation here (token
   verification delegation, `st.session_state` caching logic with a stubbed cookie manager)
   and leave the full flow to the `AppTest` coverage in task 11.

10. [x] **`app.py` rewrite** — auth gate: login/signup tabs when logged out, minimal home +
    logout when logged in, per `design.md`. Manual smoke check: `streamlit run app.py`,
    sign up, refresh the browser, confirm still logged in, log out, confirm gate reappears.

11. [x] **`pages/0_👤_Profile.py`** — profile view/edit form gated by `require_auth()`, per
    `design.md`. `AppTest` tests (`tests/test_app_auth_flow.py`,
    `tests/test_profile_page.py`): signup success path, signup validation errors, login
    success/failure, logout, auth-gate stop when logged out, profile pre-fill, profile
    update success, profile update with conflicting email.

12. [x] **Coverage + lint pass** — run the full suite with `pytest --cov`, `ruff check`,
    `mypy`; fix anything under the 80% bar or failing lint/type-check introduced by this
    phase's new code, per `tech.md`'s testing section. (Full gate re-run is `/phase-verify`'s
    job, but `/phase-build` should leave the branch passing locally before handing off.)
