#!/usr/bin/env python3
"""Frozen PR1298 replay on Windows CPython3.12. woklerx/Codex; Apache-2.0."""
from hashlib import sha256, sha1
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return sha256(data).hexdigest(), sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def main():
    require(sys.version_info[:2] == (3, 12), 'Use Python3.12 to cover the previously skipped test')
    require(os.name == 'nt', 'Windows audit; other hosts need separate receipts')
    inventory = json.loads((HERE/'SOURCES.json').read_bytes())
    overlay = json.loads((HERE/'PR1298-SOURCE.json').read_bytes())
    inputs = {}
    for row in inventory['files']:
        if row['usage'] != 'input':
            continue
        data = (ROOT/row['path']).read_bytes()
        require(digest(data) == (row['sha256'], row['git_blob']), 'Input drift: '+row['path'])
        inputs[row['path']] = data
    changed = {}
    for row in overlay['files']:
        data = (HERE/'vendor'/row['path']).read_bytes()
        require(digest(data) == (row['sha256'], row['git_blob']), 'Overlay drift: '+row['path'])
        changed[row['path']] = data
    reports = []
    scratch = ROOT/'.firecrawl'/'pr1298-audit'
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='fixture-', dir=scratch) as tmp:
        sandbox = Path(tmp)
        for name, data in inputs.items():
            dest = sandbox/name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        for name, data in changed.items():
            (sandbox/name).write_bytes(data)
        env = dict(os.environ, PYTHONUTF8='0', PYTHONIOENCODING='cp1252', PYTHONDONTWRITEBYTECODE='1', TEMP=str(scratch), TMP=str(scratch))
        env.pop('PYTHONPATH', None)
        def run(label, args, should_pass, pattern):
            result = subprocess.run([sys.executable, '-X', 'utf8=0', '-B', '-m', 'unittest', *args],
                                    cwd=sandbox, env=env, capture_output=True, timeout=90)
            output = (result.stdout+result.stderr).decode('cp1252', errors='backslashreplace')
            require((result.returncode == 0) == should_pass, label+' unexpected exit:\n'+output)
            require(re.search(pattern, output), label+' missing coverage marker:\n'+output)
            require('skipped=' not in output, label+' unexpectedly skipped checks')
            reports.append({'case':label,'exit_code':result.returncode,'output':output})
        run('full-patched-suite', ['discover','-s','tests','-p','test_research_*.py','-v'], True,
            r'test_ready_package_replays_and_mutation_fails[\s\S]*?ok[\s\S]*Ran 23 tests')
        (sandbox/'scripts/find_overlap.py').write_bytes(inputs['scripts/find_overlap.py'])
        run('revert-overlap-only', ['discover','-s','tests','-p','test_research_onboarding.py','-k','report_survives','-v'], False,
            r'UnicodeEncodeError[\s\S]*Ran 1 test')
        (sandbox/'scripts/find_overlap.py').write_bytes(changed['scripts/find_overlap.py'])
        (sandbox/'scripts/research_package.py').write_bytes(inputs['scripts/research_package.py'])
        run('revert-metadata-only', ['discover','-s','tests','-p','test_research_onboarding.py','-k','utf8_metadata','-v'], False,
            r'UnicodeDecodeError[\s\S]*Ran 1 test')
    print(json.dumps({'status':'PASS_PR1298_WINDOWS_PY312_AUDIT','python':sys.version,
                      'audited_head':overlay['head'],'suite_tests':23,'skips':0,
                      'source_reversion_controls':2,'reports':reports}, indent=2, ensure_ascii=True))


if __name__ == '__main__':
    main()
