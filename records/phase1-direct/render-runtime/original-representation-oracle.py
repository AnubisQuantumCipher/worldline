from pathlib import Path
import hashlib
import json
import random
import subprocess
import sys
import time

root = Path('/home/sicarii/Work/worldline-phase1-completion-20261016')
temp = Path(__file__).resolve().parent
out = Path(sys.argv[1])
rng = random.Random(20261017)
alphabet = ['a', 'Z', ' ', "'", '"', '\\', '\x00', '\n', '\t', 'é', 'Π', '\u0301', '\u2028', '\u200b', '😀', '\ud800', '\udfff', '\u00a0']
def value(depth):
    choice = rng.randrange(6 if depth else 4)
    if choice == 0: return rng.choice([None, True, False])
    if choice == 1: return rng.randrange(-100000000000000000000000, 100000000000000000000000)
    if choice == 2: return ''.join(rng.choice(alphabet) for _ in range(rng.randrange(20)))
    if choice == 3: return rng.choice([-0.0, 1.25, 0.000125, 1e18])
    if choice == 4: return [value(depth - 1) for _ in range(rng.randrange(6))]
    return {''.join(rng.choice(alphabet) for _ in range(rng.randrange(8))): value(depth - 1) for _ in range(rng.randrange(6))}

cases = [(f'generated-{i}', json.dumps(value(3), ensure_ascii=True)) for i in range(512)]
cases += [
    ('duplicate-order', '{"b":1,"a":2,"b":3}'),
    ('escaped-key-equality', '{"\\u0061":1,"a":2,"A":3}'),
    ('surrogate-pair-key-equality', '{"\\ud83d\\ude00":1,"😀":2}'),
    ('empty-key', '{"":1,"x":2,"":3}'),
    ('special-numbers', '[NaN,Infinity,-Infinity,-0.0]'),
    ('linear-array-100000', '[' + ','.join(['0'] * 100000) + ']'),
    ('indexed-object-20000', json.dumps({f'key{i:07d}': i for i in range(20000)}, separators=(',', ':'))),
]
subprocess.run(['gprbuild', '-p', '-j2', '-P', str(temp / 'representation_oracle.gpr')], check=True)
inputs = ''.join(source + '\n' for _, source in cases).encode('utf-8', 'surrogatepass')
started = time.monotonic()
child = subprocess.run([str(temp / 'after-bin/representation_oracle')], input=inputs, capture_output=True, timeout=240)
(out / 'oracle.stdout').write_bytes(child.stdout)
(out / 'oracle.stderr').write_bytes(child.stderr)
lines = child.stdout.splitlines()
failures = []
rows = []
for index, (label, source) in enumerate(cases):
    decoded = json.loads(source)
    expected = str(decoded).encode('utf-8', 'surrogatepass')
    actual = bytes.fromhex(lines[index].decode('ascii')) if index < len(lines) else None
    matched = actual == expected
    row = {'label': label, 'input_bytes': len(source.encode('utf-8', 'surrogatepass')), 'expected_bytes': len(expected), 'matched': matched, 'expected_sha256': hashlib.sha256(expected).hexdigest(), 'actual_sha256': hashlib.sha256(actual).hexdigest() if actual is not None else None}
    rows.append(row)
    if not matched:
        failures.append(dict(row, source=source, expected_hex=expected[:256].hex(), actual_hex=actual[:256].hex() if actual is not None else None))
record = {'classification': 'TESTED', 'exit_code': child.returncode, 'elapsed_seconds': time.monotonic() - started, 'cases': len(cases), 'output_lines': len(lines), 'failures': failures, 'rows': rows, 'library_sha256': hashlib.sha256((root / 'lib/libworldline_core.so').read_bytes()).hexdigest(), 'phase1_acceptance': 'NOT PERFORMED'}
(out / 'result.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({key: record[key] for key in ('exit_code', 'elapsed_seconds', 'cases', 'output_lines', 'failures')}), flush=True)
raise SystemExit(0 if child.returncode == 0 and len(lines) == len(cases) and not failures else 1)
