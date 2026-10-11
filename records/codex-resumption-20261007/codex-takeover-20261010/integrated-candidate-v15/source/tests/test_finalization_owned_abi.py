"""UNRUN native finalization owned-ABI controls; original suites remain required."""
import ctypes as C
import gc
import unittest
import weakref
from worldline import finalization_kernel as native
import test_finalization_kernel as original


class FinalizationOwnedAbiControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        original.FinalizationNativeControls.setUpClass()
        cls.fixture = original.FinalizationNativeControls()
        cls.kernel = cls.fixture.kernel

    def packed(self):
        capture = self.fixture.capture()
        value = self.fixture.sealed(capture)
        return self.kernel._pack(3, capture.start, capture.input, capture, value)

    def test_all_native_layout_queries_and_unknown_sentinels(self):
        layout = self.kernel.library.wl_finalization_layout_v1
        for kind, typ in enumerate((native.Start, native.Input, native.Row, native.Request, native.Result), 1):
            self.assertEqual(layout(kind, 0), C.sizeof(typ))
            self.assertEqual(layout(kind, 1), C.alignment(typ))
            for field, (name, _) in enumerate(typ._fields_, 2):
                self.assertEqual(layout(kind, field), getattr(typ, name).offset)
            self.assertEqual(layout(kind, 0xffffffff), (1 << 63) - 1)
        self.assertEqual(layout(0xffffffff, 0), (1 << 63) - 1)

    def test_nested_readonly_arrays_can_alias_the_whole_byte_arena(self):
        request, owners = self.packed()
        expected = native.Result()
        self.assertEqual(self.kernel.call(C.byref(request), C.byref(expected)), 0)
        # Preserve every original span and row; put their exact raw bytes inside
        # the same owned arena, beyond the bytes named by semantic spans.
        arena = bytearray(bytes(owners[0]))
        offsets = []
        for owner, typ in ((owners[1], native.Row), (owners[2], native.Required_Row)):
            arena.extend(bytes((-len(arena)) % C.alignment(typ)))
            offsets.append(len(arena))
            arena.extend(bytes(owner))
        shared = (C.c_uint8 * len(arena)).from_buffer_copy(arena)
        request.data, request.data_length = C.addressof(shared), len(shared)
        request.rows = C.addressof(shared) + offsets[0]
        request.required = C.addressof(shared) + offsets[1]
        request._transport_owners = (shared,)
        before = bytes(shared), bytes(request)
        result = native.Result()
        self.assertEqual(self.kernel.call(C.byref(request), C.byref(result)), 0)
        self.assertEqual(bytes(result), bytes(expected))
        self.assertEqual((bytes(shared), bytes(request)), before)

    def test_mutable_output_overlap_every_original_input_extent_refuses(self):
        for extent in ('descriptor', 'data', 'rows', 'required'):
            with self.subTest(extent=extent):
                request, owners = self.packed()
                address = C.addressof(request) if extent == 'descriptor' else getattr(request, extent)
                before = bytes(request), tuple(bytes(owner) for owner in owners)
                self.assertEqual(self.kernel.call(C.byref(request), C.c_void_p(address)), 255)
                self.assertEqual((bytes(request), tuple(bytes(owner) for owner in owners)), before)

    def test_numeric_transport_refusal_keeps_complete_output_unchanged(self):
        damaged = (('data_length', -1), ('row_count', -1), ('required_count', -1),
                   ('row_count', (1 << 63) - 1), ('required_count', (1 << 63) - 1),
                   ('data', None), ('rows', None), ('required', None))
        for field, value in damaged:
            with self.subTest(field=field, value=value):
                request, owners = self.packed()
                setattr(request, field, value)
                result = native.Result()
                C.memset(C.byref(result), 0xa5, C.sizeof(result))
                before = bytes(result)
                self.assertEqual(self.kernel.call(C.byref(request), C.byref(result)), 255)
                self.assertEqual(bytes(result), before)
        request, owners = self.packed()
        result = native.Result()
        for input_address, output_address in ((None, C.byref(result)),
                (C.c_void_p(C.addressof(request) + 1), C.byref(result)),
                (C.byref(request), None),
                (C.byref(request), C.c_void_p(C.addressof(result) + 1))):
            before = bytes(result)
            self.assertEqual(self.kernel.call(input_address, output_address), 255)
            self.assertEqual(bytes(result), before)

    def test_zero_extents_accept_null_and_ignored_rows_without_reading(self):
        start, _inputs = self.fixture.values(False)
        request, owners = self.kernel._pack(0, start)
        request.required, request.rows = None, None
        result = native.Result()
        self.assertEqual(self.kernel.call(C.byref(request), C.byref(result)), 0)
        self.assertEqual(result.reason, 0)
        # Original start operation numerically validates rows but never reads
        # their values. This live row deliberately has malformed semantic spans.
        row = native.Row()
        request.rows, request.row_count = C.addressof(row), 1
        self.assertEqual(self.kernel.call(C.byref(request), C.byref(result)), 0)
        self.assertEqual(result.reason, 0)

    def test_live_descriptor_owns_every_array_at_actual_native_call(self):
        request, owners = self.packed()
        refs = tuple(weakref.ref(owner) for owner in owners)
        before = bytes(request), tuple(bytes(owner) for owner in owners)
        del owners
        gc.collect()
        self.assertTrue(all(ref() is not None for ref in refs))
        result = native.Result()
        self.assertEqual(self.kernel.call(C.byref(request), C.byref(result)), 0)
        self.assertEqual(result.reason, 0)
        self.assertEqual((bytes(request), tuple(bytes(owner) for owner in request._transport_owners)), before)
        del request
        gc.collect()
        self.assertTrue(all(ref() is None for ref in refs))

    def test_mixed_absence_ignores_unneeded_checkpoint_descriptors(self):
        from test_raw_evaluation_default import RawDependencyControls
        from worldline.evaluation_wire import Authority
        call = self.kernel.library.wl_collapse_decide_finalization_v1
        call.argtypes = ([C.c_void_p] + [native.U32] + [C.c_void_p] * 4
                         + [native.U32] + [C.c_void_p] * 5 + [C.c_uint8])
        call.restype = C.c_uint8
        value = RawDependencyControls.checkpoint()
        request = self.fixture.core._raw_collapse_request(value)
        needed = Authority(self.fixture.core).dependencies(request)
        # Select a real dependency-free collapse request from the original Core
        # builder; skip no assertion and never dereference fabricated addresses.
        if needed['primary'] or needed['staged'] or needed['agent']:
            self.fail('original checkpoint collapse fixture is not dependency-free')
        malformed = native.Request()
        before = bytes(malformed)
        expected = self.fixture.core.collapse_decide(value)
        code = int(call(C.byref(request), 2, C.byref(malformed), None, None, None,
                        2, C.byref(malformed), None, None, None, None, 0))
        from worldline.core import COLLAPSE_DECISIONS
        self.assertEqual(COLLAPSE_DECISIONS.get(code, 'INVALID_REQUEST'), expected)
        self.assertEqual(bytes(malformed), before)

    def test_actual_mixed_native_call_retains_all_context_metadata_owners(self):
        value, agent = self.fixture.collapse_values()
        prepared = self.kernel.prepare_finalization(self.fixture.sealed(self.fixture.capture()))
        self.fixture.joined(prepared, value, agent)
        before = bytes(prepared.native_request), tuple(bytes(owner) for owner in prepared.native_owners)
        gc.collect()
        self.assertEqual(self.fixture.core.collapse_decide_with_evaluation(value,
            primary=prepared, staged=None, agent=agent), 'AUTHORIZED')
        self.assertEqual((bytes(prepared.native_request),
            tuple(bytes(owner) for owner in prepared.native_owners)), before)
        # None is real absence, not an empty successful metadata assertion.
        prepared.metadata_context = None
        self.assertEqual(self.fixture.core.collapse_decide_with_evaluation(value,
            primary=prepared, staged=None, agent=agent), 'INVALID_REQUEST')


if __name__ == '__main__':
    unittest.main()
