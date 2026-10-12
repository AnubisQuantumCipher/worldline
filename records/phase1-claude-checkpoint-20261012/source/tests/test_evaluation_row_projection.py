"""Owned ordinary source controls, prepared but not executed.

The native relation compares independently supplied complete typed values. The
producer controls separately exercise original payload encodings. These finite
controls make no protected-store, pointer, provenance or universal-proof claim.
"""
import ctypes as C
from dataclasses import replace
from pathlib import Path
import os
import unittest
from test_raw_evaluation_default import RawRequiredFailureControls
from worldline.evaluation_context import (
    RowMetadata, project_metadata, metadata_descriptor, require_metadata,
)
from worldline.completion_kernel import Span, Optional_Span, KernelRefused
from worldline.evaluation_terminal import TerminalRefused, value_bytes


class MetadataNativeControls(RawRequiredFailureControls):
    def direct(self, values, projections):
        request, input_owners = self.raw_kernel._owned(
            (), None, self.capture, tuple(values), None, (), None, None, None,
            None, None, None)
        descriptor, output_owners = metadata_descriptor(self.core, request, projections)
        call = self.core._lib.wl_completion_metadata_matches_v1
        call.argtypes = [C.c_void_p, C.c_void_p]; call.restype = C.c_int
        before = bytes(request), bytes(descriptor), tuple(bytes(x) for x in input_owners[2])
        result = call(C.byref(request), C.byref(descriptor))
        self.assertEqual((bytes(request), bytes(descriptor), tuple(bytes(x) for x in input_owners[2])), before)
        return result

    def sample(self, *, execution=None, verifier=None):
        row = replace(self.measured(b'\x00full-check\xff', 'PASS'),
            source=b'\x00source\xff', payload=b'\x00full-payload\xff',
            execution=execution, verifier=verifier)
        projection = RowMetadata(b'\x00full-check\xff', b'\x00source\xff',
            b'\x00full-payload\xff', execution, verifier)
        return row, projection

    def test_all_five_full_fields_and_null_array(self):
        row, projection = self.sample(execution=b'\x00exec\xff', verifier=b'\x00verifier\xff')
        self.assertEqual(self.direct((row,), (projection,)), 1)
        self.assertEqual(self.direct((), ()), 1)
        for field in ('check', 'source', 'payload', 'execution', 'verifier'):
            with self.subTest(field=field):
                self.assertEqual(self.direct((row,), (replace(projection, **{field: b'different-full-field'}),)), 0)

    def test_true_absence_present_empty_and_present_null_bytes(self):
        for execution in (None, b'', b'\0'):
            for verifier in (None, b'', b'\0'):
                with self.subTest(execution=execution, verifier=verifier):
                    row, projection = self.sample(execution=execution, verifier=verifier)
                    self.assertEqual(self.direct((row,), (projection,)), 1)
        row, projection = self.sample()
        self.assertEqual(self.direct((row,), (replace(projection, execution=b''),)), 0)
        self.assertEqual(self.direct((row,), (replace(projection, verifier=b''),)), 0)
        row, projection = self.sample(execution=b'', verifier=b'')
        self.assertEqual(self.direct((row,), (replace(projection, execution=None),)), 0)
        self.assertEqual(self.direct((row,), (replace(projection, verifier=None),)), 0)

    def test_every_ordered_row_even_earlier_duplicate_and_unrelated_failure(self):
        row, projection = self.sample()
        earlier = replace(row, state='Incomplete_Unknown', outcome='FAIL', payload=b'earlier-complete-payload')
        other = replace(row, check=b'unrelated', state='Completed', outcome='FAIL')
        values = (earlier, other, row)
        projections = (replace(projection, payload=b'earlier-complete-payload'),
                       replace(projection, check=b'unrelated'), projection)
        self.assertEqual(self.direct(values, projections), 1)
        self.assertEqual(self.direct(values, (projection, projections[1], projection)), 0)
        self.assertEqual(self.direct(values, (projections[0], projection, projection)), 0)

    def test_native_count_and_invalid_span_refusal(self):
        row, projection = self.sample()
        request, input_owners = self.raw_kernel._owned(
            (), None, self.capture, (row,), None, (), None, None, None, None, None, None)
        descriptor, owners = metadata_descriptor(self.core, request, (projection,))
        call = self.core._lib.wl_completion_metadata_matches_v1
        call.argtypes = [C.c_void_p, C.c_void_p]; call.restype = C.c_int
        descriptor.row_count = 0
        self.assertEqual(call(C.byref(request), C.byref(descriptor)), 255)
        descriptor.row_count = len(owners[1])
        owners[1][0].payload = Span(0, 0)
        self.assertEqual(call(C.byref(request), C.byref(descriptor)), 255)

    def test_default_join_requires_projection_and_keeps_legacy_layout(self):
        request, agent, prepared = self.bound_request()
        self.joined(request, prepared, agent)
        # The original descriptor and original layout query remain usable.
        from worldline.evaluation_context import ContextInput, ContextRow
        old_layout = self.core._lib.wl_completion_context_layout_v1
        old_layout.argtypes = [C.c_uint32, C.c_uint32]; old_layout.restype = C.c_int64
        self.assertEqual(old_layout(1, 0), C.sizeof(ContextInput))
        self.assertEqual(old_layout(2, 0), C.sizeof(ContextRow))
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=None, agent=agent), 'AUTHORIZED')
        prepared.metadata_owners[1][0].source_id = prepared.metadata_owners[1][0].check_id
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=None, agent=agent), 'INVALID_REQUEST')

    def test_default_history_checks_metadata_before_required_fail_classification(self):
        self.assertEqual(self.retained_error_case(has_final=True,
            metadata_source=b'other-complete-source'), 'EVALUATION_CAPTURE_INVALID')

    def test_missing_projection_has_no_legacy_authorization_fallback(self):
        request, agent, prepared = self.bound_request()
        self.joined(request, prepared, agent)
        prepared.metadata_context = None
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=None, agent=agent), 'INVALID_REQUEST')


