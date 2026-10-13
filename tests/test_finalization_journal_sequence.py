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
        self.assertIn('\udfff\x00whole', identities)
        self.assertIn('\ud800-key\x00', identities)
        self.assertIn(original_magnitude(abs(value['signed'][0]).to_bytes(
            (abs(value['signed'][0]).bit_length() + 7) // 8, 'little')), magnitudes)
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


if __name__ == '__main__':
    unittest.main()
