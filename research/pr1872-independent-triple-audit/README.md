# Independently verify PR1872 triple sharing and its clean-helper boundary

Intentional independent audit of [PR1872](https://github.com/CrocSwap/integer-mult-bounds/pull/1872), exact head `626ce207ec92a76f70a84843fe4ce3c39f67899d`. This is a corroborating review/handoff, not a new supplier or selected-frontier change.

Required Python 3.12 registered replay passes. A new formal-polynomial checker proves the dirty-helper output syndrome and exact inverse, exhausts 4096 F2 states, and independently certifies thresholds 764/765/766 with outward fixed-point arithmetic.

## Reproduction

Start from main checkpoint `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. The independent checker imports no predecessor executable; it reads only declared exact Git objects. Fetch the reviewed head before replay:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git 626ce207ec92a76f70a84843fe4ce3c39f67899d
python -I -O -B research/pr1872-independent-triple-audit/verify.py
```

Python3.12 standard library only. Normal replay writes no result files; --write explicitly regenerates the deterministic receipt.

SOURCES.json binds every consumed source by exact Git blob and SHA256. RESULT.json is recomputed, not trusted as the answer. TASK.json preserves the original random allocation and refined scope. The prior author registered replay was run separately; its success is credited as imported validation. Delivered logs name the environment and any initial setup failures.

## Scope

No selected occurrence, clean physical helper, full supplier, or kappa claim. The threshold preserves the declared average-profile coverage hypothesis; additional physical work is not supplied.

## Open next questions

Expose exact common bilinear operand pairs in a selected source representation; event rank labels alone do not identify reusable products.

## Credit

Cinna / commdata2338 PR1872; Douglas Colkitt ceiling, Sagar Thakrar coverage, Rohan Arun and Jeremy Kothe selected lineage. Prepared by woklerx with substantial OpenAI Codex assistance. The checker is implementation-independent where stated, not independent human or proof-kernel review. New audit material is Apache-2.0; upstream source notices remain unchanged.