class MetadataProducerControls(unittest.TestCase):
    def test_original_string_and_nonstring_check_encodings(self):
        payload = {'id': 'check\0é', 'origin': 'engine'}
        actual = project_metadata(payload, capture_source=b'unused-capture-source')
        self.assertEqual(actual, RowMetadata('check\0é'.encode('utf-8'), value_bytes('engine'),
            value_bytes(payload), None, None))
        for check in (None, False, [], {}):
            with self.subTest(check=check):
                payload = {'id': check, 'origin': None}
                self.assertEqual(project_metadata(payload, capture_source=b'unused'),
                    RowMetadata(value_bytes(check), value_bytes(None), value_bytes(payload), None, None))

    def test_present_malformed_objects_are_complete_not_absent(self):
        for present in ({}, [], False, ''):
            with self.subTest(present=present):
                payload = {'id': 'check', 'origin': 'candidate',
                    'evaluatorBoundary': present, 'executedVerifierSet': present}
                result = project_metadata(payload, capture_source=b'unused')
                self.assertEqual(result.execution, value_bytes({'engineInvocation': None, 'evaluatorBoundary': present}))
                self.assertEqual(result.verifier, value_bytes(present))
                self.assertEqual(result.payload, value_bytes(payload))

    def test_unsupported_payload_bytes_are_explicit_refusals(self):
        # Preserve the original payload-byte cases as refusals. Native byte
        # identities are a different domain, covered unchanged above.
        payloads = (
            {'id': b'\0bytes', 'origin': None},
            {'id': 'check', 'origin': 'candidate',
             'evaluatorBoundary': b'', 'executedVerifierSet': b''},
        )
        for payload in payloads:
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(TerminalRefused, 'CAPTURE_VALUE_UNSUPPORTED'):
                    project_metadata(payload, capture_source=b'unused')

    def test_missing_return_encoding_uses_retained_start_and_capture_source(self):
        started = {'checkId': 'owned-check', 'invocationId': 'owned-invocation'}
        payload = {'id': 'owned-check', 'origin': 'engine-observer',
            'engineInvocationObservation': started, 'kind': 'invocation-return-not-retained'}
        result = project_metadata(payload, capture_source=b'whole-capture-source',
            invocation=('owned-invocation', started, None))
        self.assertEqual(result, RowMetadata(b'owned-check', b'whole-capture-source',
            value_bytes(payload), b'owned-invocation', None))
        # A completed invocation remains the normal writer encoding even when
        # the payload contains a similarly named diagnostic kind.
        regular = project_metadata(payload, capture_source=b'whole-capture-source',
            invocation=('owned-invocation', started, {'result': payload}))
        self.assertEqual(regular.source, value_bytes('engine-observer'))
        self.assertEqual(regular.execution, value_bytes({'engineInvocation': started, 'evaluatorBoundary': None}))
