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


def event_values(row):
    # Retained events are mappings; compare every selected value, not dict keys.
    return tuple(row[name] for name in ('event', 'ordinal', 'invocation', 'phase', 'payload'))


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
        before = [event_values(row) for row in self.log._events(self.start.run)]
        statements = []
        self.log.db.set_trace_callback(statements.append)
        try:
            self.append(b'second', b'whole\x00\xffnew\r\n')
        finally:
            self.log.db.set_trace_callback(None)
        after = [event_values(row) for row in self.log._events(self.start.run)]
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
        before = [event_values(row) for row in self.log._events(self.start.run)]
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
        self.assertEqual([event_values(row) for row in self.log._events(self.start.run)], before)

    def test_invalid_prefix_rolls_back_new_append_without_rewriting_evidence(self):
        with self.log._transaction():
            self.insert(b'bad-prior', b'\x01', b'prior\x00\xff')
        before = [tuple(row) for row in self.log.db.execute('SELECT * FROM main.observations')]
        with self.assertRaises(WorldlineError) as caught:
            self.append(b'new-event', b'new-payload')
        self.assertEqual(caught.exception.code, 'FINALIZATION_OBSERVATION_SEQUENCE_INVALID')
        self.assertFalse(self.log.db.in_transaction)
        self.assertEqual([tuple(row) for row in self.log.db.execute('SELECT * FROM main.observations')], before)


