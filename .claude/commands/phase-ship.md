---
name: phase-ship
description: Commit, push, and open a PR for the current, already-verified phase. Marks it shipped. Does not merge — merging is a human decision.
---

Invoked as: `/phase-ship` (no arguments).

## Preconditions
`progress.md` must show the active phase as `verified`. If it's anything else (`built`,
`verify-failed`, etc.), stop and tell the human to run `/phase-verify` first (or fix the
failure it reported).

## Do this, in order

1. Review the diff (`git status` / `git diff`) to confirm only this phase's intended files
   changed — no stray files, no secrets, no debug prints.
2. Stage and commit with Conventional Commits, split into logical commits rather than one
   giant commit where it makes sense (e.g. `spec(04): add requirements and design`,
   `feat(04): implement voice capture and parsing`, `test(04): add voice parser tests`). If
   the spec commit already happened in `/phase-start`, just add the implementation/test
   commits here.
3. Push the branch: `git push -u origin feature/phase-<NN>-<slug>`.
4. Open a PR (`gh pr create`) targeting the default branch. PR description should be
   generated from the phase's `requirements.md` (what/why), `design.md` (how), and a
   checklist from `tasks.md` (all checked), plus the `/phase-verify` summary (test/lint/
   coverage results) so the reviewer doesn't have to re-derive any of it.
5. Update the roadmap row to `shipped` and `progress.md`: active phase → none, append a log
   line with the PR link.
6. Tell the human the PR is open and ready for their review, and that the next phase can be
   started with `/phase-start` once they've merged it.

## Stop here
Do not merge the PR. Do not start the next phase. That's two separate human decisions
(review/merge, then choosing to proceed) and this command doesn't make either of them.
