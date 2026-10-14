# Independently audit twisted helper compensation and cleanup

Intentional independent review of [PR1868](https://github.com/CrocSwap/integer-mult-bounds/pull/1868) at `6b222d01fee072bcd3a680e6a96ae7d22e13bcac`, starting from main `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.

A literal binary-matrix oracle checks all 6 helper twists and 168 raw three-coordinate invertible blocks. Its factored census validates 4,032 compensated tuples, rejects 12,096 wrong helper compensations and 168,336 wrong cleanup matrices, and detects 840 omitted-twist cleanups. Compensation and cleanup affect distinct output blocks, which is why their complete small-domain censuses can be factored. The full predecessor Python 3.12 registered replay passes on all four lineage words and both 661-column instances.

## Reproduce

Requires Python 3.12+ and Git. Only the Python standard library is used. Fetch the exact predecessor object, then run from this artifact branch:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git 6b222d01fee072bcd3a680e6a96ae7d22e13bcac
python -O -B research/twisted-contract-independent-audit/audit.py
```

The checker recomputes its result and verifies each consumed source hash. SOURCES.json records Git blob and SHA256 pins. audit-result.json is the recorded output, not the acceptance oracle. The two modes produced identical output. Predecessor replay logs are separate imported validation and do not count as a code-disjoint checker.

## Scope

The independent finite census checks the scalar equations only; it does not extend the chronological bridge to arbitrary cleanup words. The source proof, frame work, absorption census and full-word replay are credited to PR1868; native replay is an open predecessor obligation.

## Open next questions

A general non-literal cleanup still needs a chronological bridge. First specify one admitted full-frame cleanup and compare every cut, rather than treating endpoint equality as enough.

## Credit

Sagar Thakrar, PR1868; woklerx PR1194, Arham Tahir PR1311/1580/1592, Zhihao Chen PR425, eumemic PR555, Dylan Crow, Sricharan Vagvala, Gareth Davidson, Aaron Wang, Ross Richardson and DreamingOfClouds as credited in the pinned source.

Prepared by woklerx with substantial OpenAI Codex assistance. This is independent agent implementation where stated, not independent human review or formal proof-kernel verification. New audit code is Apache-2.0. No selected source, frozen input, or kappa changes.
