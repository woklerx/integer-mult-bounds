# Independently check PR1638 true-input cells through precision twelve

Intentional independent audit of [PR1638](https://github.com/CrocSwap/integer-mult-bounds/pull/1638), exact head `394b90ee7fdaedd1f666a78a442127be3da17810`. This is a corroborating review/handoff, not a new supplier or selected-frontier change.

Required Python 3.12 registered replay passes. A separately written integer-significand checker validates 65600 candidate cells and 646656 conservative endpoint inequalities through p12, retaining six-bit incoming warm-up precision. It reproduces generic-state zero/one/two-guard counterexamples.

## Reproduction

Start from main checkpoint `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. The independent checker imports no predecessor executable; it reads only declared exact Git objects. Fetch the reviewed head before replay:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git 394b90ee7fdaedd1f666a78a442127be3da17810
python -I -O -B research/pr1638-independent-prefix-audit/verify.py
```

Python3.12 standard library only. Normal replay writes no result files; --write explicitly regenerates the deterministic receipt.

SOURCES.json binds every consumed source by exact Git blob and SHA256. RESULT.json is recomputed, not trusted as the answer. TASK.json preserves the original random allocation and refined scope. The prior author registered replay was run separately; its success is credited as imported validation. Delivered logs name the environment and any initial setup failures.

## Scope

Exact finite cells corroborate the written quantified induction; they are not the all-precision proof. Seeded two-guard correctness, full root/recovery caller, physical tape and theorem formalization remain open.

## Open next questions

Derive a reachable-state invariant for the actual warm-up before deciding seeded two guards; additional finite passes alone cannot settle it.

## Credit

ToikY PR1638; Hanson Sun PR1528; retained OpenAI manuscript and classical Brent reductions; Douglas Colkitt repository guidance. Prepared by woklerx with substantial OpenAI Codex assistance. The checker is implementation-independent where stated, not independent human or proof-kernel review. New audit material is Apache-2.0; upstream source notices remain unchanged.
