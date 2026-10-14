# Independent shared-return invoice and precision-tariff audit

PR1748 by @ToikY supplies a conditional shared reverse-centre phase. This audit independently parses its selected source events, verifies its scalar endpoint and determines exact break-even precision widths for a declared family of tariffs. It does not establish an eligible selected caller pair or an actual native price.

## Source binding and independent check

The unchanged selected-replay archive contains the backward centres phase starting at event 12550. Its eight blocks contain 208 macros and 176 signed quarter-coefficient gathers. This parser checks each block's initial/final CLEAR, rank8 ascent, source subtraction, 22 distinct panel ports and positive coefficient envelope11/2. From the literal grammar it reconstructs two-phase counts (16 R8,368 ADD,32 CLEAR) and fused counts (8 R8,360 ADD,16 CLEAR). All352 reads of the two panels remain charged.

A separate sparse-polynomial interpreter compares all 240 scalar input columns: eight sinks, two112-row panels and eight arbitrary scratch rows. It matches the separate and fused endpoint at identity scalar return operators, including zero scratch at exit. This is an independent scalar control; the predecessor's written linearity argument supplies the arbitrary common-operator implication. It is not a 512-dimensional native replay. Removing an initial CLEAR, a final CLEAR, or one panel read each changes the full endpoint.

## Exact tariff frontier

The inherited local envelope guard prices the fused phase at width mu+1. Suppose, solely for this tariff experiment, every macro has cost c*mu^p for common c>0 and positive integer p. Then a saving with overhead H requires

    H < c [416 mu^p -384(mu+1)^p].

For zero overhead, this is exactly 13 mu^p>12(mu+1)^p. The ratio (1+1/mu)^p strictly decreases with positive mu, so checking the first passing integer and its predecessor proves the complete integer threshold. The first widths for p=1,2,3,4 are13,25,37,50. The verifier certifies p=1..16 and records the exact strictly permitted overhead at each first passing width. The p=1,mu=13 result is the predecessor's illustrative tariff and is explicitly a calibration, not a new claim. In particular mu=13 loses under quadratic width cost despite384<416.

For a separately declared mixed tariff R8(mu)=alpha*mu^p, ADD(mu)=beta*mu, CLEAR(mu)=gamma*mu, the exact saving before added overhead is

    8 alpha [2 mu^p-(mu+1)^p]
       +(8 beta+16 gamma)mu -360 beta -16 gamma.

Independent literal invoices agree with that expression for 3072 cases (p1..4, alpha in1,2,8, beta in1,3, gamma in0,1, mu1..64). This finite grid is not a universal claim about native costs. The symbolic formula follows by subtraction.

## Reproduce and limits

    python3.12 scripts/research_package.py --package research/shared-return-tariff-audit

Standard-library exact arithmetic, read-only, explicit checks under -O. Source archive SHA256/Git blob and predecessor statement are pinned. The addition is a source-bound independent invoice and exact declared-tariff threshold certificate. PR1748 already states that actual tariffs and extra overhead are required. No defect is alleged. No common post-A sinks, physical hosting, actual prefix precision, rounded-child correctness, full-call recurrence, cold replay or new kappa is certified.

## Open next questions

Do native child/scalar tariffs satisfy this guarded inequality for an actual eligible pair? First bind its common sinks/operators and instantiate the three tariffs plus all additional preparation/routing/hosting costs. Those two obligations remain blockers; macro counts alone cannot resolve them.

## Credit

@ToikY / PR1748 supplies the selected backward binding and guard, Cinna Davis /1337isnot1337 /PR1708 the forward fanout, Sagar Thakrar /PR751 common-target batching, Ryan Haines /PR830 the adjoint and prefix warning, and Scratch-net the private-centre/CLEAR audit. Selected construction lineage remains credited. New audit prepared for woklerx with substantial OpenAI Codex assistance, Apache-2.0; no independent human or formal review claimed.
