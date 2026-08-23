# Tech Steering

These are settled decisions. Don't re-litigate them inside a phase — if something needs to
change, update this file first, in its own small commit, with the reason noted.

## App
- **Streamlit** (Python) — single app, no separate frontend/backend split. UI and logic
  live in the same process.
- Multi-page app via Streamlit's `pages/` convention (numbered, emoji-prefixed filenames
  control sidebar order/icons — see `structure.md`).
- Voice capture via the built-in **`st.audio_input`** widget (records mic audio directly in
  the browser) — no third-party JS component and no separate upload endpoint needed; the
  page's callback gets the audio bytes and calls the Gemini service module directly.
- Pydantic models for validation and for the Gemini structured-output schemas (shared shape
  where possible).
- SQLAlchemy ORM against Postgres (see Database below) — one dialect only, no
  SQLite-compatibility constraints on the models.

## UI polish
Priority is to push Streamlit as far as it goes (product.md #2) — Streamlit is
server-rendered Python widgets, not a custom app, but invest real effort within that:
- **Theme** via `.streamlit/config.toml` (primary color, font, base) as the first layer.
- **Custom CSS** injected through a shared `inject_css()` helper reading a checked-in `.css`
  file, for anything `config.toml` can't reach (cards, spacing, micro-animations).
- **Component libraries** allowed for polish, added per-phase as needed and noted in that
  phase's `design.md` — e.g. `streamlit-extras` (UI helpers), `streamlit-lottie`
  (animations for confirmations/empty states).
- **Charts:** **Plotly** (`st.plotly_chart`) for analytics — more customizable and
  interactive than Streamlit's native chart types.
- Mobile-first intent stays, but accept Streamlit's layout ceiling — test each polish pass
  at a phone-width viewport rather than aiming for app-native feel.

## Database
- **Supabase** (hosted Postgres) in production.
- **Local Postgres via Docker Compose** for dev — same engine as prod, so no
  dialect-switching logic anywhere in the app.
- Core tables: `users`, `nutrition_log`, `daily_summary`, `settings`, `water_log`.
- Alembic for migrations — every phase that changes the schema ships a migration, run
  against local Docker Postgres in dev and against Supabase's **direct** connection string
  (not the pooled/pgbouncer one) for the deployed database.
- Using Supabase purely as a hosted Postgres instance via SQLAlchemy — not its client SDK,
  Auth, Storage, or RLS features. Phase 02's auth (password hashing) stays app-owned, to
  keep one code path between local and prod.

## Voice + AI
- **Google Gemini API** for voice understanding:
  - Audio captured via `st.audio_input`, sent directly to Gemini (no separate
    transcription step)
  - `response_schema` constrains output to structured JSON: an array of typed entries
    (`meal` | `water` | `weight` | `activity`), each with its own fields
  - Store the raw model response alongside parsed fields for auditability
- Keep the Gemini client isolated behind a service module (`services/voice_parser.py`) so
  the model/provider can be swapped without touching page code.

## Secrets & environment variables
- Streamlit's own secrets mechanism — **not** `.env` files:
  - Local dev: `.streamlit/secrets.toml` (gitignored). A checked-in
    `.streamlit/secrets.toml.example` lists required keys with placeholder values.
  - Deployed: the same keys are set in the Streamlit Community Cloud app's
    **Settings → Secrets** panel (TOML format) — a manual step in the Cloud UI per app;
    Claude cannot set this remotely.
  - Access in code via `st.secrets["KEY_NAME"]`.
  - Required keys (grows per phase): `GEMINI_API_KEY`, `SUPABASE_DB_URL`, an auth signing
    secret (added in phase 02).
- Whichever phase first needs a new secret adds it to `.streamlit/secrets.toml.example` and
  documents it in that phase's `design.md`.

## CI
- **GitHub Actions.** Workflow(s) live in `.github/workflows/`, created as part of phase 01.
- On every PR: lint (`ruff`) + type-check (`mypy`) + full `pytest` suite — the same checks
  `/phase-verify` runs locally, so CI is a backstop, not a separate bar. No image build/push
  step — Streamlit Community Cloud builds directly from the repo on deploy.
- CI must pass before a PR is merged (branch protection on the default branch), but Claude
  does not configure branch protection itself — that's a one-time human step in the GitHub
  repo settings.

## Deployment
- **Streamlit Community Cloud** (free): connect the GitHub repo, point it at the app's
  entrypoint, deploy from `main` — every merge to `main` auto-redeploys.
- Secrets configured once in the Cloud app's dashboard (see Secrets above); no Docker, no
  VM, no reverse proxy, no SSL management to maintain.
- Known constraints to design around: the free tier sleeps an inactive app (a few seconds'
  cold start on the next visit) and caps resources at roughly 1 GB RAM per app — fine for
  this app's scale, but keep Gemini calls and dataframe work mindful of that ceiling.

## Testing
- `pytest` for all business logic (`services/`, calculations, Gemini parsing), against a
  throwaway Postgres schema (Dockerized) as the test DB.
- **`streamlit.testing.v1.AppTest`** (built into Streamlit) for page/widget-level tests —
  runs a page script and drives its widgets without a browser. This replaces
  Vitest/Playwright as the default for UI logic.
- Playwright is allowed for a small number of true end-to-end smoke tests if a phase's
  `design.md` calls for it, but `AppTest` is the default.
- Every phase's `/phase-verify` gate must run the full suite, not just the new phase's tests.
- **Coverage threshold: 80% line coverage**, measured via `pytest --cov` on the code a phase
  adds or changes. `/phase-verify` flags (does not silently pass) any phase under this bar.
