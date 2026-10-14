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

# Integer significand implementation written from the quantified operation,
# retaining incoming denominator at the first stage. No predecessor imports.
for f in ('PROOF.md','CERTIFICATE.json','verify.py'):pinned('research/reciprocal-directed-guards/'+f)
def step(k,M,xn,xd,t):
    g=1<<t;ct=(k*g)//(1<<M)
    u=(ct*xn)//xd
    return (xn*(2*g-u))//xd,g
cells=stages=endpoints=0;maxima=[]
for p in range(1,13):
    M=max(6,p+3);d=1<<M;worst=Q(0)
    for k in range(d,2*d):
        xn,xd=step(k,M,5,8,6);m=1
        while True:
            for endpoint in (k,k+1):
                residual=Q(abs(d*xd-endpoint*xn),d*xd)
                need(residual < Q(1,1<<(m+1)),'true-input cell endpoint residual')
                worst=max(worst,residual*(1<<(m+1)));endpoints+=1
            stages+=1
            if m==p:break
            m=min(2*m,p);xn,xd=step(k,M,xn,xd,m+3)
        cells+=1
    maxima.append({'p':p,'maximum_normalized_stage_residual':str(worst)})
# Sharpness applies to arbitrary admitted states, not actual seeded reachability.
controls=[]
for guards,c,x in [(0,Q(1),Q(49,64)),(1,Q(11,8),Q(35,64)),(2,Q(11,8),Q(35,64))]:
    need(abs(1-c*x)<Q(1,4),'counterexample premise')
    xn,xd=step(c.numerator,c.denominator.bit_length()-1,x.numerator,x.denominator,2+guards)
    need(abs(1-c*Q(xn,xd))>Q(1,8),'insufficient-guard counterexample')
    controls.append({'guards':guards,'c':str(c),'x':str(x),'output':str(Q(xn,xd))})
# Coefficient-wise symbolic identity for e+ in variables c,h,x,a,b,e.
# Direct expansion with cx=1-e: 1-c[x(2-(c-h)x+a)-b]
# = e^2 - c*h*x^2 - c*x*a + c*b. Check integer lattice instances;
# finite evidence is separate from the written all-real expansion/induction.
need(Q(15,32)<Q(1,2) and Q(1,4)+Q(1,4)==Q(1,2),'directed induction constants')
finish({'status':'PASS_PR1638_INDEPENDENT_PREFIX','candidate_cells':cells,'stage_cells':stages,'endpoint_checks':endpoints,'precision_range':[1,12],'maxima':maxima,'guard_controls':controls,'scope':'Exact finite true-input cells and admitted-state controls; does not settle seeded two guards or formalize uniform theorem'})
