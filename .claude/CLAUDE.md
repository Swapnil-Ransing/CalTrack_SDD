# HealthTracker — Project Context

This file is read by Claude Code at the start of every session. Keep it accurate and short.

## What this project is
A voice-first, extremely user-friendly health tracker (calories, water, weight, activity)
for individuals, built as a modern web app.
See `.claude/steering/product.md` for the full product intent.

## Stack
See `.claude/steering/tech.md` for the authoritative, current stack decisions: a single
Streamlit (Python) app on Supabase Postgres, deployed to Streamlit Community Cloud.

## How we develop here: phase-wise, not one-shot

**This project is built one feature (phase) at a time. Never attempt to build multiple
phases or the whole app in a single command or a single sitting.** Each phase follows this
strict, human-gated cycle:

1. `/phase-start <phase-name>` — creates the branch and the spec (requirements → design →
   tasks) for ONE phase only. Stops after the spec is written for human review.
2. Human reviews the spec, edits if needed, then says "go" / "approved".
3. `/phase-build` — implements the approved tasks for the current phase, writing tests
   alongside each unit of work. Stops when all tasks are implemented and passing locally.
4. `/phase-verify` — runs the full gate: full test suite, lint, type-check, coverage
   threshold. Reports pass/fail. Do not proceed to ship on a failing gate.
5. `/phase-ship` — commits with conventional commit messages, pushes the branch, opens a
   PR with a description generated from the phase's requirements/design/tasks, and marks
   the phase complete in the roadmap.
6. Human reviews and merges the PR on GitHub. **Claude does not merge PRs.**
7. Only after merge does the human invoke `/phase-start` again for the next phase.

Never chain steps 1–5 together automatically. Each command does its one job and stops,
handing control back. This is intentional — it's how the human stays in the loop and how
each feature gets reviewed before the next one starts.

## Roadmap
The ordered list of phases lives in `.claude/specs/roadmap.md`. Read it before starting a
new phase to confirm what's next and what's already shipped.

## Current state
Always check `.claude/state/progress.md` before doing anything — it records which phase is
active, its branch name, and its status. If it says a phase is "in progress," resume that
phase; do not start a new one.

## Conventions
- Branch naming: `feature/phase-<NN>-<slug>` (e.g. `feature/phase-04-voice-logging`)
- Commit messages: Conventional Commits — `spec(04): add requirements`, `feat(04): implement
  voice capture and parsing`, `test(04): add voice parser unit tests`
- Every phase must ship with tests. No phase is "done" without a passing `/phase-verify`.
- Keep the database schema additive across phases where possible — prefer new migrations
  over destructive changes to earlier phases' tables.