class AcquisitionDetachedCloneCorrespondence(unittest.TestCase):
    """Original-codec and ownership controls, not a performance/proof claim."""

    def clone(self, value):
        from worldline.finalization_writer import _owned_acquisition
        return _owned_acquisition(value)

    def legacy(self, value):
        from worldline.finalization_journal import encode, decode
        return decode(encode(value))

    def codec_outcome(self, operation, value):
        from worldline.finalization_journal import encode
        try:
            return ('accepted', encode(operation(value)))
        except Exception as error:
            return ('refused', type(error), getattr(error, 'code', None), error.args)

    def test_complete_builtin_values_keep_codec_order_and_immutable_leaves(self):
        from unittest.mock import patch
        from worldline import finalization_writer as writer_module
        from worldline.finalization_journal import encode
        value = {'z': b'\x00\xffwhole\r\n', 'a': '\ud800\x00\udfff',
                 'tuple': (None, True, False, 1 << 20000, -(1 << 20000), []),
                 'empty': {'bytes': b'', 'str': '', 'tuple': (), 'list': [], 'dict': {}}}
        # Only the transient structural witness is serialized on this path.
        witnesses = []
        expected_shape = {'z': b'', 'a': '',
            'tuple': (None, True, False, 0, 0, []),
            'empty': {'bytes': b'', 'str': '', 'tuple': (), 'list': [], 'dict': {}}}
        def structural_only(item):
            witnesses.append(item)
            self.assertEqual(item, expected_shape)
            return encode(item)
        with patch.object(writer_module, 'encode', side_effect=structural_only):
            owned = self.clone(value)
        self.assertEqual(witnesses, [expected_shape])
        self.assertEqual(encode(owned), encode(self.legacy(value)))
        self.assertEqual(list(owned), list(value))
        self.assertIs(owned['z'], value['z'])
        self.assertIs(owned['a'], value['a'])
        self.assertIs(type(owned['tuple']), tuple)
        self.assertIs(type(owned['tuple'][-1]), list)
        self.assertIsNot(owned['tuple'][-1], value['tuple'][-1])

    def test_aliases_are_detached_per_occurrence_and_both_directions(self):
        shared = [{'bytes': b'original'}]
        value = {'left': shared, 'right': shared, 'tuple': (shared,)}
        owned = self.clone(value)
        self.assertIsNot(owned, value)
        self.assertIsNot(owned['left'], shared)
        self.assertIsNot(owned['left'], owned['right'])
        self.assertIsNot(owned['left'][0], owned['right'][0])
        self.assertIsNot(owned['tuple'][0], owned['left'])
        owned['left'][0]['bytes'] = b'owned mutation'
        self.assertEqual(owned['right'][0]['bytes'], b'original')
        self.assertEqual(shared[0]['bytes'], b'original')
        shared.append({'later': b'caller mutation'})
        self.assertEqual(owned['right'], [{'bytes': b'original'}])
        self.assertEqual(owned['tuple'], ([{'bytes': b'original'}],))

    def test_float_normalization_matches_original_packed_bits_or_refusal(self):
        import struct
        from unittest.mock import patch
        from worldline import finalization_writer as writer_module
        from worldline.finalization_journal import encode
        # Existing test_runner_outcome_native_v35 fixtures include signed zero,
        # subnormal, infinity, signaling NaN and a signed payload NaN pattern.
        for bits in ('0000000000000000', '8000000000000000',
                     '0000000000000001', '8000000000000001',
                     '7ff0000000000000', 'fff0000000000000',
                     '7ff0000000000001', 'fff8000000000011'):
            value = struct.unpack('!d', bytes.fromhex(bits))[0]
            root = {'float': value}
            with self.subTest(bits=bits):
                expected = self.codec_outcome(self.legacy, root)
                self.assertEqual(self.codec_outcome(self.clone, root), expected)
                if expected[0] == 'accepted':
                    original = self.legacy(root)['float']
                    calls = []
                    def scalar(item):
                        calls.append(item)
                        return encode(item)
                    with patch.object(writer_module, 'encode', side_effect=scalar):
                        copied = self.clone(root)['float']
                    self.assertEqual([type(item) for item in calls], [dict])
                    self.assertIsNot(calls[0], root)
                    self.assertEqual(struct.pack('!d', copied), struct.pack('!d', original))

    def test_subclasses_fall_back_once_with_original_foreign_dispatch(self):
        from unittest.mock import patch
        from worldline import finalization_writer as writer_module
        from worldline.finalization_journal import encode
        effects = []
        class Word(str):
            def __str__(self):
                raise AssertionError('base identity codec must not call override')
            def encode(self, *args, **kwargs):
                raise AssertionError('base identity codec must not call override')
        class Rows(list):
            def __iter__(self):
                effects.append('rows-iter')
                return super().__iter__()
        class Row(dict):
            def __iter__(self):
                effects.append('row-iter')
                return super().__iter__()
            def items(self):
                effects.append('row-items')
                return super().items()
        value = {'nested': Row({Word('text'): Rows([Word('\ud800\x00'), b'whole'])})}
        expected = self.legacy(value)
        original_effects = list(effects)
        effects.clear()
        roots = []
        def original_root(item):
            roots.append(item)
            return encode(item)
        with patch.object(writer_module, 'encode', side_effect=original_root):
            actual = self.clone(value)
        self.assertEqual([id(item) for item in roots], [id(value)])
        self.assertEqual(effects, original_effects)
        self.assertEqual(encode(actual), encode(expected))
        self.assertIs(type(actual['nested']), dict)
        self.assertIs(type(actual['nested']['text']), list)
        self.assertIs(type(actual['nested']['text'][0]), str)

    def test_whole_root_fallback_preserves_invalid_key_and_value_precedence(self):
        from unittest.mock import patch
        from worldline import finalization_writer as writer_module
        from worldline.finalization_journal import encode
        class Pairs(dict):
            def __init__(self, pairs):
                super().__init__(valid='original-key-precheck')
                self.pairs = pairs
            def items(self):
                return self.pairs
        class Bytes(bytes):
            pass
        class Integer(int):
            pass
        class Float(float):
            pass
        unsupported = object()
        cases = [
            {'first': float('nan'), 'later': unsupported},
            {1: unsupported},
            {'nested': Bytes(b'original')},
            {'nested': Integer(1)},
            {'nested': Float(0.0)},
            {'nested': memoryview(b'original')},
            Pairs([(1, 'invalid-decoded-key')]),
            Pairs([(1, 'invalid-decoded-key'), ('later', unsupported)]),
            Pairs([('same', 'first'), ('same', 'duplicate')]),
            Pairs([('same', 'first'), ('same', 'duplicate'), ('later', unsupported)]),
        ]
        for value in cases:
            with self.subTest(kind=type(value).__name__):
                expected = self.codec_outcome(self.legacy, value)
                self.assertEqual(expected[0], 'refused')
                roots = []
                def original_root(item):
                    roots.append(item)
                    return encode(item)
                with patch.object(writer_module, 'encode', side_effect=original_root):
                    actual = self.codec_outcome(self.clone, value)
                self.assertEqual(actual, expected)
                # No early scalar float conversion or nested substitute codec.
                self.assertEqual([id(item) for item in roots], [id(value)])

    def test_cycles_use_original_whole_root_refusal_without_alias_memo(self):
        from unittest.mock import patch
        from worldline import finalization_writer as writer_module
        from worldline.finalization_journal import encode
        array = []; array.append(array)
        mapping = {}; mapping['self'] = mapping
        child = []; tuple_cycle = (child,); child.append(tuple_cycle)
        for value in (array, mapping, tuple_cycle):
            with self.subTest(kind=type(value).__name__):
                with self.assertRaises(RecursionError):
                    self.legacy(value)
                roots = []
                def original_root(item):
                    roots.append(item)
                    return encode(item)
                with patch.object(writer_module, 'encode', side_effect=original_root):
                    with self.assertRaises(RecursionError):
                        self.clone(value)
                self.assertEqual([id(item) for item in roots], [id(value)])

    def test_codec_refusal_precedes_every_writer_publication(self):
        from threading import RLock
        from worldline.finalization_writer import EngineFinalizationWriter
        cycle = []; cycle.append(cycle)
        for observed in ({'bad': object()}, {1: 'invalid-key'}, cycle):
            journal = object.__new__(FinalizationJournal)
            journal.lock = RLock()
            persisted = []
            journal.observe = lambda *args: persisted.append(args)
            writer = EngineFinalizationWriter(journal, None)
            writer.invocations[('subject', 'check')] = ('owned-invocation', {})
            with self.subTest(kind=type(observed).__name__):
                with self.assertRaises((WorldlineError, RecursionError)):
                    writer.invocation_raw(world_instance='subject', check='check',
                        kind='original-observation', observed=observed)
                self.assertEqual(writer.raw_observations, {})
                self.assertEqual(writer._raw_events, [])
                self.assertIsNone(writer._acquisition_failure)
                self.assertEqual(persisted, [])

    def test_preflight_interruption_is_preserved_without_root_retry(self):
        from unittest.mock import patch
        from worldline import finalization_writer as writer_module
        original = KeyboardInterrupt('actual scalar interruption control')
        calls = []
        def interrupted(item):
            calls.append(item)
            raise original
        with patch.object(writer_module, 'encode', side_effect=interrupted):
            with self.assertRaises(KeyboardInterrupt) as caught:
                self.clone({'float': -0.0})
        self.assertIs(caught.exception, original)
        self.assertEqual([type(item) for item in calls], [dict])


    def test_acyclic_expanded_codec_depth_matches_original_caller_and_publication(self):
        import sys
        import struct
        from threading import RLock
        from unittest.mock import patch
        from worldline import finalization_writer as writer_module
        from worldline.finalization_writer import EngineFinalizationWriter
        from worldline.finalization_journal import encode, decode

        def original_owned(value):
            return decode(encode(value))

        def outcome(operation, value):
            try:
                return ('accepted', encode(operation(value)))
            except Exception as error:
                return ('refused', type(error), getattr(error, 'code', None))

        def extra_caller(operation, value):
            return outcome(operation, value)

        # This is a finite original-codec oracle ladder, not a product depth
        # limit or a guessed admissibility threshold. Both helpers see the same
        # caller context; the additional caller also exercises reduced headroom.
        refused = None
        for caller in (outcome, extra_caller):
            value = None
            boundary = None
            for _ in range(sys.getrecursionlimit()):
                value = [{'tuple': (value,)}]
                expected = caller(original_owned, value)
                self.assertEqual(caller(writer_module._owned_acquisition, value), expected)
                if expected[0] == 'refused':
                    self.assertIs(expected[1], RecursionError)
                    boundary = value
                    break
            self.assertIsNotNone(boundary, 'original expanded-codec refusal was not reached')
            refused = boundary

        # Original structural traversal precedes even an earlier signaling-NaN
        # candidate. No scalar conversion may preempt a later deep-tree refusal.
        floating = struct.unpack('!d', bytes.fromhex('7ff0000000000001'))[0]
        root = {'earlier-float': floating, 'later-deep-tree': refused}
        expected = outcome(original_owned, root)
        self.assertEqual(expected[0], 'refused')
        self.assertIs(expected[1], RecursionError)
        roots = []
        def recorded(item):
            roots.append(item)
            return encode(item)
        with patch.object(writer_module, 'encode', side_effect=recorded):
            self.assertEqual(outcome(writer_module._owned_acquisition, root), expected)
        self.assertTrue(roots)
        self.assertIs(roots[-1], root)
        self.assertTrue(all(type(item) is dict for item in roots))

        for helper in (original_owned, writer_module._owned_acquisition):
            journal = object.__new__(FinalizationJournal)
            journal.lock = RLock()
            persisted = []
            journal.observe = lambda *args: persisted.append(args)
            writer = EngineFinalizationWriter(journal, None)
            writer.invocations[('subject', 'check')] = ('owned-invocation', {})
            with self.subTest(helper=helper.__name__):
                with patch.object(writer_module, '_owned_acquisition', helper):
                    with self.assertRaises(RecursionError):
                        writer.invocation_raw(world_instance='subject', check='check',
                            kind='depth-sensitive-original-control', observed=root)
                self.assertEqual(writer.raw_observations, {})
                self.assertEqual(writer._raw_events, [])
                self.assertIsNone(writer._acquisition_failure)
                self.assertEqual(persisted, [])

    def test_original_fallback_refusal_does_not_expose_internal_decline_context(self):
        from worldline.finalization_journal import encode, decode
        value = {'unsupported': object()}
        for operation in (lambda item: decode(encode(item)), self.clone):
            with self.assertRaises(WorldlineError) as caught:
                operation(value)
            self.assertEqual(caught.exception.code, 'FINALIZATION_VALUE_UNSUPPORTED')
            self.assertIsNone(caught.exception.__context__)


