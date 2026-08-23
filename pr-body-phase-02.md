## Summary

Adds account creation and login to HealthTracker: signup/login/logout, bcrypt password
hashing, a signed session token persisted via a browser cookie (so login survives a
refresh), and a one-time health-metrics profile (date of birth, sex, height, weight,
activity level, goal) that later phases (calorie calc, analytics) will read.

- `users` table (auth fields + health-metrics profile) with a reversible Alembic migration
- `services/auth_service.py`: bcrypt password hashing, signed/expiring session tokens
  (`itsdangerous`, using the new `AUTH_SECRET_KEY` secret)
- `core/auth.py`: cookie-backed login persistence (`extra-streamlit-components`'
  `CookieManager`) so sessions survive a browser refresh, plus the `require_auth()` gate
  every logged-in-only page calls
- `services/user_service.py`: create/authenticate/get/update with duplicate-email handling
- `app.py` rewritten as the login/signup auth gate; new `pages/0_👤_Profile.py` for
  viewing/editing the profile after signup

### Bugs found and fixed during manual + AppTest verification
Three real issues surfaced while testing the cookie-based session flow end-to-end in a
real browser (not just via automated tests):
1. `core/config.py`'s Streamlit-secrets-vs-env-var resolver read `st.secrets` off disk even
   outside a live Streamlit session, breaking test isolation once a real local
   `secrets.toml` existed — fixed by checking `get_script_run_ctx()` first.
2. `CookieManager.get()` reads a cookie snapshot frozen at construction time, so a session
   restored after a refresh looked permanently logged out — fixed by using `get_all()`
   (which re-invokes the component) instead, plus an explicit "just logged out" session
   flag so an immediate post-logout rerun doesn't read back a not-yet-propagated stale
   cookie value.
3. `CookieManager.delete()` raises `KeyError` if the cookie was never fetched into its
   local dict (e.g. a session restored purely from `session_state`) — guarded.

## Design
Full design in
[`.claude/specs/phases/02-auth-user-profiles/design.md`](.claude/specs/phases/02-auth-user-profiles/design.md).
Key decisions:
- Auth stays app-owned (bcrypt + our own `users` table) rather than Supabase Auth, per
  `tech.md`.
- Session persistence uses a signed token in a cookie rather than relying solely on
  `st.session_state`, since Streamlit's session state doesn't survive a browser refresh.
- `sex = 'other'` and its effect on BMR/calorie formulas is explicitly deferred to
  whichever phase builds calorie calculation — not blocking signup here.
- `users.weight_kg` is a live "current weight" profile field, not a time series; phase 06
  ("Weight & activity logging") is expected to add a `weight_log` table for history.

## Test plan
- [x] `spec-in-progress` → `spec-approved` — requirements/design/tasks reviewed and
      approved by the human before implementation started
- [x] All 12 tasks in
      [`tasks.md`](.claude/specs/phases/02-auth-user-profiles/tasks.md) implemented and
      checked off
- [x] Full local `/phase-verify` gate, re-run from a clean working tree:
  - pytest: **54/54 passed** (includes all of phase 01's tests — no regressions)
  - ruff: clean (whole repo)
  - mypy: clean, 27 source files (whole repo)
  - coverage: **98%** on this phase's added code — above the 80% threshold and above
    phase 01's 88% baseline
- [x] Manual end-to-end smoke test in a real browser: sign up, log in, session persists
      across a hard refresh, log out, logout persists across a hard refresh
- [x] Alembic migration verified reversible (`upgrade head` → `downgrade -1` → `upgrade
      head` again) against local Docker Postgres

## Open questions carried into this PR (see design.md for full context)
1. Cookie library choice (`extra-streamlit-components`) — proceeded per the
   recommendation in the approved spec.
2. Session lifetime — 30 days, as proposed and approved.
3. `sex = 'other'` calorie-formula handling — deferred to a later phase, not blocking here.
4. `users.weight_kg` semantics vs. a future `weight_log` table — flagged for the human to
   confirm when phase 06 is scoped.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01FkYYpDzowDpVFPoDTcdwt2
