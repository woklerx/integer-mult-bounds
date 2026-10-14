# Independently certify the S3 two-target census in the faithful regular representation

Intentional independent review of [PR1870](https://github.com/CrocSwap/integer-mult-bounds/pull/1870) at `538d194e69420a6a773612e0b5ad0c94575f8aaa`, starting from main `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.

A separately implemented 12-by-12 binary regular-representation search reproduces all 13,664 radius-five states, layers 1/12/80/466/2345/10760, all 36 exact target minima and 108 omitted-call failures. Every state is checked to lie in the faithful group-algebra image. A nonzero formal sum of all six group elements vanishes in the natural three-dimensional permutation representation; the regular representation correctly distinguishes it. The previously unavailable Python 3.12 registered replay also passes.

## Reproduce

Requires Python 3.12+ and Git. Only the Python standard library is used. Fetch the exact predecessor object, then run from this artifact branch:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git 538d194e69420a6a773612e0b5ad0c94575f8aaa
python -O -B research/s3-regular-independent-audit/audit.py
```

The checker recomputes its result and verifies each consumed source hash. SOURCES.json records Git blob and SHA256 pins. audit-result.json is the recorded output, not the acceptance oracle. The two modes produced identical output. Predecessor replay logs are separate imported validation and do not count as a code-disjoint checker.

## Scope

Finite two-register S3 transposition alphabet only. No extra-register bound, rational-address transfer, supplier, or new kappa. The predecessor owns the original census and theorem.

## Open next questions

Try a third restored dirty register only after deriving a bounded target and workload; the present 13,664-state census proves no such extension.

## Credit

Cinna Davis, PR1870; the scalar-idempotent model and its predecessor credit remain in the pinned source.

Prepared by woklerx with substantial OpenAI Codex assistance. This is independent agent implementation where stated, not independent human review or formal proof-kernel verification. New audit code is Apache-2.0. No selected source, frozen input, or kappa changes.
