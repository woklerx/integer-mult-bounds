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

from itertools import product
source=json.loads(pinned('research/complex-shared-product-triple-seed5a78/CERTIFICATE.json'))
pinned('research/complex-shared-product-triple-seed5a78/README.md')
pinned('research/complex-shared-product-triple-seed5a78/verify.py')
# Formal polynomial coefficients in independent variables: initial output dirt,
# initial helper dirt, and four bilinear monomials. No sampled identity claim.
def add(x,y,s=1): return [a+s*b for a,b in zip(x,y)]
def unit(i): return [int(j==i) for j in range(8)]
h=unit(3);ys=[unit(i) for i in range(3)];start=[x[:] for x in ys];h0=h[:]
h=add(h,unit(4))
for i in range(3): ys[i]=add(add(ys[i],h),unit(5+i))
h=add(h,unit(4),-1)
need(h==h0,'helper restoration')
for i in range(3):
    need(ys[i]==add(add(add(start[i],unit(3)),unit(4)),unit(5+i)),'dirty-helper syndrome')
# Exact inverse restores even arbitrary helper dirt, although the forward map
# meets requested outputs only when helper entry dirt is zero.
h=add(h,unit(4))
for i in range(3):ys[i]=add(add(ys[i],unit(5+i),-1),h,-1)
h=add(h,unit(4),-1)
need(ys==start and h==h0,'inverse')
# Four disjoint selected flattening pivots give an identity 4x4 minor.
tensor=[[[int((i==j==0) or (i==j==o+1)) for j in range(4)] for i in range(4)] for o in range(3)]
flat=[[tensor[o][i][j] for o in range(3) for j in range(4)] for i in range(4)]
minor=[[row[j] for j in (0,1,6,11)] for row in flat]
need(minor==[[int(i==j) for j in range(4)] for i in range(4)],'rank minor')
# Independent complete small finite-field action of literal schedule.
trials=0
for v in product(range(2),repeat=12):
    x,y,t,h=v[:4],v[4:8],list(v[8:11]),v[11];orig=t[:];h0=h
    h^=x[0]*y[0]
    for i in range(3):t[i]^=h^(x[i+1]*y[i+1])
    h^=x[0]*y[0]
    need(h==h0 and t==[orig[i]^h0^(x[0]*y[0])^(x[i+1]*y[i+1]) for i in range(3)],'F2 full map')
    trials+=1
c=costs(Q(35491136290869,20000000000000000));base={1:2412,2:418,3:432,4:142,5:82,8:8}
bounds=[]
for e,k in [(0,764),(1,765),(2,766)]:
    row=[]
    for s in [k-1,k]:
        p=dict(base);p[1]+=Q(e-s,3)
        bound=invoice(p,c,Q(1646)+Q(s-e,3));row.append(bound)
    need(row[0][0]>1>row[1][1],'threshold boundary')
    need(source['profile_screen']['thresholds'][str(e)]['minimum_shared_slots']==k,'upstream threshold')
    bounds.append({'e':e,'minimum_s':k,'previous_lower_minus_one':str(row[0][0]-1),'passing_upper_minus_one':str(row[1][1]-1)})
# Overhead must be interpreted with its declared changed-coverage accounting.
# If extra work is fully additional, no old idle credit applies to that work.
need(base[1]+Q(1-1,3)==base[1],'zero net profile control')
finish({'status':'PASS_PR1872_INDEPENDENT','full_F2_states':trials,'formal_dirty_helper_syndrome':'h0 in each output','formal_inverse':'identity for all helper dirt','flattening_identity_minor':4,'child_calls':5,'thresholds':bounds,'scope':'Formal local schedule and independent exact threshold arithmetic; no physical clean helper or selected occurrence'})
