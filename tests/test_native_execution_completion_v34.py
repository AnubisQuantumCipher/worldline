"""Actual linked-library complete native boundary controls; source only, UNRUN.

No replacement fixture, mock kernel, recorded status or skip is an acceptance
source. Original fixture suites remain enrolled unchanged alongside this file.
"""
import ctypes as C
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from test_resource_child_execution_v1 import full_child
from worldline import resource_child_execution as J
from worldline import resource_scoped_run_ledger as S
from worldline import resource_actor_execution as E
from worldline import resource_actor_admission as K


def arguments(owned, output):
    actor, data, length, rosters, authority, ad, alen, named, cross, child, extra = owned
    result = [C.byref(actor), C.sizeof(actor), data, length]
    for _name, array, count in rosters:
        result.extend((array, count))
    result.extend((C.byref(authority), C.sizeof(authority), ad, alen))
    for _name, array, count in named:
        result.extend((array, count))
    result.extend((C.byref(cross), C.sizeof(cross), C.byref(child), C.sizeof(child)))
    for _name, array, count in extra:
        result.extend((array, count))
    result.extend((C.byref(output), C.sizeof(output)))
    return result


def malformed_presence(value):
    if isinstance(value, C.Array):
        for item in value:
            if malformed_presence(item):
                return True
    elif isinstance(value, C.Structure):
        for name, _kind in value._fields_:
            if name in ('present', 'negative'):
                setattr(value, name, 255)
                return True
            if malformed_presence(getattr(value, name)):
                return True
    return False


class NativeExecutionCompletionControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = SimpleNamespace(_lib=C.CDLL(os.environ.get('WORLDLINE_CORE_LIB', str(Path(__file__).resolve().parents[1] / 'lib/libworldline_core.so'))))
        cls.kernel = J.ResourceChildExecutionKernel(cls.core)

    def owned(self, mode):
        values = full_child(action='init' if mode == 'ROOT_CONTROLLER_ADMISSION' else 'fork')
        if mode == 'ROOT_CONTROLLER_ADMISSION':
            p, _actor, _caps, _groups, _proc, controller, _task, _tasks, _processes, _namespaces, cross, authority = values
            return self.kernel.prepare(mode, p, None, (), (), (), controller, None, (), (), (), cross, authority)
        return self.kernel.prepare(mode, *values)

    def test_all_original_version_and_field_layout_initializers_link(self):
        S.ScopedRunLedgerKernel(self.core)
        K.ActorAdmissionKernel(self.core)
        E.ActorExecutionKernel(self.core)
        J.ResourceChildExecutionKernel(self.core)

    def test_root_and_child_full_native_literals_not_archived_status(self):
        for mode, literal in (('ROOT_CONTROLLER_ADMISSION', 0), ('CHILD_ADMISSION', 1)):
            with self.subTest(mode=mode):
                owned = self.owned(mode)
                out = S.L.RawResult()
                self.assertEqual(self.kernel.call(*arguments(owned, out)), 0)
                self.assertEqual(out.status, literal)

    def test_every_consulted_child_roster_rejects_malformed_complete_row(self):
        names = [name for name, _array, _count in self.owned('CHILD_ADMISSION')[3]]
        names += [name for name, _array, _count in self.owned('CHILD_ADMISSION')[7]]
        names += [name for name, _array, _count in self.owned('CHILD_ADMISSION')[10]]
        for name in names:
            with self.subTest(roster=name):
                owned = self.owned('CHILD_ADMISSION')
                rosters = [*owned[3], *owned[7], *owned[10]]
                selected = next(array for row_name, array, _count in rosters if row_name == name)
                out = S.L.RawResult()
                args = arguments(owned, out)
                if len(selected) == 0:
                    # Genuine raw malformed transport data calls the actual
                    # kernel; it is not a replacement authority fixture.
                    selected = (selected._type_ * 1)()
                    parameter = name.title()
                    if name in ('grants', 'uses', 'receipts', 'events'):
                        parameter = 'Authority_' + parameter
                    index = J.PARAMETERS.index(parameter) * 2
                    args[index], args[index + 1] = selected, len(selected)
                self.assertTrue(malformed_presence(selected[0]))
                self.assertEqual(self.kernel.call(*args), -1)

    def test_original_null_zero_rosters_and_active_nonzero_shape_refusal(self):
        owned = self.owned('ROOT_CONTROLLER_ADMISSION')
        out = S.L.RawResult()
        args = arguments(owned, out)
        for name, _array, count in (*owned[3], *owned[7], *owned[10]):
            if count == 0:
                parameter = name.title()
                if name in ('grants', 'uses', 'receipts', 'events'):
                    parameter = 'Authority_' + parameter
                args[J.PARAMETERS.index(parameter) * 2] = None
        self.assertEqual(self.kernel.call(*args), 0)
        self.assertEqual(out.status, 0)
        # Wrong nonzero length is refused before a typed view is created.
        args[1] = 0
        self.assertEqual(self.kernel.call(*args), -1)

    def test_complete_child_snapshot_precedes_original_foreign_output_alias(self):
        owned = self.owned('CHILD_ADMISSION')
        actor = owned[0]
        out = S.L.RawResult()
        args = arguments(owned, out)
        args[-2] = C.byref(actor)
        self.assertEqual(self.kernel.call(*args), 0)
        self.assertEqual(C.cast(C.byref(actor), C.POINTER(S.L.RawResult)).contents.status, 1)
