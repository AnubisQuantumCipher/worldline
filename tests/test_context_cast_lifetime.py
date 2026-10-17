"""UNRUN complete context/metadata bytes, native join and lifetime controls."""
import ast
import ctypes as C
from dataclasses import replace
import gc
import hashlib
from pathlib import Path
import unittest
import weakref
from unittest.mock import patch

from worldline import evaluation_context as context
from worldline import finalization_kernel as kernel_module
from worldline.evaluation_terminal import value_bytes
import test_finalization_kernel as original_controls
from test_finalization_cast_lifetime import fields, snapshot, observe_audit


CONTEXT_ORACLE_SHA256 = 'b8b0d1365504483cf7ac31a7ef54aac63f45ed9c6a96a1ab819a344caf409b05'
KERNEL_ORACLE_SHA256 = 'fe91b945afbe61d82d2e60ba6c968092a0b4413117b0011a279dad23e0833082'


def methods(path, expected, globals_source, owner=None, names=()):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise AssertionError('complete original oracle identity differs')
    nodes = ast.parse(raw, filename=str(path)).body
    if owner is not None:
        cls, = [node for node in nodes if isinstance(node, ast.ClassDef) and node.name == owner]
        nodes = cls.body
    selected = [node for node in nodes if isinstance(node, ast.FunctionDef) and node.name in names]
    if {node.name for node in selected} != set(names):
        raise AssertionError('complete original function selection differs')
    namespace = dict(vars(globals_source))
    exec(compile(ast.fix_missing_locations(ast.Module(body=selected, type_ignores=[])),
                 str(path), 'exec'), namespace)
    return {name: namespace[name] for name in names}


def descriptor_snapshot(value, pointer_fields):
    return tuple((name, fields(getattr(value, name)))
                 for name, _kind in value._fields_ if name not in pointer_fields)


# Every c_void_p field of completion_kernel.Request. 'captured' and 'retained'
# are by-value Capture descriptors and are compared field by field below.
PROJECTION_POINTERS = ('data', 'journal', 'captured_results', 'retained_results',
                       'history', 'required')


def projection_snapshot(prepared):
    # Raw addresses of two distinct allocations never compare equal; compare the
    # complete owned bytes behind every pointer and require that each non-null
    # pointer names its retained owner and each absent one is null.
    p = prepared.request
    owners = {'data': prepared.owned[0], 'captured_results': prepared.owned[2],
              'required': prepared.owned[5]}
    if prepared.owned[0] is not prepared.native_owners[0]:
        raise AssertionError('projection data is not the native arena owner')
    for name in PROJECTION_POINTERS:
        owner = owners.get(name)
        if getattr(p, name) != (None if owner is None else C.addressof(owner)):
            raise AssertionError('projection pointer is not owned: ' + name)
    return (descriptor_snapshot(p, set(PROJECTION_POINTERS)),
            tuple((name, bytes(owners[name])) for name in PROJECTION_POINTERS if name in owners))


def complete(prepared):
    native = snapshot(prepared.native_request, prepared.native_owners)
    projection = projection_snapshot(prepared)
    x = prepared.context
    if x.data != C.addressof(prepared.context_owners[0]):
        raise AssertionError('context data is not owned')
    if x.rows != C.addressof(prepared.context_owners[1]):
        raise AssertionError('context rows are not owned')
    if x.required != C.addressof(prepared.context_owners[2]):
        raise AssertionError('context declarations are not owned')
    joined = (descriptor_snapshot(x, {'data', 'rows', 'required'}),
              tuple(bytes(owner) for owner in prepared.context_owners[:3]))
    m = prepared.metadata_context
    if m.base != C.addressof(x) or m.data != C.addressof(prepared.metadata_owners[0]) or m.rows != C.addressof(prepared.metadata_owners[1]):
        raise AssertionError('metadata pointers are not owned')
    metadata = (descriptor_snapshot(m, {'base', 'data', 'rows'}),
                tuple(bytes(owner) for owner in prepared.metadata_owners[:2]))
    return native, projection, joined, metadata


class ContextCastLifetimeControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        original_controls.FinalizationNativeControls.setUpClass()
        cls.fixture = original_controls.FinalizationNativeControls()
        cls.kernel = cls.fixture.kernel
        here = Path(__file__).parent
        cls.old_kernel = methods(here / 'oracle_finalization_kernel_cast_lifetime.py',
            KERNEL_ORACLE_SHA256, kernel_module, 'FinalizationKernel',
            ('_pack', 'prepare_finalization'))
        cls.old_context = methods(here / 'oracle_evaluation_context_cast_lifetime.py',
            CONTEXT_ORACLE_SHA256, context, names=('metadata_descriptor', 'attach'))

    def make(self, value, original=False):
        if original:
            with patch.object(kernel_module.FinalizationKernel, '_pack', self.old_kernel['_pack']), \
                 patch.object(kernel_module.FinalizationKernel, 'prepare_finalization', self.old_kernel['prepare_finalization']):
                return self.kernel.prepare_finalization(value)
        return self.kernel.prepare_finalization(value)

    def join(self, prepared, request, agent, original=False, **changes):
        if original:
            with patch.object(context, 'attach', self.old_context['attach']):
                return self.fixture.joined(prepared, request, agent, **changes)
        return self.fixture.joined(prepared, request, agent, **changes)

    def test_original_whole_projection_context_metadata_and_native_conjunction(self):
        for status in ('PASS', 'FAIL'):
            value = self.fixture.sealed(self.fixture.capture(status=status))
            request, agent = self.fixture.collapse_values()
            old, new = self.make(value, True), self.make(value)
            self.join(old, request, agent, True)
            self.join(new, request, agent)
            self.assertEqual(complete(new), complete(old))
            old_result = self.fixture.core.collapse_decide_with_evaluation(request,
                primary=old, staged=None, agent=agent)
            new_result = self.fixture.core.collapse_decide_with_evaluation(request,
                primary=new, staged=None, agent=agent)
            self.assertEqual(new_result, old_result)
            self.assertEqual(complete(new), complete(old))

    def test_original_conjunct_mutations_refuse_with_unchanged_results(self):
        value = self.fixture.sealed(self.fixture.capture())
        request, agent = self.fixture.collapse_values()
        old, new = self.make(value, True), self.make(value)
        for prepared, original in ((old, True), (new, False)):
            self.join(prepared, request, agent, original,
                expected_binding=replace(prepared.capture.bound, content=b'other-final-content'))
        self.assertEqual(complete(new), complete(old))
        self.assertEqual(self.fixture.core.collapse_decide_with_evaluation(request,
            primary=new, staged=None, agent=agent), 'INVALID_REQUEST')
        self.assertEqual(self.fixture.core.collapse_decide_with_evaluation(request,
            primary=old, staged=None, agent=agent), 'INVALID_REQUEST')

    def test_context_copy_audit_count_order_size_and_offsets_match_original(self):
        value = self.fixture.sealed(self.fixture.capture())
        request, agent = self.fixture.collapse_values()
        # ctypes resolves each CDLL export once per process (a 'ctypes.dlsym'
        # audit event on first attribute lookup, then cached). Whichever join runs
        # first would carry that process-global event. Perform one unobserved join
        # on each path first so both observations below are in the same state.
        for original in (True, False):
            self.join(self.make(value, original), request, agent, original)
        observations = []
        for original in (True, False):
            prepared = self.make(value, original)
            events, copies = [], []
            def callback(event, arguments):
                events.append(event)
                if event == 'ctypes.cdata/buffer':
                    copies.append(tuple(arguments[1:]))
            observe_audit(callback, lambda: self.join(prepared, request, agent, original))
            observations.append((events, copies, complete(prepared)))
        self.assertEqual(observations[0], observations[1])

    def test_descriptors_alone_keep_complete_original_transport_owners(self):
        value = self.fixture.sealed(self.fixture.capture())
        request, agent = self.fixture.collapse_values()
        prepared = self.make(value)
        self.join(prepared, request, agent)
        before = complete(prepared)
        projection, descriptor, metadata = prepared.request, prepared.context, prepared.metadata_context
        references = tuple(weakref.ref(owner) for owner in (*prepared.native_owners,
            prepared.owned[2], prepared.owned[5], *prepared.context_owners[:3], *prepared.metadata_owners[:2]))
        del prepared, value
        gc.collect()
        self.assertTrue(all(reference() is not None for reference in references))
        self.assertEqual(projection.data, C.addressof(projection._transport_owners[0]))
        self.assertEqual(tuple(bytes(owner) for owner in descriptor._transport_owners), before[2][1])
        self.assertEqual(tuple(bytes(owner) for owner in metadata._transport_owners[:2]), before[3][1])
        self.assertIs(metadata._transport_owners[2], descriptor)

    def test_discarded_full_prepared_graph_releases_without_cyclic_collection(self):
        value = self.fixture.sealed(self.fixture.capture())
        request, agent = self.fixture.collapse_values()
        enabled = gc.isenabled()
        gc.disable()
        try:
            prepared = self.make(value)
            self.join(prepared, request, agent)
            references = tuple(weakref.ref(owner) for owner in (*prepared.native_owners,
                prepared.owned[2], prepared.owned[5], *prepared.context_owners[:3], *prepared.metadata_owners[:2]))
            self.assertEqual(self.fixture.core.collapse_decide_with_evaluation(request,
                primary=prepared, staged=None, agent=agent), 'AUTHORIZED')
            del prepared
            self.assertTrue(all(reference() is None for reference in references))
        finally:
            if enabled:
                gc.enable()


if __name__ == '__main__':
    unittest.main()
