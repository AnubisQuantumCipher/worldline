"""Selected complete subprogram proofs; no whole-project acceptance claim."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'records/phase1-direct' / sys.argv[1]
if OUT.parent != ROOT / 'records/phase1-direct':
    raise ValueError('output must be a direct evidence child')
CASES = (
    ('native-projection', 'worldline-retained_evidence_replay', 'adb', 2531),
    ('maps', 'worldline-scoped_capture_projection', 'ads', 56),
    ('map-path', 'worldline-scoped_capture_projection', 'adb', 372),
)
COMMON = ['gnatprove', '-P', 'core/worldline_core_sources.gpr',
          '--no-inlining', '--mode=all', '--level=3', '--report=all',
          '--checks-as-errors=on', '--proof-warnings=on', '--warnings=error',
          '--memlimit=1024', '--timeout=60', '-j2',
          '--subdirs=direct-proof-custody-next-line', '-XWORLDLINE_BUILD=checks',
          '-XSPARKLIB_MODE=full', '-XSPARKLIB_BUILD=Production',
          '-XSPARKLIB_LIBRARY_TYPE=static', '-XSPARKLIB_INSTALLED=True']


def source_hashes():
    names = sorted({f'core/{unit}.{ext}' for _, unit, _, _ in CASES
                    for ext in ('ads', 'adb')})
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names}


def check(case):
    name, unit, ext, line = case
    directory = OUT / name
    directory.mkdir()
    argv = COMMON + ['-u', unit+'.adb', f'--limit-subp={unit}.{ext}:{line}']
    row = {'argv': argv, 'sources_before': source_hashes()}
    with (directory/'stdout').open('xb') as stdout, (directory/'stderr').open('xb') as stderr:
        result = subprocess.run(argv, cwd=ROOT, stdin=subprocess.DEVNULL,
                                stdout=stdout, stderr=stderr, timeout=240)
    row['exit_code'] = result.returncode
    text = (directory/'stdout').read_text()
    match = re.search(r'Summary logged in (.+)', text)
    if match:
        shutil.copyfile(match.group(1).strip(), directory/'gnatprove.out')
    row['fresh_report'] = bool(match)
    row['sources_after'] = source_hashes()
    row['source_stable'] = row['sources_before'] == row['sources_after']
    row['findings'] = [b for b in (directory/'stderr').read_text().split('\n\n')
                       if any(s in b for s in ('medium:', 'high:', 'warning:', 'error:'))]
    (directory/'result.json').write_text(json.dumps(row, indent=2)+'\n')
    print(json.dumps({'case': name, 'exit_code': result.returncode,
                      'fresh_report': bool(match), 'findings': row['findings']}), flush=True)
    return result.returncode == 0 and bool(match) and row['source_stable']


OUT.mkdir(exist_ok=False)
results = [check(case) for case in CASES]
sys.exit(0 if all(results) else 1)
