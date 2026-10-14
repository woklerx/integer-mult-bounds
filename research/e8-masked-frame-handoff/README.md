# Spanning-frame handoff for factor-linear masked decoders

This is a verified complementary handoff, not a proposed PR. The relevant live
work includes PR1191 (one-sided rigidity), PR1213 (P112 component), PR1292
(all P104 local rigidity), PR1389 (P111 and selected P104 global rigidity), and
PR1180 (arbitrary-term factor-linear all-pairs floor). Their stronger overlapping
work makes another factor-linear rigidity package a poor use of review time.
All are provisional pending contributions, not selected construction evidence.

**Exact implication.** Let R contain the live E8 roots in the standard norm-two
normalization. Suppose D=RA and T=RB with any finite column count, and the masked
identity DT^t=2RR^t holds on every ordered orthogonal pair and every diagonal.
If the live roots contain one complete orthogonal frame F, restriction gives
F(AB^t-2I)F^t=0. Since F is invertible, AB^t=2I; consequently the identity holds
on every live pair. Complex coefficients and arbitrary term count cause no
change to this argument. The assumption that BOTH factors lie in the live root
code is essential; arbitrary masked completions need not satisfy it.

**Independent bounded evidence.** research/e8-masked-frame-handoff/verify.py enumerates all 2025 E8
orthogonal frames from the doubled-coordinate root definition, all1260 second
frames disjoint from the canonical frame, and all131040 further one-port
deletions. Every resulting P103 set retains an intact frame. Thus the implication
applies to all1260 P104 frame-pair domains and every such P103 domain. An exact
rank-one perturbation witnesses that omitting a required ordered cross-entry
from the frame constraints invalidates the short proof.

Reproduce from this worktree with Python3.12+: `python -I -B research/e8-masked-frame-handoff/verify.py`.
It is also checked under `-O`. The output witness digest is frozen in
EVIDENCE.json. No source module is imported and no source file is changed.

The useful next question is an unrestricted factor space, or a live domain with
no complete frame. Check existing PR1360 (single odd-entry rank-nine completion)
and PR1316 (one odd rectangle) before selecting a specific new support alphabet.
No new kappa, helper inventory, physical realization, all-size or formal proof
claim is made. Geometry and mask convention: DreamingOfClouds PR717,
themilkman216 PR968, and woklerx PR1077. Prepared for woklerx with substantial
OpenAI Codex assistance; Apache-2.0.

## Open next questions

The structured next question and its overlap blockers are recorded in TASK.json.
