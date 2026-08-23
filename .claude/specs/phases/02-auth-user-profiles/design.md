# Phase 02 — Design: Auth & User Profiles

## Summary
Add an app-owned `users` table (auth fields + health-metrics profile in one row, per
`tech.md`'s decision to keep auth out of Supabase Auth), a signed-cookie session so login
survives a browser refresh, and two UI surfaces: the auth gate (signup/login, replacing the
current placeholder `app.py`) and a Profile page for viewing/editing metrics after login.

## Database

### New table: `users`
Single table for auth + profile — 1:1 relationship, no reason to split yet.

| Column           | Type                          | Notes                                   |
|------------------|-------------------------------|------------------------------------------|
| `id`             | `UUID`, PK, default `gen_random_uuid()` | matches Supabase-Postgres convention |
| `email`          | `String`, unique, not null    | lowercased before storage/lookup        |
| `password_hash`  | `String`, not null            | bcrypt hash, never the raw password     |
| `date_of_birth`  | `Date`, not null              | age is derived, not stored              |
| `sex`            | `Enum('male','female','other')`, not null | drives BMR formula in a later phase |
| `height_cm`      | `Numeric(5,1)`, not null      |                                          |
| `weight_kg`      | `Numeric(5,1)`, not null      | current weight; phase 06 adds a time-series `weight_log` — this column is just the live profile value, updated whenever the user edits it or (later) logs a new weight |
| `activity_level` | `Enum('sedentary','light','moderate','active','very_active')`, not null | |
| `goal`           | `Enum('lose_weight','maintain','gain_weight')`, not null | |
| `created_at`     | `DateTime(timezone=True)`, default `now()` | |
| `updated_at`     | `DateTime(timezone=True)`, default `now()`, onupdate `now()` | |

`gen_random_uuid()` requires the `pgcrypto` extension; the migration enables it
(`CREATE EXTENSION IF NOT EXISTS pgcrypto`) — safe on both local Docker Postgres and
Supabase (Supabase has it available by default, may already be enabled).

### Alembic migration
One new revision under `alembic/versions/`: creates the `pgcrypto` extension (if not
present), the three enum types, and the `users` table with a unique index on `email`. Ships
in this phase's PR; run against local Docker Postgres in dev, and the human runs it against
Supabase's direct connection string when deploying (per `tech.md`).

## Models — `models/user.py`
`User(Base)` SQLAlchemy 2.0-style mapped class with the columns above, using Python `Enum`
classes (`Sex`, `ActivityLevel`, `Goal`) shared with the Pydantic schemas so the same
literal values are validated at both the API-boundary (Pydantic) and DB layer (SQLAlchemy
`Enum`). Registered in `models/__init__.py` alongside `Base` so Alembic autogenerate and
`Base.metadata` pick it up (as already wired in `alembic/env.py` from phase 01).

## Schemas — `schemas/user.py`
Pydantic models:
- `UserSignup` — email, password, password_confirm, date_of_birth, sex, height_cm,
  weight_kg, activity_level, goal. Validates password length (≥8 chars) and
  password == password_confirm.
- `UserLogin` — email, password.
- `UserProfileUpdate` — same profile fields as signup minus password; email editable too.
- `UserOut` — id, email, profile fields, created_at — **never** includes password_hash.
  Used for anything that needs to hand a user object to the UI layer.

## Auth mechanics

### Password hashing — `services/auth_service.py`
`hash_password(raw: str) -> str` and `verify_password(raw: str, hashed: str) -> bool` using
`bcrypt` directly (new dependency — small, no-dependency C extension wheel, the standard
choice for this and already implied by `tech.md`'s "password hashing" phase-02 scope).

### Session tokens — `services/auth_service.py`
`tech.md` already reserves an "auth signing secret" for this phase, so sessions are a
**signed, expiring token** (not just server-side `st.session_state`, which doesn't survive
a browser refresh in Streamlit):
- `create_session_token(user_id: UUID) -> str` — signs `{"uid": str(user_id), "exp": ...}`
  with `itsdangerous.URLSafeTimedSerializer(secret_key)` (new dependency — small, no
  transitive deps, does exactly this one job). Expiry: 30 days.
- `verify_session_token(token: str) -> UUID | None` — verifies signature and expiry,
  returns the user id or `None`. A changed secret or tampered/expired token both fail
  closed to `None`.

### Persisting the token across refreshes — `core/auth.py`
Streamlit has no built-in way to set a browser cookie from Python. This phase adds
**`extra-streamlit-components`** (new dependency) for its `CookieManager` component, which
wraps a small JS component to get/set a cookie and is the standard approach in the Streamlit
ecosystem for this exact problem.

`core/auth.py` responsibilities (the only module that touches the cookie manager or
`st.session_state` for auth):
- `get_current_user() -> User | None` — on each script run: if `st.session_state["user"]`
  is already set, return it; otherwise read the `session_token` cookie via `CookieManager`,
  call `verify_session_token`, and if valid, load the `User` row via
  `user_service.get_user_by_id` and cache it in `st.session_state["user"]`. Returns `None`
  if there's no valid session.
- `login_user(user: User) -> None` — creates a session token, sets it on the cookie (30-day
  expiry) and in `st.session_state["user"]`.
- `logout_user() -> None` — clears the cookie and `st.session_state["user"]`.
- `require_auth() -> User` — calls `get_current_user()`; if `None`, renders a short "please
  log in" message and calls `st.stop()` (pages can't `st.switch_page` before their own
  script finishes running the guard, so `st.stop()` is the correct short-circuit). Every
  page except the auth gate itself calls this first.

`CookieManager`'s known quirk: it returns `None` on the very first script run after a fresh
page load (the component hasn't reported back yet) even if a cookie exists. `get_current_user`
handles this by treating "cookie manager not ready yet" the same as "not logged in" for that
one rerun — Streamlit's own rerun-on-interaction model means the next interaction re-checks
and resolves correctly. This is a one-time flash on hard reload, not a functional bug; noted
here so `/phase-build` doesn't try to "fix" it.

## Services — `services/user_service.py`
Plain functions taking a `Session` (from `core/db.get_session()`) and Pydantic
schemas/primitives, returning `User` ORM objects or `None`:
- `create_user(session, data: UserSignup) -> User` — lowercases email, checks uniqueness,
  hashes password, inserts, commits, returns the row. Raises `EmailAlreadyRegisteredError`
  (new small exception in the same module) on conflict, caught by the page layer to show
  the friendly message.
- `authenticate_user(session, data: UserLogin) -> User | None` — looks up by lowercased
  email, verifies password; returns `None` on any failure (both "no such user" and "wrong
  password" collapse to `None` so the page shows one generic message).
- `get_user_by_id(session, user_id: UUID) -> User | None`
- `get_user_by_email(session, email: str) -> User | None`
- `update_profile(session, user_id: UUID, data: UserProfileUpdate) -> User` — same
  uniqueness check if email changed; raises `EmailAlreadyRegisteredError` on conflict.

## Pages

### `app.py` (rewritten)
Becomes the auth gate:
- Calls `core.auth.get_current_user()`.
- If logged in: shows a minimal home screen (welcome message, logout button) — this is
  intentionally thin, since no logging features exist until phase 03+; it's just proof the
  gate works and a place later phases add widgets to.
- If not logged in: two tabs, "Log in" and "Sign up", each a `st.form`. On success, calls
  `core.auth.login_user(user)` and reruns (`st.rerun()`) so the gate re-evaluates.

### `pages/0_👤_Profile.py` (new)
- First line: `user = require_auth()`.
- Pre-filled `st.form` with the profile fields (not email/password — email edit is included
  per requirements, password change is explicitly out of scope for this phase since there's
  no "forgot password" counterpart yet; changing a password safely belongs with that flow).
  Actually per requirements.md story 7, email *is* editable here — password is not (no
  reset flow to pair it with yet).
- On submit, calls `user_service.update_profile`, shows `st.success` or the field-level
  error.
- A "Log out" button calling `core.auth.logout_user()` + rerun.

Numbering: this is the first entry in `pages/`, and per `structure.md`'s
`<order>_<emoji>_<Title>.py` convention it takes `0_👤_Profile.py` so it sorts before the
feature pages later phases will add (`1_💧_Water.py`, etc., already named as examples in
`structure.md`).

## Secrets & config
- New required secret: `AUTH_SECRET_KEY` (random ≥32-byte string). Added to
  `.streamlit/secrets.toml.example` with a placeholder and a comment on how to generate one
  (`python -c "import secrets; print(secrets.token_urlsafe(32))"`).
- `core/config.py`: `Settings` gains `auth_secret_key: str`, resolved the same way as
  `database_url` (required, raises `RuntimeError` if missing — mirrors the existing
  pattern exactly).

## New dependencies (added to `requirements.txt`)
| Package | Why |
|---|---|
| `bcrypt` | password hashing |
| `itsdangerous` | signed, expiring session tokens |
| `extra-streamlit-components` | `CookieManager` — only maintained way to persist a value in a real browser cookie from Streamlit |

## Testing plan
- `tests/test_auth_service.py` — pure unit tests, no DB: `hash_password`/`verify_password`
  round-trip and wrong-password rejection; `create_session_token`/`verify_session_token`
  round-trip, tampered-token rejection, expired-token rejection (freeze/patch time).
- `tests/test_user_service.py` — against the Dockerized Postgres test DB (same pattern as
  `tests/test_db_connection.py`): `create_user` success, duplicate-email rejection,
  `authenticate_user` success/wrong-password/unknown-email, `update_profile`
  success/duplicate-email-conflict. Each test creates and tears down its own rows (or runs
  in a transaction rolled back at test end) so tests don't collide.
- `tests/test_app_auth_flow.py` — `streamlit.testing.v1.AppTest` against `app.py`: signup
  with valid data logs the user in and shows the home screen; signup with mismatched
  passwords shows a validation error and stays on the form; login with wrong password shows
  the generic error; logout returns to the login/signup tabs.
- `tests/test_profile_page.py` — `AppTest` against `pages/0_👤_Profile.py`: loading without
  a session stops at the auth-gate message; loading with a session pre-fills current values;
  submitting an update persists and shows success.
- Coverage: new code in `services/`, `core/auth.py`, `schemas/user.py`, `models/user.py`
  must clear the 80% line-coverage bar per `tech.md`.

## Open questions for the human
1. **Cookie library choice** — `extra-streamlit-components` is the standard pick, but it's
   a new third-party JS component (unlike anything used in phase 01). Confirm this is
   acceptable, or say if you'd rather accept "logout on every browser refresh" for now and
   defer persistent sessions to a later phase (simpler, zero new component deps).
   **Recommendation: proceed with `extra-streamlit-components`** — matches `tech.md`'s already-planned
   auth signing secret and is the ecosystem-standard approach, so this is the only proposal
   below unless you flag it.
2. **Session lifetime** — 30 days proposed. Shorter (e.g. 7 days) or longer, your call.
3. **`sex = 'other'` and calorie formulas** — flagged in requirements.md; no decision needed
   *this* phase, just confirming it's deferred to whichever phase builds BMR/TDEE
   calculation rather than blocking signup here.
4. **Weight column semantics** — `users.weight_kg` is a live "current weight" value, not a
   history. Phase 06 ("Weight & activity logging") will very likely add a `weight_log` table
   for the time series; confirm that's the right split, or if you'd rather this phase omit
   `weight_kg` from the profile entirely and start weight tracking fresh in phase 06.
