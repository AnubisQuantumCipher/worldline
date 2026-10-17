"""Full root DTO transport controls; decoding never proves custody/authority."""
from dataclasses import dataclass, fields
import sys
import unittest

from worldline import root_worker_codec as R
from worldline import resource_scoped_run_ledger as S
from worldline import resource_run_ledger as L
from worldline.core import CollapseInput
from worldline.completion_kernel import BoundValue, CaptureValue
from worldline.errors import WorldlineError
from worldline.finalization_journal import decode, encode
from worldline.model import WorldState
from worldline.operation_capture import archive as operation_archive, restore_archive as operation_restore
from worldline.protected_startup import StartupRefusal
from worldline.resource_child_schema import ProcessObservation, RootController, TaskOrigin, NamespaceObservation
from worldline.resource_child_execution import ResourceChildNativeObservation
from worldline.resource_actor_credentials import ActorCredentialObservation
from worldline.root_worker_credentials import RootCredentialObservation
from worldline.root_worker_prepared_inputs import PreparedInputs
from worldline.root_worker_prepared_wire import SnapshotWire, PreparedWire
from worldline.root_worker_retained_inputs import RetainedInputs
from worldline.protected_scoped_resource_service import ScopedSnapshot
from worldline.scoped_source_image import source_record, source_restore
from worldline.custody_load_kernel import envelope
from worldline.custody_mutation_kernel import mutation_input


def collapse_input():
    # Preserve the original ABI control's full input, including typed absence.
    def h(byte):
        return bytes([byte]) * 32
    return CollapseInput(
        candidate_state='VALID', phase='COMMIT', mode='CANDIDATE_EVALUATION',
        conflicts='NONE_FOUND', foreign_writes='NONE_FOUND',
        roster_complete=True, staged_roster_complete=False,
        expected_parent=h(1), candidate_parent=h(1),
        expected_subject=h(2), evidence_subject=h(2),
        expected_base=h(3), candidate_base=h(3),
        expected_delta=h(4), candidate_delta=h(4),
        expected_root_set=h(5), candidate_root_set=h(5),
        expected_staged_root=h(6), actual_staged_root=h(6),
        staged_content_root=h(7), tested_root=h(7),
        current_requirement=h(8), resulting_requirement=h(8), evaluated_requirement=h(8),
        declared_verifiers=h(9), executed_verifiers=h(9),
        staged_evaluated_requirement=None, staged_executed_verifiers=None, staged_examined_root=None,
        expected_checkpoint=None, witnessed_checkpoint=None,
        registered_watch_set=h(10), watched_set=h(10), generation_before=41, generation_after=41)


def context():
    return L.RunContext(universe=b'universe', policy=b'policy', resource=b'resource', unit=b'unit',
        instance=b'instance', host=b'host', boot=b'boot', authority=b'authority', policy_epoch=7)


def binding():
    return L.RunBinding(reservation=b'reservation', operation=b'operation', owner=b'owner',
        workload=b'workload', universe_head=b'universe-head', capability=b'capability',
        grant_use=b'grant-use', payload=b'payload', provenance=b'provenance', resource_epoch=7)


