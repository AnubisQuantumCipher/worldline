"""UNRUN original-oracle, native and ownership controls for cast transport.

Every original control remains required. This module does not authorize a
workload retry, certify a peak bound, or establish protected producer custody.
"""
import ast
from collections import Counter
import ctypes as C
from dataclasses import replace
import gc
import hashlib
from pathlib import Path
import sys
import unittest
import weakref

from worldline import finalization_kernel as current
from worldline.completion_kernel import KernelRefused
import test_finalization_kernel as original_controls


ORACLE_SHA256 = 'fe91b945afbe61d82d2e60ba6c968092a0b4413117b0011a279dad23e0833082'
_audit_target = None
_hook_installed = False


def audit_hook(event, arguments):
    if _audit_target is not None and event.startswith('ctypes.'):
        _audit_target(event, arguments)


def observe_audit(callback, operation):
    global _audit_target, _hook_installed
    if not _hook_installed:
        sys.addaudithook(audit_hook)
        _hook_installed = True
    if _audit_target is not None:
        raise AssertionError('audit observer already active')
    _audit_target = callback
    try:
        return operation()
    finally:
        _audit_target = None


def original_pack():
    path = Path(__file__).with_name('oracle_finalization_kernel_cast_lifetime.py')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORACLE_SHA256:
        raise AssertionError('complete original marshaller identity differs')
    module = ast.parse(raw, filename=str(path))
    owner, = [node for node in module.body
              if isinstance(node, ast.ClassDef) and node.name == 'FinalizationKernel']
    method, = [node for node in owner.body
               if isinstance(node, ast.FunctionDef) and node.name == '_pack']
    namespace = dict(vars(current))
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 str(path), 'exec'), namespace)
    return namespace['_pack']


def fields(value):
    if isinstance(value, C.Array):
        return bytes(value)
    if isinstance(value, C.Structure):
        return tuple((name, fields(getattr(value, name)))
                     for name, _kind in value._fields_)
    return value


def snapshot(request, owners):
    for name, owner in zip(('data', 'rows', 'required'), owners):
        if getattr(request, name) != C.addressof(owner):
            raise AssertionError('pointer differs from complete live owner')
    descriptor = tuple((name, fields(getattr(request, name)))
                       for name, _kind in request._fields_
                       if name not in ('data', 'rows', 'required'))
    return descriptor, tuple(bytes(owner) for owner in owners)


class FinalizationCastLifetimeControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        original_controls.FinalizationNativeControls.setUpClass()
        cls.fixture = original_controls.FinalizationNativeControls()
        cls.kernel = cls.fixture.kernel
        cls.original = staticmethod(original_pack())

    def pairs(self, capture):
        start, inputs = capture.start, capture.input
        seal = self.fixture.sealed(capture)
        return ((0, start, None, None, None),
                (1, start, inputs, None, None),
                (2, start, inputs, capture, None),
                (3, start, inputs, capture, seal))

    def test_whole_original_arena_spans_rows_plans_all_operations(self):
        for required in (False, True):
            for args in self.pairs(self.fixture.capture(required)):
                with self.subTest(required=required, operation=args[0]):
                    old, old_owners = self.original(self.kernel, *args)
                    new, new_owners = self.kernel._pack(*args)
                    self.assertEqual(snapshot(new, new_owners), snapshot(old, old_owners))
                    self.assertIs(new._transport_owners, new_owners)

    def test_actual_native_outputs_and_full_input_snapshots(self):
        for status in ('PASS', 'FAIL'):
            for args in self.pairs(self.fixture.capture(status=status)):
                with self.subTest(status=status, operation=args[0]):
                    old, old_owners = self.original(self.kernel, *args)
                    new, new_owners = self.kernel._pack(*args)
                    before_old, before_new = snapshot(old, old_owners), snapshot(new, new_owners)
                    old_result, new_result = current.Result(), current.Result()
                    old_code = self.kernel.call(C.byref(old), C.byref(old_result))
                    new_code = self.kernel.call(C.byref(new), C.byref(new_result))
                    self.assertEqual((new_code, bytes(new_result)), (old_code, bytes(old_result)))
                    self.assertEqual(snapshot(old, old_owners), before_old)
                    self.assertEqual(snapshot(new, new_owners), before_new)

    def test_request_alone_retains_complete_owners_through_native_call(self):
        args = self.pairs(self.fixture.capture())[-1]
        request, owners = self.kernel._pack(*args)
        complete = snapshot(request, owners)
        references = tuple(weakref.ref(owner) for owner in owners)
        del args, owners
        gc.collect()
        self.assertTrue(all(reference() is not None for reference in references))
        self.assertEqual(snapshot(request, request._transport_owners), complete)
        output = current.Result()
        self.assertEqual(self.kernel.call(C.byref(request), C.byref(output)), 0)
        self.assertEqual(snapshot(request, request._transport_owners), complete)

    def test_completed_temporary_owners_release_without_cyclic_collection(self):
        start, _inputs = self.fixture.values()
        enabled = gc.isenabled()
        gc.disable()
        try:
            request, owners = self.kernel._pack(0, start)
            references = tuple(weakref.ref(owner) for owner in owners)
            output = current.Result()
            self.assertEqual(self.kernel.call(C.byref(request), C.byref(output)), 0)
            del request, owners
            self.assertTrue(all(reference() is None for reference in references))
        finally:
            if enabled:
                gc.enable()

    def test_equal_fields_remain_distinct_mutable_spans_and_packs(self):
        start, _inputs = self.fixture.values()
        start = replace(start, store_id=b'equal', subject=b'equal', run=b'equal')
        old, old_owners = self.original(self.kernel, 0, start)
        new, new_owners = self.kernel._pack(0, start)
        other, other_owners = self.kernel._pack(0, start)
        other_before = snapshot(other, other_owners)
        self.assertNotEqual(new.start.store_id.first, new.start.subject.first)
        old_owners[0][old.start.store_id.first - 1] ^= 1
        new_owners[0][new.start.store_id.first - 1] ^= 1
        self.assertEqual(snapshot(new, new_owners), snapshot(old, old_owners))
        self.assertEqual(snapshot(other, other_owners), other_before)

    def test_original_malformed_span_preserves_output_bytes(self):
        start, _inputs = self.fixture.values()
        for pack in (self.original, current.FinalizationKernel._pack):
            request, owners = pack(self.kernel, 0, start)
            request.start.subject.first = 0
            result = current.Result()
            before = bytes(result)
            self.assertEqual(self.kernel.call(C.byref(request), C.byref(result)), 255)
            self.assertEqual(bytes(result), before)

    def test_invalid_original_domains_keep_exact_named_refusals(self):
        start, _inputs = self.fixture.values()
        damaged = (replace(start, store_id=bytearray(start.store_id)),
                   replace(start, requirement=bytearray(b'requirement')),
                   replace(start, required=[(b'name', b'declaration')]),
                   replace(start, required=((b'name', bytearray(b'declaration')),)),
                   replace(start, parent=b'wrong component extent'))
        for value in damaged:
            outcomes = []
            for pack in (self.original, current.FinalizationKernel._pack):
                with self.assertRaises(KernelRefused) as error:
                    pack(self.kernel, 0, value)
                outcomes.append((type(error.exception), str(error.exception)))
            self.assertEqual(outcomes[0], outcomes[1])

    def test_required_audit_counts_copy_sizes_and_explicit_cast_transport(self):
        args = self.pairs(self.fixture.capture())[-1]
        observations = []
        for pack in (self.original, current.FinalizationKernel._pack):
            events, copies, casts = [], [], []
            def callback(event, arguments):
                events.append(event)
                if event == 'ctypes.cdata/buffer':
                    # Physical buffer addresses belong to separate allocations.
                    copies.append(tuple(arguments[1:]))
                if event == 'ctypes.call_function':
                    casts.append((arguments[0], len(arguments[1]),
                                  tuple(type(value).__name__ for value in arguments[1])))
            request, owners = observe_audit(callback, lambda: pack(self.kernel, *args))
            observations.append((events, copies, casts, snapshot(request, owners)))
        old, new = observations
        self.assertEqual(new[0], old[0])
        self.assertEqual(Counter(new[0]), Counter(old[0]))
        self.assertEqual(new[1], old[1])
        self.assertEqual(new[3], old[3])
        self.assertEqual([(address, count) for address, count, _types in new[2]],
                         [(address, count) for address, count, _types in old[2]])
        self.assertTrue(new[2], 'actual cast audit events were not observed')
        self.assertTrue(all(types[:2] == ('CArgObject', 'CArgObject')
                            for _address, _count, types in new[2]))
        self.assertNotEqual([types for _address, _count, types in old[2]],
                            [types for _address, _count, types in new[2]])

    def test_audit_primary_refusal_and_finite_reentry_are_retained(self):
        class AuditRefusal(Exception):
            pass
        start, _inputs = self.fixture.values()
        outcomes = []
        for pack in (self.original, current.FinalizationKernel._pack):
            def refusing(event, arguments):
                if event == 'ctypes.cdata/buffer':
                    raise AuditRefusal('original buffer event refused')
            with self.assertRaises(AuditRefusal) as error:
                observe_audit(refusing, lambda: pack(self.kernel, 0, start))
            outcomes.append((type(error.exception), str(error.exception)))
        self.assertEqual(outcomes[0], outcomes[1])
        snapshots = []
        for pack in (self.original, current.FinalizationKernel._pack):
            reached = False
            def reenter(event, arguments):
                nonlocal reached
                if event == 'ctypes.cdata/buffer' and not reached:
                    reached = True
                    inner, owners = pack(self.kernel, 0, start)
                    self.assertGreater(inner.data_length, 0)
            request, owners = observe_audit(reenter, lambda: pack(self.kernel, 0, start))
            self.assertTrue(reached)
            snapshots.append(snapshot(request, owners))
        self.assertEqual(snapshots[0], snapshots[1])


if __name__ == '__main__':
    unittest.main()
