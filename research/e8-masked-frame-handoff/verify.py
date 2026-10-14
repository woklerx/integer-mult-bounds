"""Independent finite check of the spanning-frame masked decoder handoff.
Prepared for woklerx with substantial OpenAI Codex assistance; Apache-2.0.
"""
from itertools import combinations, product
from pathlib import Path
import hashlib, json

def need(x, message):
    if not x: raise ValueError(message)

def main():
    roots=set()
    for i,j in combinations(range(8),2):
        for a,b in product((-2,2),repeat=2):
            v=[0]*8;v[i]=a;v[j]=b
            roots.add(max(tuple(v),tuple(-x for x in v)))
    for v in product((-1,1),repeat=8):
        if sum(x<0 for x in v)%2==0:roots.add(max(v,tuple(-x for x in v)))
    roots=sorted(roots);n=len(roots)
    need(n==120,'root count')
    dot=lambda a,b:sum(x*y for x,y in zip(a,b))
    adjacency=[sum((i!=j and dot(a,b)==0)<<j for j,b in enumerate(roots)) for i,a in enumerate(roots)]
    def frames(prefix, available):
        if len(prefix)==8:yield tuple(prefix);return
        if available.bit_count()<8-len(prefix):return
        while available:
            bit=available&-available;available-=bit;i=bit.bit_length()-1
            yield from frames(prefix+[i],available&adjacency[i])
    all_frames=list(frames([], (1<<n)-1))
    need(len(all_frames)==2025,'complete frame count')
    masks=[sum(1<<i for i in f) for f in all_frames]
    f0=[]
    for i in range(0,8,2):
        for sign in (-1,1):
            v=[0]*8;v[i]=2;v[i+1]=2*sign;f0.append(roots.index(tuple(v)))
    m0=sum(1<<i for i in f0)
    seconds=[m for m in masks if not m&m0]
    need(len(seconds)==1260,'P112 frame count')
    # A finite independent coverage check: each P104 frame-pair deletion,
    # and every further single deletion, still leaves an orthogonal basis.
    witnesses=[]
    for m1 in seconds:
        removed=m0|m1;survivors=[m for m in masks if not m&removed]
        need(survivors,'intact frame')
        for i in range(n):
            if removed>>i&1:continue
            witness=next((m for m in survivors if not m>>i&1),None)
            need(witness is not None,'single-port survivor')
            witnesses.append([str(m1),i,str(witness)])
    need(len(witnesses)==131040,'bounded domain')
    # Identity on an intact orthogonal frame fixes every entry of M, since
    # F F^t = 8 I in doubled coordinates. Dropping a cross constraint permits
    # F^t e_0 e_1^t F, an exact failure control.
    f=[roots[i] for i in all_frames[0]]
    perturb=[[f[0][i]*f[1][j] for j in range(8)] for i in range(8)]
    evaluations=[[sum(f[a][i]*perturb[i][j]*f[b][j] for i in range(8) for j in range(8)) for b in range(8)] for a in range(8)]
    need(evaluations[0][1]==64 and sum(x!=0 for row in evaluations for x in row)==1,'cross-constraint control')
    result={'status':'PASS_MASKED_SPANNING_FRAME_HANDOFF','frames':len(all_frames),'P104_domains':1260,'P103_domains':len(witnesses),'witness_sha256':hashlib.sha256(json.dumps(witnesses,separators=(',',':')).encode()).hexdigest(),'control':'Dropping a required ordered frame cross-entry admits a nonzero perturbation.'}
    print(json.dumps(result,indent=2))
    need(result==json.loads(Path(__file__).with_name('EVIDENCE.json').read_text()), 'complete receipt comparison')

if __name__=='__main__':main()
