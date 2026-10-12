"""Actual native policy/syscall controls in temporary namespace-owned trees.

Run only in a disposable root user namespace, never on authoritative state.
This mirrors canonical_exchange_controls.adb's accepted pure value fixture;
it establishes no installed-principal/provider/custody claim. No mocked native
verdict or fsync is used. Missing namespace/second-filesystem premises fail.
"""
import ctypes as C
import errno
import os
from pathlib import Path
import socket
import tempfile
import unittest
from worldline.core import Core, CCollapseRequest, COptionalHash, C_HASH
from worldline import operation_authority_kernel as A
from worldline import recovery_authority_kernel_v3 as R
from worldline import resource_run_ledger as L
from worldline.canonical_exchange_kernel import CanonicalExchangeKernel, Input, Result, Material
from worldline.canonical_physical import Request, Witness, entry
from worldline.chain_authority import _digest, _Row


def accepted_frame(core):
    # Literal fixture values are retained from original native semantic controls.
    one = bytes([1]) * 32
    other = bytes([2]) * 32
    zero = A.Quantity(1, 0, 1, 0)
    number_one = L.RawQuantity(0, 1, 1)
    epoch = L.RawEpoch(1, L.RawQuantity(0, 1, 0))
    identifier = L.RawId(1, 1, 32)
    absent = L.RawId(0, 1, 0)
    collapse = CCollapseRequest()
    collapse.candidate_state = 2
    collapse.phase = collapse.evaluation_mode = 0
    collapse.conflicts = collapse.foreign_writes = collapse.roster_complete = 1
    collapse.generation_before.present = collapse.generation_after.present = 1
    collapse.generation_before.value_le[0] = collapse.generation_after.value_le[0] = 41
    for names, value in ((('expected_parent', 'candidate_parent'), 1),
                         (('expected_subject', 'evidence_subject'), 2),
                         (('expected_base', 'candidate_base'), 3),
                         (('expected_delta', 'candidate_delta'), 4),
                         (('expected_root_set', 'candidate_root_set'), 5),
                         (('expected_staged_root', 'actual_staged_root'), 6),
                         (('staged_content_root', 'tested_root'), 7),
                         (('current_requirement', 'resulting_requirement', 'evaluated_requirement'), 8),
                         (('declared_verifiers', 'executed_verifiers'), 9),
                         (('registered_watch_set', 'watched_set'), 10)):
        for name in names:
            setattr(collapse, name, COptionalHash(1, C_HASH.from_buffer_copy(bytes([value]) * 32)))
    bound = A.Binding()
    bound.action = A.OPS.index('collapse.commit')
    for index in range(len(A.FIELDS)):
        bound.id[index] = _digest(one)
    bound.id[A.FIELDS.index('requirement')] = _digest(bytes([8]) * 32)
    for name in ('peer', 'preparer', 'owner', 'target_owner'):
        setattr(bound, name, A.UID(1, os.geteuid()))
    bound.policy_epoch = bound.resource_epoch = zero
    grant = A.Grant()
    for name in ('id', 'issuer', 'instance', 'root_set', 'policy'):
        setattr(grant, name, _digest(one))
    grant.subject = grant.owner = A.UID(1, os.geteuid())
    grant.allowed = (C.c_uint8 * len(A.OPS))(*([1] * len(A.OPS)))
    grant.epoch = grant.issued_at = zero
    grant.ceiling = grant.expires_at = A.Quantity(1, 0, 1, 32)
    use = A.Use(bound, A.STATES.index('RESERVED'))
    recovery = R.Binding()
    for name in R.HASH_FIELDS:
        setattr(recovery, name, R.OptionalDigest(1, R.Digest.from_buffer_copy(one)))
    recovery.policy_epoch = recovery.resource_epoch = R.OptionalEpoch(1, 0, 1, 0)
    for name, value in (('subject', 2), ('staged_root', 6), ('current_requirement', 8),
                        ('resulting_requirement', 8), ('staged_mapping', 2)):
        setattr(recovery, name, R.OptionalDigest(1, R.Digest.from_buffer_copy(bytes([value]) * 32)))
    material = Material()
    for name in ('worker_issued', 'worker_recovered', 'canonical_issued', 'canonical_recovered'):
        setattr(material, name, recovery)
    material.worker_native = R.Native(R.OptionalDigest(1, R.Digest.from_buffer_copy(other)),
                                     recovery.staged_root)
    material.canonical_native = R.Native(R.OptionalDigest(1, R.Digest.from_buffer_copy(one)),
                                        R.OptionalDigest(1, R.Digest.from_buffer_copy(one)))
    for name in ('worker_receipt_genesis', 'owner_receipt_genesis', 'worker_causal_genesis',
                 'owner_causal_genesis', 'quarantine_head'):
        setattr(material, name, R.OptionalDigest(1, R.Digest.from_buffer_copy(one)))
    receipt_head = core.receipt_link(one, one)
    causal_head = core.causal_link(one, one)
    material.worker_receipt_head = R.OptionalDigest(1, R.Digest.from_buffer_copy(receipt_head))
    material.worker_causal_head = R.OptionalDigest(1, R.Digest.from_buffer_copy(causal_head))
    evidence = A.Evidence()
    evidence.effect_binding = evidence.no_effect_binding = evidence.owner_resolution = bound
    for name in ('actual_receipt_root', 'actual_causal_root', 'quarantine_head',
                 'witnessed_receipt_head', 'witnessed_causal_head', 'original_use'):
        setattr(evidence, name, _digest(one))
    historical = R.Binding()
    for name in R.HASH_FIELDS:
        setattr(historical, name, R.OptionalDigest(1, R.Digest.from_buffer_copy(one)))
    historical.policy_epoch = historical.resource_epoch = R.OptionalEpoch(1, 0, 1, 0)
    evidence.recovery = R.Request(3, 1, 1, 0, 0, historical, historical,
                                 R.Native(R.OptionalDigest(1, R.Digest.from_buffer_copy(one)),
                                          R.OptionalDigest(1, R.Digest.from_buffer_copy(one))))
    context = L.RawContext(*(identifier for _ in range(8)), epoch)
    resource_binding = L.RawBinding(*(identifier for _ in range(9)), epoch)
    state = L.RawState(context, epoch, identifier, identifier, number_one, number_one, L.RawQuantity(0, 1, 0))
    row = L.RawRow(context, resource_binding, absent, 0, 0, number_one,
                   L.RawEpoch(0, L.RawQuantity(0, 1, 0)), absent, absent, absent, absent)
    observed = L.RawNative(context, epoch, resource_binding, absent, absent, absent, identifier,
                           L.LIVENESS.index('NEVER_LAUNCHED'))
    raw = Input()
    raw.operation_input.authority = A.Input(1, 0, bound, zero, evidence)
    raw.operation_input.state = state
    raw.operation_input.bound = resource_binding
    raw.operation_input.requester = identifier
    raw.operation_input.peer = A.UID(1, os.geteuid())
    raw.operation_input.collapse = collapse
    raw.material = material
    raw.before = 2  # original Worker_Observed
    raw.mode = 0
    receipts = (_Row * 1)(_Row(_digest(one), _digest(one), _digest(one), _digest(receipt_head)))
    events = (_Row * 1)(_Row(_digest(one), _digest(one), _digest(one), _digest(causal_head)))
    rosters = ((A.Grant * 1)(grant), (A.Use * 1)(use), (L.RawRow * 1)(row),
               (L.RawNative * 1)(observed), receipts, events, receipts, events)
    storage = (C.c_uint8 * len(one)).from_buffer_copy(one)
    return raw, storage, rosters


class FullPhysicalSyscallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.geteuid() != 0 or os.environ.get('WORLDLINE_TEMP_PHYSICAL_NAMESPACE') != '1':
            raise RuntimeError('run in explicitly selected disposable root user namespace')
        cls.core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))
        cls.kernel = CanonicalExchangeKernel(cls.core)
        cls.arguments = [C.c_int] * 4 + cls.kernel.call.argtypes[:-2] + [C.c_void_p, C.c_size_t] * 2
        cls.exchange = cls.core._lib.wl_full_physical_exchange_v1
        cls.recover = cls.core._lib.wl_full_physical_recover_v1
        for call in (cls.exchange, cls.recover):
            call.argtypes, call.restype = cls.arguments, C.c_int

    def native(self, frame):
        raw, storage, rosters = frame
        args = [C.byref(raw), C.sizeof(raw), storage, C.sizeof(storage)]
        for roster in rosters:
            args.extend((roster, len(roster), C.sizeof(roster)))
        output = Result()
        self.assertEqual(self.kernel.call(*args, C.byref(output), C.sizeof(output)), 0)
        return output.disposition

    def tree(self, base, *, data_parent=None):
        data = (base if data_parent is None else data_parent) / 'data'
        transaction, payload = base / 'transaction', base / 'payload'
        for path in (data, transaction, payload, data / 'live', transaction / 'mapping'):
            path.mkdir(mode=0o700)
        for root in ('first-root', 'second-root'):
            slot = payload / root
            slot.mkdir(mode=0o700)
            (slot / 'bytes').write_bytes(b'actual native durability readback\x00\xff')
            os.link(slot / 'bytes', slot / 'hardlink')
            os.symlink('bytes', slot / 'symlink')
            os.symlink(str(slot), transaction / 'mapping' / root)
        marker = b'{"schemaVersion":1,"transactionId":"temporary-original"}'
        (transaction / 'mapping' / '.worldline-generation.json').write_bytes(marker)
        (data / 'live' / '.worldline-generation.json').write_bytes(b'original-before')
        return data, transaction, payload, marker

    def invoke(self, call, frame, paths, request, peer, *, output=None):
        raw, storage, rosters = frame
        data, transaction, payload, _marker = paths
        fds = []
        output = Witness() if output is None else output
        try:
            for path in (data, transaction, payload):
                fds.append(os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC))
            args = [peer, *fds, C.byref(raw), C.sizeof(raw), storage, C.sizeof(storage)]
            for roster in rosters:
                args.extend((roster, len(roster), C.sizeof(roster)))
            return call(*args, C.byref(request), C.sizeof(request), C.byref(output), C.sizeof(Witness)), output
        finally:
            for fd in fds:
                os.close(fd)

    def request(self, frame, paths):
        data, transaction, _payload, marker = paths
        live, stage = entry(data / 'live'), entry(transaction / 'mapping')
        digest = C_HASH.from_buffer_copy(self.core.hash_bytes(marker))
        return Request(frame[0].operation_input.collapse, live, live, stage, stage, digest, digest, 0, 0)

    def test_genuine_exchange_and_historical_durable_recovery(self):
        with tempfile.TemporaryDirectory() as temporary:
            left, right = socket.socketpair()
            with left, right:
                paths = self.tree(Path(temporary))
                frame = accepted_frame(self.core)
                self.assertEqual(self.native(frame), 3)
                request = self.request(frame, paths)
                status, witness = self.invoke(self.exchange, frame, paths, request, left.fileno())
                self.assertEqual(status, 0)
                self.assertEqual((witness.exchange_attempted, witness.syscall_errno), (1, 0))
                self.assertEqual((witness.payload_durable, witness.recovery_clean, witness.parents_durable), (1, 1, 1))
                self.assertEqual((request.payload_durable, request.recovery_clean), (0, 0))
                self.assertEqual(entry(paths[0] / 'live').inode, request.expected_stage.inode)
                self.assertEqual(entry(paths[1] / 'mapping').inode, request.expected_live.inode)
                frame[0].before = 3  # original Canonical_Intent
                frame[0].material.canonical_native = frame[0].material.worker_native
                frame[2][0][0].state = 1  # revoked current grant cannot erase genuine prior effect
                self.assertEqual(self.native(frame), 4)
                for _ in range(2):
                    status, recovery = self.invoke(self.recover, frame, paths, request, -1)
                    self.assertEqual(status, 0)
                    self.assertEqual(recovery.exchange_attempted, 0)
                    self.assertEqual((recovery.payload_durable, recovery.recovery_clean, recovery.parents_durable), (1, 1, 1))
                    self.assertEqual(entry(paths[0] / 'live').inode, request.expected_stage.inode)
                    self.assertEqual(entry(paths[1] / 'mapping').inode, request.expected_live.inode)

    def test_refused_grant_and_asserted_success_cannot_exchange(self):
        with tempfile.TemporaryDirectory() as temporary:
            left, right = socket.socketpair()
            with left, right:
                paths = self.tree(Path(temporary))
                frame = accepted_frame(self.core)
                request = self.request(frame, paths)
                request.payload_durable = request.recovery_clean = 1
                frame[2][0][0].state = 1
                self.assertEqual(self.native(frame), 0)
                status, witness = self.invoke(self.exchange, frame, paths, request, left.fileno())
                self.assertEqual(status, 1)
                self.assertEqual((witness.exchange_attempted, witness.payload_durable, witness.recovery_clean), (0, 0, 0))
                self.assertEqual(entry(paths[0] / 'live').inode, request.expected_live.inode)
                self.assertEqual(entry(paths[1] / 'mapping').inode, request.expected_stage.inode)

    def test_marker_mismatch_is_not_repaired_or_exchanged(self):
        with tempfile.TemporaryDirectory() as temporary:
            left, right = socket.socketpair()
            with left, right:
                paths = self.tree(Path(temporary))
                frame = accepted_frame(self.core)
                request = self.request(frame, paths)
                request.expected_marker_digest[0] ^= 1
                self.assertEqual(self.native(frame), 3)
                status, witness = self.invoke(self.exchange, frame, paths, request, left.fileno())
                self.assertEqual(status, 1)
                self.assertEqual(witness.exchange_attempted, 0)
                self.assertEqual(entry(paths[0] / 'live').inode, request.expected_live.inode)
                self.assertEqual(entry(paths[1] / 'mapping').inode, request.expected_stage.inode)

    def test_output_alias_refuses_without_input_or_filesystem_mutation(self):
        with tempfile.TemporaryDirectory() as temporary:
            left, right = socket.socketpair()
            with left, right:
                paths = self.tree(Path(temporary))
                frame = accepted_frame(self.core)
                request = self.request(frame, paths)
                self.assertEqual(self.native(frame), 3)
                original = C.string_at(C.byref(frame[0]), C.sizeof(frame[0]))
                status, _ = self.invoke(self.exchange, frame, paths, request, left.fileno(), output=frame[0])
                self.assertEqual(status, 1)
                self.assertEqual(C.string_at(C.byref(frame[0]), C.sizeof(frame[0])), original)
                self.assertEqual(entry(paths[0] / 'live').inode, request.expected_live.inode)
                self.assertEqual(entry(paths[1] / 'mapping').inode, request.expected_stage.inode)

    def test_wrong_payload_inode_cannot_supply_durable_fact(self):
        with tempfile.TemporaryDirectory() as temporary:
            left, right = socket.socketpair()
            with left, right:
                base = Path(temporary)
                paths = self.tree(base)
                outside = base / 'unjoined-root'
                outside.mkdir(mode=0o700)
                link = paths[1] / 'mapping' / 'first-root'
                link.unlink()
                os.symlink(str(outside), link)
                frame = accepted_frame(self.core)
                request = self.request(frame, paths)
                request.payload_durable = request.recovery_clean = 1
                self.assertEqual(self.native(frame), 3)
                status, witness = self.invoke(self.exchange, frame, paths, request, left.fileno())
                self.assertEqual(status, 2)
                self.assertEqual((witness.exchange_attempted, witness.payload_durable), (0, 0))
                self.assertEqual(entry(paths[0] / 'live').inode, request.expected_live.inode)
                self.assertEqual(entry(paths[1] / 'mapping').inode, request.expected_stage.inode)

    def test_actual_cross_device_syscall_error_preserves_both_mappings(self):
        second = os.environ.get('WORLDLINE_PHYSICAL_SECOND_TMP', '/dev/shm')
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory(dir=second) as other:
            left, right = socket.socketpair()
            with left, right:
                paths = self.tree(Path(other), data_parent=Path(first))
                self.assertNotEqual(paths[0].stat().st_dev, paths[1].stat().st_dev,
                                    'control needs actual distinct temporary filesystems')
                frame = accepted_frame(self.core)
                request = self.request(frame, paths)
                self.assertEqual(self.native(frame), 3)
                status, witness = self.invoke(self.exchange, frame, paths, request, left.fileno())
                self.assertEqual(status, 2)
                self.assertEqual((witness.exchange_attempted, witness.syscall_errno), (1, errno.EXDEV))
                self.assertEqual((witness.payload_durable, witness.recovery_clean, witness.parents_durable), (1, 1, 0))
                self.assertEqual(entry(paths[0] / 'live').inode, request.expected_live.inode)
                self.assertEqual(entry(paths[1] / 'mapping').inode, request.expected_stage.inode)
