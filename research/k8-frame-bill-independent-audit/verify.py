#!/usr/bin/env python3
"""Independent literal event-chain billing audit of PR1671's selected baseline.
No predecessor frame model, subspace routine or numeric engine is imported.
Prepared for woklerx with OpenAI Codex assistance. Apache-2.0.
"""

from collections import Counter
from hashlib import sha256
from functools import lru_cache
from pathlib import Path
import gzip, json, sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/r480-owner-optimum/inputs/local/FULL-WORD.json.gz"
WORD_SHA = "c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8"
EXPECTED = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


@lru_cache(None)
def span(basis):
    values = {0}
    for v in basis:
        need(type(v) is int and 0 <= v < 512, "vector range")
        values |= {x ^ v for x in list(values)}
    return frozenset(values)


def dim(values):
    n = len(values)
    need(n > 0 and not n & (n - 1), "power-of-two span")
    return n.bit_length() - 1


def bill(w, omit_source=False, omit_centres=False, omit_ends=False):
    v, R, h = w["report"]["v"], w["report"]["R"], w["report"]["h"]
    need((v, R, h) == (112, 480, 9), "selected size")
    n = 2 * v + R
    full = frozenset(range(512))
    zero = frozenset([0])
    start = [span((p,)) for p in w["ports"]] + [zero] * (v + R)
    for q, f in w["start_extra"].items():
        start[int(q)] = span(tuple(f))
    end = (
        [full] * v
        + [
            frozenset(x for x in range(512) if (x & p).bit_count() % 2 == 0)
            for p in w["ports"]
        ]
        + [full] * R
    )
    for q, f in w["helper_final"].items():
        end[int(q)] = span(tuple(f))
    current = list(start)
    stages = {}
    events = 0
    omitted = False
    climbs = []

    def advance(q, next_frame, label):
        need(current[q] <= next_frame, f"non-nested frame at {label} role{q}")
        d = dim(next_frame) - dim(current[q])
        current[q] = next_frame
        if d:
            stages.setdefault(label, Counter())[d] += 1
            climbs.append([label, q, d])

    def phase(ops, label):
        nonlocal events, omitted
        stages.setdefault(label, Counter())
        for e in ops:
            need(e[0] in ("add", "scale"), "primitive kind")
            regs = e[1:3] if e[0] == "add" else e[1:2]
            need(len(regs) == len(set(regs)), "aliased operands")
            f = span(tuple(e[-1]))
            events += 1
            for j, q in enumerate(regs):
                if omit_source and j == 1 and not omitted and current[q] < f:
                    omitted = True
                    current[q] = f
                    continue
                advance(q, f, label)

    phase(w["A"], "A")
    pins = {q: span(tuple(f)) for q, f in zip(w["centers"], w["center_frames"])}
    target_levels = {int(q): span(tuple(f)) for q, f in w["target_levels"].items()}
    for t in range(v):
        pins[v + t] = target_levels.get(t, zero)
    for q, f in pins.items():
        advance(q, f, "boundary-pins")
    centre = Counter()
    for q, frame in zip(w["centers"], w["center_frames"]):
        previous = span(tuple(frame))
        served = {target_levels.get(e[1] - v, zero) for e in w["cut"] if e[2] == q}
        for target in sorted(served, key=lambda f: -len(f)):
            need(target <= previous, "centre descent order")
            d = dim(previous) - dim(target)
            if d:
                centre[d] += 1
            previous = target
    if not omit_centres:
        stages["centres"] = centre
    phase(w["B"], "B")
    indices = [row[0] for row in w["early_cleanup"]]
    need(len(indices) == len(set(indices)), "duplicate early cleanup")
    phase(
        [w["cleanup"][i][:-1] + [frame] for i, frame in w["early_cleanup"]],
        "early-cleanup",
    )
    if not omit_ends:
        for q, f in enumerate(end):
            advance(q, f, "final-climbs")
    total = Counter()
    for x in stages.values():
        total.update(x)
    endpoint_mass = sum(dim(e) - dim(s) for s, e in zip(start, end))
    return dict(
        profile=dict(sorted(total.items())),
        stages={k: dict(sorted(c.items())) for k, c in stages.items()},
        gate_events=events,
        endpoint_mass=endpoint_mass,
        centre_mass=sum(r * n for r, n in centre.items()),
        paid_climbs=len(climbs) + sum(centre.values()),
        omission_reached=omitted,
    )


def check_input_pins():
    for row in json.loads((HERE / "SOURCES.json").read_bytes())["files"]:
        if row["usage"] == "input":
            need(
                sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                "pinned input drift: " + row["path"],
            )


def main():
    check_input_pins()
    raw = gzip.decompress((ROOT / WORD).read_bytes())
    need(sha256(raw).hexdigest() == WORD_SHA, "word drift")
    w = json.loads(raw)
    result = bill(w)
    need(result["profile"] == EXPECTED, "literal paid profile")
    need(result["gate_events"] == 5413, "complete gate count")
    mass = sum(r * n for r, n in result["profile"].items())
    need(
        mass == result["endpoint_mass"] + result["centre_mass"] == 5586,
        "telescoping mass",
    )
    controls = []
    for label, kwargs in [
        ("source-operand", {"omit_source": True}),
        ("centre-charge", {"omit_centres": True}),
        ("final-climbs", {"omit_ends": True}),
    ]:
        mutant = bill(w, **kwargs)
        need(mutant["profile"] != EXPECTED, "missing coverage escaped: " + label)
        controls.append(
            {"mutation": label, "profile": mutant["profile"], "rejected": True}
        )
    # Same dimension is insufficient: use an incomparable line in a frame incidence.
    x = span((1,))
    y = span((2,))
    need(dim(x) == dim(y) and not x <= y, "containment versus dimension control")
    out = {
        "status": "PASS_LITERAL_K8_BILL",
        "source_pr": 1671,
        "source_head": "ce130d291f5ab6dd801544886a16f62d42d86118",
        "word_sha256": WORD_SHA,
        **result,
        "rank_mass": mass,
        "semantic_controls": controls,
        "incomparable_equal_dimension_control": True,
        "limits": "Independent literal baseline invoice and telescoping-mass check; not an independent proof of the complete free-frame domains or dual inequalities. Supplied primary and independent dual checkers are replayed separately.",
    }
    path = HERE / "RESULT.json"
    if "--write" in sys.argv:
        path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    else:
        need(
            json.loads(path.read_bytes()) == json.loads(json.dumps(out)),
            "receipt mismatch",
        )
    print(
        out["status"],
        f"events=5413 children={result['paid_climbs']} mass={mass} controls=4",
    )


if __name__ == "__main__":
    main()
