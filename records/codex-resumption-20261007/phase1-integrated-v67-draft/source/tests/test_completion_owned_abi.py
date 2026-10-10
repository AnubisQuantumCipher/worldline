"""Additive actual-native extent/custody controls; no proof or run claim.

The unchanged original suites remain required. These controls use their real
producer fixtures, not a substituted semantic decoder or a fake native call.
"""
import ctypes as C
import gc
import threading
import unittest
import weakref

import test_raw_evaluation_default as original
from worldline.completion_kernel import LAYOUTS, Result, Check_Row
from worldline.evaluation_context import MetadataContext, MetadataRow


class CompletionOwnedAbiControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        original.RawRequiredFailureControls.setUpClass()

    def setUp(self):
        self.fixture = original.RawRequiredFailureControls(methodName='runTest')
        self.fixture.setUp()
        self.collapse, self.agent, self.prepared = self.fixture.bound_request()
        self.kernel = self.fixture.raw_kernel
        self.raw_call = self.kernel.raw_call

    def call(self, prepared=None, output=None):
        prepared = self.prepared if prepared is None else prepared
        output = Result() if output is None else output
        status = self.raw_call(*prepared.arguments(), C.byref(output))
        return status, output

    def snapshot(self):
        p = self.prepared
        return tuple(bytes(x) for x in
                     (p.request, p.raw, p.confinement, *p.owned))

    def test_layout_every_original_completion_field_and_sentinel(self):
        lib = self.kernel.library
        self.assertEqual(lib.wl_completion_abi_version_v1(), 1)
        for kind, typ in enumerate(LAYOUTS, 1):
            with self.subTest(kind=kind):
                self.assertEqual(lib.wl_completion_layout_size_v1(kind), C.sizeof(typ))
                self.assertEqual(lib.wl_completion_layout_alignment_v1(kind), C.alignment(typ))
                for field, (name, _) in enumerate(typ._fields_, 1):
                    self.assertEqual(lib.wl_completion_layout_offset_v1(kind, field),
                                     getattr(typ, name).offset)
                self.assertEqual(lib.wl_completion_layout_offset_v1(kind, 0), (1 << 63) - 1)
        self.assertEqual(lib.wl_completion_layout_size_v1(0), (1 << 63) - 1)
        self.assertEqual(lib.wl_completion_layout_alignment_v1(0), (1 << 63) - 1)
        layout = lib.wl_completion_metadata_layout_v1
        layout.argtypes = [C.c_uint32, C.c_uint32]
        layout.restype = C.c_int64
        for kind, typ in ((1, MetadataContext), (2, MetadataRow)):
            self.assertEqual(layout(kind, 0), C.sizeof(typ))
            self.assertEqual(layout(kind, 1), C.alignment(typ))
            for field, (name, _) in enumerate(typ._fields_, 2):
                self.assertEqual(layout(kind, field), getattr(typ, name).offset)
        self.assertEqual(layout(0, 0), (1 << 63) - 1)

    def test_actual_native_call_preserves_all_input_preimages(self):
        before = self.snapshot()
        status, output = self.call()
        self.assertEqual(status, 0)
        self.assertEqual(output.promotion, 1)
        self.assertEqual(before, self.snapshot())

    def test_read_only_captured_retained_alias_is_accepted(self):
        p = self.prepared
        # Compare distinct read-only allocations with accepted shared storage
        # under the same original retained-present semantic request.
        retained = (Check_Row * p.request.captured_count).from_buffer_copy(p.owned[2])
        p.request.retained_present = 1
        p.request.retained = p.request.captured
        p.request.retained_count = p.request.captured_count
        p.request.retained_results = C.addressof(retained)
        status, expected = self.call()
        self.assertEqual(status, 0)
        p.request.retained_results = p.request.captured_results
        before = self.snapshot()
        status, output = self.call()
        self.assertEqual(status, 0)
        self.assertEqual(bytes(output), bytes(expected))
        self.assertEqual(before, self.snapshot())

    def test_native_output_overlap_refused_without_mutating_request(self):
        before = bytes(self.prepared.request)
        status = self.raw_call(*self.prepared.arguments(), C.byref(self.prepared.request))
        self.assertEqual(status, 255)
        self.assertEqual(bytes(self.prepared.request), before)

    def test_every_nonempty_input_output_overlap_is_refused(self):
        # Each proposed output is itself backed by a live full-sized allocation.
        # This is a mutable-overlap refusal, never an arbitrary-pointer probe.
        for field, owner_index in (('data', 0), ('journal', 1), ('captured_results', 2),
                                   ('required', 5)):
            with self.subTest(field=field):
                p = self.prepared
                old = getattr(p.request, field)
                owner = p.owned[owner_index]
                extent = max(C.sizeof(owner), C.sizeof(Result))
                buffer = (C.c_uint64 * ((extent + 7) // 8))()
                C.memmove(C.addressof(buffer), C.addressof(owner), C.sizeof(owner))
                setattr(p.request, field, C.addressof(buffer))
                before = bytes(buffer)
                try:
                    status = self.raw_call(*p.arguments(), C.addressof(buffer))
                    self.assertEqual(status, 255)
                    self.assertEqual(bytes(buffer), before)
                finally:
                    setattr(p.request, field, old)
        for field in ('raw', 'confinement'):
            with self.subTest(field=field):
                p = self.prepared
                owner = getattr(p, field)
                extent = max(C.sizeof(owner), C.sizeof(Result))
                buffer = (C.c_uint64 * ((extent + 7) // 8))()
                C.memmove(C.addressof(buffer), C.addressof(owner), C.sizeof(owner))
                raw = C.addressof(buffer) if field == 'raw' else C.cast(p.raw, C.c_void_p)
                confinement = (C.addressof(buffer) if field == 'confinement'
                               else C.cast(p.confinement, C.c_void_p))
                before = bytes(buffer)
                self.assertEqual(self.raw_call(C.byref(p.request), raw, confinement,
                                               C.addressof(buffer)), 255)
                self.assertEqual(bytes(buffer), before)

    def test_null_zero_absence_and_nonzero_null_keep_original_domain(self):
        p = self.prepared
        for address, count in (('retained_results', 'retained_count'), ('history', 'history_count')):
            self.assertEqual(getattr(p.request, count), 0)
            setattr(p.request, address, None)
        self.assertEqual(self.call()[0], 0)
        for address in ('data', 'journal', 'captured_results', 'required'):
            with self.subTest(address=address):
                old = getattr(p.request, address)
                setattr(p.request, address, None)
                output = Result()
                C.memset(C.addressof(output), 0xA5, C.sizeof(output))
                before = bytes(output)
                try:
                    self.assertEqual(self.call(output=output)[0], 255)
                    self.assertEqual(bytes(output), before)
                finally:
                    setattr(p.request, address, old)

    def test_malformed_numeric_extent_is_refused_before_array_read(self):
        p = self.prepared
        for count in ('journal_count', 'captured_count', 'retained_count',
                      'history_count', 'required_count'):
            for value in (-1, (1 << 63) - 1):
                with self.subTest(count=count, value=value):
                    old = getattr(p.request, count)
                    setattr(p.request, count, value)
                    output = Result()
                    C.memset(C.addressof(output), 0xA5, C.sizeof(output))
                    before = bytes(output)
                    try:
                        self.assertEqual(self.call(output=output)[0], 255)
                        self.assertEqual(bytes(output), before)
                    finally:
                        setattr(p.request, count, old)

    def test_descriptor_alone_retains_original_nested_allocations(self):
        p = self.prepared
        request, raw, confinement = p.request, p.raw, p.confinement
        refs = tuple(weakref.ref(owner) for owner in p.owned)
        self.assertIs(request._transport_owners, p.owned)
        self.prepared = None
        del p
        gc.collect()
        self.assertTrue(all(ref() is not None for ref in refs))
        output = Result()
        self.assertEqual(self.raw_call(C.byref(request), C.cast(raw, C.c_void_p),
                                      C.cast(confinement, C.c_void_p), C.byref(output)), 0)
        self.assertEqual(output.promotion, 1)

    def test_gc_during_real_native_calls_does_not_change_inputs(self):
        before = self.snapshot()
        stop = threading.Event()
        def collect():
            while not stop.is_set():
                gc.collect()
        collector = threading.Thread(target=collect)
        collector.start()
        try:
            for _ in range(3):
                self.assertEqual(self.kernel.classify(self.prepared), ('Completed', 'PASS', True))
        finally:
            stop.set()
            collector.join()
        self.assertEqual(self.snapshot(), before)

    def test_actual_nested_context_metadata_producer_survives_owner_tuple_drop(self):
        from worldline.evaluation_context import require_metadata
        p = self.fixture.joined(self.collapse, self.prepared, self.agent)
        descriptor = p.metadata_context
        base = descriptor._transport_owners[2]
        base_refs = tuple(weakref.ref(owner) for owner in base._transport_owners)
        metadata_refs = tuple(weakref.ref(owner) for owner in descriptor._transport_owners[:2])
        p.context_owners = ()
        p.metadata_owners = ()
        gc.collect()
        self.assertTrue(all(ref() is not None for ref in (*base_refs, *metadata_refs)))
        require_metadata(self.fixture.core, p.request, descriptor)
        self.assertEqual(self.fixture.core.collapse_decide_with_evaluation(
            self.collapse, primary=p, staged=None, agent=self.agent), 'AUTHORIZED')

    def test_metadata_does_not_observe_unneeded_journal_or_required_arrays(self):
        from worldline.evaluation_context import require_metadata
        p = self.fixture.joined(self.collapse, self.prepared, self.agent)
        for address, count in (('journal', 'journal_count'), ('required', 'required_count'),
                               ('retained_results', 'retained_count'), ('history', 'history_count')):
            setattr(p.request, address, None)
            setattr(p.request, count, -1)
        # The original metadata helper observes only Data and Captured_Results.
        # It must not gain a stronger domain from a general view factory.
        require_metadata(self.fixture.core, p.request, p.metadata_context)

    def test_metadata_preserves_original_descriptor_row_overlap_refusal(self):
        p = self.fixture.joined(self.collapse, self.prepared, self.agent)
        descriptor = p.metadata_context
        extent = max(C.sizeof(MetadataContext),
                     descriptor.row_count * C.sizeof(MetadataRow))
        buffer = (C.c_uint64 * ((extent + 7) // 8))()
        C.memmove(C.addressof(buffer), C.addressof(descriptor), C.sizeof(descriptor))
        aliased = MetadataContext.from_buffer(buffer)
        aliased.rows = C.addressof(buffer)
        before = bytes(buffer)
        call = self.kernel.library.wl_completion_metadata_matches_v1
        call.argtypes = [C.c_void_p, C.c_void_p]
        call.restype = C.c_int
        self.assertEqual(call(C.byref(p.request), C.byref(aliased)), 255)
        self.assertEqual(bytes(buffer), before)


if __name__ == '__main__':
    unittest.main()
