"""Bounded build/runtime verification of the custody flow and policy refusal repairs; no acceptance claim."""
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'records/phase1-direct/custody-discard-runtime-v2'
OUT.mkdir(exist_ok=False)
LIB = ROOT / 'lib/libworldline_core.so'
SOURCES = ['core/worldline-root_custody_request_abandon.adb', 'core/worldline-root_custody_request_abandon.ads', 'core/worldline-custody_v2_fold_engine.adb', 'core/worldline-custody_v2_fold_engine.ads', 'core/worldline-custody_v2_mutation_decision.adb', 'core/worldline-custody_v2_mutation_decision.ads', 'core/worldline-resource_policy_c_api.adb', 'core/worldline-resource_policy_c_api.ads', 'tests/resource_policy_transport_tests.adb', 'tests/worldline_tests.gpr', 'runtime/worldline/root_worker_prepared_wire.py', 'tests/test_prepared_wire_values.py', 'tests/test_custody_successor_encoding.py', 'tests/fixtures/custody-successor-oracles-v1.json']
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
prior = json.loads((ROOT/'records/phase1-direct/custody-discard-runtime-v1/result.json').read_text())
record['library_before_tests'] = digest(LIB)
if record['library_before_tests'] != prior['library_after_tests']:
    raise SystemExit('refuse changed library before continuation')
record['build_receipt'] = 'records/phase1-direct/custody-discard-runtime-v1/result.json'
steps = [
 ('resource-regression', [sys.executable, '-m', 'unittest', '-v',
  'test_resource_owned_abi', 'test_resource_policy', 'test_custody_prepared_abi',
  'test_custody_v2_explicit_provision', 'test_custody_provision_kernel',
  'test_delta', 'test_prepared_wire_values', 'test_root_worker_codec_lossless',
  'test_custody_successor_encoding'], 180),
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
