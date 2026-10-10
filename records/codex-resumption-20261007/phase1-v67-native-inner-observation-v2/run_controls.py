"""Retained throwaway refusal/transport smoke plus both whole original suites.

The smoke uses the real retained compiled DLL, not a mock or an authority fixture.
Its separate child can fail/crash/timeout without suppressing the original suites.
All controls share the unchanged outer 180-second timeout; no testcase filter,
skip, failfast, changed expectation, provisioning, readiness or accepted-head case.
"""
from pathlib import Path
import ctypes
import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
import time
import traceback
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
manifest = json.loads((HERE / "manifest.json").read_text())
SYMBOLS = (
    "wl_custody_operation_startup_decide_v2",
    "wl_custody_operation_append_decide_v2",
    "wl_custody_operation_recovery_decide_v2",
    "wl_custody_operation_bootstrap_decide_v2",
)
CASE_NAMES = (
    "malformed_unaligned", "empty_owned_unaligned",
    "input_status_overlap", "input_position_overlap",
    "outputs_exact_overlap", "outputs_partial_overlap",
    "count_and_storage_excess", "uint64_max_excess",
)


def emit(kind, **fields):
    print(json.dumps({"kind": kind, **fields}, sort_keys=True), flush=True)


def owned_buffer(size, sentinel):
    return (ctypes.c_ubyte * size)(*([sentinel] * size))


def unaligned_offset(buffer):
    base = ctypes.addressof(buffer)
    alignment = ctypes.alignment(ctypes.c_uint64)
    offset = next(index for index in range(8, 16) if (base + index) % alignment)
    assert offset + 8 < len(buffer)
    return offset


def make_case(name, smoke):
    # Every pointer is into a live owned allocation. Only rejected excessive
    # lengths intentionally exceed that allocation; no hostile address is used.
    owners = {"input": owned_buffer(48, 0xC3),
              "status": owned_buffer(32, 0xA5),
              "position": owned_buffer(32, 0x5A)}
    input_offset = 8
    status = ("status", unaligned_offset(owners["status"]))
    position = ("position", unaligned_offset(owners["position"]))
    length = 1
    owners["input"][input_offset] = 0xFF  # malformed bytes, not authority DATA
    error = smoke["error_codes"]["Error_OK"]
    zero_outputs = True
    if name == "empty_owned_unaligned":
        length = 0
    elif name in ("input_status_overlap", "input_position_overlap"):
        length = 16
        owners["input"][input_offset:input_offset + length] = [0xFF] * length
        if name == "input_status_overlap":
            status = ("input", input_offset + 3)
        else:
            position = ("input", input_offset + 3)
        error = smoke["error_codes"]["Error_Invalid_Argument"]
        zero_outputs = False
    elif name in ("outputs_exact_overlap", "outputs_partial_overlap"):
        position = ("status", status[1] + (4 if name == "outputs_partial_overlap" else 0))
        error = smoke["error_codes"]["Error_Invalid_Argument"]
        zero_outputs = False
    elif name in ("count_and_storage_excess", "uint64_max_excess"):
        bounds = smoke["native_domain_bounds"]
        if name == "count_and_storage_excess":
            assert bounds["Count_Last"] == bounds["Storage_Offset_Last"]
            length = bounds["Count_Last"] + 1
        else:
            length = bounds["uint64_max"]
        error = smoke["error_codes"]["Error_Too_Large"]
        zero_outputs = False
    before = {key: bytes(buffer) for key, buffer in owners.items()}
    expected = {key: bytearray(raw) for key, raw in before.items()}
    if zero_outputs:
        for key, offset in (status, position):
            expected[key][offset:offset + 8] = bytes(8)
    addresses = {
        "input": ctypes.addressof(owners["input"]) + input_offset,
        "status": ctypes.addressof(owners[status[0]]) + status[1],
        "position": ctypes.addressof(owners[position[0]]) + position[1],
    }
    if zero_outputs:
        assert addresses["status"] % ctypes.alignment(ctypes.c_uint64) != 0
        assert addresses["position"] % ctypes.alignment(ctypes.c_uint64) != 0
    return owners, before, expected, addresses, length, status, position, error


