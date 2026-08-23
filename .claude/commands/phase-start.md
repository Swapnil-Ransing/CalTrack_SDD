---
name: phase-start
description: Begin ONE phase from the roadmap — create its branch and write its spec (requirements, design, tasks). Stops for human review. Never implements code.
---

Invoked as: `/phase-start <phase-number-or-slug>` (e.g. `/phase-start 03` or
`/phase-start voice-logging`). If no argument is given, pick the next `pending` phase from
`.claude/specs/roadmap.md`.

## Do this, in order

1. Read `.claude/CLAUDE.md`, `.claude/steering/*.md`, `.claude/specs/roadmap.md`, and
   `.claude/state/progress.md`. If `progress.md` shows a phase already `in progress` that
   isn't `shipped`, stop and tell the human — don't start a new phase over an unfinished one.
2. Confirm the target phase's row in the roadmap. Update its status to `spec-in-progress`.
3. Create and check out branch `feature/phase-<NN>-<slug>` from the current default branch
   (confirm it's up to date first — `git pull`).
4. Create `.claude/specs/phases/<NN>-<slug>/` with three files:
   - **requirements.md** — user stories + acceptance criteria for this feature ONLY. Pull
     from `product.md`. Be concrete and testable ("given X, when Y, then Z"), not vague.
   - **design.md** — technical design for this feature ONLY: API endpoints, DB schema
     changes (with an Alembic migration plan if needed), component structure, and how it
     integrates with what earlier phases already built. Respect `tech.md` and
     `structure.md`. Call out any open questions for the human.
   - **tasks.md** — numbered, small, independently testable tasks, each phrased so
     `/phase-build` can implement and test it one at a time. Include a task for tests
     themselves, not just implementation.
5. Update `.claude/state/progress.md`: active phase, branch name, status `spec-in-progress`,
   append a log line.
6. **Stop here.** Do not write implementation code. Do not run `/phase-build` yourself.
   Present a short summary of the spec and explicitly ask the human to review
   `requirements.md`, `design.md`, and `tasks.md` and reply "approved" (or request changes)
   before you continue.

## On approval
When the human approves, update the roadmap row and `progress.md` status to
`spec-approved`, and tell them to run `/phase-build` when ready. Do not auto-chain into it.
