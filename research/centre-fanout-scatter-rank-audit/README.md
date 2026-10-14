# The selected centre scatter makes source agreement necessary

An independent extraction of the selected emitted centre phase gives **176 nonzero scatter edges on 88 target rows**, with rational scatter matrix S of size 88 by 8 and **column rank eight**. Eight explicit target rows form a minor of determinant **-1/16384**. Gaussian elimination and a separate 40,320-term Leibniz determinant sum agree.

This sharpens the interface interpretation of Cinna Davis's PR1708 two-panel fanout. Let z_k be the difference between the separate and reused output of centre k, expressed in the same chart for that centre. The complete second-panel error is `(S tensor I) z`. The displayed invertible minor proves this error is zero **if and only if every z_k is zero**. Indeed, restricting to its eight target rows and multiplying by its rational inverse recovers each z_k. This works over any rational vector space, without a dimension limit.

If the common centre map T_k is injective, z_k=T_k(x_k^B-x_k^A) vanishes exactly when the two source inputs agree. Thus the eight source-agreement assumptions cannot be relaxed by relying on cross-centre cancellation in the selected scatter. Injectivity is an explicit premise: frame rank eight alone is not a proof of operator injectivity. For singular maps the exact requirement is output agreement, which the singular-map control demonstrates.

The checker reads the actual pinned emitted LOCAL-PROGRAMS archive; it does not call PR1708's parser, runner or transforms. It checks every scalar coefficient, a 64-column tensor disagreement basis, eight omitted-column controls and a singular-map countercontrol. It separately verifies the matching-source zero-error case. RESULT.json contains the selected source registers, minor target rows and exact matrix.

The supplied PR1708 registered replay passed separately. Its private zero-clear convention is not upgraded here into restoration of arbitrary borrowed dirty centre state. No selected invocation pair, chart transformation, owner schedule, precision/compiler admission, full cold replay or new kappa is claimed.

## Reproduce

`python3.12 scripts/research_package.py --package research/centre-fanout-scatter-rank-audit`

`python3 -I -O -B research/centre-fanout-scatter-rank-audit/verify.py`

Expected: `PASS_CENTRE_SCATTER_RANK targets=88 edges=176 rank=8 det=-1/16384`.

## Open next questions

Do any selected invocations share the necessary eight source functionals in compatible charts? A feasible first step is to compare those functionals at candidate call boundaries, using the extracted source list. The blocker is global scheduling and its complete cost, not a further scatter census.

## Credit

Cinna Davis PR1708; Rohan Arun selected PR1094; retained gauge44-slots-t16 provider lineage. Prepared for woklerx with substantial OpenAI Codex assistance. Apache-2.0. No independent human or proof-assistant review is claimed.