class TerminalDetachedOwnershipCorrespondence(unittest.TestCase):
    """Exact original terminal semantics; finite memory control is not acceptance."""

    @staticmethod
    def legacy(value):
        from worldline import finalization_writer as writer
        return writer.bytes_value(writer.value_bytes(value))

    @staticmethod
    def outcome(operation, value):
        from worldline.evaluation_terminal import value_bytes
        try:
            return ('accepted', value_bytes(operation(value)))
        except Exception as error:
            return ('refused', type(error), error.args, type(error.__context__))

    def test_full_leaves_keys_magnitudes_surrogates_and_terminal_array_shape(self):
        import sys
        from unittest.mock import patch
        from worldline import finalization_writer as writer
        original_codec = writer.value_bytes
        original_identity, original_magnitude = writer.identity, writer.magnitude
        value = {'\ud800-key\x00': '\udfff\x00whole', 'signed': (1 << 20000, -(1 << 20000)),
                 'scalars': [None, True, False, 0, '', (), [], {}]}
        shape = {'\ud800-key\x00': '', 'signed': [0, 0],
                 'scalars': [None, True, False, 0, '', [], [], {}]}
        witnesses, identities, magnitudes = [], [], []
        def structural(item):
            witnesses.append(item)
            self.assertEqual(item, shape)
            return original_codec(item)
        def identity_leaf(item):
            identities.append(item)
            return original_identity(item)
        def magnitude_leaf(item):
            magnitudes.append(item)
            return original_magnitude(item)
        previous = sys.get_int_max_str_digits()
        try:
            sys.set_int_max_str_digits(sys.int_info.str_digits_check_threshold)
            with patch.object(writer, 'value_bytes', side_effect=structural), \
                 patch.object(writer, 'identity', side_effect=identity_leaf), \
                 patch.object(writer, 'magnitude', side_effect=magnitude_leaf):
                owned = writer._owned(value)
        finally:
            sys.set_int_max_str_digits(previous)
        self.assertEqual(original_codec(owned), original_codec(self.legacy(value)))
        self.assertEqual(witnesses, [shape])
        # Whole exact immutable values need no ownership serialization. Keep
        # the original full-codec equality above and every real leaf/key below.
        self.assertIs(owned['\ud800-key\x00'], value['\ud800-key\x00'])
        self.assertIs(next(iter(owned)), next(iter(value)))
        self.assertIs(owned['signed'][0], value['signed'][0])
        self.assertIs(owned['signed'][1], value['signed'][1])
        self.assertIs(type(owned['signed']), list)
        self.assertEqual(list(owned), list(value))

    def test_aliases_detach_per_occurrence_in_both_directions(self):
        from worldline.finalization_writer import _owned
        shared = [{'text': 'original'}]
        value = {'left': shared, 'right': shared, 'tuple': (shared,)}
        owned = _owned(value)
        self.assertIs(type(owned['tuple']), list)
        self.assertIsNot(owned['left'], shared)
        self.assertIsNot(owned['left'], owned['right'])
        self.assertIsNot(owned['left'][0], owned['right'][0])
        self.assertIsNot(owned['tuple'][0], owned['left'])
        owned['left'][0]['text'] = 'owned mutation'
        shared.append({'text': 'caller mutation'})
        self.assertEqual(owned['right'], [{'text': 'original'}])
        self.assertEqual(owned['tuple'], [[{'text': 'original'}]])
        self.assertEqual(shared[0]['text'], 'original')

    def test_float_packed_bits_match_original_including_nan_payload_and_signed_zero(self):
        import struct
        from worldline.finalization_writer import _owned
        for bits in ('0000000000000000', '8000000000000000',
                     '0000000000000001', '8000000000000001',
                     '7ff0000000000000', 'fff0000000000000',
                     '7ff0000000000001', 'fff8000000000011'):
            root = {'float': struct.unpack('!d', bytes.fromhex(bits))[0]}
            with self.subTest(bits=bits):
                expected = self.legacy(root)['float']
                actual = _owned(root)['float']
                self.assertEqual(struct.pack('!d', actual), struct.pack('!d', expected))
                self.assertEqual(self.outcome(_owned, root), self.outcome(self.legacy, root))

    def test_terminal_negative_domains_and_first_refusal_keep_original_context(self):
        from worldline import finalization_writer as writer
        from worldline.evaluation_terminal import TerminalRefused
        class IntSubclass(int): pass
        class FloatSubclass(float): pass
        for unsupported in (b'', b'full\x00\xff', bytearray(b'full'), Path('/report'),
                            object(), IntSubclass(1), FloatSubclass(1.0)):
            root = {'unsupported': unsupported}
            with self.subTest(kind=type(unsupported).__name__):
                expected = self.outcome(self.legacy, root)
                self.assertEqual(expected[0], 'refused')
                self.assertEqual(self.outcome(writer._owned, root), expected)
                with self.assertRaises(TerminalRefused) as caught:
                    writer._owned(root)
                self.assertEqual(caught.exception.args, ('CAPTURE_VALUE_UNSUPPORTED',))
                self.assertIsNone(caught.exception.__context__)
        root = {'earlier-invalid-key': {1: 'value'}, 'later-bytes': b'unsupported'}
        self.assertEqual(self.outcome(writer._owned, root), self.outcome(self.legacy, root))

    def test_subclasses_foreign_hooks_use_original_whole_root_once(self):
        from worldline import finalization_writer as writer
        def make():
            root, calls = {'earlier': 'before'}, []
            class EffectfulList(list):
                def __iter__(self):
                    calls.append('iterate')
                    root['earlier'] = 'after'
                    return super().__iter__()
            root['later'] = EffectfulList([1])
            return root, calls
        for operation in (self.legacy, writer._owned):
            root, calls = make()
            owned = operation(root)
            self.assertEqual(owned, {'earlier': 'before', 'later': [1]})
            self.assertEqual(root['earlier'], 'after')
            self.assertEqual(calls, ['iterate'])
        class StringSubclass(str):
            def encode(self, *args, **kwargs):
                raise AssertionError('base str.encode must ignore this override')
        root = {StringSubclass('\ud800-key'): StringSubclass('\udfff-value')}
        self.assertEqual(self.outcome(writer._owned, root), self.outcome(self.legacy, root))
        calls = []
        class LaterHook(list):
            def __iter__(self):
                calls.append('not reached')
                raise AssertionError('earlier original refusal must win')
        root = {'earlier-bytes': b'refused', 'later': LaterHook([1])}
        self.assertEqual(self.outcome(writer._owned, root), self.outcome(self.legacy, root))
        self.assertEqual(calls, [])

    def test_cycle_and_expanded_depth_match_same_original_caller_context(self):
        import sys
        from worldline import finalization_writer as writer
        def original_owned(value):
            return writer.bytes_value(writer.value_bytes(value))
        def outcome(operation, value):
            try:
                return ('accepted', writer.value_bytes(operation(value)))
            except Exception as error:
                return ('refused', type(error), error.args, type(error.__context__))
        def extra_caller(operation, value):
            return outcome(operation, value)
        for caller in (outcome, extra_caller):
            value, refused = None, None
            for _ in range(sys.getrecursionlimit()):
                value = [{'tuple': (value,)}]
                expected = caller(original_owned, value)
                self.assertEqual(caller(writer._owned, value), expected)
                if expected[0] == 'refused':
                    self.assertIs(expected[1], RecursionError)
                    refused = value
                    break
            self.assertIsNotNone(refused, 'original expanded terminal depth refusal was not reached')
        cycle = []; cycle.append(cycle)
        self.assertEqual(outcome(writer._owned, cycle), outcome(original_owned, cycle))
        import struct
        root = {'earlier-float': struct.unpack('!d', bytes.fromhex('7ff0000000000001'))[0],
                'later-depth': refused}
        self.assertEqual(outcome(writer._owned, root), outcome(original_owned, root))

    def test_writer_refusal_precedes_publication_and_persistence_failure_keeps_return(self):
        from threading import RLock
        from unittest.mock import patch
        from worldline import finalization_writer as writer
        from worldline.evaluation_terminal import TerminalRefused
        for helper in (self.legacy, writer._owned):
            journal = object.__new__(FinalizationJournal)
            journal.lock = RLock()
            calls = []
            journal.observe = lambda *args: calls.append(args)
            owned_writer = writer.EngineFinalizationWriter(journal, None)
            owned_writer.invocations[('subject', 'check')] = ('owned-invocation', {})
            owned_writer._require_acquisitions_open = lambda: None
            with patch.object(writer, '_owned', helper):
                with self.assertRaises(TerminalRefused):
                    owned_writer.invocation_result(world_instance='subject', check='check',
                                                   result={'not-terminal': b'refused'})
            self.assertEqual(owned_writer.actual_returns, {})
            self.assertEqual(calls, [])
            original = RuntimeError('original persistence refusal')
            def persist(*args): raise original
            journal.observe = persist
            with patch.object(writer, '_owned', helper):
                with self.assertRaises(RuntimeError) as caught:
                    owned_writer.invocation_result(world_instance='subject', check='check',
                                                   result={'tuple': ('kept',)})
            self.assertIs(caught.exception, original)
            self.assertEqual(owned_writer.actual_returns['owned-invocation'],
                             {'started': {}, 'result': {'tuple': ['kept']}})

    def test_original_structural_codec_baseexception_is_not_retried(self):
        from unittest.mock import patch
        from worldline import finalization_writer as writer
        original, calls = KeyboardInterrupt('actual original interruption'), []
        def interrupted(value):
            calls.append(value)
            raise original
        with patch.object(writer, 'value_bytes', side_effect=interrupted):
            with self.assertRaises(KeyboardInterrupt) as caught:
                writer._owned({'float': -0.0})
        self.assertIs(caught.exception, original)
        self.assertEqual(len(calls), 1)

    def test_full_value_semantics_with_lower_measured_transient_python_peak(self):
        import gc
        import tracemalloc
        from worldline import finalization_writer as writer
        payload = 'full-original-value\x00\ud800' * 65536
        value = {'left': [payload, payload], 'right': (payload, payload)}
        def measured(operation):
            gc.collect()
            tracemalloc.start()
            try:
                owned = operation(value)
                _current, peak = tracemalloc.get_traced_memory()
            finally:
                tracemalloc.stop()
            return owned, peak
        expected, original_peak = measured(self.legacy)
        actual, detached_peak = measured(writer._owned)
        self.assertEqual(writer.value_bytes(actual), writer.value_bytes(expected))
        self.assertLess(detached_peak, original_peak)
        self.assertIsNot(actual['left'], actual['right'])
        # Finite comparative allocation control, not exclusive process/cgroup
        # attribution or original campaign/timeout/proof acceptance.


