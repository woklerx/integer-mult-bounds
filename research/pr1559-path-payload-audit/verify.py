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

import gzip,os,tempfile,shlex,difflib
source=pinned('research/bit589-gzip-replay/replay.py').decode()
pinned('research/bit589-gzip-replay/verify.py');pinned('research/e8-bit-p111-tuned/tune/verify.sh')
anchor='source = source.replace(old + "\\n", command + old[len("cmp"):] + "\\n")'
# Match the exact adapter expression before proposing a bounded source patch.
anchor='        source = source.replace(old + "\n", command + old[len("cmp"):] + "\n")'
# The Python source contains literal backslash-n strings, not newlines here.
anchor=anchor.replace('"\n"','"\\n"')
replacement='        arguments = " ".join(chr(34) + item + chr(34) for item in old.split()[1:])\n        source = source.replace(old + "\\n", command + " " + arguments + "\\n")'
need(source.count(anchor)==1,'exact candidate patch anchor')
fixed=source.replace(anchor,replacement)
patch=''.join(difflib.unified_diff(source.splitlines(True),fixed.splitlines(True),fromfile='a/research/bit589-gzip-replay/replay.py',tofile='b/research/bit589-gzip-replay/replay.py',n=2))
if '--write' in sys.argv: (HERE/'UPSTREAM-FIX.patch').write_bytes(patch.encode('utf8'))
else: need((HERE/'UPSTREAM-FIX.patch').read_text(encoding='utf8')==patch,'repair patch drift')
words=['research/e8-bit-p111-tuned/data/bitE8mut-p111.json.gz','research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz']
accepted=rejected=0
with tempfile.TemporaryDirectory(prefix="payload spaces ' ",dir=HERE) as temp:
    td=Path(temp);helper=td/"helper spaces 'quoted.py";helper.write_text(source,encoding='utf8')
    refs=[];gens=[]
    for n,path in enumerate(words):
        raw=pinned(path);data=gzip.decompress(raw);ref=td/('reference '+str(n)+'.gz');ref.write_bytes(raw);refs.append(ref)
        gen=td/('base.json.gz' if n==0 else 'tuned.json.gz');gens.append(gen)
        variants=[gzip.compress(data,compresslevel=level,mtime=12345) for level in (0,1,6,9)]
        variants += [gzip.compress(data[:len(data)//2])+gzip.compress(data[len(data)//2:]),raw+b'\0'*7]
        badcrc=bytearray(raw);badcrc[-8]^=1
        bad=[gzip.compress(data+b'\n'),gzip.compress(data[:-1]),raw[:-2],bytes(badcrc),raw+gzip.compress(b'extra')]
        for expected,items in [(True,variants),(False,bad)]:
            for item in items:
                gen.write_bytes(item)
                for opts in ([],['-O']):
                    q=subprocess.run([sys.executable,'-I','-B',*opts,str(helper),'--compare',str(gen),str(ref)],capture_output=True)
                    need((q.returncode==0)==expected,'full-payload CLI verdict')
                    if expected:accepted+=1
                    else:rejected+=1
        gen.write_bytes(variants[1])
    env=dict(os.environ,PYTHON=Path(sys.executable).as_posix(),WD=td.as_posix(),BASE=refs[0].as_posix(),WORD=refs[1].as_posix())
    ns={'__name__':'audited','__file__':str(helper)};exec(compile(source,'upstream-replay.py','exec'),ns)
    snippet='\n'.join(ns['COMPARISONS'])+'\nprintf "%s\\n" "'+ns['OLD_MESSAGE']+'"\n'
    before=ns['adapted_script'](snippet,helper.as_posix())
    ns2={'__name__':'fixed','__file__':str(helper)};exec(compile(fixed,'fixed-replay.py','exec'),ns2)
    after=ns2['adapted_script'](snippet,helper.as_posix())
    bash=os.environ.get('AUDIT_BASH','bash')
    # Execute each site in a separate shell: errexit cannot hide the second failure.
    before_lines=before.splitlines();after_lines=after.splitlines()
    need(len(before_lines)==len(after_lines)==3,'exact two-site snippet layout')
    site_results=[];diagnostics=[]
    for index in range(2):
        old=subprocess.run([bash,'-ec',before_lines[index]],env=env,capture_output=True)
        new=subprocess.run([bash,'-ec',after_lines[index]],env=env,capture_output=True)
        need(old.returncode!=0,'upstream space-path defect at site '+str(index))
        need(new.returncode==0,'quoted argument repair at site '+str(index)+': '+new.stderr.decode(errors='replace'))
        site_results.append({'site':ns['COMPARISONS'][index],'original':'rejects','quoted':'passes'})
        diagnostics.append(('SITE '+str(index+1)+' '+ns['COMPARISONS'][index]+'\n').encode()+old.stderr.replace(bytes([13]),b''))
    if '--write' in sys.argv: (HERE/'PATH-FAILURE.txt').write_bytes(b'\n'.join(diagnostics))
finish({'status':'PASS_PR1559_PATH_PAYLOAD_AUDIT','equivalent_payload_CLI_accepts':accepted,'changed_or_corrupt_CLI_rejects':rejected,'upstream_adapted_shell_space_paths':site_results,'quoted_comparison_arguments':'passes both sites','scope':'Focused payload adapter and shell sites only; no full native selected replay or Windows shell portability claim beyond tested Git Bash'})
