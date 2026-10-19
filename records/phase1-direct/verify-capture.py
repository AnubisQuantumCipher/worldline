"""Bounded capture repair build and original regression checks; no acceptance claim."""
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'records/phase1-direct/capture-runtime-v1'
OUT.mkdir(exist_ok=False)
LIB = ROOT / 'lib/libworldline_core.so'
SOURCES = ['core/'+name+'.'+ext for name in (
 'worldline-scoped_capture_projection', 'worldline-scoped_capture_evolution_projection',
 'worldline-retained_evidence_replay', 'worldline-custody_v2_values')
 for ext in ('ads','adb')] + ['runtime/worldline/proof_manifest.py',
 'tests/scoped_capture_scan_tests.adb', 'tests/scoped_capture_probe.adb',
 'tests/test_scoped_capture_scan.py', 'tests/worldline_tests.gpr']
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
 ('scoped-scanners', [str(ROOT/'bin/scoped_capture_scan_tests')], 60),
 ('capture-regression', [sys.executable, '-m', 'unittest', '-v',
  'test_scoped_capture_scan', 'test_custody_subject_primitives',
  'test_custody_v2_sql_capture', 'test_custody_foreign_key_capture',
  'test_resource_scoped_history_v1', 'test_root_worker_codec_lossless'], 180),
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
