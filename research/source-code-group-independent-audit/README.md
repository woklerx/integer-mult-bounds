# Independently check dyadic source-code inversion and ordered composition

Intentional independent review of [PR1862](https://github.com/CrocSwap/integer-mult-bounds/pull/1862) at `7649d9ceecec949541bec4bbde5929344166ba59`, starting from main `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.

An exact Fraction implementation checks 1,728 distinct low-dimensional parameter cases for logger, fixed-support, inverse and ordered prelude-composition equations. It includes singular RK and RK-I, 384 singular G cases, and 1,104 cases with dyadic inverses. It explicitly distinguishes rational invertibility from a dyadic unit: inverse(3)=1/3 is outside the allowed ring. Dropping RP=I breaks the construction. The pinned complete local cold replay independently executes on this machine: all 712 formal input columns and 4,096 new native Gaussian columns pass.

## Reproduce

Requires Python 3.12+ and Git. Only the Python standard library is used. Fetch the exact predecessor object, then run from this artifact branch:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git 7649d9ceecec949541bec4bbde5929344166ba59
python -O -B research/source-code-group-independent-audit/audit.py
```

The checker recomputes its result and verifies each consumed source hash. SOURCES.json records Git blob and SHA256 pins. audit-result.json is the recorded output, not the acceptance oracle. The two modes produced identical output. Predecessor replay logs are separate imported validation and do not count as a code-disjoint checker.

## Scope

The low-dimensional census corroborates the general written proof; it is not that proof. The 112-field cold replay uses the predecessor implementation. Global chart restoration, recursive hosting and complete supplier pricing remain unverified here.

## Open next questions

Construct an actual routed chart transition preserving the stored source query and explicitly price its inverse. The local algebra does not provide global restoration.

## Credit

Ali Romman, PR1862. Native/source lineage and license notices are retained by reference to the exact original package; no source is copied or relicensed.

Prepared by woklerx with substantial OpenAI Codex assistance. This is independent agent implementation where stated, not independent human review or formal proof-kernel verification. New audit code is Apache-2.0. No selected source, frozen input, or kappa changes.