def mapped_library(library):
    metadata = library.stat()
    rows = []
    for line in Path("/proc/self/maps").read_text().splitlines():
        fields = line.split(None, 5)
        if len(fields) != 6 or fields[5] != str(library):
            continue
        start, end = (int(item, 16) for item in fields[0].split("-"))
        major, minor = (int(item, 16) for item in fields[3].split(":"))
        assert int(fields[4]) == metadata.st_ino
        assert os.makedev(major, minor) == metadata.st_dev
        rows.append({"start": start, "end": end, "permissions": fields[1],
                     "offset": int(fields[2], 16), "device": fields[3],
                     "inode": int(fields[4]), "path": fields[5]})
    assert rows and any("x" in row["permissions"] for row in rows)
    return rows


def operation_transport_smoke():
    smoke = manifest["operation_transport_smoke"]
    expected_cases = len(SYMBOLS) * len(CASE_NAMES)
    completed = failures = 0
    emit("operation_transport_smoke_begin", scope=smoke["scope"],
         expected_cases=expected_cases, symbols=list(SYMBOLS),
         native_abi_acceptance=False, provisioning_authority=False)
    try:
        assert os.getuid() != 0 and os.geteuid() != 0, "nonprivileged smoke only"
        assert list(SYMBOLS) == smoke["symbols"]
        assert ctypes.sizeof(ctypes.c_uint64) == ctypes.sizeof(ctypes.c_size_t) == 8
        assert ctypes.sizeof(ctypes.c_void_p) == ctypes.sizeof(ctypes.c_longlong) == 8
        assert sys.byteorder == "little"
        library = Path(manifest["source"]) / "lib/libworldline_core.so"
        assert os.environ["WORLDLINE_CORE_LIB"] == str(library)
        assert library.is_file() and not library.is_symlink()
        assert stat.S_ISREG(library.stat().st_mode)
        digest = hashlib.sha256(library.read_bytes()).hexdigest()
        # Library_Auto_Init is true in the selected real project. Do not call
        # adainit or fabricate an initialization path around the actual DLL.
        dll = ctypes.CDLL(str(library))
        mappings = mapped_library(library)
        emit("operation_transport_smoke_library", path=str(library), sha256=digest,
             mappings=mappings, pid=os.getpid(), uid=os.getuid(), euid=os.geteuid(),
             error_codes=smoke["error_codes"],
             native_domain_bounds=smoke["native_domain_bounds"])
        for symbol in SYMBOLS:
            try:
                function = getattr(dll, symbol)
                function.argtypes = [ctypes.c_void_p, ctypes.c_size_t,
                                     ctypes.c_void_p, ctypes.c_void_p]
                function.restype = ctypes.c_int
                address = ctypes.cast(function, ctypes.c_void_p).value
                assert any(row["start"] <= address < row["end"]
                           and "x" in row["permissions"] for row in mappings)
                emit("operation_transport_smoke_symbol", symbol=symbol,
                     address=address, mapped_selected_library=True)
            except Exception:
                failures += 1
                traceback.print_exc(file=sys.stderr)
                sys.stderr.flush()
                emit("operation_transport_smoke_symbol_error", symbol=symbol,
                     traceback=traceback.format_exc())
                continue
            for case in CASE_NAMES:
                try:
                    (owners, before, expected, addresses, length,
                     status, position, expected_error) = make_case(case, smoke)
                    emit("operation_transport_smoke_call", symbol=symbol, case=case,
                         addresses=addresses, declared_length=length,
                         owned_sizes={key: len(value) for key, value in owners.items()},
                         before={key: value.hex() for key, value in before.items()},
                         expected_error=expected_error,
                         expected_buffers={key: value.hex() for key, value in expected.items()})
                    # Local owners and their bytes remain strongly reachable
                    # through this synchronous real native call and readback.
                    error = function(addresses["input"], length,
                                     addresses["status"], addresses["position"])
                    after = {key: bytes(buffer) for key, buffer in owners.items()}
                    status_value = int.from_bytes(after[status[0]][status[1]:status[1] + 8], "little")
                    position_value = int.from_bytes(after[position[0]][position[1]:position[1] + 8], "little")
                    matches = {key: after[key] == expected[key] for key in owners}
                    passed = error == expected_error and all(matches.values())
                    completed += 1
                    failures += not passed
                    emit("operation_transport_smoke_result", symbol=symbol, case=case,
                         transport_error=error, native_status=status_value,
                         native_position=position_value, expected_error=expected_error,
                         buffer_matches=matches,
                         after={key: value.hex() for key, value in after.items()}, passed=passed)
                    if not passed:
                        print(f"Native transport smoke failure: {symbol} {case}",
                              file=sys.stderr, flush=True)
                except Exception:
                    failures += 1
                    traceback.print_exc(file=sys.stderr)
                    sys.stderr.flush()
                    emit("operation_transport_smoke_case_error", symbol=symbol,
                         case=case, traceback=traceback.format_exc())
        assert mapped_library(library) == mappings
        assert hashlib.sha256(library.read_bytes()).hexdigest() == digest
    except Exception:
        failures += 1
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        emit("operation_transport_smoke_setup_or_continuity_error",
             traceback=traceback.format_exc())
    passed = completed == expected_cases and failures == 0
    emit("operation_transport_smoke_outcome", completed_cases=completed,
         expected_cases=expected_cases, failures=failures, passed=passed,
         positive_authority_cases=0, arbitrary_hostile_address_guarantee=False,
         count_and_storage_limits_coincide=True,
         independent_second_storage_guard_coverage=False,
         provisioning_authority=False, native_abi_acceptance=False,
         startup_acceptance=False, phase_acceptance=False)
    return 0 if passed else 1


