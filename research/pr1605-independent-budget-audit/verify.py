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

# Independent fixed-point enclosure; no predecessor arithmetic is imported.
S=1<<160
def up(n,d): return (n+d-1)//d
def mul(a,b): return (a[0]*b[0]//S,up(a[1]*b[1],S))
def log_ratio(n,d):
    need(n>=d>0,'log domain')
    z=(S*(n-d)//(n+d),up(S*(n-d),n+d))
    zz=mul(z,z); p=z; lo=hi=0
    for j in range(2000):
        lo+=p[0]//(2*j+1);hi+=up(p[1],2*j+1);p=mul(p,zz)
    tail=up(p[1]*S,4001*(S-zz[1]))
    return (2*lo,2*(hi+tail))
def exp_small(x):
    need(0<=x[0]<=x[1]<S,'exp domain')
    p=(S,S);lo=hi=S
    for j in range(1,60):
        p=mul(p,x);p=(p[0]//j,up(p[1],j));lo+=p[0];hi+=p[1]
    # next term ratio <=x/60; all subsequent ratios smaller.
    nxt=up(p[1]*x[1],60*S)
    tail=up(nxt*60*S,60*S-x[1])
    return (lo,hi+tail)
def costs(a):
    out={}
    for r in range(1,52):
        l=log_ratio(73,r)
        x=(l[0]*a.numerator//a.denominator,up(l[1]*a.numerator,a.denominator))
        e=exp_small(x)
        out[r]=(Q(r*e[0],73*S),Q(r*e[1],73*S))
    return out
def invoice(profile,c,idle=Q(1646)):
    return tuple((sum(Q(n)*c[r][i] for r,n in profile.items())+idle*c[51][i]/51)*Q(9,896) for i in [0,1])

source=json.loads(pinned('research/complex-rank-one-block-budget/RESULT.json'))
pinned('research/complex-rank-one-block-budget/README.md');pinned('research/complex-rank-one-block-budget/verify.py')
a=Q(source['target']);need(a==Q(35491136290869,20000000000000000),'target')
c=costs(a);base={1:2412,2:418,3:432,4:142,5:82,8:8}
def prof(k,B):
    p=dict(base);p[1]-=k;n,r=divmod(k,B);p[B]=p.get(B,0)+n
    if r:p[r]=p.get(r,0)+1
    return p
rows=[]
for row in source['rows']:
    B=row['cap'];k=row['minimum_replaced'];e=row['all_rank1_reblocked_extra_rank1_max']
    prev=invoice(prof(k-1,B),c);win=invoice(prof(k,B),c)
    need(prev[0]>1>win[1],'adjacent threshold '+str(B))
    p=prof(2412,B);p[1]+=e;ok=invoice(p,c);p[1]+=1;bad=invoice(p,c)
    need(ok[1]<1<bad[0],'fully additional overhead '+str(B))
    # In rank-one units, adding one call to a fused block loses for all caps.
    need((B+0)*c[1][1] < c[B][0]+c[1][0],'per-block extra child erases saving')
    rows.append({'cap':B,'minimum_replaced':k,'max_extra_unit_calls':e})
# Every pair of non-full blocks can be improved by moving mass to the larger.
# Explicit strict exchange checks supply a finite target-specific corroboration
# of the README's all-q concavity proof.
exchanges=0
for x in range(1,51):
    for y in range(x,51):
        after=(c[x-1][1] if x>1 else 0)+c[y+1][1]
        need(after<c[x][0]+c[y][0],'concentration exchange')
        exchanges+=1
p=prof(2412,16);basecost=invoice(p,c)
need(basecost[1]+c[10][1]*Q(9,896)<1,'rank-ten additional mass')
need(basecost[0]+c[11][0]*Q(9,896)>1,'rank-eleven additional mass')
# Omitting a charge produces a false pass at first excluded unit overhead.
p[1]+=11
need(invoice(p,c)[0]>1,'honest added overhead rejection')
need(invoice(p,c,Q(1646)-11)[1]<1,'wrong idle-credit control')
finish({'status':'PASS_PR1605_INDEPENDENT_BUDGET','cap_rows':rows,'strict_concentration_exchanges':exchanges,'per_block_tax_controls':50,'rank16_max_extra_mass':10,'wrong_idle_credit_false_pass':True,'scope':'Exact target-specific intervals and concentration checks; no physical block decoder or new kappa'})
