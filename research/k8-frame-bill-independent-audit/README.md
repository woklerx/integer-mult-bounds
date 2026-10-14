# Independent literal baseline invoice for the complete k8 frame ceiling

The baseline invoice in Gareth Davidson's PR1671 is independently reproduced from the exact selected word: **5,413 scalar gate events, 3,494 paid children and rank mass 5,586**. The paid histogram is `{1:2412,2:418,3:432,4:142,5:82,8:8}`. This is a corroborating audit and an explicit per-phase invoice, not a new frame-optimality theorem.

The new checker imports no predecessor frame, graph, LP or numeric routines. It enumerates F2 spans as explicit sets, advances each operand register through A, fixed boundary pins, B, early cleanup and its final frame, and checks containment before charging every dimension jump. It separately recounts the eight centre descents. The direct endpoint telescope gives 5,522 climb units plus 64 centre units. RESULT.json supplies the separate A/B/early-cleanup/final-climb histograms.

Three omission controls reject an uncharged source-operand climb, omitted centre work, and omitted final climbs. An equal-dimension but incomparable-line control checks why dimension equality alone is insufficient. These controls concern billing and incidence; they are not a substitute for the complete free-frame feasibility proof.

The full supplied PR1671 registered package was also replayed on Python 3.12: its primary and separately implemented 23,004-column / 135-component dual checks pass, as do all 14 control groups, including native baseline/all-upper audits on all 704 columns in both orientations. This audit distinguishes those supplied-checker passes from the new code-disjoint literal invoice. It does **not** independently reconstruct every LP dual inequality or establish optimality at other exponents.

The fixed-word scope, selected sources and kappa remain unchanged. No full global cold replay or complete multiplication theorem is claimed.

## Reproduce

`python3.12 scripts/research_package.py --package research/k8-frame-bill-independent-audit`

`python3 -I -O -B research/k8-frame-bill-independent-audit/verify.py`

Expected: `PASS_LITERAL_K8_BILL events=5413 children=3494 mass=5586 controls=4`.

The separate complete predecessor replay requires the exact PR1671 package at `ce130d291f5ab6dd801544886a16f62d42d86118` and runs `python3.12 scripts/research_package.py --package research/selected-k8-frame-ceiling`.

## Open next questions

Can one actual scalar rewrite or changed endpoint contract evade the fixed-word obstruction? State the changed operation and its full paid profile before optimizing frames. Neither the predecessor theorem nor this audit covers that changed interface; finding such a change remains the blocker.

## Credit

Gareth Davidson PR1671; Navinor retained X4 frame method; the selected local-word, source-reconciliation and ceiling authors credited by PR1671. Prepared for woklerx with substantial OpenAI Codex assistance. Apache-2.0. No independent human review claimed.
