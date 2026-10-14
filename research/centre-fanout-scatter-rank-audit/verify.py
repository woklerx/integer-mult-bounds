#!/usr/bin/env python3
"""Independent exact scatter-rank audit of PR1708's source-agreement boundary.
Prepared for woklerx with OpenAI Codex assistance. Apache-2.0.
"""

from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip, json, tarfile, sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
PREFIX = "candidate/strict/global/base/providers/gauge44/"


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def eliminate(rows):
    a = [list(map(Q, row)) for row in rows]
    ids = list(range(len(a)))
    piv = []
    rank = 0
    for c in range(len(a[0])):
        pivot = next((r for r in range(rank, len(a)) if a[r][c]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        ids[rank], ids[pivot] = ids[pivot], ids[rank]
        p = a[rank][c]
        a[rank] = [v / p for v in a[rank]]
        for r in range(len(a)):
            if r != rank and a[r][c]:
                p = a[r][c]
                a[r] = [v - p * w for v, w in zip(a[r], a[rank])]
        piv.append(ids[rank])
        rank += 1
    return rank, piv


def determinant(rows):
    a = [list(map(Q, row)) for row in rows]
    det = Q(1)
    for c in range(len(a)):
        p = next((r for r in range(c, len(a)) if a[r][c]), None)
        if p is None:
            return Q(0)
        if p != c:
            a[c], a[p] = a[p], a[c]
            det = -det
        v = a[c][c]
        det *= v
        for r in range(c + 1, len(a)):
            q = a[r][c] / v
            a[r] = [x - q * y for x, y in zip(a[r], a[c])]
    return det


def matvec(a, x):
    return [sum((u * v for u, v in zip(row, x)), Q(0)) for row in a]


def check_input_pins():
    for row in json.loads((HERE / "SOURCES.json").read_bytes())["files"]:
        if row["usage"] == "input":
            need(
                sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                "pinned input drift: " + row["path"],
            )


def main():
    check_input_pins()
    need(sha256(ARCHIVE.read_bytes()).hexdigest() == ARCHIVE_SHA, "archive drift")
    with tarfile.open(ARCHIVE) as tar:
        raw = tar.extractfile(PREFIX + "LOCAL-PROGRAMS.json.gz").read()
        ops = json.loads(gzip.decompress(raw))["forward"]
    rows = {}
    sources = []
    edges = []
    for i, event in enumerate(ops):
        if event[0] != "center":
            continue
        k = event[1]
        need(k == len(sources), "centre order")
        copy = ops[i - 1]
        need(
            copy[0] == "scalar" and copy[1][0] == "copy" and copy[1][1] == ["C", k],
            "copy boundary",
        )
        sources.append(copy[1][2][1])
        j = i + 1
        while ops[j][0] == "scalar" and ops[j][1][0] == "add":
            add = ops[j][1]
            need(add[2] == ["C", k] and add[1][0] == "L", "scatter shape")
            target = add[1][1]
            coef = Q(add[3], add[4])
            rows.setdefault(target, [Q(0)] * 8)[k] += coef
            edges.append((target, k, coef))
            j += 1
        need(
            ops[j][0] == "scalar"
            and ops[j][1][0] == "clear"
            and ops[j][1][1] == ["C", k],
            "centre clear",
        )
    need(sources == [92, 57, 81, 224, 11, 240, 9, 256], "selected source list")
    ids = sorted(rows)
    matrix = [rows[t] for t in ids]
    rank, piv = eliminate(matrix)
    need(rank == 8 and len(edges) == 176, "selected scatter rank/edge count")
    minor = [matrix[i] for i in piv]
    det = determinant(minor)
    need(det != 0, "selected 8x8 minor")
    # Independent determinant evaluation by all permutations (8! terms).
    import itertools

    det2 = Q(0)
    for perm in itertools.permutations(range(8)):
        value = Q(
            (-1) ** sum(perm[i] > perm[j] for i in range(8) for j in range(i + 1, 8))
        )
        for i, j in enumerate(perm):
            value *= minor[i][j]
        det2 += value
    need(det2 == det, "Leibniz determinant cross-check")
    # Every centre-coordinate disagreement is visible; same-source case gives zero.
    detected = 0
    for k in range(8):
        for coord in range(8):
            z = [[Q(int(j == k and c == coord)) for c in range(8)] for j in range(8)]
            image = [
                [sum((row[j] * z[j][c] for j in range(8)), Q(0)) for c in range(8)]
                for row in matrix
            ]
            need(any(any(y) for y in image), "source basis disagreement hidden")
            detected += 1
    need(not any(matvec(matrix, [Q(0)] * 8)), "matching source positive control")
    # Essential hypothesis controls: deleting a whole centre column hides that difference;
    # a singular common centre map can hide a nonzero input even with full-rank scatter.
    for k in range(8):
        bad = [row[:k] + [Q(0)] + row[k + 1 :] for row in matrix]
        x = [Q(int(j == k)) for j in range(8)]
        need(not any(matvec(bad, x)), "column omission control")
    singular = [[Q(int(i == j and i != 7)) for j in range(8)] for i in range(8)]
    need(not any(matvec(singular, [Q(0)] * 7 + [Q(1)])), "injectivity control")
    out = {
        "status": "PASS_CENTRE_SCATTER_RANK",
        "source_pr": 1708,
        "source_head": "4d163c04c0980c5b0e9092fbd5864c7cfadc125d",
        "source_registers": sources,
        "target_registers": ids,
        "targets": len(ids),
        "scatter_edges": len(edges),
        "scatter_rank": rank,
        "minor_targets": [ids[i] for i in piv],
        "minor": [[str(x) for x in row] for row in minor],
        "minor_determinant": str(det),
        "disagreement_basis_controls": detected,
        "omitted_centre_controls": 8,
        "singular_map_control": 1,
        "theorem": "For a common vector space and arbitrary centre output discrepancies z0,...,z7, all panel discrepancies vanish iff every zk is zero. For injective common centre maps this is equivalent to equality of the eight source inputs.",
        "limits": "The tensor statement requires the same chart per centre across panels. No existence of such paired invocations, dirty borrowed-centre restoration, native precision or new supplier is established.",
    }
    target = HERE / "RESULT.json"
    if "--write" in sys.argv:
        target.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    else:
        need(json.loads(target.read_bytes()) == out, "receipt mismatch")
    print(out["status"], f"targets={len(ids)} edges=176 rank=8 det={det}")


if __name__ == "__main__":
    main()
