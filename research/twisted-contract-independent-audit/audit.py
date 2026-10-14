"""Independent literal binary-matrix census of the PR1868 scalar contract."""
import itertools,json,pathlib,hashlib,subprocess,collections
HERE=pathlib.Path(__file__).resolve().parent
def need(c,m):
    if not c:raise ValueError(m)
def source(path):
    p=json.loads((HERE/'SOURCES.json').read_text())['files'][path]
    b=subprocess.check_output(['git','show',p['head']+':'+path],cwd=HERE)
    need(hashlib.sha256(b).hexdigest()==p['sha256'],'source mismatch');return b
def action(m,x):return sum(((r&x).bit_count()%2)<<i for i,r in enumerate(m))
def mm(a,b):
    return tuple(__import__('functools').reduce(int.__xor__,(b[j] for j in range(len(b)) if row>>j&1),0) for row in a)
def gl(n):return [m for m in itertools.product(range(1<<n),repeat=n) if len({action(m,x) for x in range(1<<n)})==1<<n]
def inverse(m):
    n=len(m);inv={action(m,x):x for x in range(1<<n)}
    return tuple(sum(((inv[1<<j]>>i)&1)<<j for j in range(n)) for i in range(n))
def endpoint(t,u,c,k,n,source_term=True):
    columns=[]
    for j in range(4):
        inp=1<<j;z=inp&7;y=inp>>3;h=z>>1
        y^=(n&h).bit_count()%2;z=(z&1)|(action(t,h)<<1)
        y^=((z&1) if source_term else 0)^((k&(z>>1)).bit_count()%2)
        z=action(u,z);z=action(c,z);columns.append(z|(y<<3))
    return tuple(columns)
def main():
    source('research/r439-twisted-star-absorption-seed02/PROOF.md')
    g2,g3=gl(2),gl(3);need((len(g2),len(g3))==(6,168),'GL catalogues')
    expected=(9,2,4,8);good=bad_n=bad_c=0;omitted_twist=0;example=None
    for t in g2:
        th=(1,t[0]<<1,t[1]<<1)
        for u in g3:
            c=inverse(mm(u,th));need(mm(c,mm(u,th))==(1,2,4),'cleanup construction')
            for k in range(4):
                nt=mm((k,),t)[0]
                for n in range(4):
                    valid=endpoint(t,u,c,k,n)==expected
                    need(valid==(n==nt),'compensation equivalence')
                    good+=valid;bad_n+=not valid
            # Complete independent C census at one nonzero K; compensation and
            # cleanup act on disjoint output blocks, so these tests are factored.
            k=3;n=mm((k,),t)[0]
            for wrong in g3:
                valid=endpoint(t,u,wrong,k,n)==expected
                need(valid==(wrong==c),'cleanup necessity')
                bad_c+=not valid
            stale=inverse(u)
            if t!=(1,2):
                need(endpoint(t,u,stale,k,n)!=expected,'omitted twist missed')
                omitted_twist+=1
                if example is None:example={'T':t,'U':u,'K':k,'N':n,'stale_cleanup':stale,'columns':endpoint(t,u,stale,k,n)}
    # Removing J=I is not repaired by correct helper compensation/cleanup.
    need(endpoint((1,2),(1,2,4),(1,2,4),0,0)==expected,'positive fixture')
    wrong_j=endpoint((1,2),(1,2,4),(1,2,4),0,0,source_term=False)
    need(wrong_j!=expected,'missing source-response control')
    return {'status':'PASS_INDEPENDENT_TWISTED_CONTRACT_AUDIT','GL2':6,'GL3':168,'valid_parameter_tuples':good,'compensation_failures':bad_n,'wrong_cleanup_failures':bad_c,'omitted_twist_failures':omitted_twist,'missing_source_response_mutation_rejected':True,'stale_cleanup_example':example,'scope':'Scalar H2-tw/H4-tw/K-tw block equations only. No new chronological/native bridge; full-word replay recorded separately.'}
if __name__=='__main__':print(json.dumps(main(),indent=2))
