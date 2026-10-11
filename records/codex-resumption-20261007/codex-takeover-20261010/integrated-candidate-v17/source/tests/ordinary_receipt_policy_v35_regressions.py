"""Unrun additive original-domain regressions on a genuine isolated store.

Main supplies the real selected native kernel, original SQLite STRICT store and
an existing real world. These invoke actual append bodies and interpreter; no
positive source/grant/driver output is synthesized or mocked.
"""
from __future__ import annotations

from copy import deepcopy
from contextlib import contextmanager
import sys
import json
from pathlib import Path

from worldline.errors import WorldlineError
from worldline.operation_capture import archive
from worldline.ordinary_receipt_policy import _decide, append_postflight, receipt_policy, receipt_schema

@contextmanager
def collect_actual_sql_write_sources():
    """Observe genuine original postflight return boundaries without replacement.

    Main uses this only in an isolated control campaign. No original function,
    INSERT, binding, interpreter result or native decision is mocked or changed.
    """
    collected = []
    previous = sys.getprofile()
    code = append_postflight.__code__
    def observe(frame, event, value):
        if previous is not None:
            previous(frame, event, value)
        if frame.f_code is code and event == 'return' and type(value) is dict:
            collected.append(deepcopy(value))
    sys.setprofile(observe)
    try:
        yield collected
    finally:
        sys.setprofile(previous)


def exercise_original_event_protocols(store, world_instance):
    assert getattr(store, 'canonical_operation_principal', None) is None
    class FalseThenTrue:
        def __init__(self):
            self.calls = 0
        def __bool__(self):
            self.calls += 1
            return self.calls != 1
    class TrueOnce:
        def __init__(self):
            self.calls = 0
        def __bool__(self):
            self.calls += 1
            if self.calls != 1:
                raise AssertionError('original authored protocol was repeated')
            return True
    class KindOnce(str):
        def __new__(cls):
            value = super().__new__(cls, 'original-kind-bytes')
            value.calls = 0
            return value
        def __str__(self):
            self.calls += 1
            if self.calls != 1:
                raise AssertionError('original INSERT kind conversion was repeated')
            return 'actual-insert-kind'
    class LiveSchema(int):
        def __new__(cls):
            value = super().__new__(cls, 2)
            value.calls = 0
            return value
        def __ne__(self, other):
            self.calls += 1
            return False
    def actual(result):
        row = store._connection.execute('SELECT * FROM causal_events WHERE event_id=?',
                                        (result['eventId'],)).fetchone()
        raw = store.read_canonical('events', row['canonical_path'], chain_hash=row['chain_hash'])
        return dict(row), json.loads(raw.decode('utf-8'))
    base = {'schemaVersion': 1, 'worldInstance': world_instance,
            'actor': 'independent-agent', 'kind': 'ordinary-record'}
    false = FalseThenTrue()
    _, payload = actual(store.append_causal_event(dict(base), worldline_authored=false))
    assert false.calls == 1 and 'origin' not in payload
    true, kind = TrueOnce(), KindOnce()
    row, _ = actual(store.append_causal_event({**base, 'kind': kind}, worldline_authored=true))
    assert true.calls == 1 and kind.calls == 1 and row['kind'] == 'actual-insert-kind'
    row, _ = actual(store.append_causal_event({**base, 'lineStart': '1e1', 'lineEnd': '2e1'},
                                             worldline_authored=True))
    assert row['line_start'] == 10 and row['line_end'] == 20
    schema = LiveSchema()
    _, payload = actual(store.append_causal_event({**base, 'schemaVersion': schema},
                                                 worldline_authored=True))
    assert schema.calls == 1 and payload['schemaVersion'] == 2
    # The schema-free original history remains admissible for the next append.
    actual(store.append_causal_event(dict(base), worldline_authored=True))
    # Original binding error remains after file write, at the real INSERT.
    before_files = set(store.paths.events.iterdir())
    try:
        store.append_causal_event({**base, 'lineStart': []}, worldline_authored=True)
    except Exception as exc:
        import sqlite3
        assert isinstance(exc, sqlite3.ProgrammingError)
    else:
        raise AssertionError('original unsupported binding was accepted')
    assert set(store.paths.events.iterdir()) > before_files
    return ('single-authored-truth-false', 'single-authored-truth-true', 'single-original-kind-stage',
            'exact-original-strict-affinity', 'live-schema-source-through-candidate-and-history',
            'original-binding-error-stage')


def exercise_original_receipt_key_errors(core, actual_receipt):
    # This genuine receipt is used only for original field validation; no extra
    # receipt/transaction/source authority is manufactured or persisted.
    altered = deepcopy(actual_receipt)
    altered.pop('requesterBinding', None)
    altered[99] = 'extra-original-integer-key'
    source = receipt_schema(core, altered)
    try:
        receipt_policy(core, altered, None, source)
    except WorldlineError as exc:
        assert exc.code == 'INVALID_RECEIPT'
        assert exc.details == {'missing': [], 'extra': [99]}
    else:
        raise AssertionError('original extra field was accepted')
    return 'original-integer-key-error-before-archive-or-canonical-serialization'


def export_actual_sql_write(packet, destination):
    """Main acquires packet at original append_postflight's live source boundary.

    It contains the genuine INSERT cursor/lastrowid/full output row/STRICT schema
    and separately acquired full current rows/files. It is not a replay grant.
    """
    assert 'sqlite_write' in packet and 'current' in packet
    Path(destination).write_bytes(archive(packet))
    return packet


def exercise_actual_sql_write_joins(core, packet):
    assert _decide(core, 9, packet) == 'READY'
    for label, mutate in (
        ('connection', lambda p: p['sqlite_write'].__setitem__('connection_identity', 0)),
        ('store', lambda p: p['sqlite_write'].__setitem__('store_identity', 0)),
        ('cursor-class', lambda p: p['sqlite_write']['cursor'].__setitem__('class', 'CopiedOutput')),
        ('cursor-rowid', lambda p: p['sqlite_write'].__setitem__('lastrowid', 0)),
        ('observed-rowid', lambda p: p['sqlite_write'].__setitem__('rowid', 0)),
        ('complete-output-row', lambda p: p['sqlite_write']['sql'].pop('created_at')),
        ('strict-schema', lambda p: p['sqlite_write']['schema']['columns'].pop()),
        ('independent-readback', lambda p: p['current'][-1]['sql'].__setitem__('created_at', 'changed')),
    ):
        altered = deepcopy(packet)
        mutate(altered)
        assert _decide(core, 9, altered) == 'ACTUAL_WRITE_MISMATCH', label
    return ('connection', 'store', 'cursor-class', 'cursor-rowid', 'observed-rowid',
            'complete-output-row', 'strict-schema', 'independent-readback')