# Observation selection is not testcase selection: all original cases still run.
INNER_OBSERVED_TEST = (
    "test_raw_evaluation_default.RawRequiredFailureControls."
    "test_post_stage_error_head_is_not_replaced_by_old_pass")
INNER_EVENT_CAP = 1024
# Only cold phase/native-boundary lines are selected; no archive recursion,
# layout-field loop, row-marshalling loop or native diagnostic sink is observed.
INNER_BOUNDARIES = {
    ("tests/test_raw_evaluation_default.py", "producer_case"): (),
    ("tests/test_raw_evaluation_default.py", "staged_journal"): (),
    ("tests/test_raw_evaluation_default.py", "opened"):
        (313, 318, 320, 322, 324, 350, 351, 352, 353, 354, 356),
    ("tests/test_raw_evaluation_default.py", "append"):
        (334, 335, 340, 341, 347, 348),
    ("tests/test_raw_evaluation_default.py",
     "test_post_stage_error_head_is_not_replaced_by_old_pass"):
        (409, 410, 411, 412, 414),
    ("runtime/worldline/evaluation_pending.py", "__init__"): (),
    ("runtime/worldline/evaluation_pending.py", "begin"): (370, 373),
    ("runtime/worldline/evaluation_pending.py", "_reserve_locked"): (333, 336),
    ("runtime/worldline/evaluation_pending.py", "replay"): (433, 436, 458),
    ("runtime/worldline/evaluation_pending.py", "close"): (495, 496, 497),
    ("runtime/worldline/evaluation_terminal.py", "__init__"): (),
    ("runtime/worldline/evaluation_terminal.py", "enable_raw_capture"): (),
    ("runtime/worldline/evaluation_terminal.py", "open_stream"): (548, 549),
    ("runtime/worldline/evaluation_terminal.py", "retain"): (330, 332, 338),
    ("runtime/worldline/evaluation_terminal.py", "replay"): (403, 405, 420),
    ("runtime/worldline/evaluation_terminal.py", "complete"): (423, 424),
    ("runtime/worldline/evaluation_terminal.py", "authority_material_full"): (488,),
    ("runtime/worldline/evaluation_terminal.py", "_authority_material"):
        (498, 502, 504, 506, 515, 522),
    ("runtime/worldline/evaluation_terminal.py", "close"): (696,),
    ("runtime/worldline/completion_kernel.py", "_owned"): (229, 230, 231),
    ("runtime/worldline/raw_completion_kernel.py", "prepare"): (39, 43, 49),
    ("runtime/worldline/raw_completion_kernel.py", "classify"): (59, 60, 61),
    ("runtime/worldline/evaluation_authority.py", "_read"): (308, 312, 314),
    ("runtime/worldline/evaluation_authority.py", "_read_material"):
        (190, 193, 194, 198, 205, 206, 207, 258, 265, 266, 277, 279, 280),
    ("runtime/worldline/evaluation_authority.py", "read"): (419, 421, 423),
    ("runtime/worldline/evaluation_authority.py", "_refuse"): (33,),
    ("runtime/worldline/evaluation_context.py", "require_metadata"): (132, 133),
    ("runtime/worldline/evaluation_wire.py", "record"): (129,),
    ("runtime/worldline/evaluation_producer.py", "derive"): (301, 302, 314, 315),
    ("runtime/worldline/evaluation_wire.py", "evaluate"): (62, 63, 64, 65, 69, 70),
    ("runtime/worldline/evaluation_history.py", "select_history"): (191, 194, 208),
    ("runtime/worldline/transaction.py", "_selected_freshness"):
        (1424, 1425, 1426, 1427, 1432, 1434, 1436, 1441),
    ("runtime/worldline/transaction.py", "_execution_identity"): (1369, 1370),
    ("runtime/worldline/transaction.py", "_freshness_after_staged"):
        (1044, 1046, 1050),
    ("runtime/worldline/transaction.py", "_owner_evidence"): (2037, 2041),
    ("runtime/worldline/transaction_relation.py", "freshness"): (65,),
    ("runtime/worldline/transaction_relation.py", "execution"): (100,),
    ("runtime/worldline/transaction_relation.py", "_decide"): (40, 41, 46, 47, 49),
}


