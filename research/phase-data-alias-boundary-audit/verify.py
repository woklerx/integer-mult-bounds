#!/usr/bin/env python3
"""Independent current-main corroboration of known PR673 alias finding."""
import ast
import hashlib
import importlib.util
import json
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'research/dirty-prefix-precision'
def need(ok,message):
    if not ok: raise ValueError(message)
def run():
    for entry in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if entry['usage']=='input':
            need(hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()==entry['sha256'],'source drift')
    spec=importlib.util.spec_from_file_location('alias_vendor',SOURCE/'vendor/pr628/dirty.py')
    v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
    # This is the exact live caller predicate, not a newly supplied replacement.
    tree=ast.parse((SOURCE/'numeric.py').read_text())
    matches=[node for node in ast.walk(tree) if isinstance(node,ast.Call) and
             len(node.args)==2 and isinstance(node.args[1],ast.Constant) and
             node.args[1].value=='phase alias outside contract']
    need(len(matches)==1,'caller guard not unique')
    guard=compile(ast.Expression(matches[0].args[0]),'<pinned phase predicate>','eval')
    factor=[(False,(F(1,4),F(0)),F(1))]
    x=[v.c.ONE]*2; y=[v.c.ZERO]*2; initial=x.copy()
    v.compose(x,y,factor,[],x,F(1,2),4,1)
    need(x==[v.c.ONE,(F(15,16),F(0))] and x!=initial,'known silent alias witness')
    witness=dict(source_before=initial,source_after=x,target_after=y)
    positives=[]
    for bits in (4,8,16):
        for d in (-1,1):
            x=[v.c.ONE]*2; y=[(F(3,16),F(-1,16))]*2; phases=x.copy()
            before=[x.copy(),y.copy(),phases.copy()]
            need(eval(guard,{'phases':phases,'arrays':[x,y]}),'equal-valued disjoint rejected')
            v.compose(x,y,factor,[],phases,F(1,2),bits,d)
            need(x==before[0] and phases==before[2],'valid source/phase preservation')
            v.compose(x,y,factor,[],phases,F(1,2),bits,d,-1)
            need([x,y,phases]==before,'valid exact inverse')
            positives.append(dict(bits=bits,direction=d))
    rejected=[]
    arrays=[[v.c.ONE]*2 for _ in range(4)]
    for i,phases in enumerate(arrays):
        before=[a.copy() for a in arrays]
        need(not eval(guard,{'phases':phases,'arrays':arrays}),'caller admits aliased row')
        need(arrays==before,'predicate mutated inputs')
        rejected.append(i)
    return dict(status='PASS_KNOWN_PHASE_ALIAS_CORROBORATION',prior_pr=673,
                prior_head='0b4f514c60d9bc7786415d7cbc24754f24d6dc3b',
                exact_raw_witness=witness,disjoint_positive_cases=positives,
                live_caller_guard_rejects_rows=rejected,
                disposition='Known finding independently corroborated; no new PR recommended')
if __name__=='__main__':
    result=json.loads(json.dumps(run(),default=str)); receipt=HERE/'EXPECTED.json'
    if receipt.exists(): need(json.loads(receipt.read_text())==result,'receipt mismatch')
    print(json.dumps(result,indent=2,sort_keys=True))
