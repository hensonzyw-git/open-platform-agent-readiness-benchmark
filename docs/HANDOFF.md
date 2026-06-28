# Handoff — Open Platform Agent Readiness Benchmark

Start here after `AGENTS.md`.

## Read First

1. `PROJECT_STATE.md`
2. `PROJECT-LOG.md`
3. `scoring-model-design.md`
4. `docs/DECISIONS.md`

## Continue From

Confirm whether POP has a usable sandbox/test environment. If no sandbox exists, treat live TSR as blocked and focus on doc-only end-to-end scenarios.

## Current Best Next Task

Draft the first scenario four-piece set for POP x P1 "dependent idempotent write":

- developer need
- golden end-to-end trace
- step-level assertions
- A0-A4 hint ladder

## Guardrails

- Do not reintroduce harness code into the repo before the scenario standard stabilizes.
- Do not change the scoring model without recording the reason in `docs/DECISIONS.md`.
- Direct push to `main` is allowed for this repo unless the user asks for a branch/PR.
