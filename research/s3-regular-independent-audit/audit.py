"""Code-disjoint faithful F2 regular-representation check of PR1870."""
import itertools,json,collections,pathlib,hashlib,subprocess
HERE=pathlib.Path(__file__).resolve().parent
def need(c,m):
    if not c: raise ValueError(m)
def source(path):
    pins=json.loads((HERE/'SOURCES.json').read_text()); p=pins['files'][path]
    b=subprocess.check_output(['git','show',p['head']+':'+path],cwd=HERE)
    need(hashlib.sha256(b).hexdigest()==p['sha256'],'source mismatch '+path)
    return b
def mul(a,b):
    out=[]
    for row in a:
        v=0
        while row:
            bit=row&-row; v^=b[bit.bit_length()-1];row^=bit
        out.append(v)
    return tuple(out)
def main():
    cert=json.loads(source('research/bit-s3-two-target-census-seed36501/CERTIFICATE.json'))
    group=list(itertools.permutations(range(3))); index={p:i for i,p in enumerate(group)}
    def product(a,b):return tuple(a[b[i]] for i in range(3))
    def regular(p):
        rows=[0]*6
        for j,h in enumerate(group):rows[index[product(p,h)]]|=1<<j
        return tuple(rows)
    reg=[regular(p) for p in group]; ident=tuple(1<<i for i in range(12))
    # Enumerate every 2x2 binary matrix independently, then filter rank-one idempotents.
    projectors=[]
    for n in itertools.product(range(4),repeat=2):
        vals={0,n[0],n[1],n[0]^n[1]}
        if len(vals)==2 and mul(n,n)==n:projectors.append(n)
    need(len(projectors)==6,'projector catalogue')
    x=(1,0,2);y=(0,2,1);generators=[]
    for s in (x,y):
        delta=tuple(a^(1<<i) for i,a in enumerate(regular(s)))
        for n in projectors:
            rows=list(ident)
            for i in range(2):
                for j in range(2):
                    if n[i]>>j&1:
                        for k in range(6):rows[6*i+k]^=delta[k]<<(6*j)
            generators.append(tuple(rows))
    # Complete linear action tables accelerate ordinary 12x12 binary products.
    tables=[]
    for g in generators:
        t=[0]*4096
        for b in range(1,4096):q=b&-b;t[b]=t[b^q]^g[q.bit_length()-1]
        tables.append(t)
        need(mul(g,g)==ident,'generator involution')
    seen={ident:0};front={ident};layers=[1]
    for depth in range(1,6):
        nxt={tuple(t[row] for row in a) for a in front for t in tables}-seen.keys()
        for a in nxt:seen[a]=depth
        front=nxt;layers.append(len(front))
    need(layers==[1,12,80,466,2345,10760],'radius-five layers')
    # Faithfulness: each coefficient is recovered from the identity column;
    # verify the entire regular block, not merely its image on one probe.
    faithful=0
    for a in seen:
        for i,j in itertools.product(range(2),repeat=2):
            block=tuple((a[6*i+k]>>(6*j))&63 for k in range(6))
            coeff=[k for k in range(6) if block[k]&1]
            rebuilt=tuple(__import__('functools').reduce(int.__xor__,(reg[k][r] for k in coeff),0) for r in range(6))
            need(block==rebuilt,'regular block outside group algebra')
        faithful+=1
    dist={(0,1,2):0};paths={(0,1,2):()};todo=collections.deque(dist)
    while todo:
        a=todo.popleft()
        for s in (x,y):
            b=product(a,s)
            if b not in dist:dist[b]=dist[a]+1;paths[b]=paths[a]+(s,);todo.append(b)
    histogram=collections.Counter();omissions=0
    for a,b in itertools.product(group,repeat=2):
        target=reg[index[a]]+tuple(v<<6 for v in reg[index[b]])
        bill=dist[a]+dist[b];histogram[bill]+=1
        need(seen.get(target,6)==bill,'minimum differs from direct bill')
        word=[]
        for role,p in enumerate((a,b)):
            for s in paths[p]:
                n=(1,0) if role==0 else (0,2)
                word.append(generators[(0 if s==x else 6)+projectors.index(n)])
        value=ident
        for g in word:value=mul(value,g)
        need(value==target,'direct target')
        for skip in range(len(word)):
            value=ident
            for i,g in enumerate(word):
                if i!=skip:value=mul(value,g)
            need(value!=target,'omission control');omissions+=1
    need(dict(sorted(histogram.items()))=={int(k):v for k,v in cert['direct_call_histogram'].items()},'source histogram mismatch')
    # All six nonzero formal coefficients collapse to zero in the natural 3D
    # permutation representation, but their regular image is nonzero.
    natural=[0]*3
    for p in group:
        for j in range(3):natural[p[j]]^=1<<j
    need(natural==[0]*3,'natural-image alias fixture')
    need(any(__import__('functools').reduce(int.__xor__,(r[i] for r in reg),0) for i in range(6)),'faithful representation control')
    return {'status':'PASS_INDEPENDENT_S3_REGULAR_AUDIT','layers':layers,'faithful_states':faithful,'target_minima':36,'omission_controls':omissions,'natural_representation_alias_detected':True,'scope':'Finite two-register S3 model only; no additional-register or physical supplier theorem.'}
if __name__=='__main__':print(json.dumps(main(),indent=2))