NATIVE_ACTIVE_FD = "WORLDLINE_NATIVE_TRANSACTION_OBSERVATION_ACTIVE_FD"
NATIVE_PENDING_FD = "WORLDLINE_NATIVE_TRANSACTION_OBSERVATION_PENDING_FD"


def restore_native_observation(previous):
    try:
        if previous is None:
            os.environ.pop(NATIVE_ACTIVE_FD, None)
        else:
            os.environ[NATIVE_ACTIVE_FD] = previous
    except Exception:
        try:
            emit("native_transaction_observation_unavailable",
                 test_id=INNER_OBSERVED_TEST, stage="restore_environment",
                 later_inner_state="UNOBSERVED", no_acceptance=True)
        except Exception:
            pass


class NativeTransactionBoundaryObservation:
    """Arm only the existing observed case; never select or modify testcases."""
    def __init__(self):
        self.previous = os.environ.get(NATIVE_ACTIVE_FD)
        self.armed = False

    def start(self):
        try:
            raw_descriptor = os.environ[NATIVE_PENDING_FD]
            descriptor = int(raw_descriptor)
            if descriptor <= 2 or not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise OSError("native observation regular-file descriptor unavailable")
            os.environ[NATIVE_ACTIVE_FD] = raw_descriptor
            self.armed = True
            emit("native_transaction_observation_start", test_id=INNER_OBSERVED_TEST,
                 monotonic_ns=time.monotonic_ns(), pid=os.getpid(),
                 stream="tests.native-boundaries.stdout",
                 only_exact_complete_native_rows_are_evidence=True,
                 last_visible_boundary_is_not_root_cause=True, no_acceptance=True)
        except Exception:
            self.finish()
            try:
                emit("native_transaction_observation_unavailable",
                     test_id=INNER_OBSERVED_TEST, stage="arm_descriptor",
                     later_inner_state="UNOBSERVED", no_acceptance=True)
            except Exception:
                pass

    def finish(self):
        if self.armed:
            restore_native_observation(self.previous)
            self.armed = False


