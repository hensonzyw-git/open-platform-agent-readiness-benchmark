# Run: POP / T3-write + signing-example defect — 2026-06-16

Model under test: Claude, doc-only, context-isolated, K=5 per task.

## T3 — Create Consignment Application (`enterprise-stock-apply/add`)

Two task framings:
- **t3 (leaky)**: task pre-specified `language`/`timeZone`/`timestamp` → **FPSR 5/5 = 100%**.
  Invalid measurement: the task leaked the answer (the obscure required params were the trap).
- **t3b (leak-free)**: task gave only business intent + credentials; agent had to discover
  required params from the doc → **FPSR 5/5 = 100%**.

Scorer (`score/score_t3.py`): endpoint correct, all 6 required general params present,
`skuId` used over `globalSkuId`, `applyQty` present, and **sign recomputed from each agent's
own emitted params matches the emitted sign**.

**Read**: POP's param doc clearly marks params "required" and the signing doc ships reference
code → a strong model with doc-only context succeeds reliably. For happy-path T1/T3, POP is
genuinely agent-friendly. These tasks therefore have **no discriminating power**.

## Methodology lesson (the day's most important finding)
The first T3 framing scored 100% only because I leaked `language`/`timeZone` in the task —
"假绿" (§7) appearing inside the measurement rig itself. **Writing tasks that don't leak the
answer is the core, hard craft of this benchmark.** Every task needs a leak audit.

## Signing-example DEFECT probe (where the benchmark earns its keep)
POP's own worked signing example is internally inconsistent:
- Input JSON: `timestamp=1603354338917` → signs to `9DADEBE04D488DEDE1D49F136B5EACD9`
- Claimed result: `A0BC221AB4EF5190EFD7D593566C6747` — only reproducible with `1603353500369`,
  a value present nowhere in the input.

=> Any agent faithfully signing the documented input produces `9DADEBE0...`, never the
documented `A0BC...`. **FPSR-strict vs the doc's stated answer = 0%.** Plus the Java reference
(preserve nested key order) and Python reference (sort nested keys) contradict each other, so
faithful agents can split across multiple wrong hashes — and the *correct* one can't be
confirmed without a live sandbox call. This is the doc-only ceiling, located precisely.

## Net picture for POP (v0 signal)
| Layer | Signal |
|-------|--------|
| Layer 1/2 (happy-path signing & write) | **Strong** — clear required-field marking, reference code, FPSR 100% |
| Layer 2 (worked examples) | **Defective** — signing example self-inconsistent; faithful agents can't reproduce it |
| Layer 3/4 (navigation / fetchability) | **Weak** — doc site is a JS-SPA; static GET returns empty shell; API param tables not text-extractable |

The benchmark's discriminating power lives in Layers 3/4 and in worked-example fidelity,
NOT in happy-path code generation where good docs ship copyable code.
