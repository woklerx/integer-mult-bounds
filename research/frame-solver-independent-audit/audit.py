"""Exhaustive small-model audit of PR1186's exact VE and chain-dual core."""
import ast,collections,itertools,json,pathlib,hashlib,subprocess,types,math,time
from fractions import Fraction as Q
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent
def need(c,m):
    if not c:raise ValueError(m)
def source(path):
    p=json.loads((HERE/'SOURCES.json').read_text())['files'][path]
    b=subprocess.check_output(['git','show',p['head']+':'+path],cwd=HERE)
    need(hashlib.sha256(b).hexdigest()==p['sha256'],'source mismatch');return b
def space(b):
    s={0}
    for v in b:s|={x^v for x in tuple(s)}
    return frozenset(s)
def leq(a,b):return space(a)<=space(b)
def load_core(raw):
    tree=ast.parse(raw); names={'ChainDD','solve_component_ve'}
    selected=[x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name in names]
    need(len(selected)==2,'target AST scope')
    ns={'np':np,'Q':Q,'leq':leq,'collections':collections,'time':time,'Graph':object,'Costs':object}
    exec(compile(ast.Module(body=selected,type_ignores=[]),'<pinned-frame-core>','exec'),ns)
    return ns
def graph(domains,topology):
    g=types.SimpleNamespace();g.varset=set(range(3));g.var=list(range(3));g.dom=dict(enumerate(domains));g.nodes=[([0,1],(),'',0)]*3;g.prev={};g.nxt={};g.chains=[]
    for r,mids in enumerate(topology):
        s=len(g.nodes);g.nodes.append(([r],(),'',0));e=len(g.nodes);g.nodes.append(([r],(1,2,4),'',0))
        ch=[s,*mids,e];g.chains.append(ch)
        for a,b in zip(ch,ch[1:]):g.prev[b,r]=a;g.nxt[a,r]=b
    return g
def brute(g,c):
    best=None;count=0
    for a in itertools.product(*(g.dom[k] for k in range(3))):
        f=lambda k:a[k] if k<3 else g.nodes[k][1]
        if not all(leq(f(j),f(k)) for (k,r),j in g.prev.items()):continue
        total=sum(c[len(f(k))-len(f(j))] for (k,r),j in g.prev.items());count+=1
        if best is None or total<best:best=total
    need(best is not None,'no oracle fixture');return best,count
def main():
    raw=source('research/exact-frame-toolkit/frames.py').decode();core=load_core(raw)
    reps={}
    for n in range(4):
        for b in itertools.combinations(range(1,8),n):
            s=space(b)
            if len(s)==1<<n:reps.setdefault(s,b)
    domains=sorted(reps.values());need(len(domains)==16,'F2^3 subspaces')
    tops=[[[0,1],[0,2],[1,2]],[[0,1,2],[0],[1,2]],[[0,2],[0,1],[1,2]]]
    weights=[(0,9,14,17),(0,1,4,9),(0,-3,-8,-15),(0,1000000000007,2000000000001,3000000000000),(0,5,5,5)]
    instances=assignments=dual_checks=0;mutations=0
    for top,mode,w in itertools.product(tops,range(4),weights):
        ds=[domains if mode==0 else [f for f in domains if not f or len(f)==3 or (sum(f)+k+mode)%3] for k in range(3)]
        g=graph(ds,top);c=dict(enumerate(w));co=types.SimpleNamespace(c=c,vec=np.array([*w,0,0,0,0,0,0],dtype=float),mu_shift=0)
        opt,count=brute(g,c);assignments+=count;instances+=1
        got,a=core['solve_component_ve'](g,co,[0,1,2]);need(got==opt,'VE differs from exhaustive optimum')
        f=lambda k:a[k] if k<3 else g.nodes[k][1]
        need(all(leq(f(j),f(k)) for (k,r),j in g.prev.items()),'VE infeasible witness')
        need(sum(c[len(f(k))-len(f(j))] for (k,r),j in g.prev.items())==opt,'VE primal bill')
        dd=core['ChainDD'](g,co)
        for scale in (0,1,-7,1<<80):
            mu={k:[scale*(i-2) for i in range(len(g.dom[k]))] for k in dd.mu}
            bound=dd.dual_bound_exact(mu);need(bound<=opt,'invalid exact dual');dual_checks+=1
        # Wrong multiplier sign must invalidate weak duality on positive constant multipliers.
        if not mutations:
            need(raw.count('x - m[a]')==1,'mutation site changed')
            mutant=load_core(raw.replace('x - m[a]','x + m[a]'))['ChainDD'](g,co)
            mu={k:[1<<80]*len(g.dom[k]) for k in mutant.mu}
            need(mutant.dual_bound_exact(mu)>opt,'sign mutation not detected');mutations+=1
            dd.mu[next(iter(dd.mu))][0]=np.nan
            try:dd.exact_multipliers()
            except ValueError:pass
            else:raise ValueError('NaN multiplier admitted')
            mutations+=1
    return {'status':'PASS_INDEPENDENT_FRAME_CORE_AUDIT','numpy':np.__version__,'subspaces':16,'models':instances,'feasible_assignments':assignments,'exact_dual_checks':dual_checks,'controls':mutations,'scope':'Pinned AST-extracted VE and exact chain dual, exhaustive three-variable F2^3 models; does not certify Graph construction, all words, floating heuristic convergence, or global kappa.'}
if __name__=='__main__':print(json.dumps(main(),indent=2))
