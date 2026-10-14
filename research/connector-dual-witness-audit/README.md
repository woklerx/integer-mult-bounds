# Supply independent dual witnesses for all 144 single-connector cap obstructions

Intentional independent review of [PR1775](https://github.com/CrocSwap/integer-mult-bounds/pull/1775) at `b3b03a65d340bfdf2335a850c526eed733b603df`, starting from main `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.

Instead of elimination or comparing rank totals, the checker enumerates each rank-eight cap annihilator and gives an explicit input vector with nonzero dual parity. It emits 144 source/cap witness tuples covering all 36 blocks, separately verifies the 288 two-port input incidences, and confirms six 256-vector joins and thirty 512-vector joins. All 511 hyperplanes and their 512 membership queries are checked; compatible-cap and deficient-cap mutations fail. The complete predecessor Python 3.12 registered replay passes.

## Reproduce

Requires Python 3.12+ and Git. Only the Python standard library is used. Fetch the exact predecessor object, then run from this artifact branch:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git b3b03a65d340bfdf2335a850c526eed733b603df
python -O -B research/connector-dual-witness-audit/audit.py
```

The checker recomputes its result and verifies each consumed source hash. SOURCES.json records Git blob and SHA256 pins. audit-result.json is the recorded output, not the acceptance oracle. The two modes produced identical output. Predecessor replay logs are separate imported validation and do not count as a code-disjoint checker.

## Scope

Only the all-eight-input sole-carrier class with the specified output incidences is excluded. These certificates do not exclude multiple accumulators, direct source delivery, changed output caps or other schedules outside the proof premises.

## Open next questions

Test a two-carrier partition against the literal output-cap incidence constraints. A scalar rank split alone is insufficient; each input and each required output contribution must have a legal route.

## Credit

Cinna Davis, PR1775, and the complex-block-rank-optimum source and credited predecessor frame work.

Prepared by woklerx with substantial OpenAI Codex assistance. This is independent agent implementation where stated, not independent human review or formal proof-kernel verification. New audit code is Apache-2.0. No selected source, frozen input, or kappa changes.