class FixedInnerBoundaryTrace:
    """Bounded scalar observations only, never retained frames/locals/arguments.

    Repeated calls and selected pre/post-native lines are NOT deduplicated.
    Ordinals identify separate invocations; a Python return event can also mean
    a generator yield or exception unwind, never a native success decision.
    """
    def __init__(self):
        self.previous_trace = sys.gettrace()
        self.boundaries = {
            (str(Path(manifest["source"]) / relative), function):
                (relative, frozenset(lines))
            for (relative, function), lines in INNER_BOUNDARIES.items()}
        self.ordinals = {key: 0 for key in self.boundaries}
        self.active_ordinals = {key: [] for key in self.boundaries}
        self.events = 0
        self.saturated = False
        self.failed = False

    def start(self):
        try:
            emit("inner_boundary_observation_start", test_id=INNER_OBSERVED_TEST,
                 monotonic_ns=time.monotonic_ns(), event_cap=INNER_EVENT_CAP,
                 later_state_after_saturation="UNOBSERVED", no_acceptance=True)
            sys.settrace(self)
        except Exception:
            self.failed = True
            sys.settrace(self.previous_trace)

    def __call__(self, frame, event, _unused_argument):
        if self.saturated or self.failed:
            return None
        try:
            key = (frame.f_code.co_filename, frame.f_code.co_name)
            boundary = self.boundaries.get(key)
            if boundary is None:
                return None
            relative, lines = boundary
            if event == "call":
                frame.f_trace_lines = bool(lines)
                self.ordinals[key] += 1
                ordinal = self.ordinals[key]
                self.active_ordinals[key].append(ordinal)
            elif event == "return":
                ordinal = self.active_ordinals[key].pop()
            elif event == "line" and frame.f_lineno in lines:
                ordinal = self.active_ordinals[key][-1]
            else:
                return self
            if self.events == INNER_EVENT_CAP:
                self.saturated = True
                sys.settrace(self.previous_trace)
                for active in self.active_ordinals.values():
                    active.clear()
                emit("inner_boundary_observation_saturation", test_id=INNER_OBSERVED_TEST,
                     monotonic_ns=time.monotonic_ns(), event_cap=INNER_EVENT_CAP,
                     observed_events=self.events, later_inner_state="UNOBSERVED",
                     last_visible_event_is_not_root_cause=True, no_acceptance=True)
                return None
            emit("inner_boundary_timing", test_id=INNER_OBSERVED_TEST,
                 location=relative, function=key[1], event=event,
                 line=frame.f_lineno, invocation=ordinal, sequence=self.events + 1,
                 monotonic_ns=time.monotonic_ns(), no_acceptance=True)
            self.events += 1
            return self
        except Exception:
            # An observer failure supplies no inner evidence and must not
            # replace the original test's exception or interrupt its cleanup.
            # No exception object, traceback, argument or frame is retained.
            self.failed = True
            sys.settrace(self.previous_trace)
            for active in self.active_ordinals.values():
                active.clear()
            return None

    def finish(self):
        sys.settrace(self.previous_trace)
        try:
            emit("inner_boundary_observation_stop", test_id=INNER_OBSERVED_TEST,
                 monotonic_ns=time.monotonic_ns(), observed_events=self.events,
                 saturated=self.saturated, observation_failed=self.failed,
                 later_inner_state="UNOBSERVED" if self.saturated or self.failed
                     else "ONLY_EXACT_RECORDED_BOUNDARIES_OBSERVED",
                 last_visible_event_is_not_root_cause=True, no_acceptance=True)
        except Exception:
            self.failed = True


