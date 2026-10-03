"""Storage sequence controls; no native admission, custody or proof claim."""
from __future__ import annotations

from pathlib import Path
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest

from worldline.errors import WorldlineError
from worldline.evaluation_pending import PendingRefused
from worldline.finalization_journal import FinalizationJournal, _FinalizationLog


def ordinal(number):
    return number.to_bytes((number.bit_length() + 7) // 8, 'little')


class FinalizationObservationSequence(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='worldline-journal-sequence-')
        self.addCleanup(temporary.cleanup)
        self.log = _FinalizationLog(Path(temporary.name) / 'journal.sqlite', 'owned-store', create=True)
        self.addCleanup(self.log.close)
        self.start = SimpleNamespace(run=b'owned-run')
        with self.log._transaction():
            self.log._start(self.start.run, b'owned-subject', b'owned-start-bytes')

    def insert(self, event, position, payload=b'prior-payload', *, run=None):
        self.log.db.execute('INSERT INTO main.observations VALUES(?,?,?,?,?,?)',
            (self.start.run if run is None else run, event, position,
             b'owned-invocation', 'raw-acquisition', payload))

    def append(self, event, payload, *, invocation=b'owned-invocation', phase='raw-acquisition'):
        # Exercise the real storage append branch under its original guarded
        # transaction. Native admission is outside this internal storage test.
        with self.log._transaction():
            FinalizationJournal._observe_locked(self.log, self.start, event, invocation, phase, payload)

    def test_empty_and_complete_numeric_sequence_keep_all_full_events(self):
        with self.log._transaction():
            self.assertEqual(self.log._events(self.start.run), ())
            self.assertEqual(self.log._event_count(self.start.run), 0)
            # Cross a little-endian byte boundary and insert in reverse order.
            # Byte-order or query-order sorting would not give the numeric order.
            expected = [(str(n).encode(), ordinal(n), b'payload-' + str(n).encode())
                        for n in range(258)]
            for event, position, payload in reversed(expected):
                self.insert(event, position, payload)
            events = self.log._events(self.start.run)
            self.assertEqual(self.log._event_count(self.start.run), len(events))
            self.assertEqual([(row['event'], row['ordinal'], row['payload']) for row in events], expected)
            self.assertTrue(all(row['invocation'] == b'owned-invocation'
                                and row['phase'] == 'raw-acquisition' for row in events))

    def test_count_does_not_read_payload_column_and_remains_run_scoped(self):
        with self.log._transaction():
            self.insert(b'first', b'', b'original\x00\xffpayload' * 4096)
            self.log._start(b'other-run', b'other-subject', b'other-start')
            self.insert(b'other', b'', b'other', run=b'other-run')
            reads = []

            def authorize(action, table, column, database, _source):
                if action == sqlite3.SQLITE_READ and table == 'observations':
                    reads.append((database, column))
                    if column == 'payload':
                        return sqlite3.SQLITE_DENY
                return sqlite3.SQLITE_OK

            self.log.db.set_authorizer(authorize)
            try:
                self.assertEqual(self.log._event_count(self.start.run), 1)
                self.assertIn(('main', 'ordinal'), reads)
                self.assertNotIn(('main', 'payload'), reads)
                with self.assertRaises(sqlite3.DatabaseError):
                    self.log._events(self.start.run)
            finally:
                self.log.db.set_authorizer(None)
            # A fresh count observes a newly stored frontier; no cached count.
            self.insert(b'second', b'\x01')
            self.assertEqual(self.log._event_count(self.start.run), 2)
            self.assertEqual(self.log._event_count(b'other-run'), 1)

    def test_noncanonical_and_gapped_prefixes_refuse_on_both_paths(self):
        for positions, expected_type, expected_code in (
            ([b'\x00'], PendingRefused, 'EPOCH_STORAGE_NOT_CANONICAL'),
            ([b'', b'\x01\x00'], PendingRefused, 'EPOCH_STORAGE_NOT_CANONICAL'),
            ([b'\x01'], WorldlineError, 'FINALIZATION_OBSERVATION_SEQUENCE_INVALID'),
            ([b'', b'\x02'], WorldlineError, 'FINALIZATION_OBSERVATION_SEQUENCE_INVALID'),
        ):
            with self.subTest(positions=positions), self.log._transaction():
                self.log.db.execute('DELETE FROM main.observations')
                for index, position in enumerate(positions):
                    self.insert(str(index).encode(), position)
                for reader in (self.log._events, self.log._event_count):
                    with self.assertRaises(expected_type) as caught:
                        reader(self.start.run)
                    if expected_type is PendingRefused:
                        self.assertEqual(str(caught.exception), expected_code)
                    else:
                        self.assertEqual(caught.exception.code, expected_code)

    def test_duplicate_ordinals_refuse_and_schema_keeps_its_unique_constraint(self):
        with self.assertRaises(WorldlineError) as caught:
            self.log._ordered_events([{'ordinal': b''}, {'ordinal': b''}])
        self.assertEqual(caught.exception.code, 'FINALIZATION_OBSERVATION_SEQUENCE_INVALID')
        with self.log._transaction():
            self.insert(b'first', b'')
            with self.assertRaises(sqlite3.IntegrityError):
                self.insert(b'duplicate', b'')
            self.assertEqual(self.log._event_count(self.start.run), 1)

    def test_append_preserves_every_prior_byte_and_uses_only_ordinal_projection_for_position(self):
        original = b'whole\x00\xffprior\r\n' * 4096
        self.append(b'first', original)
        before = [tuple(row) for row in self.log._events(self.start.run)]
        statements = []
        self.log.db.set_trace_callback(statements.append)
        try:
            self.append(b'second', b'whole\x00\xffnew\r\n')
        finally:
            self.log.db.set_trace_callback(None)
        after = [tuple(row) for row in self.log._events(self.start.run)]
        self.assertEqual(after[:-1], before)
        self.assertEqual(after[0][-1], original)
        self.assertEqual(after[-1][-1], b'whole\x00\xffnew\r\n')
        self.assertTrue(any(sql.startswith('SELECT ordinal FROM main.observations WHERE run=')
                            for sql in statements))
        self.assertFalse(any(sql.startswith('SELECT event,ordinal,invocation,phase,payload ')
                             for sql in statements))
        self.assertEqual(statements[0], 'BEGIN IMMEDIATE')
        self.assertEqual(statements[-1], 'COMMIT')

    def test_replay_conflict_and_capture_boundary_remain_unchanged(self):
        payload = b'original\x00\xff'
        self.append(b'event', payload)
        with self.log._transaction():
            self.log._once('captures', self.start.run, b'capture')
        before = [tuple(row) for row in self.log._events(self.start.run)]
        self.append(b'event', payload)  # The original exact replay remains idempotent.
        for options in ({'payload': b'different'},
                        {'payload': payload, 'invocation': b'another'},
                        {'payload': payload, 'phase': 'another'}):
            with self.subTest(options=options), self.assertRaises(WorldlineError) as caught:
                self.append(b'event', **options)
            self.assertEqual(caught.exception.code, 'FINALIZATION_OBSERVATION_REPLAY_CONFLICT')
        with self.assertRaises(WorldlineError) as caught:
            self.append(b'new-event', b'new-payload')
        self.assertEqual(caught.exception.code, 'FINALIZATION_CAPTURE_ALREADY_RETURNED')
        self.assertEqual([tuple(row) for row in self.log._events(self.start.run)], before)

    def test_invalid_prefix_rolls_back_new_append_without_rewriting_evidence(self):
        with self.log._transaction():
            self.insert(b'bad-prior', b'\x01', b'prior\x00\xff')
        before = [tuple(row) for row in self.log.db.execute('SELECT * FROM main.observations')]
        with self.assertRaises(WorldlineError) as caught:
            self.append(b'new-event', b'new-payload')
        self.assertEqual(caught.exception.code, 'FINALIZATION_OBSERVATION_SEQUENCE_INVALID')
        self.assertFalse(self.log.db.in_transaction)
        self.assertEqual([tuple(row) for row in self.log.db.execute('SELECT * FROM main.observations')], before)


if __name__ == '__main__':
    unittest.main()
