"""Closed-form audit of corrected PR1348. Apache-2.0; woklerx / OpenAI Codex."""
import ast
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BETA = ETA = Q(1, 10**24)
SHAVE = Q(1, 10**27)
A0 = Q(384599, 10**10)


def require(ok, why):
    if not ok:
        raise ValueError(why)


def oracle(b, c, grid=Q(1, 10**18)):
    # Closed-form solution, independent of the candidate's seven-step loop.
    gap = (1-BETA)*b-c
    s = c + min(gap, Q(0)) - SHAVE
    a = s + (A0-s)*s**7
    q = a*(1-2*ETA)
    margin = (1-ETA)*q/(1+q)
    ticks, rem = divmod(margin.numerator*grid.denominator,
                        margin.denominator*grid.numerator)
    return (ticks-(rem == 0))*grid, margin, ('bit' if gap >= 0 else 'complex'), a


def main():
    pins = json.loads((HERE/'UPSTREAM.json').read_text())
    raw = (HERE/'inputs/PR1348-verify.py').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == pins['sha256'], 'candidate bytes')
    require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pins['git_blob'], 'candidate Git blob')
    for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if pin['usage'] == 'input':
            require(hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest() == pin['sha256'], 'input '+pin['path'])
    nodes = [n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == 'assembly_reduction']
    require(len(nodes) == 1, 'candidate function')
    ns = dict(Q=Q, BETA=BETA, ETA=ETA, SHAVE=SHAVE, BOOT_A0=A0, BOOT_STEPS=7, require=require)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(HERE/'inputs/PR1348-verify.py'), 'exec'), ns)
    candidate = ns['assembly_reduction']
    rec = json.loads((ROOT/'research/community-frontier1094-audit/ASSEMBLY.json').read_text())
    b, c = Q(rec['complex_lower']), Q(rec['bit_lower'])
    threshold = c/(1-BETA)
    retired = c/(1-c)
    fixtures = [b, c, threshold, retired] + [threshold+Q(i,10**30) for i in range(-50,51)]
    comparisons = 0
    for bb in fixtures:
        for grid in (Q(1,10**18), Q(1,10**24), Q(1,10**30)):
            require(candidate(bb,c,grid) == oracle(bb,c,grid)[:3], 'closed-form/candidate disagreement')
            comparisons += 1
    require(oracle(b,c)[0] == Q(rec['kappa']), 'selected kappa replay')
    require(oracle(threshold-Q(1,10**30),c)[2] == 'complex', 'below switch')
    require(oracle(threshold,c)[2] == 'bit', 'at switch')
    require(oracle(threshold+Q(1,10**30),c)[2] == 'bit', 'above switch')
    require(retired > threshold, 'retired target must differ')
    require(oracle(threshold-Q(1,10**30),c)[0] == oracle(threshold,c)[0], 'grid plateau control')
    for key, value in [('BOOT_STEPS', 6), ('BETA', Q(0)), ('SHAVE', Q(0))]:
        saved = ns[key]; ns[key] = value
        require(candidate(b,c,Q(1,10**30)) != oracle(b,c,Q(1,10**30))[:3], 'mutated '+key+' must fail')
        ns[key] = saved
    outer_path = ROOT/'research/complex-sw4-frame8/vendor/main/research/complex-k492-owner-repair/vendor/multicold/engines/outer.py'
    spec = importlib.util.spec_from_file_location('retained_outer', outer_path)
    outer = importlib.util.module_from_spec(spec); spec.loader.exec_module(outer)
    bridge = {'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},
              'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}}
    outer_cases = 0
    for bb in (b, c, threshold-Q(1,10**30), threshold, threshold+Q(1,10**30), retired):
        k, margin, _, a = oracle(bb,c)
        out = outer.assembly(a,bb,bridge,k,eta=ETA,beta=BETA)
        require(len(out['strict_constraints']) == 47 and min(out['strict_constraints'].values()) > 0, 'outer constraints')
        require(out['minimum_margin'] == margin, 'independent margin binding')
        outer_cases += 1
    for ticks in (Q(3), Q(7,2), Q(399,100)):
        n,r = divmod(ticks.numerator,ticks.denominator)
        below = n-(r == 0)
        require(Q(below) < ticks <= Q(below+1), 'strict floor')
    result = dict(status='PASS_CORRECTED_PR1348_OUTER_AUDIT', upstream_head=pins['commit'],
                  comparisons=comparisons, outer_cases=outer_cases, strict_constraints_per_case=47,
                  corrected_threshold=str(threshold), retired_threshold=str(retired),
                  source_bit_endpoint=str(c), selected_kappa=str(oracle(b,c)[0]),
                  controls=['below/equal/above min switch','retired double conversion differs',
                            'grid plateau does not imply bit branch','strict grid integer boundary',
                            'omitted bootstrap round','zero beta','omitted shave'],
                  scope='Corrected T2 binding and outer reduction only; no coverage threshold tables or supplier replay.')
    if (HERE/'EXPECTED.json').exists():
        require(json.loads((HERE/'EXPECTED.json').read_text()) == result, 'receipt drift')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
