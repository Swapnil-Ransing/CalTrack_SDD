---
name: phase-verify
description: Run the full quality gate for the current phase — full test suite (not just the new phase's tests), lint, type-check, coverage. Pass/fail report only, no fixing beyond obvious breakage caused by this phase.
---

Invoked as: `/phase-verify` (no arguments).

## Preconditions
`progress.md` must show the active phase as `built`. If not, stop and say so.

## Do this, in order

1. Run the **entire** `pytest` suite (business logic, services, and `AppTest` page/widget
   tests together), not just this phase's new tests — a phase can silently break an earlier
   one.
2. Run lint (`ruff`) and type-check (`mypy`) across the whole repo.
3. Check coverage on the code this phase added/changed — flag (don't silently accept) if
   it's materially under the rest of the codebase's baseline.
4. If anything fails **and the failure is caused by this phase**, fix it, re-run, and repeat
   until green. If a failure looks pre-existing and unrelated to this phase, stop and report
   it to the human rather than fixing it here — that belongs to whichever phase caused it.
5. Report a clear pass/fail summary: tests run, tests passed, lint result, type-check
   result, coverage note.
6. On a full pass, update `progress.md` status to `verified` and the roadmap row to
   `verified`, with a log line.
7. On failure that you couldn't resolve, update `progress.md` status to `verify-failed`
   with a log line describing what's blocking, and stop — do not proceed to `/phase-ship`.

## Stop here
Do not commit, push, or open a PR from this command, even on a full pass. That's
`/phase-ship`'s job, and it should be a distinct, deliberate step.
