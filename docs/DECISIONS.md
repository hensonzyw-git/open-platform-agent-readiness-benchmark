# Decisions — Open Platform Agent Readiness Benchmark

This file is the durable decision record for fresh Codex/Claude sessions. Keep `PROJECT-LOG.md` as the detailed historical source; keep this file concise.

## D1 — Measure End-To-End Scenarios, Not Atomic APIs

Atomic single-API doc-only tasks were not informative enough. The real integration difficulty appears in multi-step flows: API selection, field transfer, units, signing, idempotency, and runtime constraints.

## D2 — Primary Success Metric Is TSR, Not FPSR

The benchmark uses Task Success Rate for autonomous end-to-end completion within the token budget and without human repair. "First pass" was misleading because agents naturally iterate and self-correct.

## D3 — Token Cost Is A First-Class Axis

Tokens-to-success stays separate from success rate. Fetchable, machine-readable documentation may not change pass/fail in easy cases, but it can drastically reduce token cost compared with screenshot/OCR-heavy docs.

## D4 — Use A0-A4 Autonomy Rungs

The benchmark diagnoses failure severity by the type of human hint required:

- A4: autonomous success.
- A3: saved by high-level direction.
- A2: saved by pointing out the key issue.
- A1: saved only by near-code-level help.
- A0: deadlocked or unrecoverable.

Only A4 counts toward TSR; the rung distribution explains which platform layer failed.

## D5 — Doc-Only And Live Tracks Share The Same Task

Doc-only uses static golden trace comparison. Live adds sandbox/runtime verification. They should test the same end-to-end scenario at different depths instead of becoming separate benchmark units.

## D6 — Scenario Set Is The Benchmark Asset

Each scenario should be a frozen four-piece artifact: developer need, golden end-to-end trace, step-level assertions, and pre-registered hint ladder.

## D7 — Harness Stays Out Until The Standard Stabilizes

Early harness spikes are useful locally but should not become the public repo's stable surface until the v0.3 scenario structure has real traction.
