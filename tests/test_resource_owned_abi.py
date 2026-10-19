"""Actual native owned resource ABI controls; no native decisions are mocked.

The supported premise is live allocated storage, stable read-only input, and
exclusive writable output except the run-ledger's original post-snapshot alias.
These controls deliberately never manufacture unreadable or dangling pointers.
"""
import ctypes as C
import gc
import os
from pathlib import Path
from types import SimpleNamespace
import unittest

from worldline.core import Core
from worldline import resource_kernel as K, resource_policy as P
from worldline import resource_ledger as L, reservation_lifecycle as V
from worldline import resource_machine_evidence as E, resource_run_ledger as R
from test_resource_run_ledger_v1 import row, state, request, LARGE


class ResourceOwnedABITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))

    def test_resources_null_empty_and_shared_readonly_magnitudes(self):
        K.can_reserve(0, 0, 0, 0, core=self.core)  # enroll original layout/version binding
        call = self.core._lib.wl_resources_can_reserve
        self.assertEqual(call(0, None, 0, None, 0, None, 0, None, 0), 1)
        arena = (C.c_uint8 * 4)(7, 0, 0, 0)
        copies = tuple((C.c_uint8 * 4).from_buffer_copy(arena) for _ in range(4))
        expected = call(0, *sum(([part, len(part)] for part in copies), []))
        before = bytes(arena)
        gc.collect()
        self.assertEqual(call(0, *([arena, len(arena)] * 4)), expected)
        self.assertEqual(bytes(arena), before)
        self.assertEqual(call(0, None, 1, None, 0, None, 0, None, 0), 255)
        self.assertEqual(call(2, None, 0, None, 0, None, 0, None, 0), 255)

    def _policy_input(self):
        zero = P._Quantity(1, 0, 0)
        absent = P._Optional(0, zero)
        return P._Input(zero, absent, absent, zero, zero, zero, zero, zero, zero, zero)

    def test_policy_absence_extent_alignment_and_output_custody(self):
        call = P._api(self.core)
        inputs = self._policy_input()
        baseline = P._Result()
        self.assertEqual(call(None, 0, C.byref(inputs), None, 0, C.byref(baseline)), 0)
        poison = P._Quantity(C.c_size_t(-1).value, C.c_size_t(-1).value, 255)
        inputs.concurrency_limit = P._Optional(0, poison)
        inputs.memory_pressure = P._Optional(0, poison)
        output = P._Result()
        before = bytes(inputs)
        gc.collect()
        self.assertEqual(call(None, 0, C.byref(inputs), None, 0, C.byref(output)), 0)
        self.assertEqual(bytes(output), bytes(baseline))
        self.assertEqual(bytes(inputs), before)
        C.memset(C.byref(output), 0xA5, C.sizeof(output))
        sentinel = bytes(output)
        self.assertEqual(call(None, 1, C.byref(inputs), None, 0, C.byref(output)), 255)
        self.assertEqual(bytes(output), sentinel)
        storage = (C.c_uint8 * (C.sizeof(inputs) + C.alignment(P._Input)))()
        unaligned = C.cast(C.byref(storage, 1), C.POINTER(P._Input))
        self.assertEqual(call(None, 0, unaligned, None, 0, C.byref(output)), 255)
        self.assertEqual(bytes(output), sentinel)

    def _ledger(self, poison=False):
        call = L._api(self.core)
        data = (C.c_uint8 * 1)(7)
        absent = L._Quantity(C.c_size_t(-1).value, C.c_size_t(-1).value, 255) if poison else L._Quantity(1, 0, 0)
        rows = (L._Row * 1)(L._Row(L._Quantity(1, 1, 0), L._Optional(0, absent), 1, 2))
        detail = (C.c_uint8 * 2)()
        total = (C.c_uint8 * 2)()
        descriptors = (L._Quantity * 1)()
        result = L._Result()
        before = bytes(data), bytes(rows)
        gc.collect()
        transport = call(data, len(data), rows, len(rows), detail, len(detail), total, len(total), descriptors, C.byref(result))
        self.assertEqual(transport, 0)
        self.assertEqual((bytes(data), bytes(rows)), before)
        expected_quantity = L._Quantity(descriptors[0].first, descriptors[0].length,
                                        descriptors[0].negative)
        expected_result = L._Result(result.status,
            L._Quantity(result.total.first, result.total.length, result.total.negative))
        self.assertEqual(bytes(descriptors), bytes(expected_quantity))
        self.assertEqual(bytes(result), bytes(expected_result))
        return bytes(detail), bytes(total), bytes(descriptors), bytes(result)

    def test_ledger_absent_usage_is_ignored_and_owned(self):
        self.assertEqual(self._ledger(True), self._ledger(False))

    def test_ledger_null_row_extent_preserves_all_mutable_outputs(self):
        call = L._api(self.core)
        detail = (C.c_uint8 * 2)(0xA5, 0xA5)
        total = (C.c_uint8 * 2)(0xA5, 0xA5)
        descriptors = (L._Quantity * 1)()
        result = L._Result()
        C.memset(descriptors, 0xA5, C.sizeof(descriptors))
        C.memset(C.byref(result), 0xA5, C.sizeof(result))
        before = bytes(detail), bytes(total), bytes(descriptors), bytes(result)
        self.assertEqual(call(None, 0, None, 1, detail, 2, total, 2, descriptors, C.byref(result)), 255)
        self.assertEqual((bytes(detail), bytes(total), bytes(descriptors), bytes(result)), before)

    def test_ledger_mutable_aliases_are_refused_before_any_write(self):
        call = L._api(self.core)
        arena = (C.c_uint8 * 128)(7)
        rows = (L._Row * 2)()
        rows[0] = L._Row(L._Quantity(1, 1, 0), L._Optional(0, L._Quantity(1, 0, 0)), 1, 2)
        detail = (C.c_uint8 * 128)()
        total = (C.c_uint8 * 128)()
        descriptors = (L._Quantity * 8)()
        result_slab = (C.c_uint8 * 128)()
        result = C.cast(result_slab, C.POINTER(L._Result))
        owners = (arena, rows, detail, total, descriptors, result_slab)
        arguments = [arena, 1, rows, 1, detail, 2, total, 2, descriptors, result]
        inputs, outputs = (0, 2), (4, 6, 8, 9)
        for number, destination in enumerate(outputs):
            for source in inputs + outputs[:number]:
                with self.subTest(destination=destination, source=source):
                    args = list(arguments)
                    typ = call.argtypes[destination]
                    args[destination] = C.cast(args[source], typ)
                    before = tuple(bytes(owner) for owner in owners)
                    self.assertEqual(call(*args), 255)
                    self.assertEqual(tuple(bytes(owner) for owner in owners), before)

    def test_ledger_typed_shape_refusal_preserves_foreign_outputs(self):
        call = L._api(self.core)
        data = (C.c_uint8 * 1)(7)
        rows = (L._Row * 1)(L._Row(L._Quantity(1, 1, 2),
            L._Optional(0, L._Quantity(1, 0, 0)), 1, 2))
        detail = (C.c_uint8 * 2)(0xA5, 0xA5)
        total = (C.c_uint8 * 2)(0xA5, 0xA5)
        descriptors = (L._Quantity * 1)()
        result = L._Result()
        C.memset(descriptors, 0xA5, C.sizeof(descriptors))
        C.memset(C.byref(result), 0xA5, C.sizeof(result))
        owners = (data, rows, detail, total, descriptors, result)
        before = tuple(bytes(owner) for owner in owners)
        self.assertEqual(call(data, 1, rows, 1, detail, 2, total, 2,
                              descriptors, C.byref(result)), 255)
        self.assertEqual(tuple(bytes(owner) for owner in owners), before)

    def test_headroom_typed_shape_refusal_preserves_foreign_outputs(self):
        call = L._headroom_api(self.core)
        data = (C.c_uint8 * 1)(7)
        invalid = L._Quantity(1, 1, 2)
        zero = L._Quantity(1, 0, 0)
        output = (C.c_uint8 * 2)(0xA5, 0xA5)
        result = L._Result()
        C.memset(C.byref(result), 0xA5, C.sizeof(result))
        owners = (data, invalid, zero, output, result)
        before = tuple(bytes(owner) for owner in owners)
        self.assertEqual(call(data, 1, C.byref(invalid), C.byref(zero),
                              C.byref(zero), output, 2, C.byref(result)), 255)
        self.assertEqual(tuple(bytes(owner) for owner in owners), before)

    def test_headroom_readonly_descriptor_alias_and_checked_extent(self):
        call = L._headroom_api(self.core)
        arena = (C.c_uint8 * 1)(7)
        q = L._Quantity(1, 1, 0)
        clones = tuple(L._Quantity.from_buffer_copy(q) for _ in range(3))
        output = (C.c_uint8 * 3)()
        result = L._Result()
        self.assertEqual(call(arena, 1, *(C.byref(v) for v in clones), output, 3, C.byref(result)), 0)
        baseline = bytes(output), bytes(result)
        before = bytes(arena), bytes(q)
        self.assertEqual(call(arena, 1, C.byref(q), C.byref(q), C.byref(q), output, 3, C.byref(result)), 0)
        self.assertEqual((bytes(output), bytes(result)), baseline)
        self.assertEqual((bytes(arena), bytes(q)), before)
        self.assertEqual(call(None, 1, C.byref(q), C.byref(q), C.byref(q), output, 3, C.byref(result)), 255)
        self.assertEqual((bytes(output), bytes(result)), baseline)

    def test_lifecycle_absent_request_and_refusal_preserve_output(self):
        call = V._api(self.core)
        rows = (V._Row * 1)(V._Row(1, 0, 2))
        mask = (C.c_uint8 * 1)(0xA5)
        self.assertEqual(call(None, 0, rows, 1, 2, 0, 1, 0, mask, 1), 3)
        baseline = bytes(mask)
        before = bytes(rows)
        self.assertEqual(call(None, 0, rows, 1, 2, 0, 0, C.c_size_t(-1).value, mask, 1), 3)
        self.assertEqual(bytes(mask), baseline)
        self.assertEqual(bytes(rows), before)
        mask[0] = 0xA5
        self.assertEqual(call(None, 1, rows, 1, 2, 0, 1, 0, mask, 1), 255)
        self.assertEqual(bytes(mask), b'\xa5')
        rows[0].observed = 255
        self.assertEqual(call(None, 0, rows, 1, 2, 0, 1, 0, mask, 1), 255)
        self.assertEqual(bytes(mask), b'\xa5')

    def test_lifecycle_mutable_input_alias_is_refused(self):
        call = V._api(self.core)
        data = (C.c_uint8 * 32)(7)
        rows = (V._Row * 1)(V._Row(1, 1, 2))
        for storage in (data, rows):
            before = bytes(data), bytes(rows)
            output = C.cast(storage, C.POINTER(C.c_uint8))
            self.assertEqual(call(data, 1, rows, 1, 2, 0, 1, 0, output, 1), 255)
            self.assertEqual((bytes(data), bytes(rows)), before)

    def _run_owned(self):
        kernel = R.ResourceRunLedgerKernel(self.core)
        before = state(0)
        item = row()
        return kernel, kernel.prepare(before=before, before_rows=(), proposed=state(1, held=10),
                                      proposed_rows=(item,), observed=(), request=request(before, item))

    def _run_call(self, kernel, owned, output, output_length=None):
        return kernel.call(C.byref(owned.packet), C.sizeof(owned.packet), owned.arena, owned.arena_length,
                           owned.before_rows, len(owned.before_rows), owned.proposed_rows, len(owned.proposed_rows),
                           owned.native, len(owned.native), output,
                           C.sizeof(R.RawResult) if output_length is None else output_length)

    def test_run_ledger_snapshot_before_accepted_output_alias(self):
        kernel, owned = self._run_owned()
        result = R.RawResult()
        before = bytes(owned.packet), bytes(owned.arena), bytes(owned.proposed_rows)
        gc.collect()
        self.assertEqual(self._run_call(kernel, owned, C.byref(result)), 0)
        self.assertEqual(R.STATUS[result.status], 'READY')
        self.assertEqual((bytes(owned.packet), bytes(owned.arena), bytes(owned.proposed_rows)), before)
        expected = bytes(result)
        aliased = C.cast(C.byref(owned.packet), C.POINTER(R.RawResult))
        self.assertEqual(self._run_call(kernel, owned, aliased), 0)
        self.assertEqual(bytes(aliased.contents), expected)
        self.assertEqual(bytes(owned.packet)[C.sizeof(result):], before[0][C.sizeof(result):])
        self.assertEqual((bytes(owned.arena), bytes(owned.proposed_rows)), before[1:])

    def test_run_ledger_readonly_row_rosters_may_alias(self):
        kernel, owned = self._run_owned()
        rows = owned.proposed_rows
        copy = (R.RawRow * len(rows)).from_buffer_copy(rows)
        baseline = R.RawResult()
        aliased = R.RawResult()
        before = bytes(rows)
        def invoke(prior, output):
            return kernel.call(C.byref(owned.packet), C.sizeof(owned.packet), owned.arena, owned.arena_length,
                               prior, len(prior), rows, len(rows), owned.native, len(owned.native),
                               C.byref(output), C.sizeof(output))
        self.assertEqual(invoke(copy, baseline), 0)
        self.assertEqual(invoke(rows, aliased), 0)
        self.assertEqual(bytes(aliased), bytes(baseline))
        self.assertEqual(bytes(rows), before)

    def test_run_ledger_checked_output_extent_leaves_storage_unchanged(self):
        kernel, owned = self._run_owned()
        result = R.RawResult(255)
        self.assertEqual(self._run_call(kernel, owned, C.byref(result), C.sizeof(result) + 1), -1)
        self.assertEqual(bytes(result), bytes(R.RawResult(255)))

    def test_original_production_callers_survive_collection_at_native_extent(self):
        spans = {
            'wl_resources_can_reserve': ((1, 2, 1), (3, 4, 1), (5, 6, 1), (7, 8, 1)),
            'wl_resource_policy_admit': ((0, 1, 1), (2, None, C.sizeof(P._Input)), (3, 4, C.sizeof(P._Disk))),
            'wl_resource_ledger_compute': ((0, 1, 1), (2, 3, C.sizeof(L._Row))),
            'wl_resource_ledger_headroom': ((0, 1, 1), (2, None, C.sizeof(P._Quantity)),
                                            (3, None, C.sizeof(P._Quantity)), (4, None, C.sizeof(P._Quantity))),
            'wl_reservation_lifecycle_plan': ((0, 1, 1), (2, 3, C.sizeof(V._Row))),
            'wl_ordinary_reservation_lifecycle_plan': ((0, 1, 1),),
            'wl_resource_run_ledger_check_v1': ((0, 1, 1), (2, 3, 1), (4, 5, C.sizeof(R.RawRow)),
                                               (6, 7, C.sizeof(R.RawRow)), (8, 9, C.sizeof(R.RawNative))),
        }
        output_spans = {
            'wl_resources_can_reserve': (),
            'wl_resource_policy_admit': ((5, None, C.sizeof(P._Result)),),
            'wl_resource_ledger_compute': ((4, 5, 1), (6, 7, 1), (8, 3, C.sizeof(P._Quantity)), (9, None, C.sizeof(L._Result))),
            'wl_resource_ledger_headroom': ((5, 6, 1), (7, None, C.sizeof(L._Result))),
            'wl_reservation_lifecycle_plan': ((8, 9, 1),),
            'wl_ordinary_reservation_lifecycle_plan': ((2, 3, 1),
                (4, None, C.sizeof(C.c_uint32)), (5, None, C.sizeof(C.c_size_t))),
            'wl_resource_run_ledger_check_v1': ((10, 11, 1),),
        }
        observed = []
        actual = self.core._lib
        test = self

        class NativeExtentObserver:
            def __getattr__(self, name):
                native = getattr(actual, name)
                if name not in spans:
                    return native
                def call(*args):
                    frames = [(args[index], factor if count is None else int(args[count]) * factor)
                              for index, count, factor in spans[name]]
                    outputs = [(args[index], factor if count is None else int(args[count]) * factor)
                               for index, count, factor in output_spans[name]]
                    def interval(frame):
                        address, size = frame
                        start = C.cast(address, C.c_void_p).value or 0
                        return start, start + size
                    for number, output in enumerate(outputs):
                        start, end = interval(output)
                        for other in frames + outputs[:number]:
                            low, high = interval(other)
                            test.assertTrue(start == end or low == high or end <= low or high <= start,
                                            'production caller mutable storage must be exclusive')
                    preimage = tuple(C.string_at(address, size) for address, size in frames)
                    gc.collect()
                    native.argtypes, native.restype = call.argtypes, call.restype
                    status = native(*args)
                    test.assertEqual(tuple(C.string_at(address, size) for address, size in frames), preimage)
                    observed.append(name)
                    return status
                return call

        core = SimpleNamespace(_lib=NativeExtentObserver())
        K.can_reserve(LARGE, 0, 0, LARGE, core=core)
        policy = dict(outstanding_count=0, concurrency_limit=None, memory_pressure=None,
                      memory_pressure_ceiling=0, disks=(), disk_byte_floor=0, disk_inode_floor=0,
                      available_memory=LARGE, withheld_memory=0, memory_floor=0, requested_memory=LARGE)
        P.decide_policy(**policy, core=core)
        L.compute_ledger(((LARGE, None),), core=core)
        L.compute_headroom(LARGE, 0, 0, core=core)
        self.assertEqual(V.release_plan(('identity',), 'identity', core=core), (True,))
        # The original exact-byte ABI remains a separate compatibility control.
        # The production facade now uses the ordinary full-protocol ABI above.
        legacy_rows = (V._Row * 1)(V._Row(1, 0, 2))
        legacy_mask = (C.c_uint8 * 1)(0xA5)
        self.assertEqual(V._api(core)(None, 0, legacy_rows, 1, 2, 0,
                                     1, 0, legacy_mask, 1), 3)
        E.observe_policy(**policy, core=core)
        E.observe_ledger(((LARGE, None),), core=core)
        before = state(0)
        item = row()
        self.assertEqual(R.ResourceRunLedgerKernel(core).check(before=before, before_rows=(),
                         proposed=state(1, held=10), proposed_rows=(item,), observed=(),
                         request=request(before, item)), 'READY')
        self.assertEqual(set(observed), set(spans))


if __name__ == '__main__':
    unittest.main()
