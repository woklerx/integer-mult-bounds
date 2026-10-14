from pathlib import Path
import hashlib,json,subprocess,sys
from fractions import Fraction as Q
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def need(ok,message):
    if not ok: raise RuntimeError(message)
def pinned(path):
    manifest=json.loads((HERE/'SOURCES.json').read_text(encoding='utf8'))
    row=next(x for x in manifest['files'] if x['path']==path)
    raw=subprocess.check_output(['git','show',manifest['source_head']+':'+path],cwd=ROOT)
    need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source bytes differ: '+path)
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    need(blob==row['git_blob'],'source Git blob differs: '+path)
    return raw
def finish(result):
    text=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if '--write' in sys.argv: (HERE/'RESULT.json').write_text(text,encoding='utf8')
    else: need(json.loads((HERE/'RESULT.json').read_text(encoding='utf8'))==result,'receipt mismatch')
    print(json.dumps(result,sort_keys=True))

import gzip,itertools
from collections import Counter
w=json.loads(gzip.decompress(pinned('research/r439-bsection-stars-seed01/candidate.json.gz')))
receipt=json.loads(pinned('research/bit-two-copy-scatter/CERTIFICATE.json'))
pinned('research/bit-two-copy-scatter/README.md')
supports=[set() for _ in w['ret']]
for target,cols in enumerate(w['scatter']):
    for col in cols:supports[col].add(target)
need(len(supports)==9,'nine retained totals')
inter=[[len(a&b) for b in supports] for a in supports]
need(inter==receipt['search']['intersection_matrix'],'intersection matrix independently rebuilt')
edges=list(itertools.combinations(range(9),2));dist=Counter();matchings=0
# Enumerate edge subsets, not predecessor's recursive set partitions/DP.
for k in range(5):
    for es in itertools.combinations(edges,k):
        flat=[v for e in es for v in e]
        if len(set(flat))!=2*k:continue
        dist[sum(inter[a][b]-2 for a,b in es)]+=1;matchings+=1
need(matchings==2620 and max(dist)==120 and dist[120]==105,'complete matching census')
need({str(k):v for k,v in dist.items()}==receipt['search']['saving_distribution'],'complete cost distribution')
# Independently replay each possible pair over free integer generators a,b,
# plus an independent initial generator for each output. Zero assumed nowhere.
checks=0;controls=0
for a,b in edges:
    A,B=supports[a],supports[b]
    y={t:[0,0,1] for t in A|B};p=[1,0,0];q=[0,1,0]
    def plus(x,z,s=1):return [i+s*j for i,j in zip(x,z)]
    for t in A-B:y[t]=plus(y[t],p)
    for t in B-A:y[t]=plus(y[t],q)
    p=plus(p,q)
    for t in A&B:y[t]=plus(y[t],p)
    need(p!=[1,0,0],'premature ERASE control');controls+=1
    p=plus(p,q,-1)
    need(p==[1,0,0] and q==[0,1,0],'chronological copy restoration')
    need(all(y[t]==[int(t in A),int(t in B),1] for t in y),'free-module dirty endpoint')
    need(plus(plus(p,q),q)!=p,'wrong restoration sign control');controls+=1
    checks+=len(y)
# Composition on disjoint copied-role blocks follows because each pair adds only
# the required output increments and returns both copies before the next block.
finish({'status':'PASS_PR1704_INDEPENDENT_SCATTER','matching_partitions':matchings,'optimum':120,'optima':105,'pair_blocks':36,'formal_output_checks':checks,'chronology_and_sign_controls':controls,'scatter_adds':[sum(map(len,supports)),sum(map(len,supports))-120],'scope':'All pair blocks over arbitrary commutative rings and complete restricted matching census; physical two-copy admission unproved'})
