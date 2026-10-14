# Independent audit of PR1348's corrected complex-unbinding threshold

The repaired PR1348 head `74768ab408b1ae2ce2c7094b49457a86fcb06e94`
correctly locates the selected outer generator's **min-branch switch** at
`b = c_bit/(1-beta)`, with `beta=10^-24`. This is corroboration of Navinor's
repair, not a new threshold or a remaining error in that head. The historical
main review describes the earlier double-conversion error.

The independent oracle solves the bootstrap in closed form. For
`s=min(c_bit,(1-beta)b)-10^-27`, its seven-step endpoint is
`a7=s+(a0-s)s^7`, where `a0=384599/10^10`. Substituting this into the outer
margin and using integer quotient/remainder gives the largest grid point
strictly below the margin. The candidate instead uses seven iterative updates.
The switch condition follows before either calculation; all subsequent
operations preserve the branch's value at and above the switch.

The audit compares 315 candidate/oracle cases across three grids, including
101 inputs spaced `10^-30` around the switch. Six fixtures are passed through
the retained outer engine, independently checking every one of its 47 strict
slacks and agreement with the closed-form margin. The selected record's exact
kappa is reproduced. Omitting a bootstrap round, beta or the shave changes
the result and is rejected. A further control shows the grid output is already
constant immediately below the switch: equality of rounded kappa alone does
**not** establish that the bit branch is active.

The old value `c_bit/(1-c_bit)` is larger and is a different planning target.
The repaired threshold is exactly `1733427039589844234749/(10^24-1)`.

## Reproduce

```
python -B research/coupled-bit-ceiling-threshold/verify.py
python -B scripts/research_package.py --package research/coupled-bit-ceiling-threshold
```

The registered replay uses Python 3.12 and no dependencies. `UPSTREAM.json`
pins the exact candidate file by commit, Git blob and SHA256. The unchanged
candidate source is retained in `inputs/` for a self-contained comparison;
only its `assembly_reduction` function is executed. `SOURCES.json` binds the
current selected assembly and retained outer engine. The producer's complete
coverage-law threshold tables, supplier circuits, native execution, Lean and
full cold replay are outside this audit and are not claimed as rerun.

## Open next questions

Independently certify the corrected coverage-law relief tables using a
different exact moment enclosure. That would strengthen the remaining
arithmetic evidence; this audit deliberately covers only T2 conversion and
the coupled outer reduction. No physical interface improvement follows.

## Credit

Navinor with opencode assistance authored and repaired PR1348. The selected
assembly retains Rohan Arun, Jeremy Kothe and the full supplier lineage;
the outer engine credits eumemic, icekylinx, Zhihao Chen and the RaD project.
This independent audit was prepared by woklerx with substantial OpenAI Codex
assistance. Apache-2.0; no independent human review or new kappa is asserted.
