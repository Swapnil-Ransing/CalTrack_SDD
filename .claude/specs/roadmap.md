# Phase Roadmap

Ordered list of phases. One phase = one feature = one branch = one PR. Edit this file
freely as scope evolves, but keep numbering sequential and don't skip ahead — `/phase-start`
picks the next `pending` phase unless told otherwise.

| # | Phase | Status |
|---|-------|--------|
| 01 | Project scaffolding (Next.js + FastAPI skeletons, Docker Compose, Postgres + Alembic init, CI) | pending |
| 02 | Auth & user profiles (signup/login, health metrics profile, password hashing) | pending |
| 03 | Manual meal logging + Gemini calorie/macro calculation (text input) | pending |
| 04 | Voice logging (audio upload → Gemini structured parse → routes to meal/water/weight/activity) | pending |
| 05 | Water intake tracking (quick-add, custom, daily goal, hydration viz) | pending |
| 06 | Weight & activity logging (walk/gym, cheat day flag) | pending |
| 07 | Analytics dashboard (trends, macros breakdown, daily/weekly/monthly) | pending |
| 08 | UI polish pass (animation, empty states, error states, accessibility) | pending |
| 09 | Deployment (Oracle Free VM + Coolify, production Postgres, SSL, backups) | pending |

## Status values
`pending` → `spec-in-progress` → `spec-approved` → `building` → `verified` → `shipped`

`/phase-start` updates a row to `spec-in-progress` then `spec-approved` (after you approve).
`/phase-build` moves it to `building`. `/phase-verify` moves it to `verified` on a passing
gate. `/phase-ship` moves it to `shipped` once the PR is opened.
