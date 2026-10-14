"""Independent dyadic block-matrix audit of PR1862 source group identities."""
from fractions import Fraction as Q
import itertools,json,pathlib,hashlib,subprocess
HERE=pathlib.Path(__file__).resolve().parent
def need(c,m):
    if not c:raise ValueError(m)
def source(path):
    p=json.loads((HERE/'SOURCES.json').read_text())['files'][path]
    b=subprocess.check_output(['git','show',p['head']+':'+path],cwd=HERE)
    need(hashlib.sha256(b).hexdigest()==p['sha256'],'source mismatch');return b
def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def zero(n,m):return [[Q(0) for j in range(m)] for i in range(n)]
def add(a,b):return [[x+y for x,y in zip(r,s)] for r,s in zip(a,b)]
def neg(a):return [[-x for x in r] for r in a]
def sub(a,b):return add(a,neg(b))
def mm(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def inverse(a):
    n=len(a);m=[list(r)+s for r,s in zip(a,eye(n))]
    for j in range(n):
        piv=next((i for i in range(j,n) if m[i][j]),None)
        if piv is None:return None
        m[j],m[piv]=m[piv],m[j];q=m[j][j];m[j]=[v/q for v in m[j]]
        for i in range(n):
            if i!=j:q=m[i][j];m[i]=[x-q*y for x,y in zip(m[i],m[j])]
    return [row[n:] for row in m]
def dyadic(a):return all(v.denominator&(v.denominator-1)==0 for row in a for v in row)
def main():
    source('research/native-source-codes/PROOF.md')
    # R=[I A], K=[B;I], P=[I;0], L=[0 I] meet all three
    # hypotheses for every rational A,B, including singular RK and RK-I.
    alphabet=[Q(-1),Q(0),Q(1,2),Q(1)]
    cases=singular_m=singular_m_minus=singular_g=dyadic_inverse_cases=0
    for av,bv in itertools.product(itertools.product(alphabet,repeat=2),alphabet):
        R=[[Q(1),av[0],av[1]]];K=[[bv],[Q(1)],[Q(0)]]
        # Use a disjoint right inverse and dual; coefficient K[0] is arbitrary.
        P=[[Q(1)],[Q(0)],[Q(0)]];L=[[Q(0),Q(1),Q(0)]]
        I=eye(3);M=mm(R,K);Z=sub(K,mm(P,sub(M,eye(1))));C=sub(R,L);J=sub(I,mm(K,R))
        need(mm(R,Z)==eye(1) and mm(L,Z)==eye(1),'left inverse identities')
        need(mm(C,Z)==zero(1,1),'nilpotent query')
        need(mm(J,Z)==neg(mm(P,sub(M,eye(1)))),'support identity')
        singular_m+=M==zero(1,1);singular_m_minus+=M==eye(1)
        logger=add(I,mm(Z,C));need(mm(logger,sub(I,mm(Z,C)))==I and mm(L,logger)==R,'logger inverse/query')
        for b in itertools.product([Q(-1),Q(0),Q(1)],repeat=3):
            B=[list(b)];G=add(I,mm(Z,B));small=add(eye(1),mm(B,Z));gi=inverse(G);si=inverse(small)
            need((gi is None)==(si is None),'invertibility equivalence')
            need(mm(J,sub(G,I))[1:]==zero(2,3),'fixed support')
            if gi is None:singular_g+=1
            else:
                need(gi==sub(I,mm(mm(Z,si),B)),'Woodbury inverse')
                need(dyadic(gi)==dyadic(si),'dyadic-unit equivalence');dyadic_inverse_cases+=dyadic(gi)
            B2=C;G2=add(I,mm(Z,B2));B12=add(add(B,B2),mm(mm(B,Z),B2))
            need(mm(G,G2)==add(I,mm(Z,B12)),'ordered group law')
            # E_G target correction composition: C1 G2 + C2 = J(G1 G2-I).
            need(add(mm(mm(J,sub(G,I)),G2),mm(J,sub(G2,I)))==mm(J,sub(mm(G,G2),I)),'prelude cocycle')
            cases+=1
    need(singular_m>0 and singular_m_minus>0 and singular_g>0,'degenerate coverage')
    # A rational inverse need not be dyadic: BZ=2 gives I+BZ=3.
    need(inverse([[Q(3)]])==[[Q(1,3)]] and not dyadic([[Q(1,3)]]),'odd-unit counterexample')
    # Dropping RP=I breaks RZ=I even though LK=I and LP=0 still hold.
    R=[[Q(1),Q(1)]];K=[[Q(0)],[Q(1)]];P=[[Q(0)],[Q(0)]]
    Z=sub(K,mm(P,sub(mm(R,K),eye(1))))
    # Here M=1 masks the omitted premise; choose M=2 to expose it.
    R=[[Q(1),Q(2)]];Z=sub(K,mm(P,sub(mm(R,K),eye(1))))
    need(mm(R,Z)!=eye(1),'missing RP control')
    return {'status':'PASS_INDEPENDENT_DYADIC_SOURCE_GROUP','base_geometries':64,'parameter_cases':cases,'singular_RK_base_geometries':singular_m,'singular_RK_minus_I_base_geometries':singular_m_minus,'singular_G_cases':singular_g,'dyadic_inverse_cases':dyadic_inverse_cases,'controls':['odd determinant rational inverse is not dyadic','omitted RP identity breaks construction'],'scope':'Independent exact low-dimensional algebra stress test, not a proof by finite enumeration. General symbolic proof and full 112-field cold replay are separately credited to PR1862.'}
if __name__=='__main__':print(json.dumps(main(),indent=2))
