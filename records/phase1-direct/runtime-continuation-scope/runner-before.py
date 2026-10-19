"""Continue the exact original unittest roster after the retained timed-out prefix."""
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import unittest
from datetime import datetime, timezone

root = Path(__file__).resolve().parents[2]
for name in ('runtime', 'tests'):
    sys.path.insert(0, str(root / name))
lib = root / 'lib/libworldline_core.so'
os.environ['WORLDLINE_CORE_LIB'] = str(lib)
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
prior = json.loads((root / 'records/phase1-direct/runtime-controls/result.json').read_text())
if digest(lib) != prior['library_after'] or not prior['library_unchanged']:
    raise SystemExit('Library differs from the retained prefix')
argv = prior['steps'][-1]['argv']
suite = unittest.defaultTestLoader.loadTestsFromNames(argv[5:])
# unittest suite nesting is finite and comes from the fixed original modules.
queue = list(suite)
cases = []
while queue:
    item = queue.pop(0)
    if isinstance(item, unittest.TestSuite):
        queue[0:0] = list(item)
    else:
        cases.append(item)
log = (root / 'records/phase1-direct/runtime-controls/native-evaluation-controls.stderr').read_text()
passed = [f'{owner}.{name}' for name, owner in re.findall(r'^(\w+) \(([^)]+)\) \.\.\. ok$', log, re.M)]
ids = [case.id() for case in cases]
if not passed or passed != ids[:len(passed)] or len(passed) >= len(ids):
    raise SystemExit('Prefix does not match the complete original roster')
out = root / 'records/phase1-direct/runtime-continuation'
out.mkdir(exist_ok=False)
record = {'claim': 'TESTED selected original roster only; not complete F3',
          'utc_start': datetime.now(timezone.utc).isoformat(), 'original_argv': argv,
          'library_before': digest(lib), 'original_roster': ids, 'retained_passed_prefix': passed,
          'prior_result_sha256': digest(root / 'records/phase1-direct/runtime-controls/result.json')}
(out / 'result.json').write_text(json.dumps(record, indent=2)+'\n')
with (out / 'unittest.stderr').open('w') as stream:
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.TestSuite(cases[len(passed):]))
record.update(utc_end=datetime.now(timezone.utc).isoformat(), tests_run=result.testsRun,
              failures=[i.id() for i, _ in result.failures], errors=[i.id() for i, _ in result.errors],
              skipped=[(i.id(), reason) for i, reason in result.skipped],
              unexpected_successes=[i.id() for i in result.unexpectedSuccesses],
              expected_failures=[i.id() for i, _ in result.expectedFailures],
              library_after=digest(lib), output_sha256=digest(out/'unittest.stderr'))
record['success'] = (result.wasSuccessful() and not result.skipped and not result.expectedFailures
                     and result.testsRun == len(ids)-len(passed) and digest(lib) == record['library_before'])
(out / 'result.json').write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k not in ('original_roster','retained_passed_prefix')}))
sys.exit(0 if record['success'] else 1)
