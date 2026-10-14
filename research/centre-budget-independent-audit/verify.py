#!/usr/bin/env python3
"""Independent PR1791 budget audit: dyadic rational powers, no logarithm/Taylor engine.
Prepared for woklerx with OpenAI Codex assistance. Apache-2.0.
"""

from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from math import isqrt
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
S = 1 << 384
BITS = 128
CERT = "research/community-frontier1094-audit/ASSEMBLY.json"
CERT_SHA = "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045"


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def ceildiv(a, b):
    return (a + b - 1) // b


def csqrt(n):
    r = isqrt(n)
    return r + (r * r < n)


@lru_cache(None)
def power(base, a):
    """For base>=1 and 0<=a<1, repeated outward square roots and products."""
    base, a = Q(base), Q(a)
    need(base >= 1 and 0 <= a < 1, "power domain")
    lo = base.numerator * S // base.denominator
    hi = ceildiv(base.numerator * S, base.denominator)
    roots = []
    for _ in range(BITS):
        lo, hi = isqrt(lo * S), csqrt(hi * S)
        roots.append((lo, hi))
    k = a.numerator * (1 << BITS) // a.denominator

    def product(j):
        if j == 1 << BITS:
            return (
                base.numerator * S // base.denominator,
                ceildiv(base.numerator * S, base.denominator),
            )
        l = h = S
        for bit, (ll, hh) in enumerate(roots):
            if (j >> (BITS - 1 - bit)) & 1:
                l, h = l * ll // S, ceildiv(h * hh, S)
        return l, h

    return Q(product(k)[0], S), Q(product(k + 1)[1], S)


def residual(hist, a):
    lo = hi = Q(-1)
    for r, n in hist.items():
        l, h = power(Q(73, r), a)
        lo += Q(n * r, 73 * 14336) * l
        hi += Q(n * r, 73 * 14336) * h
    return lo, hi


def mutate(h, r, n):
    out = dict(h)
    out[r] = out.get(r, 0) + n
    need(out[r] >= 0, "negative count")
    return out


def check_input_pins():
    for row in json.loads((HERE / "SOURCES.json").read_bytes())["files"]:
        if row["usage"] == "input":
            need(
                sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                "pinned input drift: " + row["path"],
            )
    need(
        sha256((HERE / "PREDECESSOR-RESULT.json").read_bytes()).hexdigest()
        == json.loads((HERE / "DEPENDENCY.json").read_bytes())["retained_input"][
            "sha256"
        ],
        "predecessor receipt drift",
    )


def main():
    check_input_pins()
    raw = (ROOT / CERT).read_bytes()
    need(sha256(raw).hexdigest() == CERT_SHA, "certificate source drift")
    asm = json.loads(raw)
    h = {int(r): n for r, n in asm["complex_profile"].items()}
    receipt = json.loads((HERE / "PREDECESSOR-RESULT.json").read_bytes())
    selected, bit = Q(asm["complex_lower"]), Q(asm["bit_lower"])
    grid = Q(1, 10**24)
    signs = []

    def accept(hist, a, label):
        lo, hi = residual(hist, a)
        need(hi < 0, label + " not accepted")
        signs.append([label, "negative", str(lo), str(hi)])

    def reject(hist, a, label):
        lo, hi = residual(hist, a)
        need(lo > 0, label + " not rejected")
        signs.append([label, "positive", str(lo), str(hi)])

    accept(h, selected, "selected endpoint")
    reject(h, selected + grid, "next endpoint grid")
    for row in receipt["k_sharing"]:
        k = row["k"]
        need(1152 % k == 0, "integer sharing domain")
        g = dict(h)
        g[8] = 1152 // k
        need(
            sum(r * n for r, n in g.items()) == 72 * 14336 + 64 * 144 // k,
            "coverage law",
        )
        for rank, budget in row["overhead_budget_full_gain"].items():
            r = int(rank)
            x = budget["total"]
            accept(mutate(g, r, x), bit, f"k{k}/r{r}/max")
            reject(mutate(g, r, x + 1), bit, f"k{k}/r{r}/max+1")
    g = dict(h)
    g[8] = 576
    for row in receipt["two_call"]["budgets"]:
        r = row["rank"]
        for field, a in [("full_gain_total", bit), ("any_gain_total", selected + grid)]:
            x = row[field]
            accept(mutate(g, r, x), a, f"r{r}/{field}/max")
            reject(mutate(g, r, x + 1), a, f"r{r}/{field}/max+1")
    for row in receipt["complex_saving_to_reach_bit_cap"]:
        r, x = row["rank"], row["children_removed"]
        accept(mutate(h, r, -x), bit, f"remove{r}/min")
        reject(mutate(h, r, 1 - x), bit, f"remove{r}/min-1")
    # Mathematical calibration independent of every receipt.
    for d in range(1, 73):
        lo, hi = power(Q(73, d), Q(1, 2))
        need(lo * lo <= Q(73, d) <= hi * hi, "square-root calibration")
    need(mutate(g, 8, 576) == h, "undo sharing control")
    reject(mutate(g, 8, 576), selected + grid, "undo full sharing")
    # A deliberately overreported budget must fail acceptance for every table row.
    faults = 0
    for row in receipt["two_call"]["budgets"]:
        lo, _ = residual(mutate(g, row["rank"], row["full_gain_total"] + 1), bit)
        need(lo > 0, "overbudget escaped")
        faults += 1
    out = {
        "status": "PASS_INDEPENDENT_CENTRE_BUDGET",
        "source_pr": 1791,
        "source_head": "00d05a64898571cf57a14310fbcd3507ca99c5ec",
        "exact_sign_checks": len(signs),
        "sharp_overbudget_controls": faults,
        "root_calibrations": 72,
        "k2_rank1_budget": 4415,
        "k2_rank8_budget": 553,
        "method": "128-bit dyadic exponent brackets and outward integer square roots at 384-bit precision; no predecessor arithmetic imports",
        "signs": signs,
        "limits": "Complex-side overhead tables and minimum-removal thresholds only. Supplied package replay separately covers outer bootstrap, bit surcharge target and scalar guard.",
    }
    target = HERE / "RESULT.json"
    if "--write" in __import__("sys").argv:
        target.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    else:
        need(json.loads(target.read_bytes()) == out, "receipt differs")
    print(out["status"], f"signs={len(signs)} controls={faults} calibrations=72")


if __name__ == "__main__":
    main()
