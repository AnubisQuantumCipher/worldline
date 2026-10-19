"""Bounded build/runtime verification of the resource-ledger refusal-handler repair; no acceptance claim."""
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'records/phase1-direct/ledger-transport-runtime-v3'
OUT.mkdir(exist_ok=False)
LIB = ROOT / 'lib/libworldline_core.so'
SOURCES = ['core/worldline-resource_ledger_c_api.adb', 'core/worldline-resource_ledger_c_api.ads', 'core/worldline-c_api.adb', 'core/worldline-custody_v2_machine_evidence.adb', 'tests/resource_ledger_transport_tests.adb', 'tests/test_resource_owned_abi.py', 'tests/worldline_tests.gpr']
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
        except OSError as error:
            row.update(exit_code=None, launch_error=str(error))
        except subprocess.TimeoutExpired:
            row.update(exit_code=None, timed_out=True)
    row['finished'] = datetime.now(timezone.utc).isoformat()
    row['artifacts'] = {s: digest(OUT/(name+'.'+s)) for s in ('stdout','stderr')}
    return row

env = dict(os.environ)
env.update(WORLDLINE_CORE_LIB=str(LIB), PYTHONPATH=str(ROOT/'runtime')+':'+str(ROOT/'tests'),
           PYTHONDONTWRITEBYTECODE='1')
record = {'claim':'TESTED focused source repair only; original Phase One gates remain open',
          'sources_before':sources(), 'steps': []}
steps = [
 ('checked-build', ['gprbuild','-p','-j2','-P','worldline.gpr','-XWORLDLINE_BUILD=checks',
  '-XSPARKLIB_MODE=full','-XSPARKLIB_BUILD=Production','-XSPARKLIB_LIBRARY_TYPE=static',
  '-XSPARKLIB_INSTALLED=True','-cargs:Ada','-fPIC'], 300),
 ('ada-tests', [str(ROOT/'bin/worldline_core_tests')], 60),
 ('ada-fuzz', [str(ROOT/'bin/worldline_core_fuzz')], 60),
 ('typed-refusal-controls', [str(ROOT/'bin/resource_ledger_transport_tests')], 60),
 ('resource-regression', [sys.executable, '-m', 'unittest', '-v', 'test_resource_owned_abi', 'test_resource_ledger', 'test_resource_headroom', 'test_resource_policy'], 180),
]
for name, argv, seconds in steps:
    row = run(name, argv, seconds, env)
    record['steps'].append(row)
    if name == 'checked-build' and row['exit_code'] == 0:
        record['library_before_tests'] = digest(LIB)
    (OUT/'result.json').write_text(json.dumps(record,indent=2)+'\n')
    if row['exit_code'] != 0:
        break
record['sources_after'] = sources()
record['library_after_tests'] = digest(LIB) if LIB.exists() else None
record['success'] = (len(record['steps']) == len(steps) and all(s['exit_code']==0 for s in record['steps']) and record['sources_before']==record['sources_after'] and record.get('library_before_tests')==record['library_after_tests'])
(OUT/'result.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
sys.exit(0 if record['success'] else 1)