class RootWorkerCodecLosslessControls(unittest.TestCase):
    def assert_roundtrip(self, value):
        raw = R.raw_archive(value)
        restored = R.raw_restore_archive(raw)
        self.assertEqual(restored, value)
        self.assertIs(type(restored), type(value))
        self.assertEqual(R.raw_archive(restored), raw)
        return restored

    def test_original_collapse_input_archive_and_hex_are_byte_exact(self):
        value = collapse_input()
        raw = operation_archive(value)
        self.assertEqual(R.raw_archive(value), raw)
        self.assertEqual(R.original_archive(value), raw)
        self.assertEqual(R.raw_archive(value).hex(), raw.hex())
        self.assertEqual(R.raw_restore_archive(raw), operation_restore(raw))
        self.assertIs(type(self.assert_roundtrip(value)), CollapseInput)

    def test_operation_snapshot_preserves_original_raw_archive_nested_values(self):
        bound = BoundValue(b'store', b'subject', b'content', b'run', b'epoch', None)
        capture = CaptureValue(bound, b'producer', b'full raw context', 'COMPLETED', 'PASS')
        snapshot = {b'\xff\x00': (capture, collapse_input(), None, WorldState.VALID),
                    'history': [b'old-failure', b'new-success'], 'empty': {},
                    'huge': -(1 << 32768), 'raw': b'\x00\xff\x00'}
        original = operation_archive(snapshot)
        self.assertEqual(R.raw_archive(snapshot), original)
        restored = self.assert_roundtrip(snapshot)
        self.assertIs(type(restored[b'\xff\x00']), tuple)
        self.assertIs(type(restored[b'\xff\x00'][0]), CaptureValue)
        self.assertIs(type(restored[b'\xff\x00'][0].bound), BoundValue)
        self.assertIs(type(restored['history']), list)

    def test_bytes_and_string_keys_remain_distinct_ordered_and_untrimmed(self):
        original = {b' key ': b'bytes', ' key ': b'string', b'key': b'plain',
                    b'': None, b'\xff\xfe\x00': ([], {}), '': True}
        raw = R.raw_archive(original)
        self.assertEqual(raw, operation_archive(original))
        restored = self.assert_roundtrip(original)
        self.assertEqual(list(restored), list(original))
        self.assertEqual([type(key) for key in restored], [type(key) for key in original])
        self.assertEqual([pair[0] for pair in decode(raw)[1]],
                         [['atom', key] for key in original])

    def test_explicit_root_prepared_and_retained_dataclasses_roundtrip(self):
        snapshot = operation_archive({'values': collapse_input(), b'key': b'\x00\xff'})
        prepared = PreparedInputs('operation', b'journal\x00', ('head', b'raw'),
            b'reserved-event', b'effect-intent-event', snapshot, snapshot, operation_archive([]))
        wire = PreparedWire(prepared, b'whole arena\x00',
            SnapshotWire(b'request-1', (b'grants', b'uses', b'', b'events'), (1, 1, 0, 1)),
            SnapshotWire(b'request-2', (b'grants', b'uses', b'', b'events'), (1, 1, 0, 1)))
        retained = RetainedInputs(b'whole arena\xff', (1, 3), (4, 5), (9, 6),
            ((b'name', b'raw'),), ((b'event', b'mac'),), ((b'head', b'mac'),),
            operation_archive({b'owner': b'full'}), b'gate', operation_archive({'rows': ()}))
        restored = self.assert_roundtrip({b'wire': wire, 'retained': retained})
        self.assertIs(type(restored[b'wire']), PreparedWire)
        self.assertIs(type(restored[b'wire'].retained), PreparedInputs)
        self.assertIs(type(restored[b'wire'].reserve), SnapshotWire)
        self.assertIs(type(restored['retained']), RetainedInputs)
        self.assertEqual(restored[b'wire'].retained.reserved_snapshot, snapshot)
        self.assertEqual(restored['retained'].owner_capture_archive, retained.owner_capture_archive)

    def test_full_scoped_and_child_dataclasses_roundtrip_without_projection(self):
        scoped = S.ScopedState(current=context(), resource_epoch=7, universe_head=b'u',
            ledger_head=b'l', history_head=b'h', physical_head=None)
        process = ProcessObservation(raw_status=b'status\x00', raw_stat=b'stat', raw_cgroup=b'cgroup',
            raw_maps=b'maps', raw_cmdline=b'argv\x00tail\x00', raw_pidfd_info=b'pidfd',
            namespace=b'namespace', cgroup=b'cgroup-id', actual_unit=b'unit', invocation=b'invocation',
            source_lease=b'lease', pidfd_wait=b'wait', host_pid=100, start_tick=200,
            parent_pid=90, parent_start_tick=180, real_uid=1000, effective_uid=1000, saved_uid=1000,
            real_gid=1000, effective_gid=1000, saved_gid=1000)
        controller = RootController(bound=binding(), process=process, requester_uid=1000,
            requester_gid=1000, **{field.name: field.name.encode() + b'\x00\xff'
                for field in fields(RootController)
                if field.name not in ('bound', 'process', 'requester_uid', 'requester_gid')})
        task = TaskOrigin(action='fork', root=binding(), child=binding(),
            **{field.name: None if field.name in ('root_world', 'child_world',
                    'task_reservation_event', 'task_launch_event') else field.name.encode() + b'\x00'
               for field in fields(TaskOrigin) if field.name not in ('action', 'root', 'child')})
        namespace = NamespaceObservation(identity=b'ns', parent=None, raw_nsfs=b'raw-nsfs',
            raw_get_parent=b'raw-parent', source_lease=b'lease')
        observation = ResourceChildNativeObservation('wl_resource_child_decide_v1', 'CHILD_ADMISSION',
            'CHILD_READY_CONJUNCTION', b'actor', b'full-resource-arena', (('rows', b'row-bytes', 1),),
            b'authority', b'authority-arena', (('grants', b'grant-bytes', 1),), b'crosswalk',
            b'child-input', b'raw-output', 0)
        for value in (scoped, process, controller, task, namespace, observation):
            with self.subTest(dto=type(value).__name__):
                self.assert_roundtrip(value)
        self.assertIs(type(R.raw_restore_archive(R.raw_archive(controller)).bound), L.RunBinding)
        self.assertIs(type(R.raw_restore_archive(R.raw_archive(controller)).process), ProcessObservation)
        self.assertIs(type(R.raw_restore_archive(R.raw_archive(scoped)).current), L.RunContext)

    def test_complete_scoped_source_image_preserves_original_packet_and_physical_byte_keys(self):
        state = S.ScopedState(current=context(), resource_epoch=7, universe_head=b'u',
            ledger_head=b'l', history_head=b'h', physical_head=None)
        source = {'packet': S.record(state), 'physical_source':
            {b'\xff\x00': {b'source': (b'raw\x00', b'\xfe')}, 'source': b'distinct'}}
        self.assertEqual(source_restore(source_record(source)), source)
        self.assertEqual(source_restore(source_record(source))['packet'], source['packet'])
        self.assertEqual(R.raw_archive(source_restore(source_record(source))), operation_archive(source))

    def test_retained_original_scoped_source_grammar_remains_readable(self):
        source = {'packet': {'class': 'original'}, 'physical_source': b'complete original bytes'}
        self.assertEqual(source_restore(S.record(source)), source)

    def test_original_scoped_snapshot_preserves_all_typed_fields(self):
        state = S.ScopedState(current=context(), resource_epoch=7, universe_head=b'u',
            ledger_head=b'l', history_head=b'h', physical_head=None)
        snapshot = ScopedSnapshot(state=state, history=(), rows=(), projection=(), buckets=())
        # ScopedSnapshot and ScopedState are root DTOs (R._schema), not members of
        # the unchanged original operation-capture grammar, which refuses them.
        # The original-grammar oracle is therefore the original operation-capture
        # tags of every operand that grammar has, in the original record framing,
        # with the complete declared field order of the two root DTOs.
        for root_only in (snapshot, state):
            with self.assertRaises(WorldlineError) as refused:
                operation_archive(root_only)
            self.assertEqual(refused.exception.code, 'RECOVERY_PACKET_TYPE')
        def original_tags(value):
            return decode(operation_archive(value))
        original_state = ['record', S.ScopedState.__module__, 'ScopedState',
            [[name, original_tags(getattr(state, name))] for name in
             ('current', 'resource_epoch', 'universe_head', 'ledger_head', 'history_head', 'physical_head')]]
        original = encode(['record', ScopedSnapshot.__module__, 'ScopedSnapshot',
            [['state', original_state]] + [[name, original_tags(getattr(snapshot, name))]
                for name in ('history', 'rows', 'projection', 'buckets')]])
        self.assertEqual(original_tags(context())[:3],
                         ['record', L.RunContext.__module__, 'RunContext'])
        self.assertEqual(R.raw_archive(snapshot), original)
        restored = self.assert_roundtrip({b'snapshot': snapshot, 'snapshot': original})
        self.assertIs(type(restored[b'snapshot']), ScopedSnapshot)
        self.assertIs(type(restored[b'snapshot'].state), S.ScopedState)
        self.assertIs(type(restored[b'snapshot'].state.current), L.RunContext)
        self.assertEqual(tuple(field.name for field in fields(restored[b'snapshot'])),
                         ('state', 'history', 'rows', 'projection', 'buckets'))
        for name in ('history', 'rows', 'projection', 'buckets'):
            self.assertIs(type(getattr(restored[b'snapshot'], name)), tuple)

    def test_complete_root_and_actor_credential_dataclasses_are_not_hex_projected(self):
        for kind in (RootCredentialObservation, ActorCredentialObservation):
            value = kind(raw_frame=b'whole frame\x00\xff', raw_sender_credentials=b'raw ucred\x00',
                host_pid=100, sender_real_uid=1000, sender_real_gid=1000, ticket=b'nonce',
                namespace_pid=1, uids=(1000, 1000, 1000), gids=(1000, 1000, 1000),
                capability_version=0x20080522, capability_words=((1, 2, 3), (4, 5, 6)),
                securebits=0, no_new_privs=1, capabilities=((0, 1, 0), (1, 0, 0)),
                supplementary_groups=(1000, 1001))
            with self.subTest(dto=kind.__name__):
                restored = self.assert_roundtrip(value)
                self.assertIs(type(restored.raw_frame), bytes)
                self.assertIs(type(restored.capability_words), tuple)

    def test_root_registry_covers_selected_original_scoped_and_root_classes(self):
        selected = set(R._schema())
        self.assertTrue(set(R.ORIGINAL_RECORDS) <= selected)
        self.assertTrue(set(S._KNOWN.values()) <= selected)
        self.assertTrue({PreparedInputs, PreparedWire, SnapshotWire, RetainedInputs} <= selected)

    def test_unknown_record_module_and_registry_injection_never_enroll(self):
        @dataclass(frozen=True)
        class UnknownDTO:
            raw: bytes
        with self.assertRaises(WorldlineError):
            R.raw_archive(UnknownDTO(b'raw'))
        S._KNOWN['UnknownDTO'] = UnknownDTO
        try:
            with self.assertRaises(WorldlineError):
                R.raw_archive(UnknownDTO(b'raw'))
            with self.assertRaises(WorldlineError):
                R.raw_restore_archive(encode(['record', UnknownDTO.__module__, 'UnknownDTO',
                                          [['raw', ['atom', b'raw']]]]))
        finally:
            del S._KNOWN['UnknownDTO']
        module = 'operator-supplied-module'
        before = set(sys.modules)
        for name in ('UnknownDTO', 'CollapseInput', 'RootController'):
            with self.subTest(name=name), self.assertRaises(WorldlineError):
                R.raw_restore_archive(encode(['record', module, name, []]))
        self.assertNotIn(module, sys.modules)
        self.assertNotIn(module, before)

    def test_missing_duplicate_extra_and_reordered_dataclass_fields_refuse(self):
        for value in (collapse_input(), SnapshotWire(b'request', (), ())):
            tree = decode(R.raw_archive(value))
            alternatives = (tree[3][:-1], tree[3] + [tree[3][0]],
                            list(reversed(tree[3])), tree[3] + [['unselected', ['atom', None]]])
            for changed in alternatives:
                with self.subTest(dto=type(value).__name__, fields=changed), self.assertRaises(WorldlineError):
                    R.raw_restore_archive(encode([*tree[:3], changed]))

    def test_duplicate_keys_unknown_tags_and_wrong_shapes_refuse(self):
        cases = (['object', [[['atom', b'key'], ['atom', b'one']],
                             [['atom', b'key'], ['atom', b'two']]]],
                 ['object', [[['integer-magnitude', False, b'\x01'], ['atom', b'value']]]],
                 ['record', 'worldline.core', 'MissingDTO', []],
                 ['atom', {}], ['tuple', {}], ['unknown', None],
                 ['integer-magnitude', 0, b'\x01'])
        for tree in cases:
            with self.subTest(tree=tree), self.assertRaises(WorldlineError):
                R.raw_restore_archive(encode(tree))
        for value in ({1: b'value'}, {False: b'value'}, {('key',): b'value'}):
            with self.subTest(value=value), self.assertRaises(WorldlineError):
                R.raw_archive(value)
        for raw in ('not-bytes', bytearray(b'raw'), None):
            with self.subTest(raw=raw), self.assertRaises(WorldlineError):
                R.raw_restore_archive(raw)

    def test_noncanonical_integer_magnitudes_and_negative_zero_refuse(self):
        for tree in (['integer-magnitude', False, b'\x01\x00'],
                     ['integer-magnitude', True, b''],
                     ['integer-magnitude', False, b'\x00']):
            with self.subTest(tree=tree), self.assertRaises(StartupRefusal):
                R.raw_restore_archive(encode(tree))
        for value in (0, 1, -1, 1 << 32768, -(1 << 32768)):
            with self.subTest(value=value):
                self.assert_roundtrip(value)

    def test_scoped_native_transport_remains_exact_ordinary_S_grammar(self):
        value = {'state': S.ScopedState(current=context(), resource_epoch=7, universe_head=b'u',
            ledger_head=b'l', history_head=None, physical_head=b'p'),
            'sql': ((None, b'\x00\xff', 'text', 1, -2, 0.125),)}
        expected = operation_archive(S.record(value))
        self.assertEqual(R.scoped_archive(value), expected)
        self.assertEqual(R.scoped_restore_archive(expected), value)
        self.assertEqual(R.archive(value), expected)
        self.assertEqual(R.restore_archive(expected), value)
        self.assertEqual(R.raw_restore_archive(expected), S.record(value))
        with self.assertRaises(ValueError):
            R.archive(collapse_input())
        with self.assertRaises(ValueError):
            R.archive({b'raw-key': b'raw-value'})
        with self.assertRaises(ValueError):
            R.restore_archive(R.raw_archive(collapse_input()))
        self.assertNotEqual(R.raw_archive(value), expected)
        with self.assertRaises(ValueError):
            R.scoped_archive({b'not-a-scoped-key': b'raw'})
        with self.assertRaises(ValueError):
            S.record({b'not-a-scoped-key': b'raw'})
        reordered = operation_restore(expected)
        reordered = {'fields': reordered['fields'], 'type': reordered['type']}
        with self.assertRaises(StartupRefusal):
            R.scoped_restore_archive(operation_archive(reordered))

    def test_native_load_and_mutation_clients_use_only_scoped_envelopes(self):
        rows = {name: () for name in ('events', 'heads', 'roots', 'subjects', 'alternatives', 'blobs')}
        genesis = {'schema': 'genesis', 'initial_event': None}
        owner = {'operation_context': {'binding': b'complete-original-binding'}}
        before = envelope(b'key', b'genesis-file', b'genesis-row', 'mac', owner, rows, genesis)
        expected_before = {'schema': 'worldline.custody-load-v2', 'key': b'key',
            'genesis_file': b'genesis-file', 'genesis_row': b'genesis-row',
            'genesis_message': operation_archive(S.record({'genesis': genesis})),
            'genesis_mac': 'mac', 'owner_roster': owner, **rows}
        self.assertEqual(before, operation_archive(S.record(expected_before)))
        snapshot = operation_archive({'values': collapse_input(), b'key': b'\x00\xff'})
        record = {'original': {'operation_snapshot': snapshot}, 'x5': {'request': b'raw-request'}}
        raw = mutation_input(before, 'operation', 'PREPARED', 'FRONT', 'ROOT', '', record)
        expected = {'schema': 'worldline.custody-mutation-v2', 'before': expected_before,
            'candidate': {'operation': 'operation', 'kind': 'PREPARED', 'actor': 'FRONT',
                          'subject_kind': 'ROOT', 'subject': '', 'record': record}}
        self.assertEqual(raw, operation_archive(S.record(expected)))
        restored = R.scoped_restore_archive(raw)
        self.assertEqual(restored['candidate']['record']['original']['operation_snapshot'], snapshot)


if __name__ == '__main__':
    unittest.main()
