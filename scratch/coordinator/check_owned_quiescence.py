"""Read-only, fail-closed check of retained job scopes and attributed services."""
from pathlib import Path
import datetime
import importlib.util
import json
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
out = Path(sys.argv[1]).resolve()
assert out.is_relative_to(root) and not out.exists()
runtime = root / 'scratch/old-analysis/full_runtime_supervisor.py'
spec = importlib.util.spec_from_file_location('quiescence_inventory', runtime)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
current_path = Path('/proc/self/cgroup').read_text()
current = current_path.strip().split(':')[-1].split('/')[-1]
result = {'classification': 'MEASURED recorded own jobs and attributed services only',
          'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'current_cgroup': current_path, 'scopes': [], 'services': [], 'refusals': [],
          'non_claims': ['Not a universal process inventory or permission to signal any process']}
paths = list((root / 'records/phase1-blockers').glob('*/scope.jsonl'))
for area in ('acquisition', 'old-analysis', 'reviewer', 'coordinator'):
    paths.extend((root / 'scratch' / area).glob('*/scope.jsonl'))
units = {}
for path in paths:
    for line in path.read_text().splitlines():
        row = json.loads(line)
        unit = row.get('unit')
        if not isinstance(unit, str) or not re.fullmatch(r'wl-phase1-[0-9a-f]+\.scope', unit):
            result['refusals'].append({'receipt': str(path), 'reason': 'unrecognized retained scope'})
            continue
        units.setdefault(unit, []).append(str(path))
def observe(unit):
    raw = m.command(['systemctl', '--user', 'show', unit, '-p', 'Id', '-p', 'LoadState',
                     '-p', 'ActiveState', '-p', 'SubState', '-p', 'ControlGroup'])
    values = dict(line.split('=', 1) for line in raw.get('stdout', '').splitlines() if '=' in line)
    row = {'unit': unit, 'query': raw, 'values': values, 'quiescent': False}
    if values.get('LoadState') == 'not-found' and values.get('ActiveState') == 'inactive':
        row['quiescent'] = True
    elif raw.get('exit_code') == 0 and values.get('Id') == unit:
        cg = values.get('ControlGroup')
        if not cg:
            row['quiescent'] = values.get('ActiveState') in ('inactive', 'failed')
        else:
            try:
                base = Path('/sys/fs/cgroup') / cg.lstrip('/')
                events = (base / 'cgroup.events').read_text()
                procs = (base / 'cgroup.procs').read_text()
                row.update(cgroup_events=events, cgroup_procs=procs)
                row['quiescent'] = dict(line.split() for line in events.splitlines()).get('populated') == '0' and not procs.strip()
            except OSError as error:
                row['refusal'] = repr(error)
    return row
for unit, receipts in sorted(units.items()):
    if unit == current:
        result['scopes'].append({'unit': unit, 'receipts': receipts, 'current_worker': True})
        continue
    row = observe(unit)
    row['receipts'] = receipts
    result['scopes'].append(row)
    if not row['quiescent']:
        result['refusals'].append({'unit': unit, 'reason': 'retained scope not positively quiescent'})
try:
    roster, receipt = m.units()
    result['manager_roster'] = receipt
    for unit in sorted(roster):
        if not m.canonical(unit):
            continue
        info, typed = m.typed_exec(unit)
        if info is None:
            result['refusals'].append({'unit': unit, 'reason': 'typed service identity unreadable', 'query': typed})
            continue
        cwd = info.get('cwd')
        if isinstance(cwd, list) and len(cwd) == 1:
            cwd = cwd[0]
        owned = m.inside(cwd) or any(m.owned_exec(entry) for entry in info['execs'])
        row = {'unit': unit, 'typed': typed, 'worktree_path_attribution': owned}
        if owned:
            row['observation'] = observe(unit)
            if not row['observation']['quiescent']:
                result['refusals'].append({'unit': unit, 'reason': 'attributed service not positively quiescent'})
        result['services'].append(row)
except Exception as error:
    result['refusals'].append({'reason': 'manager inspection refused', 'error': repr(error)})
result['passed'] = not result['refusals'] and bool(units)
out.open('x').write(json.dumps(result, indent=2) + '\n')
print(json.dumps({'output': str(out), 'passed': result['passed'], 'refusals': result['refusals']}))
raise SystemExit(0 if result['passed'] else 1)
