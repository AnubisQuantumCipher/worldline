"""Unexecuted ordinary controls of the actual new native finalization API.

Owned typed inputs do not establish protected producer/custody truth. The
separate real Finalizer/journal controls must exercise the actual path.
"""
import ctypes as C
from dataclasses import asdict, replace
from pathlib import Path
import os
import unittest
from worldline.core import Core, HASH_BYTES
from worldline.finalization_kernel import FinalizationKernel, Result
from worldline.finalization_values import (StartValue, InputValue, UnsealedResult,
    CaptureValue, ComponentsValue, SealValue)
from worldline.completion_kernel import KernelRefused, Span
from worldline.evaluation_wire import record
from worldline.evaluation_terminal import value_bytes, bytes_value
from worldline.canonical import canonical_bytes
from worldline.environment import evidence_manifest, EnvironmentCapture
from worldline.finalize import ENGINE_DECLARATIONS


class FinalizationNativeControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.library = Path(os.environ['WORLDLINE_CORE_LIB'])
        cls.core = Core(cls.library)
        cls.kernel = FinalizationKernel(cls.library)

    def values(self, required=True):
        zero = bytes(HASH_BYTES)
        self.declaration = value_bytes(asdict(ENGINE_DECLARATIONS['protected-paths']))
        start = StartValue(b'store\0whole', b'world\0whole', b'run\0whole', b'',
            b'requirement\0whole', b'full-policy', b'full-verifier-plan', b'full-base-context',
            zero, zero, zero,
            ((b'protected-paths', self.declaration),) if required else (),
            'Required_Checks' if required else 'Explicit_Empty')
        # Legitimate agent effects may change config/repository after Start.
        config = self.core.hash_bytes(b'actual-final-config')
        repository = self.core.hash_bytes(b'actual-final-repository')
        inputs = InputValue(start, b'full-root', b'full-manifests', zero, config, repository)
        return start, inputs

    def row(self, start, check, status='PASS'):
        payload = {'id': check, 'origin': 'engine', 'format': 'engine',
            'status': status, 'required': True}
        wire = record(payload, ENGINE_DECLARATIONS['protected-paths'])
        return UnsealedResult(start, check.encode(), value_bytes('engine'), None,
            None, 'Completed', status, value_bytes(payload), self.declaration, wire)

    def capture(self, required=True, status='PASS', *, final=True):
        start, inputs = self.values(required)
        rows = ((self.row(start, 'protected-paths', status),) if required else ())
        if final: rows += (self.row(start, 'evaluation-complete'),)
        return CaptureValue(start, inputs, inputs.root, inputs.manifests,
            value_bytes({'subject': start.subject.decode('utf8'), 'full': [None, True, '\u0000', '\u2028', 'é']}), b'actual-finalization-source', rows,
            (b'evaluation-complete', self.declaration))

    def artifacts(self, capture, *, metrics=None):
        evidence_value = evidence_manifest([bytes_value(row.payload) for row in capture.results],
            self.core, validation=bytes_value(capture.context), metrics=metrics)
        evidence = canonical_bytes(evidence_value)
        environment_value = EnvironmentCapture(self.core).capture(processes=(), toolchains=(),
            dependency_roots=(), agent={}, evidence=evidence_value, environment={}, workspace={})
        environment = canonical_bytes(environment_value.value)
        return evidence, environment

    def with_artifacts(self, capture, evidence, environment):
        import json
        # Original evidence hashing excludes exactly its top-level root.
        value = json.loads(evidence)
        del value['root']
        evidence_root = self.core.hash_bytes(b'worldline-evidence-v1' + canonical_bytes(value))
        env_root = self.core.hash_bytes(b'worldline-environment-v1' + environment)
        inputs = capture.input
        identity = self.core.world_id(dict(parent=capture.start.parent,
            filesystem=inputs.filesystem, config=inputs.config,
            repository=inputs.repository, environment=env_root, evidence=evidence_root))
        return SealValue(capture, ('sha256:' + identity.hex()).encode(),
            ComponentsValue(env_root, evidence_root), evidence, environment)

    def sealed(self, capture):
        return self.with_artifacts(capture, *self.artifacts(capture))

    def test_start_and_input_actual_components_are_separate(self):
        start, inputs = self.values()
        self.kernel.validate_start(start)
        self.kernel.validate_input(start, inputs)
        self.assertNotEqual(inputs.config, start.config)
        self.assertNotEqual(inputs.repository, start.repository)
        with self.assertRaises(KernelRefused):
            self.kernel.validate_input(start, replace(inputs, start=replace(start, run=b'other-run')))

    def test_epoch_zero_all_padding_and_true_optional_requirement(self):
        start, _inputs = self.values()
        for sequence in (b'', b'\0', b'\0\0\0'):
            for requirement in (None, b'', b'\0'):
                with self.subTest(sequence=sequence, requirement=requirement):
                    self.kernel.validate_start(replace(start, epoch=sequence, requirement=requirement))
        with self.assertRaises(KernelRefused): self.kernel.validate_start(replace(start, epoch=b'\1'))

    def test_completed_pass_and_actual_final_content(self):
        value = self.sealed(self.capture())
        sealed = self.kernel.seal(value)
        self.assertEqual((sealed.classification.state, sealed.classification.outcome,
            sealed.classification.promotion, sealed.finalization_state),
            ('Completed', 'PASS', True, 'COMPLETED'))
        self.assertEqual(value.content, ('sha256:' + sealed.identity.hex()).encode())
        with self.assertRaises(KernelRefused): self.kernel.seal(replace(value, content=b'not-the-final-content'))

    def test_empty_declared_roster_and_missing_final_are_distinct(self):
        self.assertTrue(self.kernel.seal(self.sealed(self.capture(False))).classification.promotion)
        sealed = self.kernel.seal(self.sealed(self.capture(False, final=False)))
        self.assertEqual((sealed.finalization_state, sealed.finalization_outcome), ('ERROR', None))
        self.assertFalse(sealed.classification.promotion)

    def test_required_fail_retained_even_with_later_pass_and_unadmitted_sibling(self):
        capture = self.capture(status='FAIL')
        rows = (capture.results[0], self.row(capture.start, 'protected-paths'),
            replace(self.row(capture.start, 'unrelated'), state='Incomplete_Unknown', outcome=None),
            capture.results[-1])
        sealed = self.kernel.seal(self.sealed(replace(capture, results=rows)))
        self.assertEqual((sealed.finalization_state, sealed.finalization_outcome,
                          sealed.classification.promotion), ('COMPLETED', 'FAIL', False))

    def test_required_fail_is_not_erased_by_malformed_raw_sibling(self):
        from worldline.evaluation_wire import OwnedRecord
        capture = self.capture(status='FAIL')
        sibling = self.row(capture.start, 'unrelated')
        raw = sibling.wire.native()
        raw.observations[0] = 255
        sibling = replace(sibling, wire=OwnedRecord(bytes(raw), 0))
        sealed = self.kernel.seal(self.sealed(replace(capture,
            results=(capture.results[0], sibling, capture.results[-1]))))
        self.assertEqual((sealed.finalization_state, sealed.finalization_outcome,
            sealed.classification.promotion), ('COMPLETED', 'FAIL', False))

    def test_changed_full_post_manifest_refuses(self):
        capture = self.capture()
        with self.assertRaises(KernelRefused):
            self.kernel.seal(self.sealed(replace(capture, post_manifests=b'other-full-manifests')))

    def test_changed_full_recapture_retains_error_without_d15(self):
        capture = replace(self.capture(final=False), post_manifests=b'changed-full-manifests')
        self.assertEqual(self.kernel.classify_capture(capture).state, 'Incomplete_Unknown')
        sealed = self.kernel.seal(self.sealed(capture))
        self.assertEqual((sealed.finalization_state, sealed.finalization_outcome), ('ERROR', None))
        self.assertFalse(sealed.classification.promotion)

    def test_same_arena_projection_retains_every_original_byte_and_no_intent(self):
        value = self.sealed(self.capture())
        prepared = self.kernel.prepare_finalization(value)
        self.assertIs(prepared.seal_value, value)
        self.assertEqual(prepared.request.data, prepared.native_request.data)
        self.assertEqual(prepared.request.journal_count, 0)
        self.assertIsNone(prepared.request.journal)
        self.assertEqual(prepared.request.data_length, prepared.native_request.data_length)
        for native, projected in zip(prepared.native_owners[1], prepared.owned[2]):
            for field in ('check_id', 'source_id', 'payload', 'execution', 'verifier', 'declared'):
                self.assertEqual(bytes(getattr(native, field)), bytes(getattr(projected, field)))
        self.assertEqual(prepared.capture.source, value.capture.source)

    def test_owned_malformed_span_refusal_does_not_publish_partial_output(self):
        start, _inputs = self.values()
        request, owners = self.kernel._pack(0, start)
        request.start.subject = Span(0, 0)
        result = Result()
        before = bytes(result)
        self.assertEqual(self.kernel.call(C.byref(request), C.byref(result)), 255)
        self.assertEqual(bytes(result), before)

    def test_genuine_artifact_whole_values_and_nested_root_are_retained(self):
        capture = self.capture()
        metrics = {'root': {'root': 'root,\\" quoted'}, 'items': [None, False, 'é', '\u2028',
            '\u0000\b\t\n\f\r', 123456789012345678901234567890123456789012345678901234567890]}
        value = self.with_artifacts(capture, *self.artifacts(capture, metrics=metrics))
        self.assertTrue(self.kernel.seal(value).classification.promotion)

    def test_artifact_payload_integer_and_object_order_correspondence(self):
        capture = self.capture()
        row = capture.results[0]
        original = bytes_value(row.payload)
        # Deliberately use insertion order different from canonical key order.
        payload = {'z': -12345678901234567890123456789012345678901234567890,
            'a': [0, None, '\u0001', '😀'], **original}
        capture = replace(capture, results=(replace(row, payload=value_bytes(payload)), *capture.results[1:]))
        self.assertTrue(self.kernel.seal(self.sealed(capture)).classification.promotion)

    def test_checks_order_and_validation_context_are_not_hash_only(self):
        import json
        capture = self.capture()
        evidence, environment = self.artifacts(capture)
        for changed in (replace(capture, results=tuple(reversed(capture.results))),
                        replace(capture, context=value_bytes({'other': 'context'}))):
            with self.subTest(changed=changed):
                with self.assertRaises(KernelRefused):
                    self.kernel.seal(self.with_artifacts(changed, evidence, environment))
        included = json.loads(environment)
        included['evidence']['metrics']['changed'] = True
        with self.assertRaises(KernelRefused):
            self.kernel.seal(self.with_artifacts(capture, evidence, canonical_bytes(included)))

    def test_artifact_noncanonical_duplicate_and_mismatched_roots_refuse(self):
        capture = self.capture()
        evidence, environment = self.artifacts(capture)
        ordinary = self.with_artifacts(capture, evidence, environment)
        # Each malformed whole artifact remains owned, readable bytes. These
        # are parser correctness cases, not arbitrary memory representations.
        for damaged in (b' ' + evidence, evidence + b' ',
                        evidence.replace(b'{', b'{"root":"decoy",', 1),
                        evidence.replace(b'"schemaVersion":1', b'"schemaVersion":1.0'),
                        evidence.replace(b'"schemaVersion":1', b'"schemaVersion":01')):
            with self.subTest(damaged=damaged):
                with self.assertRaises(KernelRefused):
                    self.kernel.seal(replace(ordinary, evidence=damaged))
        root = bytes_value(capture.context)
        self.assertIsInstance(root, dict)
        with self.assertRaises(KernelRefused):
            self.kernel.seal(replace(ordinary, environment=environment + b' '))
        with self.assertRaises(KernelRefused):
            self.kernel.seal(replace(ordinary,
                components=replace(ordinary.components, evidence=bytes(HASH_BYTES))))

    def joined(self, prepared, request, agent, **changes):
        from worldline.evaluation_context import attach, CONTEXT_FIELDS, ROW_FIELDS, RowMetadata
        # TEST_ONLY paired context inputs, distinct from the real Finalizer
        # producer. Actual source tests below check all native join fields.
        expected = {name: value_bytes({'field': name}) for name in CONTEXT_FIELDS}
        expected['returned_context'] = prepared.capture.context
        expected['source_id'] = prepared.capture.source
        expected['examined_root'] = prepared.seal_value.capture.input.root
        pairs = [({name: None for name in ROW_FIELDS}, {name: None for name in ROW_FIELDS})
                 for _ in prepared.typed_rows]
        start = prepared.seal_value.capture.start
        args = dict(expected_binding=prepared.capture.bound,
            expected_current=(start.epoch, start.run), prepared_current=(start.epoch, start.run),
            expected=expected, observed=dict(expected), row_pairs=pairs,
            required=start.required, policy=2 if start.required else 1,
            projection=self.core._raw_collapse_request(request), agent=agent,
            row_metadata=tuple(RowMetadata(row.check, row.source, row.payload,
                row.execution, row.verifier) for row in prepared.typed_rows))
        args.update(changes)
        return attach(self.core, prepared, **args)

    def collapse_values(self):
        from test_raw_evaluation_default import RawDependencyControls
        original = RawDependencyControls.checkpoint()
        request = replace(original, mode='CANDIDATE_EVALUATION',
            evaluated_requirement=original.current_requirement,
            executed_verifiers=original.declared_verifiers,
            expected_checkpoint=None, witnessed_checkpoint=None)
        agent = record({'id': 'agent', 'origin': 'agent', 'format': 'exit', 'status': 'PASS',
            'exitCode': 0, 'supervision': {'kind': 'SUPERVISED'},
            'resources': {'ceilingFired': False}}, ENGINE_DECLARATIONS['agent'])
        return request, agent

    def test_additive_finalization_collapse_requires_full_context_and_metadata(self):
        request, agent = self.collapse_values()
        value = self.sealed(self.capture())
        prepared = self.kernel.prepare_finalization(value)
        self.joined(prepared, request, agent)
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=None, agent=agent), 'AUTHORIZED')
        prepared.metadata_context = None
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=None, agent=agent), 'INVALID_REQUEST')

    def test_native_collapse_rechecks_original_seal_and_full_final_binding(self):
        request, agent = self.collapse_values()
        prepared = self.kernel.prepare_finalization(self.sealed(self.capture()))
        self.joined(prepared, request, agent,
            expected_binding=replace(prepared.capture.bound, content=b'other-final-content'))
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=None, agent=agent), 'INVALID_REQUEST')
        prepared = self.kernel.prepare_finalization(self.sealed(self.capture()))
        self.joined(prepared, request, agent)
        # A well-owned changed actual component cannot keep the old Seal ID.
        prepared.native_request.inputs.config[0] ^= 1
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=None, agent=agent), 'INVALID_REQUEST')

    def test_additive_finalization_checkpoint_keeps_ignored_data_semantics(self):
        from test_raw_evaluation_default import RawDependencyControls
        request = RawDependencyControls.checkpoint()
        prepared = self.kernel.prepare_finalization(self.sealed(self.capture()))
        prepared.native_request.operation = 0
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=object(), agent=object()),
            self.core.collapse_decide(request))
