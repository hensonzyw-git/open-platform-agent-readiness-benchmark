# Project State — Open Platform Agent Readiness Benchmark

Last updated: 2026-06-28

## Current Status

This repo is a behavior benchmark for whether an open platform lets an AI agent complete an end-to-end integration from docs and a developer need.

The scoring model is currently `v0.3` in `scoring-model-design.md`. The older all-in-one working memory remains in `PROJECT-LOG.md`; this file is the short cross-machine state snapshot.

## Source Of Truth

- Working memory and detailed history: `PROJECT-LOG.md`
- Scoring model: `scoring-model-design.md`
- Long-term decisions: `docs/DECISIONS.md`
- Milestone log: `docs/PROJECT_LOG.md`
- Next-agent handoff: `docs/HANDOFF.md`

## Current Blocker

POP live-track evaluation may not be feasible if there is no executable sandbox. Confirm sandbox/test-environment availability before investing in live TSR measurement.

## Next Steps

1. Build the first scenario four-piece set: POP x P1 "dependent idempotent write" for item number -> pricing -> listing.
2. Implement the progressive-disclosure harness: start from docs URL, inject frozen hints only when blocked, score by rung.
3. Add Stripe as the first cross-platform comparison target.
4. Decide whether the live track is feasible after sandbox confirmation.

## Validation State

No code validation was run for this context-sync update; this is documentation-only.
