# Independently audit PR1704 two-copy scatter and chronological restoration

Intentional independent audit of [PR1704](https://github.com/CrocSwap/integer-mult-bounds/pull/1704), exact head `7f14aa7285cf10a7be350472fab25a25ef898484`. This is a corroborating review/handoff, not a new supplier or selected-frontier change.

Required Python 3.12 registered replay passes. New source-derived edge-subset enumeration reproduces 2620 partitions, optimum 120 and 105 optima. Formal integer-module replay checks all 36 pair blocks, 3128 target equations and 72 chronological/sign controls.

## Reproduction

Start from main checkpoint `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. The independent checker imports no predecessor executable; it reads only declared exact Git objects. Fetch the reviewed head before replay:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git 7f14aa7285cf10a7be350472fab25a25ef898484
python -I -O -B research/pr1704-independent-scatter-audit/verify.py
```

Python3.12 standard library only. Normal replay writes no result files; --write explicitly regenerates the deterministic receipt.

SOURCES.json binds every consumed source by exact Git blob and SHA256. RESULT.json is recomputed, not trusted as the answer. TASK.json preserves the original random allocation and refined scope. The prior author registered replay was run separately; its success is credited as imported validation. Delivered logs name the environment and any initial setup failures.

## Scope

Independent new checker focuses on scatter boundary and restricted matching census. Whole-word 661-column replay is imported upstream validation, not a new implementation. Two physical live COPY slots and native admission remain open.

## Open next questions

Construct and price a physical two-copy interface preserving temporary lifetimes and precision; the scalar reduction leaves recursive profile unchanged.

## Credit

Ross Richardson PR1704; Sagar Thakrar PR1062; PR967/926, Aaron Wang PR1015, Ross Richardson PR923, DreamingOfClouds PR589, eumemic PR555 and live-copy audit predecessors. Prepared by woklerx with substantial OpenAI Codex assistance. The checker is implementation-independent where stated, not independent human or proof-kernel review. New audit material is Apache-2.0; upstream source notices remain unchanged.
