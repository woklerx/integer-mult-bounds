"""Independent F2 dual-functional witnesses for PR1775, without elimination."""
import json,pathlib,hashlib,subprocess,collections
HERE=pathlib.Path(__file__).resolve().parent
def need(c,m):
    if not c:raise ValueError(m)
def source(path):
    p=json.loads((HERE/'SOURCES.json').read_text())['files'][path]
    b=subprocess.check_output(['git','show',p['head']+':'+path],cwd=HERE)
    need(hashlib.sha256(b).hexdigest()==p['sha256'],'source mismatch');return b
def dot(a,b):return (a&b).bit_count()%2
def span(vectors):
    out={0}
    for v in vectors:out|={x^v for x in tuple(out)}
    return out
def witness(inputs,cap):
    ann=[a for a in range(1,512) if all(not dot(a,c) for c in cap)]
    need(len(ann)==1,'cap must be hyperplane')
    a=ann[0];outside=[(i,v) for i,f in enumerate(inputs) for v in f if dot(a,v)]
    need(outside,'join lies in cap')
    return a,outside[0]
def main():
    cert=json.loads(source('research/complex-block-rank-optimum/CERTIFICATE.json'))
    receipts=[];counts=collections.Counter();incidence=0
    for si,s in enumerate(cert['sources']):
        need(len(s['blocks'])==12,'source block coverage')
        for bi,b in enumerate(s['blocks']):
            inputs=b['input_frames']; joined=span(v for f in inputs for v in f)
            counts[len(joined)]+=1
            for col in range(8):
                active=[i for i,row in enumerate(b['Q']) if row[col]!='0']
                need(len(active)==2,'two independent output incidences');incidence+=1
            for ci,cap in enumerate(b['target_caps']):
                ann,(ii,v)=witness(inputs,cap)
                need(all(not dot(ann,u) for u in span(cap)) and dot(ann,v),'dual witness invalid')
                need(len(span(cap))==256 and len(span([*cap,v]))==512,'finite space witness')
                receipts.append([si,bi,ci,ann,ii,v])
    need(len(receipts)==144 and counts=={256:6,512:30},'coverage or join counts')
    # All 511 hyperplanes: a vector is outside iff its dual parity is one.
    classifications=0
    for a in range(1,512):
        cap=[v for v in range(512) if not dot(a,v)]
        for v in range(512):
            need((v not in cap)==bool(dot(a,v)),'exhaustive dual characterization');classifications+=1
    inputs=[[1],[2]];cap=[1,2,4,8,16,32,64,128]
    try:witness(inputs,cap)
    except ValueError:pass
    else:raise ValueError('compatible-cap mutation accepted')
    try:witness([[256]],cap[:-1])
    except ValueError:pass
    else:raise ValueError('rank-seven cap mutation accepted')
    raw=json.dumps(receipts,separators=(',',':')).encode()
    return {'status':'PASS_INDEPENDENT_CONNECTOR_DUAL_WITNESSES','source_sets':3,'blocks':36,'witnesses':receipts,'witness_sha256':hashlib.sha256(raw).hexdigest(),'join_size_counts':dict(counts),'two_port_columns':incidence,'hyperplane_classifications':classifications,'negative_controls':2,'scope':'Dual certificates for the pinned all-eight-input single-carrier class; not multiple carriers or direct delivery.'}
if __name__=='__main__':print(json.dumps(main(),indent=2))