class TerminalImmutableLeafOwnership(unittest.TestCase):
    """Full terminal values and detached containers; resource control is finite."""

    @staticmethod
    def preceding_scalar_roundtrip_owned(value):
        from worldline.finalization_writer import identity, text, magnitude, bytes_value, value_bytes
        # Exact builtins have no foreign hooks. Everything uncertain retains the
        # original whole-root terminal codec, including its caller-depth refusal.
        class _NotTerminalBuiltinTree(Exception):
            pass

        def copy_tree(item, active):
            kind = type(item)
            if item is None or kind is bool:
                return item
            if kind is str:
                # Validate the real value with the original base-method,
                # surrogatepass identity/text pair before eliding witness payloads.
                return text(identity(item))
            if kind is int:
                absolute = abs(item)
                blob = magnitude(absolute.to_bytes((absolute.bit_length() + 7) // 8, 'little'))
                decoded = int.from_bytes(blob, 'little')
                return -decoded if item < 0 else decoded
            if kind is float:
                return item  # Original witness codec supplies pack/unpack bits below.
            if kind not in (list, tuple, dict):
                raise _NotTerminalBuiltinTree
            if kind is dict and any(type(key) is not str for key in item):
                raise _NotTerminalBuiltinTree
            token = id(item)
            if token in active:
                raise _NotTerminalBuiltinTree
            active.add(token)
            try:
                if kind is dict:
                    return {text(identity(key)): copy_tree(child, active)
                            for key, child in item.items()}
                # The original terminal array decoder converts BOTH forms to lists.
                return [copy_tree(child, active) for child in item]
            finally:
                active.remove(token)

        def witness(item):
            kind = type(item)
            if kind is str: return ''
            if kind is int: return 0
            if kind is dict:
                return {key: witness(child) for key, child in item.items()}
            if kind is list:
                return [witness(child) for child in item]
            return item  # Complete real float values, bool and None remain present.

        def finish(item, shape):
            kind = type(item)
            if type(shape) is not kind:
                raise _NotTerminalBuiltinTree
            if kind is float:
                return shape  # Exact original terminal struct pack/unpack result.
            if kind is dict:
                if tuple(item) != tuple(shape):
                    raise _NotTerminalBuiltinTree
                for key, child in item.items():
                    item[key] = finish(child, shape[key])
            elif kind is list:
                if len(item) != len(shape):
                    raise _NotTerminalBuiltinTree
                for index, child in enumerate(item):
                    item[index] = finish(child, shape[index])
            return item

        owned = shape = normalized = None
        try:
            owned = copy_tree(value, set())
            shape = witness(owned)
            # Original expanded tagged/JSON/decode recursion at the original helper
            # call depth, with full keys and real floats, before any publication.
            normalized = bytes_value(value_bytes(shape))
            return finish(owned, normalized)
        except Exception:
            owned = shape = normalized = None
        # The original exception must not inherit internal decline as its context.
        # BaseException interruptions propagate without a retry or success sentinel.
        return bytes_value(value_bytes(value))

    def test_exact_immutable_leaves_preserve_original_wire_and_detach_each_container(self):
        import struct
        from worldline import finalization_writer as writer
        from worldline.evaluation_terminal import bytes_value, value_bytes
        key = '\ud800-full-key\x00' * 32
        payload = '\udfff-full-value\x00' * 32
        integer = int.from_bytes(b'\xff' * 4096, 'little')
        nan = struct.unpack('!d', bytes.fromhex('fff8000000000011'))[0]
        shared = [payload, integer, -integer, -0.0, nan]
        value = {key: shared, 'other': shared, 'tuple': (shared,)}
        actual = writer._owned(value)
        self.assertEqual(value_bytes(actual), value_bytes(bytes_value(value_bytes(value))))
        self.assertEqual(value_bytes(actual), value_bytes(self.preceding_scalar_roundtrip_owned(value)))
        self.assertIs(next(iter(actual)), key)
        self.assertIs(actual[key][0], payload)
        self.assertIs(actual[key][1], integer)
        self.assertIs(actual[key][2], shared[2])
        self.assertIs(type(actual['tuple']), list)
        self.assertIsNot(actual[key], shared)
        self.assertIsNot(actual[key], actual['other'])
        self.assertIsNot(actual[key], actual['tuple'][0])
        self.assertEqual(struct.pack('!d', actual[key][3]), struct.pack('!d', shared[3]))
        self.assertEqual(struct.pack('!d', actual[key][4]), struct.pack('!d', shared[4]))
        actual[key].append('owned change')
        shared.append('source change')
        self.assertEqual(actual['other'][0], payload)
        self.assertEqual(len(actual['other']), len(actual['tuple'][0]))
        self.assertNotIn('source change', actual['other'])
        self.assertNotIn('owned change', shared)

    def test_full_payload_has_lower_peak_than_exact_preceding_scalar_roundtrip(self):
        import gc
        import tracemalloc
        from worldline import finalization_writer as writer
        payload = 'full-original-value\x00\ud800' * 65536
        integer = int.from_bytes(b'\xff' * 4096, 'little')
        value = {'left': [payload, payload, integer, -integer],
                 'right': (payload, payload, integer, -integer)}
        def measured(operation):
            gc.collect()
            tracemalloc.start()
            try:
                owned = operation(value)
                _current, peak = tracemalloc.get_traced_memory()
            finally:
                tracemalloc.stop()
            return owned, peak
        preceding, preceding_peak = measured(self.preceding_scalar_roundtrip_owned)
        actual, immutable_leaf_peak = measured(writer._owned)
        self.assertEqual(writer.value_bytes(actual), writer.value_bytes(preceding))
        self.assertLess(immutable_leaf_peak, preceding_peak)
        self.assertIs(actual['left'][0], payload)
        self.assertIs(actual['right'][1], payload)
        self.assertIsNot(actual['left'], actual['right'])
        # No process/cgroup attribution, runtime budget, or campaign acceptance.

    def test_foreign_hook_refusal_and_original_exception_context_remain_whole_root(self):
        from worldline import finalization_writer as writer
        from worldline.evaluation_terminal import TerminalRefused, value_bytes
        def outcome(operation, value):
            try:
                return ('accepted', value_bytes(operation(value)))
            except Exception as error:
                return ('refused', type(error), error.args, type(error.__context__))
        class IntegerSubclass(int): pass
        class StringSubclass(str):
            def encode(self, *args, **kwargs):
                raise AssertionError('original base str.encode must remain authoritative')
        for value in ({'full': '\ud800\x00value', 'later': IntegerSubclass(1)},
                      {StringSubclass('\udfff-key'): StringSubclass('\ud800-value')},
                      {'full': 1 << 20000, 'later': bytearray(b'original refusal')}):
            self.assertEqual(outcome(writer._owned, value),
                             outcome(self.preceding_scalar_roundtrip_owned, value))
        calls = []
        class LaterHook(list):
            def __iter__(self):
                calls.append('unexpected later hook')
                raise AssertionError('original earlier refusal must win')
        value = {'earlier': bytearray(b'original refusal'), 'later': LaterHook([1])}
        with self.assertRaises(TerminalRefused) as caught:
            writer._owned(value)
        self.assertEqual(caught.exception.args, ('CAPTURE_VALUE_UNSUPPORTED',))
        self.assertIsNone(caught.exception.__context__)
        self.assertEqual(calls, [])




class OwnershipWitnessLifetime(unittest.TestCase):
    """Exact existing codec calls with shorter transient witness lifetime."""

    @staticmethod
    def preceding_owned(value):
        from worldline.finalization_writer import identity, text, magnitude, bytes_value, value_bytes, encode, decode
        # Exact builtins have no foreign hooks. Everything uncertain retains the
        # original whole-root terminal codec, including its caller-depth refusal.
        class _NotTerminalBuiltinTree(Exception):
            pass

        def copy_tree(item, active):
            kind = type(item)
            if item is None or kind is bool:
                return item
            if kind in (str, int):
                # Exact builtin strings and arbitrary integers are immutable and
                # already in the terminal codec's domain. Keep their whole values;
                # copying mutable containers does not require scalar roundtrips.
                return item
            if kind is float:
                return item  # Original witness codec supplies pack/unpack bits below.
            if kind not in (list, tuple, dict):
                raise _NotTerminalBuiltinTree
            if kind is dict and any(type(key) is not str for key in item):
                raise _NotTerminalBuiltinTree
            token = id(item)
            if token in active:
                raise _NotTerminalBuiltinTree
            active.add(token)
            try:
                if kind is dict:
                    return {key: copy_tree(child, active)
                            for key, child in item.items()}
                # The original terminal array decoder converts BOTH forms to lists.
                return [copy_tree(child, active) for child in item]
            finally:
                active.remove(token)

        def witness(item):
            kind = type(item)
            if kind is str: return ''
            if kind is int: return 0
            if kind is dict:
                return {key: witness(child) for key, child in item.items()}
            if kind is list:
                return [witness(child) for child in item]
            return item  # Complete real float values, bool and None remain present.

        def finish(item, shape):
            kind = type(item)
            if type(shape) is not kind:
                raise _NotTerminalBuiltinTree
            if kind is float:
                return shape  # Exact original terminal struct pack/unpack result.
            if kind is dict:
                if tuple(item) != tuple(shape):
                    raise _NotTerminalBuiltinTree
                for key, child in item.items():
                    item[key] = finish(child, shape[key])
            elif kind is list:
                if len(item) != len(shape):
                    raise _NotTerminalBuiltinTree
                for index, child in enumerate(item):
                    item[index] = finish(child, shape[index])
            return item

        owned = shape = normalized = None
        try:
            owned = copy_tree(value, set())
            shape = witness(owned)
            # Original expanded tagged/JSON/decode recursion at the original helper
            # call depth, with full keys and real floats, before any publication.
            normalized = bytes_value(value_bytes(shape))
            return finish(owned, normalized)
        except Exception:
            owned = shape = normalized = None
        # The original exception must not inherit internal decline as its context.
        # BaseException interruptions propagate without a retry or success sentinel.
        return bytes_value(value_bytes(value))

    @staticmethod
    def preceding_owned_acquisition(value):
        from worldline.finalization_writer import identity, text, magnitude, bytes_value, value_bytes, encode, decode
        # Foreign/uncertain trees keep the original whole-root codec and refusal.
        class _NotBuiltinTree(Exception):
            pass

        def visit(item, active, *, copy):
            kind = type(item)
            if item is None or kind in (bool, int, float, str, bytes):
                return item  # Float normalization follows whole structural validation.
            if kind not in (list, tuple, dict):
                raise _NotBuiltinTree
            if kind is dict and any(type(key) is not str for key in item):
                raise _NotBuiltinTree
            token = id(item)
            if token in active:
                raise _NotBuiltinTree
            active.add(token)
            try:
                if not copy:
                    for child in item.values() if kind is dict else item:
                        visit(child, active, copy=False)
                    return None
                if kind is dict:
                    return {key: visit(child, active, copy=True)
                            for key, child in item.items()}
                children = [visit(child, active, copy=True) for child in item]
                return tuple(children) if kind is tuple else children
            finally:
                active.remove(token)

        def witness(item):
            kind = type(item)
            if kind is bytes: return b''
            if kind is str: return ''
            if kind is int: return 0
            if kind is dict:
                return {key: witness(child) for key, child in item.items()}
            if kind in (list, tuple):
                children = [witness(child) for child in item]
                return tuple(children) if kind is tuple else children
            return item  # Complete float values, bool and None retain their types.

        def normalize(item, shape):
            kind = type(item)
            if type(shape) is not kind:
                raise _NotBuiltinTree
            if kind is float:
                return shape  # The original whole witness codec normalized this leaf.
            if kind is dict:
                if tuple(item) != tuple(shape):
                    raise _NotBuiltinTree
                for key, child in item.items():
                    item[key] = normalize(child, shape[key])
            elif kind in (list, tuple):
                if len(item) != len(shape):
                    raise _NotBuiltinTree
                if kind is tuple:
                    return tuple(normalize(child, normalized)
                                 for child, normalized in zip(item, shape))
                for index, child in enumerate(item):
                    item[index] = normalize(child, shape[index])
            return item

        owned = shape = normalized = None
        try:
            visit(value, set(), copy=False)
            owned = visit(value, set(), copy=True)
            shape = witness(owned)
            # Exact original codec at the original helper call depth: expanded
            # tagged/JSON recursion and float refusal precede any publication.
            normalized = decode(encode(shape))
            return normalize(owned, normalized)
        except Exception:
            owned = shape = normalized = None
        # Leave the handler before fallback so internal decline is not exposed as
        # the original exception's context. BaseException interruptions propagate.
        return decode(encode(value))

    def test_transient_witness_is_released_before_each_original_decoder(self):
        import sys
        import struct
        from unittest.mock import patch
        from worldline import finalization_writer as writer
        value = {'whole': ['\ud800\x00payload', 1 << 20000, -(1 << 20000),
                           -0.0, struct.unpack('!d', bytes.fromhex('fff8000000000011'))[0]],
                 'tuple': (None, False, {'key\udfff': []})}
        for helper, decoder_name, codec, preceding in (
                (writer._owned, 'bytes_value', writer.value_bytes, self.preceding_owned),
                (writer._owned_acquisition, 'decode', writer.encode, self.preceding_owned_acquisition)):
            decoder = getattr(writer, decoder_name)
            entries = []
            def observe_decode(raw):
                frame = sys._getframe(1)
                try:
                    self.assertIsNone(frame.f_locals['shape'])
                    self.assertIs(frame.f_locals['encoded'], raw)
                    self.assertIsNot(frame.f_locals['owned'], value)
                    entries.append(frame.f_code.co_name)
                finally:
                    del frame
                return decoder(raw)
            with self.subTest(helper=helper.__name__):
                expected = preceding(value)
                with patch.object(writer, decoder_name, new=observe_decode):
                    actual = helper(value)
                self.assertEqual(entries, [helper.__name__])
                self.assertEqual(codec(actual), codec(expected))
                self.assertIsNot(actual['whole'], value['whole'])
                self.assertIs(actual['whole'][0], value['whole'][0])

    def test_decode_exception_clears_temporary_before_original_whole_root_fallback(self):
        import sys
        from unittest.mock import patch
        from worldline import finalization_writer as writer
        value = {'whole': ['\ud800\x00payload', 1 << 20000, -0.0]}
        for helper, encoder_name, decoder_name in (
                (writer._owned, 'value_bytes', 'bytes_value'),
                (writer._owned_acquisition, 'encode', 'decode')):
            encoder, decoder = getattr(writer, encoder_name), getattr(writer, decoder_name)
            events = []
            def observe_encode(item):
                if item is value:
                    frame = sys._getframe(1)
                    try:
                        self.assertIsNone(frame.f_locals['encoded'])
                        self.assertIsNone(frame.f_locals['shape'])
                        self.assertIsNone(frame.f_locals['owned'])
                        self.assertIsNone(frame.f_locals['normalized'])
                        self.assertIsNone(sys.exception())
                    finally:
                        del frame
                    events.append('original-root')
                else:
                    events.append('whole-witness')
                return encoder(item)
            def first_decode_refuses(raw):
                if events == ['whole-witness']:
                    events.append('decode-refusal')
                    raise ValueError('transient decoder refusal control')
                events.append('original-root-decoded')
                return decoder(raw)
            with self.subTest(helper=helper.__name__):
                expected = decoder(encoder(value))
                with patch.object(writer, encoder_name, new=observe_encode), \
                     patch.object(writer, decoder_name, new=first_decode_refuses):
                    actual = helper(value)
                self.assertEqual(events, ['whole-witness', 'decode-refusal',
                                          'original-root', 'original-root-decoded'])
                self.assertEqual(encoder(actual), encoder(expected))

    def test_decoder_baseexception_propagates_once_and_helper_releases_encoded_reference(self):
        from unittest.mock import patch
        from worldline import finalization_writer as writer
        value = {'whole': ['\ud800\x00payload', 1 << 20000, -0.0]}
        for helper, encoder_name, decoder_name in (
                (writer._owned, 'value_bytes', 'bytes_value'),
                (writer._owned_acquisition, 'encode', 'decode')):
            encoder = getattr(writer, encoder_name)
            original = KeyboardInterrupt('original decoder interruption control')
            events = []
            def observe_encode(item):
                events.append('encode')
                return encoder(item)
            def interrupt_decode(raw):
                events.append('decode')
                raise original
            with self.subTest(helper=helper.__name__):
                with patch.object(writer, encoder_name, new=observe_encode), \
                     patch.object(writer, decoder_name, new=interrupt_decode):
                    try:
                        helper(value)
                    except KeyboardInterrupt as caught:
                        self.assertIs(caught, original)
                        frame = caught.__traceback__
                        while frame is not None and frame.tb_frame.f_code is not helper.__code__:
                            frame = frame.tb_next
                        self.assertIsNotNone(frame)
                        self.assertIsNone(frame.tb_frame.f_locals['encoded'])
                        self.assertIsNone(frame.tb_frame.f_locals['shape'])
                        del frame
                    else:
                        self.fail('original BaseException was swallowed')
                self.assertEqual(events, ['encode', 'decode'])

    def test_breadth_fixture_reduces_retained_allocation_at_decode_entry(self):
        import gc
        import tracemalloc
        from unittest.mock import patch
        from worldline import finalization_writer as writer
        # Finite structural allocation control, not a product capacity/depth cap
        # or an assertion that the observed memcg failure is now resolved.
        value = {'integer': 1 << 20000,
                 'rows': [{'whole': ['\ud800payload', 1, -0.0, None],
                           'tuple': (False, [], {})} for _ in range(4096)]}
        for helper, preceding, decoder_name, codec in (
                (writer._owned, self.preceding_owned, 'bytes_value', writer.value_bytes),
                (writer._owned_acquisition, self.preceding_owned_acquisition, 'decode', writer.encode)):
            decoder = getattr(writer, decoder_name)
            def measured(operation):
                entries = []
                def at_decode(raw):
                    entries.append(tracemalloc.get_traced_memory()[0])
                    return decoder(raw)
                gc.collect()
                tracemalloc.start()
                try:
                    with patch.object(writer, decoder_name, new=at_decode):
                        owned = operation(value)
                finally:
                    tracemalloc.stop()
                self.assertEqual(len(entries), 1, 'fallback must not substitute for measured fast path')
                return owned, entries[0]
            with self.subTest(helper=helper.__name__):
                old, old_live = measured(preceding)
                current, current_live = measured(helper)
                self.assertEqual(codec(current), codec(old))
                self.assertLess(current_live, old_live)
                self.assertIsNot(current['rows'][0], value['rows'][0])
                self.assertIsNot(current['rows'][0], current['rows'][1])
                # Peak cgroup ownership and same-case runtime success remain
                # original-carrier measurements; no attribution from this test.


if __name__ == '__main__':
    unittest.main()