class ImmediateTracebackResult(unittest.TextTestResult):
    def startTest(self, test):
        self._test_started_ns = time.monotonic_ns()
        emit("original_test_start", test_id=test.id(),
             monotonic_ns=self._test_started_ns, no_acceptance=True)
        super().startTest(test)
        self._inner_observer = None
        self._native_observer = None
        if test.id() == INNER_OBSERVED_TEST:
            try:
                self._native_observer = NativeTransactionBoundaryObservation()
                self._native_observer.start()
            except Exception:
                # Secondary observation setup never suppresses the original case.
                self._native_observer = None
            previous_trace = sys.gettrace()
            try:
                self._inner_observer = FixedInnerBoundaryTrace()
                self._inner_observer.start()
            except Exception:
                # Failure to allocate observer-only metadata must not suppress
                # the original selected test or replace its eventual exception.
                sys.settrace(previous_trace)
                try:
                    emit("inner_boundary_observation_unavailable", test_id=test.id(),
                         monotonic_ns=time.monotonic_ns(), later_inner_state="UNOBSERVED",
                         observation_failed=True, no_acceptance=True)
                except Exception:
                    self._inner_observer = None

    def stopTest(self, test):
        try:
            super().stopTest(test)
            stopped_ns = time.monotonic_ns()
            emit("original_test_stop", test_id=test.id(), monotonic_ns=stopped_ns,
                 elapsed_ns=stopped_ns - self._test_started_ns, no_acceptance=True)
        finally:
            try:
                if self._inner_observer is not None:
                    self._inner_observer.finish()
                    self._inner_observer = None
            finally:
                if self._native_observer is not None:
                    self._native_observer.finish()
                    self._native_observer = None

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.stream.writeln(self.failures[-1][1])
        self.stream.flush()

    def addError(self, test, err):
        super().addError(test, err)
        self.stream.writeln(self.errors[-1][1])
        self.stream.flush()


def main():
    if sys.argv[1:] == ["--operation-transport-smoke"]:
        return operation_transport_smoke()
    assert len(sys.argv) == 1
    original_tests = Path(manifest["source"]) / "tests"
    for name in ("test_raw_evaluation_default", "test_core_abi"):
        spec = importlib.util.find_spec(name)
        assert spec is not None and Path(spec.origin).resolve() == original_tests / (name + ".py")
    # Inherit the captured tests stdout/stderr, flushing raw evidence as each
    # native case completes. A nonzero return/signal/timeout still runs the full
    # unchanged original suites; it can never turn the combined result into pass.
    command = ["/usr/bin/python3", "-B", str(HERE / "run_controls.py"),
               "--operation-transport-smoke"]
    smoke_code = None
    smoke_error = None
    smoke_timeout = False
    try:
        smoke_code = subprocess.run(
            command, timeout=manifest["operation_transport_smoke"]["child_timeout_seconds"],
            check=False).returncode
    except subprocess.TimeoutExpired as error:
        # subprocess.run kills and waits for its own direct child before raising.
        smoke_timeout = True
        smoke_error = repr(error)
    except Exception as error:
        smoke_error = repr(error)
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
    emit("operation_transport_smoke_wait", argv=command, returncode=smoke_code,
         timed_out=smoke_timeout, error=smoke_error,
         original_whole_suites_still_required=True, no_acceptance=True)
    suite = unittest.defaultTestLoader.loadTestsFromNames(
        ["test_raw_evaluation_default", "test_core_abi"])
    previous_trace = sys.gettrace()
    previous_native_observation = os.environ.get(NATIVE_ACTIVE_FD)
    try:
        result = unittest.TextTestRunner(
            verbosity=2, resultclass=ImmediateTracebackResult, failfast=False).run(suite)
    finally:
        # Also cover abrupt unittest/result-hook exits before stopTest completes.
        sys.settrace(previous_trace)
        restore_native_observation(previous_native_observation)
    # An unexpected skip or expected-failure annotation supplies no credit.
    original_pass = result.wasSuccessful() and not result.skipped and not result.expectedFailures
    smoke_pass = smoke_code == 0 and not smoke_timeout and smoke_error is None
    emit("diagnostic_controls_outcome", original_suites=list(manifest["agent_control_modules"]),
         original_tests_run=result.testsRun, original_suites_pass=bool(original_pass),
         original_failures=len(result.failures), original_errors=len(result.errors),
         skipped=len(result.skipped), expected_failures=len(result.expectedFailures),
         operation_transport_smoke_pass=smoke_pass,
         combined_pass=bool(original_pass and smoke_pass), provisioning_authority=False,
         native_abi_acceptance=False, startup_acceptance=False, phase_acceptance=False)
    return 0 if original_pass and smoke_pass else 1


if __name__ == "__main__":
    sys.exit(main())
