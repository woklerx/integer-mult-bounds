# Cross-check exact frame optimization and dual bounds against exhaustive small models

Intentional independent review of [PR1186](https://github.com/CrocSwap/integer-mult-bounds/pull/1186) at `3855fd413a3ccfc31988033801b9648c25aee783`, starting from main `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.

The original exact variable-elimination and chain-dual routines are extracted without edits from the SHA256-pinned frames.py AST. A separate exhaustive oracle enumerates valid assignments over all 16 subspaces of F2^3. Across 60 three-variable chain models, five signed/large cost tables and four domain restrictions, 5,610 feasible assignments agree with the exact optimum and 240 integer dual bounds remain valid, including multipliers of magnitude 2^80. Changing the cancelling multiplier sign produces an invalid lower bound, and NaN multipliers are rejected.

## Reproduce

Requires Python 3.12+ and Git. Install NumPy 2.2.6 in an isolated environment for this exact-core audit. Fetch the exact predecessor object, then run from this artifact branch:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git 3855fd413a3ccfc31988033801b9648c25aee783
python -O -B research/frame-solver-independent-audit/audit.py
```

The checker recomputes its result and verifies each consumed source hash. SOURCES.json records Git blob and SHA256 pins. audit-result.json is the recorded output, not the acceptance oracle. The two modes produced identical output. Predecessor replay logs are separate imported validation and do not count as a code-disjoint checker.

## Scope

This covers the exact VE and dual core, not graph construction, the true-moment wrapper, every supplier word or floating heuristic convergence. The full upstream selftest cannot run on this Windows host because harness.py imports Unix-only resource. The exact core audit runs on Windows Python 3.12.7 with NumPy 2.2.6; no full upstream pass is claimed.

## Open next questions

Expose a platform-independent exact-core test entry point or guard the optional Unix resource limit, then run the unchanged full selftest on Windows and Linux. Preserve exact arithmetic and the original source/model contracts.

## Credit

Marius-Paul Dumitrean, PR1186 revision 2; chafreaky frame-domain model and other authors credited in the original NOTICE. AST execution tests the actual upstream algorithms; the oracle is independent.

Prepared by woklerx with substantial OpenAI Codex assistance. This is independent agent implementation where stated, not independent human review or formal proof-kernel verification. New audit code is Apache-2.0. No selected source, frozen input, or kappa changes.
