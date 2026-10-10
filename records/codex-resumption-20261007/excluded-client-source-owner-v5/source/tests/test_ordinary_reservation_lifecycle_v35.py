"""Source-authored UNRUN controls; real selected native library, temporary I/O only."""
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from worldline.admission import (AdmissionAuthority, Floors, Ledger, Reservation, Gate,
                                Decision, ADMITTED, _Guard)
from worldline.core import Core
from worldline.errors import CoreUnavailable, WorldlineError
from worldline.linux.systemd import SystemdProcess, WorkloadIdentity, WorkloadTerminalObservation
from worldline import ordinary_reservation_lifecycle as native

class OrdinaryReservationV35(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ["WORLDLINE_CORE_LIB"]))

    def setUp(self):
        self.selected = patch.object(Core, "shared", return_value=self.core)
        self.selected.start()
        self.addCleanup(self.selected.stop)
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.ledger = Ledger(Path(self.temporary.name))
        self.authority = AdmissionAuthority(self.ledger, Floors())

    def rows(self, ids=("a", "b"), units=("same.service", "same.service")):
        result = [Reservation(rid, "work-" + rid, unit, 1, 1 << 512, 7, 9,
                              {"retained": rid}) for rid, unit in zip(ids, units)]
        for row in result:
            self.ledger.add(row)
        return result

    def test_absent_empty_authority_and_direct_empty_identity(self):
        calls = []
        class Absent:
            def __bool__(self):
                calls.append("truth"); return False
            def __str__(self):
                raise AssertionError("false original must not be normalized")
        before = self.ledger.path.exists()
        for value in (None, "", Absent()):
            self.assertFalse(self.authority.release(value))
        self.assertEqual(calls, ["truth"])
        self.assertEqual(self.ledger.path.exists(), before)
        self.rows(("", "a"))
        self.assertTrue(self.ledger.release(""))
        self.assertEqual([r.reservation_id for r in self.ledger.outstanding()], ["a"])

    def test_custom_string_subclass_normalization_and_ne_not_eq(self):
        calls = []
        class Selected(str):
            def __eq__(self, other):
                raise AssertionError("release must retain original !=")
            def __ne__(self, other):
                calls.append(("ne", other)); return other != "b"
        class Requested:
            def __bool__(self):
                calls.append("truth"); return True
            def __str__(self):
                calls.append("string"); return Selected("not-the-selected-bytes")
        rows = self.rows()
        self.assertTrue(self.authority.release(Requested()))
        self.assertEqual(calls, ["truth", "string", ("ne", "a"), ("ne", "b")])
        self.assertEqual(self.ledger.outstanding(), [rows[0]])

    def test_custom_truthful_comparison_result_and_primary_exception(self):
        calls = []
        class Result:
            def __init__(self, value): self.value = value
            def __bool__(self):
                calls.append(("truth", self.value)); return self.value
        class Requested:
            def __ne__(self, other):
                calls.append(("ne", other)); return Result(other != "a")
        rows = self.rows()
        self.assertTrue(self.ledger.release(Requested()))
        self.assertEqual(calls, [("ne", "a"), ("truth", False), ("ne", "b"), ("truth", True)])
        self.assertEqual(self.ledger.outstanding(), [rows[1]])
        error = RuntimeError("original custom comparison primary")
        class Broken:
            def __ne__(self, other): raise error
        before = self.ledger.path.read_bytes()
        with self.assertRaises(RuntimeError) as caught:
            self.ledger.release(Broken())
        self.assertIs(caught.exception, error)
        self.assertEqual(self.ledger.path.read_bytes(), before)

    def test_builtin_double_release_and_duplicate_corruption(self):
        rows = self.rows()
        self.assertTrue(self.authority.release("b"))
        self.assertEqual(self.ledger.outstanding(), [rows[0]])
        before = self.ledger.path.read_bytes()
        self.assertFalse(self.authority.release("b"))
        self.assertEqual(self.ledger.path.read_bytes(), before)
        duplicate = rows[0].as_dict()
        self.ledger.path.write_text(json.dumps({"reservations": [duplicate, duplicate]}))
        before = self.ledger.path.read_bytes()
        for action in (lambda: self.ledger.release("a"),
                       lambda: self.ledger.attach_unit("a", "same.service"),
                       lambda: self.ledger.reconcile(lambda row: False)):
            with self.assertRaises(WorldlineError): action()
            self.assertEqual(self.ledger.path.read_bytes(), before)

    def test_attach_unit_preserves_or_clears_actual_current_identity(self):
        rows = self.rows()
        self.ledger.attach_unit("a", "same.service")
        self.assertEqual(self.ledger.outstanding(), rows)
        self.ledger.attach_unit("a", "different.service")
        current = self.ledger.outstanding()
        self.assertEqual(current[0].unit, "different.service")
        self.assertIsNone(current[0].workload_identity)
        self.assertEqual(current[1], rows[1])
        before = self.ledger.path.read_bytes()
        for invalid in (None, "", "bad/name", "bad\nname"):
            with self.assertRaises(WorldlineError): self.ledger.attach_unit("a", invalid)
            self.assertEqual(self.ledger.path.read_bytes(), before)

    def test_identity_membership_and_second_stateful_equality_pass(self):
        calls = []
        class Requested:
            def __eq__(self, other):
                calls.append(other); return len(calls) in (1, 4)
        rows = self.rows()
        identity = WorkloadIdentity("same.service", "1" * 32, "/same.service")
        self.ledger.attach_process_identity(Requested(), identity)
        current = self.ledger.outstanding()
        self.assertEqual(calls, ["a", "b", "a", "b"])
        self.assertEqual(current[0], rows[0])
        self.assertEqual(current[1].workload_identity,
                         {"unit": identity.unit, "invocationId": identity.invocation_id,
                          "controlGroup": identity.control_group})
        before = self.ledger.path.read_bytes()
        for rid, candidate in (("absent", identity), ("a", object()),
                               ("a", WorkloadIdentity("wrong.service", "2" * 32, "/wrong.service"))):
            with self.assertRaises(WorldlineError): self.ledger.attach_process_identity(rid, candidate)
            self.assertEqual(self.ledger.path.read_bytes(), before)

    def test_literal_false_reconcile_and_restart_accounting(self):
        rows = self.rows()
        class Opaque:
            def __bool__(self): raise AssertionError("no liveness coercion")
            def __eq__(self, other): raise AssertionError("no liveness comparison")
            @property
            def __class__(self): raise AssertionError("no opaque class protocol acquisition")
        observations = iter((Opaque(), False))
        restarted = Ledger(self.ledger.directory)
        self.assertEqual(restarted.reconcile(lambda row: next(observations)), [rows[1]])
        self.assertEqual(restarted.outstanding(), [rows[0]])
        self.assertEqual(native.reconcile_plan((0, None, Opaque(), False)).mask, (0, 0, 0, 1))

    def test_native_refusal_has_no_semantic_fallback(self):
        self.rows()
        before = self.ledger.path.read_bytes()
        with patch.object(Core, "shared", return_value=SimpleNamespace(_lib=object())):
            for action in (lambda: self.ledger.release("a"),
                           lambda: self.authority.release(None),
                           lambda: self.ledger.attach_unit("a", "same.service")):
                with self.assertRaises(WorldlineError): action()
        self.assertEqual(self.ledger.path.read_bytes(), before)

    def test_native_rejects_malformed_profile_and_flags_only_release_capture(self):
        with self.assertRaises(CoreUnavailable):
            native.decide("probe", observation=True, profile="not-an-actual-protocol")
        with self.assertRaises(CoreUnavailable):
            native.decide("release", rows=[{"ne": False}])

    def guard(self):
        released = []
        authority = SimpleNamespace(release=lambda rid: released.append(rid))
        guard = _Guard(Gate(authority, None), "work", None)
        guard.decision = Decision(ADMITTED, "control", "a")
        guard._release_deferred = True
        return guard, released

    def test_guard_actual_original_observation_join_and_double_release(self):
        guard, released = self.guard()
        launcher = SimpleNamespace(returncode=0)
        manager = SimpleNamespace(terminal_observation=lambda process, **kw:
            WorkloadTerminalObservation("NORMAL_PIPE_COMPLETION", process.unit, launcher.returncode))
        process = SystemdProcess("same.service", launcher, manager)
        guard.release()
        self.assertEqual(released, [])
        self.assertIsNotNone(guard.decision)
        guard.process_settled(process)
        self.assertFalse(guard._release_deferred)
        guard.release(); guard.release()
        self.assertEqual(released, ["a"])
        self.assertIsNone(guard.decision)

    def test_guard_mismatch_unknown_and_primary_observation_failure_retain(self):
        guard, released = self.guard()
        launcher = SimpleNamespace(returncode=1)
        manager = SimpleNamespace()
        process = SystemdProcess("same.service", launcher, manager)
        for state, unit, code in (("MANAGER_CGROUP_EMPTY", "wrong.service", 1),
                                  ("MANAGER_CGROUP_EMPTY", "same.service", 0),
                                  ("UNKNOWN", "same.service", 1)):
            manager.terminal_observation = lambda process, **kw: WorkloadTerminalObservation(state, unit, code)
            guard.process_settled(process, after_failure=True)
            guard.release()
            self.assertTrue(guard._release_deferred)
        error = RuntimeError("primary effect error")
        def unavailable(*args, **kwargs): raise OSError("actual manager read failure")
        manager.terminal_observation = unavailable
        guard.process_settled(process, primary=error, after_failure=True)
        self.assertTrue(any("terminal observation also failed" in note for note in error.__notes__))
        self.assertEqual(released, [])

    def test_failure_protocol_retains_inplace_or_and_large_integer_value(self):
        calls = []
        class Before:
            def __ior__(self, other): calls.append(other); return other
        value = 1 << 10000
        self.assertIs(native.failure_merge(Before(), value), value)
        self.assertEqual(calls, [value])

    def test_guard_reauthorizes_raw_pipe_and_rejects_state_label_after_failure(self):
        from worldline.manager_resource_lifecycle import pipe_capture
        unit = "worldline-11111111-1111-1111-1111-111111111111.service"
        launcher = SimpleNamespace(returncode=0, args=["/usr/bin/systemd-run", "--user",
            "--pipe", "--service-type=exec", "--property=KillMode=control-group",
            "--unit=" + unit, "--", "/usr/bin/true"])
        manager = SimpleNamespace(systemd_run="/usr/bin/systemd-run")
        process = SystemdProcess(unit, launcher, manager, launched_at_us=1)
        def observation(process, *, after_failure):
            raw = pipe_capture(manager, process, after_failure=after_failure,
                               returncode=launcher.returncode)
            return WorkloadTerminalObservation("NORMAL_PIPE_COMPLETION", unit, 0,
                                               raw_capture=raw)
        manager.terminal_observation = observation
        guard, released = self.guard()
        guard.process_settled(process)
        guard.release()
        self.assertEqual(released, ["a"])
        guard, released = self.guard()
        guard.process_settled(process, after_failure=True)
        guard.release()
        self.assertTrue(guard._release_deferred)
        self.assertEqual(released, [])

    def test_original_coreunavailable_acquisition_identity_is_not_transport_error(self):
        self.rows()
        original_error = CoreUnavailable("actual original protocol failure", retained="detail")
        class Requested:
            def __ne__(self, other): raise original_error
        class Truth:
            def __bool__(self): raise original_error
        class Equal:
            def __eq__(self, other): raise original_error
        class Unit(str):
            def __contains__(self, other): raise original_error
        before = self.ledger.path.read_bytes()
        for action in (lambda: self.ledger.release(Requested()),
                       lambda: self.authority.release(Truth()),
                       lambda: self.ledger.attach_unit(Equal(), "same.service"),
                       lambda: self.ledger.attach_unit("a", Unit("same.service"))):
            with self.assertRaises(CoreUnavailable) as caught:
                action()
            self.assertIs(caught.exception, original_error)
            self.assertEqual(caught.exception.details, {"retained": "detail"})
            self.assertEqual(self.ledger.path.read_bytes(), before)
        # The formatting context is restored after acquisition exceptions.
        with self.assertRaises(CoreUnavailable) as caught:
            native.decide("probe", observation=True, profile="invalid-profile")
        self.assertIsInstance(caught.exception, CoreUnavailable)

    def test_guard_merge_exception_scope_and_original_assignment(self):
        guard, released = self.guard()
        primary = RuntimeError("retained unrelated primary")
        with self.assertRaises(TypeError):
            guard.process_settled(object(), after_failure="x", primary=primary)
        self.assertIs(guard._after_process_failure, False)
        original_error = CoreUnavailable("original in-place OR failure")
        calls = []
        class Merged:
            def __ior__(self, other):
                calls.append(("ior", other))
                raise original_error
        merged = Merged()
        class Incoming:
            def __ror__(self, other):
                calls.append(("ror", other))
                return merged
        guard.process_settled(object(), after_failure=Incoming())
        self.assertIs(guard._after_process_failure, merged)
        with self.assertRaises(CoreUnavailable) as caught:
            guard.process_settled(object(), after_failure=True, primary=primary)
        self.assertIs(caught.exception, original_error)
        self.assertIs(guard._after_process_failure, merged)
        self.assertEqual(calls, [("ror", False), ("ior", True)])
        self.assertFalse(hasattr(primary, "__notes__"))
        self.assertEqual(released, [])

    def test_public_reconcile_retains_native_type_unique_roster_and_direct_domain(self):
        from worldline.reservation_lifecycle import reconcile_plan
        class Subclass(str):
            pass
        for identities in (["a", "a"], [None], [1], [Subclass("a")]):
            with self.assertRaises(CoreUnavailable):
                reconcile_plan(identities, [False] * len(identities), core=self.core)
        self.assertEqual(reconcile_plan(["", "\0", "é", "e\u0301", "\ud800"],
                                       [False, None, True, 0, False], core=self.core),
                         (True, False, False, False, True))
        # Original direct ledger fixtures may expose duplicate or custom IDs;
        # this is distinct from the public exact-roster transport contract.
        row = Reservation("a", "work", None, 0, 0, 0, 0)
        with patch.object(self.ledger, "_load", return_value=[row, row]):
            self.assertEqual(self.ledger.reconcile(lambda item: False), [row, row])

if __name__ == "__main__":
    unittest.main()
