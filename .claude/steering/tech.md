# Tech Steering

These are settled decisions. Don't re-litigate them inside a phase — if something needs to
change, update this file first, in its own small commit, with the reason noted.

## Frontend
- **Next.js** (App Router) + TypeScript
- **Tailwind CSS** + **shadcn/ui** for components
- **Framer Motion** for animation/micro-interactions
- Charts: recharts or visx for analytics visualizations
- Mobile-first responsive layout; installable as a PWA

## Backend
- **FastAPI** (Python), async
- Pydantic models for request/response validation and for the Gemini structured-output
  schemas (shared shape where possible)
- SQLAlchemy ORM — models must work against both SQLite (local dev) and Postgres (prod)
  via the same models; no dialect-specific SQL in application code

## Database
- **PostgreSQL** in production
- Core SQLAlchemy models: `users`, `nutrition_log`, `daily_summary`, `settings`, `water_log`
- Alembic for migrations — every phase that changes the schema ships a migration

## Voice + AI
- **Google Gemini API** for voice understanding:
  - Audio uploaded directly to Gemini (no separate transcription step)
  - `response_schema` constrains output to structured JSON: an array of typed entries
    (`meal` | `water` | `weight` | `activity`), each with its own fields
  - Store the raw model response alongside parsed fields for auditability
- Keep the Gemini client isolated behind a service module (`services/voice_parser.py`) so
  the model/provider can be swapped without touching route handlers

## Secrets & environment variables
- All secrets (DB connection string, `GEMINI_API_KEY`, auth signing secret, etc.) live in
  `.env` files that are **never committed**. Each app ships a checked-in `.env.example`
  listing required variable names with placeholder values.
- Backend: loaded via Pydantic `Settings` (`backend/app/core/config.py`), sourced from
  `backend/.env` in local dev and from Coolify's environment injection in prod.
- Frontend: Next.js `.env.local` for local dev (server-only secrets use unprefixed names;
  anything needed client-side must use the `NEXT_PUBLIC_` prefix — never put real secrets
  there).
- Whichever phase first needs a new secret adds it to `.env.example` and documents it in
  that phase's `design.md`.

## CI
- **GitHub Actions.** Workflow(s) live in `.github/workflows/`, created as part of phase 01.
- On every PR: lint + type-check + full test suite (backend and frontend) — the same checks
  `/phase-verify` runs locally, so CI is a backstop, not a separate bar.
- CI must pass before a PR is merged (branch protection on the default branch), but Claude
  does not configure branch protection itself — that's a one-time human step in the GitHub
  repo settings.

## Deployment
- Self-hosted on an **Oracle Cloud Always Free** ARM VM (2 OCPU / 12 GB RAM)
- **Coolify** (open source, self-hosted) manages Git-push deploys, SSL, and the managed
  Postgres instance
- All Docker images must be built for `linux/arm64`
- No paid infra. If Oracle capacity can't be provisioned, fall back is noted in the repo's
  deployment doc but is not the default target

## Testing
- Backend: pytest, with a test DB (SQLite in-memory or throwaway Postgres schema)
- Frontend: Vitest/Playwright for component and e2e tests where a phase touches UI
- Every phase's `/phase-verify` gate must run the full suite, not just the new phase's tests
- **Coverage threshold: 80% line coverage**, measured per-app (backend via `pytest --cov`,
  frontend via Vitest coverage) on the code a phase adds or changes. `/phase-verify` flags
  (does not silently pass) any phase that lands under this bar.
