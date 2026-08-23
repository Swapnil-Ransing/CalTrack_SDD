---
name: phase-build
description: Implement the approved tasks for the CURRENT phase only, writing tests alongside each task. Stops when done — never runs verify/ship itself.
---

Invoked as: `/phase-build` (no arguments — always operates on whatever
`.claude/state/progress.md` says is the active phase).

## Preconditions
- `progress.md` must show a `spec-approved` phase. If it shows `spec-in-progress`
  (not yet approved) or no active phase, stop and tell the human to run `/phase-start`
  and get approval first.
- Confirm you're on the correct feature branch before touching any files.

## Do this, in order

1. Read the active phase's `requirements.md`, `design.md`, and `tasks.md`.
2. Update `progress.md` status to `building`.
3. Work through `tasks.md` **one task at a time**, in order:
   - Implement the task.
   - Write tests for it immediately (unit tests at minimum; `AppTest`-based tests where the
     task touches a page/widget). Don't defer all testing to the end.
   - Run just this task's tests before moving to the next task.
   - Check the task off in `tasks.md`.
4. Do not scope-creep into other phases' work, even if you notice something related that's
   missing — note it in `design.md`'s "open questions" section instead and move on.
5. Once every task is implemented and checked off, run the phase's own test file(s) (not
   necessarily the full repo suite yet — that's `/phase-verify`'s job) and confirm they pass.
6. Update `progress.md`: status `built`, append a log line summarizing what was implemented.

## Stop here
Do not run the full verification gate and do not commit/push/open a PR. Tell the human the
phase is implemented and locally tested, and that `/phase-verify` is the next step.
