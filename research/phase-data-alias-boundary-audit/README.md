# Current-main corroboration of PR673's phase-alias finding

**Known result; local handoff, no new PR recommended.** The assigned audit
reproduced a silent source-restoration failure in the frozen PR628 prototype,
then the overlap search identified the exact same example and guard patch in
[PR673](https://github.com/CrocSwap/integer-mult-bounds/pull/673), inspected at
head `0b4f514c60d9bc7786415d7cbc24754f24d6dc3b`. This package retains a small
independent current-main replay and traces the retained caller boundary.

## Exact result and caller distinction

In `research/dirty-prefix-precision/vendor/pr628/dirty.py`, call `compose` with
one outside factor b=1/4, scale1; beta=1/2; bits4; direction+1;
source x=[1,1], target y=[0,0], no scratch, and `phases is x`.
Every explicit entry check accepts: arrays are distinct, the input phase
entries have unit norm, all data lie on the grid and the factor is stable.
The call returns x=[1,15/16] and y=[-5/16,-5/16], silently losing exact source
restoration. A separate phase list with the same values restores x exactly.

The failure has a short exact explanation. During the positive scan the
source's second entry becomes5/4. Because it also supplies the phase, the
coefficient read during inverse restoration is now5/16 instead of1/4.
The source becomes5/4-5/16=15/16. Increasing precision does not fix those exact
dyadic values. This violates the prototype's immutable/nonaliased phase
precondition; it is not a counterexample under that precondition.

The current retained `dirty-prefix-precision/numeric.py` already calls
`core.need(not any(phases is arr for arr in arrays), 'phase alias outside contract')`
before invoking the prototype, and constructs a separate phase list. Its
PROOF.md explicitly requires immutable nonaliased phase/factor data. The
verifier extracts and evaluates that exact pinned caller predicate: it rejects
source, target and each scratch alias, while accepting equal-valued distinct
lists. No selected supplier acceptance gap is established.

## Reproduction and boundaries

```sh
python -O -B research/phase-data-alias-boundary-audit/verify.py
python scripts/research_package.py --package research/phase-data-alias-boundary-audit
```

The raw negative fixture, six disjoint-phase positive/inverse cases over
bits4,8,16 and both orientations, and four live caller-predicate alias controls
are exact Fraction computations. Source files are bound before import by
SHA256; all transitive prototype imports and the caller/proof are pinned in
[SOURCES.json](SOURCES.json). The caller guard check is deliberately narrow:
it evaluates the actual predicate, not the complete expensive precision suite.
No source patch is applied, no archived file is changed and no cold supplier
replay is claimed. [EXPECTED.json](EXPECTED.json) records the corroboration.

The shared fully paginated863-PR/112-discussion snapshot identified exact
overlap after the minimal witness; the proposed new-result claim was released.
The older forty-round scopes did not contain this finding, but PR673 does.
Root may use this as a corroborating review note on that existing contribution.
Repeated discovery does not justify another PR.

## Open next questions

No new research question is justified by this replay: PR673 already supplies
the guard repair, and the retained caller already enforces nonaliasing. If
the callable prototype is ever promoted beyond frozen historical evidence,
review the existing patch and its provenance instead of creating another fix.

## Credit

PR673 owns the prior alias finding/patch. Chafik Boukhalfa's PR628 supplies the
rounded cyclic inverse prototype; Gareth Davidson's dirty-prefix-precision
package supplies the current wrapper and explicit retained assumption. Ali
Romman's PR621 and the preserved source NOTICE retain kernel attribution.
This corroboration was prepared by woklerx with substantial OpenAI Codex
assistance, Apache-2.0. No independent human review or new theorem is claimed.
