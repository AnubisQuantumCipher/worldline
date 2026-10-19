"""Bounded build/runtime verification of the custody progress and policy extent repairs; no acceptance claim."""
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'records/phase1-direct/custody-runtime-v2'
OUT.mkdir(exist_ok=False)
LIB = ROOT / 'lib/libworldline_core.so'
SOURCES = ['core/worldline-startup_source_custody.adb', 'core/worldline-retained_custody_chain.adb', 'core/worldline-policy_syntax.adb', 'tests/startup_source_probe.adb', 'tests/worldline_tests.gpr', 'tests/test_startup_source_scan.py', 'tests/test_policy_source_raw_correspondence.py', 'tests/test_evaluation_policy_raw_producer.py']
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def sources():
    return {name: digest(ROOT / name) for name in SOURCES}

def run(name, argv, seconds, env):
    row = {'name': name, 'argv': argv, 'started': datetime.now(timezone.utc).isoformat()}
    with (OUT / (name+'.stdout')).open('xb') as stdout, (OUT / (name+'.stderr')).open('xb') as stderr:
        try:
            result = subprocess.run(argv, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                    stdout=stdout, stderr=stderr, timeout=seconds)
            row['exit_code'] = result.returncode
        except subprocess.TimeoutExpired:
            row.update(exit_code=None, timed_out=True)
    row['finished'] = datetime.now(timezone.utc).isoformat()
    row['artifacts'] = {s: digest(OUT/(name+'.'+s)) for s in ('stdout','stderr')}
    return row

env = dict(os.environ)
env.update(WORLDLINE_CORE_LIB=str(LIB), PYTHONPATH=str(ROOT/'runtime')+':'+str(ROOT/'tests'),
           PYTHONDONTWRITEBYTECODE='1')
record = {'claim':'TESTED focused source repair only; original Phase One gates remain open',
          'sources_before':sources(), 'steps': [], 'library_before_tests': digest(LIB),
          'native_build_and_ada_tests': 'records/phase1-direct/custody-runtime/result.json'}
steps = [
 ('native-controls', [sys.executable,'-B','-m','unittest','-v', 'test_startup_source_scan','test_policy_source_raw_correspondence','test_project', 'test_evaluation_policy_raw_producer'], 300),
]
for name, argv, seconds in steps:
    row = run(name, argv, seconds, env)
    record['steps'].append(row)
    if name == 'checked-build' and row['exit_code'] == 0:
        record['library_before_tests'] = digest(LIB)
    (OUT/'result.json').write_text(json.dumps(record,indent=2)+'\n')
    if name == 'checked-build' and row['exit_code'] != 0:
        break
record['sources_after'] = sources()
record['library_after_tests'] = digest(LIB) if LIB.exists() else None
test_log = OUT/'native-controls.stderr'
text = test_log.read_text() if test_log.exists() else ''
record['unittest_summaries'] = re.findall(r'^Ran ([0-9]+) tests? in ', text, re.M)
record['unittest_terminal_ok'] = bool(re.search(r'^OK$', text, re.M))
record['success'] = (record['unittest_terminal_ok'] and len(record['unittest_summaries']) == 1 and len(record['steps']) == len(steps) and all(s['exit_code']==0 for s in record['steps'])
                     and record['sources_before'] == record['sources_after']
                     and record.get('library_before_tests') == record['library_after_tests'])
(OUT/'result.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
sys.exit(0 if record['success'] else 1)
