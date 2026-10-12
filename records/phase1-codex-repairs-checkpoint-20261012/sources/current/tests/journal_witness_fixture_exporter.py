"""Retain exact native operands from the unchanged original fixture campaign.

Use install(directory, source_identity) before the original fixture suite runs.
This exporter does not fabricate packets, decisions, raw rosters, memberships or
fixtures, and does not decide whether a fixture is accepted. Its full invocation
record remains tied to the exact same candidate source identity.
"""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
from threading import Lock


@contextmanager
def install(directory, source_identity):
    from worldline import journal_witness_kernel as kernel
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=False)
    original = kernel.invoke
    mutex = Lock()
    count = 0

    def retain(native, kind, current, input_bytes):
        nonlocal count
        decision = original(native, kind, current, input_bytes)
        with mutex:
            ordinal = count
            count += 1
            current_name = f'{ordinal:08d}.current'
            input_name = f'{ordinal:08d}.input'
            (root / current_name).write_bytes(current)
            (root / input_name).write_bytes(input_bytes)
            row = {'source_identity': source_identity, 'kind': kind,
                   'decision': decision, 'current': current_name,
                   'current_sha256': hashlib.sha256(current).hexdigest(),
                   'input': input_name,
                   'input_sha256': hashlib.sha256(input_bytes).hexdigest()}
            with (root / 'invocations.jsonl').open('a', encoding='ascii') as output:
                output.write(json.dumps(row, sort_keys=True, separators=(',', ':')) + '\n')
        return decision

    kernel.invoke = retain
    try:
        yield root
    finally:
        kernel.invoke = original
