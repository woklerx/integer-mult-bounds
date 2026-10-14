# Full-inventory corroboration of the selected manifest commitment boundary

Aaron Wang's PR1864 already identifies the selected manifest's missing independent commitment. This audit reproduces that exact limitation on the **actual 1,579-file, 13-root selected inventory**, rather than a minimal synthetic inventory. The unchanged production `check()` accepts a private copy in which `research/complex-sw4-frame8/code/assemble.py` is replaced with an intentional failure and its manifest digest is updated consistently, while the selected record remains byte-identical.

The experiment uses ordinary file copies in a contained temporary directory. Seven cases cover the original snapshot, an unaccompanied source mutation, a coherent source-plus-manifest mutation, certificate/proof controls and a concrete hypothetical repair. All original live source hashes are checked again afterward and remain unchanged. RESULT.json records the exact immutable manifest digest and mutation target.

**Additional repair evidence:** the existing `proof_supplements` mapping can already anchor the manifest. Adding `source_manifest` with the original manifest SHA-256 to a private in-memory copy of that mapping accepts the original snapshot and rejects the coherent rewrite with `Selected proof supplement changed`. A new verifier field is therefore not required to express this commitment. No real selected record or frozen source is edited by this package.

This is a boundary of the fast inventory-consistency check, not evidence that the committed sources are corrupt or that an upstream theorem fails. The selected record and checker remain roots of trust. A full cold replay, native admission, source-level mathematical audit and threat model are outside scope. The existing proof/certificate digest controls reject their mutations as expected.

## Reproduce

`python3.12 scripts/research_package.py --package research/selected-manifest-full-inventory-audit`

`python3 -I -O -B research/selected-manifest-full-inventory-audit/verify.py`

Expected: `PASS_FULL_SELECTED_MANIFEST_AUDIT files=1579 roots=13 cases=7 live_unchanged=True`.

The explicit replay input list includes every file copied for the actual inventory experiment, so changes to those files select this package. The selected record, manifest and production checker are pinned to the current-main base in SOURCES.json.

## Open next questions

Should a maintainer anchor SELECTED-SOURCE.json through the existing supplement mapping or introduce an explicit field? First reconcile packages that pin the selected-record bytes, then review an authorized update using the exact digest in RESULT.json. Maintainer authorization and downstream pin reconciliation are the blockers; this audit intentionally makes no selection update.

## Credit

Aaron Wang/Navinor PR1864, exact head `3d54b62bee5e7e2027aaffd9a30c31adc3b84c0a`; Douglas Colkitt selected-checker implementation and the selected construction authors. Prepared for woklerx with substantial OpenAI Codex assistance. Apache-2.0. The missing commitment is predecessor work; the full selected-input corroboration and existing-format repair fixture are this audit's added evidence.
