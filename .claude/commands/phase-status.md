---
name: phase-status
description: Report where the project is right now — no side effects. Safe to run anytime.
---

Invoked as: `/phase-status` (no arguments).

## Do this
1. Read `.claude/state/progress.md` and `.claude/specs/roadmap.md`.
2. Report, plainly:
   - Which phase is active (if any) and its status
   - The current git branch and whether it's ahead/behind origin
   - How many tasks in the active phase's `tasks.md` are checked off vs total
   - The next command the human should run
   - A one-line view of the overall roadmap (how many phases shipped / total)

Read-only. Never modify any file when this command runs.
