# Independently certify PR1605 rank-one block thresholds and overhead bills

Intentional independent audit of [PR1605](https://github.com/CrocSwap/integer-mult-bounds/pull/1605), exact head `488f2ecf1835c6d813e96543656dddf0062fdc9a`. This is a corroborating review/handoff, not a new supplier or selected-frontier change.

Required Python 3.12 registered replay passes. Independent fixed-point log/exp enclosures certify adjacent signs for all 50 caps and fully added rank-one overhead limits, 1275 strict concentration exchanges, 50 block-tax inequalities, and rank16 extra-mass boundary 10/11. Wrong idle credit demonstrably gives a false pass.

## Reproduction

Start from main checkpoint `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. The independent checker imports no predecessor executable; it reads only declared exact Git objects. Fetch the reviewed head before replay:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git 488f2ecf1835c6d813e96543656dddf0062fdc9a
python -I -O -B research/pr1605-independent-budget-audit/verify.py
```

Python3.12 standard library only. Normal replay writes no result files; --write explicitly regenerates the deterministic receipt.

SOURCES.json binds every consumed source by exact Git blob and SHA256. RESULT.json is recomputed, not trusted as the answer. TASK.json preserves the original random allocation and refined scope. The prior author registered replay was run separately; its success is credited as imported validation. Delivered logs name the environment and any initial setup failures.

## Scope

Independent arithmetic is target-specific; the all-q concavity argument remains a written proof. No physical block decoder, inherited all-size/hosting admission or new kappa.

## Open next questions

Find a chronological group whose complete additional work fits the narrow rank16 budget; optimistic rank profiles do not construct that group.

## Credit

Arham Tahir PR1605; Douglas Colkitt PR1240, Sagar Thakrar PR1012, Rohan Arun PR1094/1042, Jeremy Kothe, Hao Yan and retained supplier lineage. Prepared by woklerx with substantial OpenAI Codex assistance. The checker is implementation-independent where stated, not independent human or proof-kernel review. New audit material is Apache-2.0; upstream source notices remain unchanged.
