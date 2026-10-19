"""Owned ctypes storage controls for the concrete C_API/SPARK bridges.

All pointers name live Python-owned objects. These controls do not probe arbitrary
nonnull addresses, establish OS mapping safety, or replace the lifetime roster.
"""
import ctypes as C
import gc
import os
from pathlib import Path
import unittest

from worldline.core import Core
from worldline.evaluation_history import _api, _Query, _Row, _Selection
from worldline.recovery_authority_kernel import (
    RecoveryAuthorityKernel, Request as RequestV2, Result as ResultV2,
)
from worldline.recovery_authority_kernel_v3 import (
    RecoveryAuthorityKernelV3, Request as RequestV3, Result as ResultV3,
    BoundUse, NativeObservation, HASH_FIELDS,
)


class QuerySelectionAlias(C.Union):
    _fields_ = [('query', _Query), ('selection', _Selection)]


class RequestResultAliasV2(C.Union):
    _fields_ = [('request', RequestV2), ('result', ResultV2)]


class RequestResultAliasV3(C.Union):
    _fields_ = [('request', RequestV3), ('result', ResultV3)]


class OwnedRecoveryHistoryAbiControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ.get('WORLDLINE_CORE_LIB', Path(__file__).resolve().parents[1] / 'lib/libworldline_core.so')))
        cls.history = _api(cls.core)
        cls.v2 = RecoveryAuthorityKernel(cls.core)
        cls.v3 = RecoveryAuthorityKernelV3(cls.core)
        cls.marker = cls.core._lib.wl_recovery_select
        cls.marker.argtypes = [C.c_void_p, C.c_size_t,
                              C.c_uint8, C.c_void_p, C.c_size_t,
                              C.c_uint8, C.c_void_p, C.c_size_t]
        cls.marker.restype = C.c_uint8

    @staticmethod
    def request_v3():
        request = RequestV3(schema_version=3)
        for binding in (request.issued_binding, request.recovered_binding):
            binding.policy_epoch.first = 1
            binding.resource_epoch.first = 1
        return request

    def test_marker_readonly_alias_and_absent_extents_retain_domain(self):
        owner = (C.c_uint8 * 1)(0x61)
        before = bytes(owner)
        pointer = C.cast(owner, C.c_void_p)
        gc.collect()
        # Expected, live and prepared all observe the same original allocation.
        self.assertEqual(self.marker(pointer, 1, 1, pointer, 1, 1, pointer, 1), 2)
        self.assertEqual(bytes(owner), before)
        # Original absent markers ignore their extent, including size_t's last.
        ignored = C.c_size_t(-1).value
        self.assertEqual(self.marker(pointer, 1, 0, None, ignored,
                                     0, None, ignored), 2)
        self.assertEqual(self.marker(pointer, 1, 2, None, 0, 0, None, 0), 255)

    def test_readonly_history_views_may_share_one_owned_allocation(self):
        row, query, output = _Row(), _Query(), _Selection()
        before = bytes(row)
        # Data, Rows and Final_Row observe the same live allocation; no writer
        # exists until the independent output result is committed by C_API.
        data = C.cast(C.pointer(row), C.POINTER(C.c_uint8))
        owners = (row, query, output, data)
        gc.collect()
        status = self.history(data, 1, C.byref(row), 1, 1,
                              C.byref(row), C.byref(query), C.byref(output))
        self.assertEqual(status, 0)
        self.assertEqual(bytes(owners[0]), before)
        self.assertEqual(output.reason, 0)  # Typed INPUT_ABSENT, not transport.

    def test_history_mutable_query_overlap_is_refused_without_write(self):
        owned = QuerySelectionAlias()
        data, rows = (C.c_uint8 * 0)(), (_Row * 0)()
        before = bytes(owned)
        query = C.cast(C.byref(owned), C.POINTER(_Query))
        output = C.cast(C.byref(owned), C.POINTER(_Selection))
        self.assertEqual(self.history(data, 0, rows, 0, 0, None,
                                      query, output), 255)
        self.assertEqual(bytes(owned), before)
        # The same query is transport-valid when only the output is detached.
        # Both overlapping views above retain the original union allocation.
        detached = _Selection()
        self.assertEqual(self.history(data, 0, rows, 0, 0, None,
                                      query, C.byref(detached)), 0)
        self.assertEqual(bytes(owned), before)

    def test_history_mutable_arena_overlap_is_refused_without_write(self):
        output, query = _Selection(), _Query()
        before = bytes(output)
        data = C.cast(C.pointer(output), C.POINTER(C.c_uint8))
        self.assertEqual(self.history(data, 1, (_Row * 0)(), 0, 0, None,
                                      C.byref(query), C.byref(output)), 255)
        self.assertEqual(bytes(output), before)

    def test_history_absent_final_does_not_map_unused_pointer(self):
        query, output = _Query(), _Selection()
        self.assertEqual(self.history(None, 0, None, 0, 0, None,
                                      C.byref(query), C.byref(output)), 0)
        self.assertEqual(output.reason, 0)

    def test_v2_original_input_output_alias_keeps_complete_snapshot(self):
        owned, expected = RequestResultAliasV2(), ResultV2()
        request = RequestV2()
        self.assertEqual(self.v2.call(C.byref(request), C.sizeof(request),
                                      C.byref(expected), C.sizeof(expected)), 0)
        owned.request = request
        self.assertEqual(self.v2.call(C.byref(owned), C.sizeof(RequestV2),
                                      C.byref(owned), C.sizeof(ResultV2)), 0)
        self.assertEqual(bytes(owned.result), bytes(expected))

    def test_v3_original_input_output_alias_keeps_complete_snapshot(self):
        owned, expected, arena = RequestResultAliasV3(), ResultV3(), (C.c_uint8 * 0)()
        request = self.request_v3()
        self.assertEqual(self.v3.call(C.byref(request), C.sizeof(request), arena, 0,
                                      C.byref(expected), C.sizeof(expected)), 0)
        owned.request = request
        self.assertEqual(self.v3.call(C.byref(owned), C.sizeof(RequestV3), arena, 0,
                                      C.byref(owned), C.sizeof(ResultV3)), 0)
        self.assertEqual(bytes(owned.result), bytes(expected))

    def test_v3_original_exact_extent_and_null_refusals_do_not_write(self):
        request, output = self.request_v3(), ResultV3(0xa5, 0x5a)
        arena = (C.c_uint8 * 0)()
        before = bytes(output)
        for pointer, extent in ((None, C.sizeof(request)),
                                (C.byref(request), C.sizeof(request) - 1)):
            self.assertEqual(self.v3.call(pointer, extent, arena, 0,
                                          C.byref(output), C.sizeof(output)), -1)
            self.assertEqual(bytes(output), before)
        self.assertEqual(self.v3.call(C.byref(request), C.sizeof(request), None, 1,
                                      C.byref(output), C.sizeof(output)), -1)
        self.assertEqual(bytes(output), before)

    def test_v3_owned_misaligned_record_is_refused_without_read_or_write(self):
        request, output = self.request_v3(), ResultV3(0xa5, 0x5a)
        storage = (C.c_uint8 * (C.sizeof(request) + C.alignment(RequestV3)))()
        offset = next(index for index in range(C.alignment(RequestV3))
                      if (C.addressof(storage) + index) % C.alignment(RequestV3))
        pointer = C.byref(storage, offset)
        C.memmove(pointer, C.byref(request), C.sizeof(request))
        before = bytes(output)
        self.assertEqual(self.v3.call(pointer, C.sizeof(request), None, 0,
                                      C.byref(output), C.sizeof(output)), -1)
        self.assertEqual(bytes(output), before)

    def test_v3_actual_prepared_owner_and_cast_survive_collection(self):
        binding = BoundUse(mode='CANDIDATE', policy_epoch=1, resource_epoch=1,
                           **dict.fromkeys(HASH_FIELDS))
        prepared = self.v3.prepare(state='ISSUED', issued=binding,
                                   recovered=binding, fresh='REFUSED',
                                   historical='UNESTABLISHED', grant_eligible=False,
                                   native=NativeObservation(live_mapping=None,
                                                            live_root=None))
        before_request, before_arena = bytes(prepared.request), bytes(prepared.arena)
        result = ResultV3()
        # Cast is not an owner: prepared retains both original concrete owners.
        pointer = C.cast(prepared.arena, C.c_void_p)
        gc.collect()
        self.assertEqual(self.v3.call(C.byref(prepared.request), C.sizeof(prepared.request),
                                      pointer, prepared.arena_length,
                                      C.byref(result), C.sizeof(result)), 0)
        self.assertEqual(bytes(prepared.request), before_request)
        self.assertEqual(bytes(prepared.arena), before_arena)


if __name__ == '__main__':
    unittest.main()
