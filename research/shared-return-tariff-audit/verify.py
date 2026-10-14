#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact audit by woklerx with substantial OpenAI Codex assistance."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product, permutations
from math import isqrt
import json, hashlib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def require(ok, message):
    if not ok: raise ValueError(message)
def source_check():
    for row in json.loads((HERE/'EXTERNAL-SOURCES.json').read_text()):
        b=(HERE/row['local']).read_bytes()
        require(hashlib.sha256(b).hexdigest()==row['sha256'],'external source bytes')
        require(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob'],'external Git blob')
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            require(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'live source bytes')
source_check()

import tarfile,gzip
archive=ROOT/'research/community-frontier1094-audit/selected-replay.tar.gz'
member='candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz'
with tarfile.open(archive,'r:gz') as tar: program=json.loads(gzip.decompress(tar.extractfile(member).read()))['backward']
start=program.index(['phase','centers'])+1
end=next((i for i in range(start,len(program)) if program[i][0]=='phase'),len(program))
phase=program[start:end]
require(len(phase)==208,'reverse phase length')
blocks=[];sinks=[]
for k in range(8):
    b=phase[k*26:(k+1)*26]
    require(b[0]==['scalar',['clear',['C',k]],0],'initial CLEAR')
    require(b[-1]==['scalar',['clear',['C',k]],415+k],'final CLEAR')
    require(b[-3]==['center',k,0,415+k,8],'rank-eight return')
    require(b[-2][1][0]=='add' and b[-2][1][2]==['C',k] and b[-2][1][3:]==[-1,1],'source subtraction')
    require(b[-2][1][1][0]=='L' and b[-2][1][1][1]>=0 and not 112<=b[-2][1][1][1]<224,'source and panel disjoint')
    sinks.append(b[-2][1][1][1])
    gathers=[]
    for e in b[1:23]:
        op=e[1];require(e[0]=='scalar' and op[:2]==['add',['C',k]] and e[2]==0,'gather grammar')
        gathers.append((op[2][1]-112,F(op[3],op[4])))
    require(len({j for j,c in gathers})==22 and all(0<=j<112 for j,c in gathers),'panel ports')
    require(sum(abs(c) for j,c in gathers)==F(11,2),'positive envelope')
    blocks.append(gathers)
require(len(set(sinks))==8,'eight distinct shared source sinks')
# A separate sparse-polynomial endpoint interpreter at scalar identity operators.
def replay(fused,initial_clear=True,final_clear=True,omit_read=False):
    state=[{i:F(1)} for i in range(240)]
    def add(t,s,c):
        for j,v in list(state[s].items()):state[t][j]=state[t].get(j,F(0))+c*v
        state[t]={j:v for j,v in state[t].items() if v}
    for k,row in enumerate(blocks):
        groups=[[0,1]] if fused else [[0],[1]]
        for group in groups:
            if initial_clear:state[232+k]={}
            for panel in group:
                for idx,(j,c) in enumerate(row):
                    if not (omit_read and k==0 and panel==1 and idx==0):add(232+k,8+112*panel+j,c)
            add(k,232+k,F(-1))
            if final_clear:state[232+k]={}
    return state
base_map=replay(False);fused_map=replay(True)
require(base_map==fused_map,'all 240 dirty symbolic inputs')
for kwargs in [{'initial_clear':False},{'final_clear':False},{'omit_read':True}]:require(replay(True,**kwargs)!=base_map,'semantic fault control')
single={'R8':sum(e[0]=='center' for e in phase),'ADD':sum(e[0]=='scalar' and e[1][0]=='add' for e in phase),'CLEAR':sum(e[0]=='scalar' and e[1][0]=='clear' for e in phase)}
separate={k:2*v for k,v in single.items()};fused={'R8':single['R8'],'ADD':2*sum(map(len,blocks))+len(blocks),'CLEAR':single['CLEAR']}
require(sum(separate.values())==416 and sum(fused.values())==384,'full macro invoice')
# Uniform degree-p tariffs: common positive multiplier cancels exactly.
# Ratio ((mu+1)/mu)^p strictly decreases, so threshold and predecessor exclude all smaller positive integers.
thresholds=[]
for p in range(1,17):
    mu=1
    while 13*mu**p<=12*(mu+1)**p:mu+=1
    require(13*(mu-1)**p<=12*mu**p and 13*mu**p>12*(mu+1)**p,'sharp tariff threshold')
    slack=416*mu**p-384*(mu+1)**p
    require(slack>0,'strict overhead allowance')
    thresholds.append({'degree':p,'first_mu':mu,'overhead_strictly_below':slack})
# Independent literal billing versus expanded mixed-degree polynomial for a bounded tariff grid.
mixed=0
for p,alpha,beta,gamma,mu in product(range(1,5),[1,2,8],[1,3],[0,1],range(1,65)):
    separate_cost=16*alpha*mu**p+368*beta*mu+32*gamma*mu
    fused_cost=8*alpha*(mu+1)**p+360*beta*(mu+1)+16*gamma*(mu+1)
    polynomial=8*alpha*(2*mu**p-(mu+1)**p)+(8*beta+16*gamma)*mu-360*beta-16*gamma
    require(separate_cost-fused_cost==polynomial,'mixed tariff polynomial')
    mixed+=1
# The lower macro count is not itself a saving under quadratic width cost at mu=13.
require(416*13**2<384*14**2,'macro-count false inference control')
require(thresholds[0]['first_mu']==13,'linear predecessor calibration')
receipt=json.loads(json.dumps({'status':'PASS_SHARED_RETURN_TARIFF_AUDIT','source_phase_start':start-1,'source_macros':len(phase),'source_gathers':sum(map(len,blocks)),'separate':separate,'fused':fused,'all_dirty_symbolic_columns':240,'homogeneous_tariff_thresholds':thresholds,'mixed_tariff_cases':mixed,'controls':4,'no_native_tariff_or_caller_admission':True,'no_new_kappa':True},sort_keys=True))
require(receipt==json.loads((HERE/'RESULT.json').read_text()),'committed audit receipt differs from recomputation')
print(json.dumps(receipt,sort_keys=True))
