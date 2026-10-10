"""Main-only native diagnostic custody over unchanged qualified N4 helpers.

No build/proof/ordinary/fixture lane. All target launch interfaces consume exact
independent emitted-frame review and fresh original stages. New scope, challenge,
JACKAL receipt, birth/pidfd custody, raw waits and separate actual Main outer wait
are required. Window reservation/release remains Main's original external action.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import resource
import signal
import shlex
import subprocess
import sys
import uuid

import controller
import observation_support as s

FRAME_FILES = ("observation_support.py", "controller.py", "Main_wait.py", "native_observation.py", "native_custody.py", "target_stdio.py", "control_smoke.py", "run_controls.py", "manifest.json", "identity.json")


def check_frame(review_row):
    assert __debug__ and Path(__file__).resolve().parent == s.F
    custody, original = s.inherited()
    capture = s.verify_capture(s.read(s.F / "manifest.json")["original_capture"])
    value = s.read(s.F / "manifest.json")
    assert value["capture_reuse_binding"] == s.INPUTS["capture_reuse_binding"]
    assert value["original_capture_namespace_projection_not_new_capture"] is True
    identity = s.read(s.F / "identity.json")
    import integrity
    import runtime_inventory
    assert integrity.snapshot(s.F, ("source", "attempts", "private-sparklib"), ("identity.json",)) == identity["immutable_snapshot"]
    for name in FRAME_FILES[:-3]:
        assert {k: v for k, v in s.pin(s.F / name).items() if k != "path"} == {k: v for k, v in s.pin(s.P / name).items() if k != "path"}, "emitted helper differs from reviewed recipe: " + name
    assert integrity.snapshot(s.F / "source", custody.SOURCE_OUTPUT_DIRS) == capture["source_snapshot"]
    assert integrity.snapshot(s.F / "private-sparklib", custody.DEPENDENCY_OUTPUT_DIRS) == capture["private_snapshot"]
    assert value["complete_original_manifest"] == original
    assert value["original_source_binding"] == original["source_binding"]
    assert value["agent_control_modules"] == original["agent_control_modules"]
    assert value["exact_target_argv"] == ["/usr/bin/python3", "-B", str(s.F / "run_controls.py")]
    assert value["exact_target_environment"] == s.target_environment(custody, original)
    assert s.pin(s.F / "run_controls.py")["sha256"] == value["run_controls_origin"]["sha256"] == s.pin(s.N4 / "run_controls.py")["sha256"]
    assert value["original_limits"] == s.INPUTS["original_limits"]
    library = s.match(value["diagnostic_library"])
    assert library == s.F / "source/lib/libworldline_core.so"
    assert value["diagnostic_library"]["sha256"] == capture["retained_library"]["sha256"]
    assert set((s.F / "source/lib").iterdir()) == {library}, "no additional diagnostic binaries"
    for name in ("obj", "resource-tests/obj", "resource-tests/bin"):
        assert not (s.F / "source" / name).exists()
    for name in custody.DEPENDENCY_OUTPUT_DIRS:
        assert not (s.F / "private-sparklib" / name).exists()
    assert custody.output_inventory(original) == capture["original_compiled_outputs"]
    assert runtime_inventory.observe(capture["debugger_closure"]["spec"]) == capture["debugger_closure"]["inventory"]
    assert Path(review_row["path"]) == Path(value["future_emitted_review_path"])
    s.reviewed(review_row, "emitted-frame", {name: s.pin(s.F / name) for name in FRAME_FILES},
               {"original_capture": value["original_capture"], "Main_adoption": value["Main_adoption"],
                "recipe_review": value["recipe_review"], "controller_review": value["controller_review"]})
    for field in ("original_build_acceptance", "whole_runtime_acceptance", "formal_acceptance", "fixture_authority", "phase_acceptance", "timeout_resolution", "source_code_changed", "compiler_or_prover_invoked"):
        assert value[field] is False
    controller.profile(value["original_capture"], value["controller_review"])
    return custody, original, value


def stage(value, label, row):
    return controller.check(label, row, value["original_capture"], value["controller_review"])


def unit_for(attempt):
    assert attempt.parent == s.F / "attempts" and len(attempt.name) == 32
    assert all(char in "0123456789abcdef" for char in attempt.name)
    return s.SCOPE_PREFIX + attempt.name + ".scope"


def show_scope(custody, unit):
    assert unit.startswith(s.SCOPE_PREFIX)
    result = subprocess.run(["/usr/bin/systemctl", "--user", "show", unit,
        "-p", "LoadState", "-p", "ActiveState", "-p", "SubState", "-p", "MainPID", "-p", "ControlGroup", "-p", "Result"],
        capture_output=True, text=True, check=True, timeout=15, env=custody.bus_environment())
    values = dict(row.split("=", 1) for row in result.stdout.splitlines() if "=" in row)
    group = values.get("ControlGroup", "")
    group_path = Path("/sys/fs/cgroup") / group.lstrip("/")
    members = (group_path / "cgroup.procs").read_text() if group and group_path.exists() else ""
    empty = (values.get("LoadState") == "not-found" and values.get("ActiveState") == "inactive"
             and values.get("SubState") == "dead" and values.get("MainPID") in (None, "", "0")
             and not group and not members.strip())
    return {"at": s.utc_now(), "argv": result.args, "returncode": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr, "cgroup_members_raw": members,
            "owned_unit_terminal_empty": empty}


def window(custody, value, attempt, label):
    state = s.read(custody.WINDOW)
    assert state["status"] == "reserved"
    assert state["holder_task"] == value["controller_profile"]["required_window_holder"]
    assert state["candidate"] == str(s.F), "never reuse N4 or another owner's reservation"
    row = {"at": s.utc_now(), "status": state["status"], "holder_task": state["holder_task"],
           "candidate": state["candidate"], "window_sha256": custody.sha(custody.WINDOW)}
    s.save_new(attempt / (label + "-window-binding.json"), row)
    return row


def scope_argv(attempt, unit):
    return ["/usr/bin/systemd-run", "--user", "--scope", "--unit=" + unit.removesuffix(".scope"),
            "-p", "MemoryMax=8G", "-p", "MemorySwapMax=0", "/usr/bin/python3", "-B",
            str(s.F / "native_custody.py"), "child", str(attempt)]


def run_scope(custody, attempt, command, env, unit):
    """Original native raw/wait/finite-stop pattern, adding scope-runner birth.

    Fixed scope action only, not a second selectable general build/test runner.
    Qualified N4 raw/save/stop routines remain unchanged and authenticated.
    """
    assert show_scope(custody, unit)["owned_unit_terminal_empty"], "new unit already exists"
    stdout, stderr = custody.open_raw(attempt / "scope.stdout"), custody.open_raw(attempt / "scope.stderr")
    process, code, timed_out, errors = None, None, False, []
    try:
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env)
        s.save_new(attempt / "scope-runner-birth.json", s.birth(process.pid))
        try:
            code = process.wait(timeout=840)
        except subprocess.TimeoutExpired:
            timed_out = True
            # The unique not-found-before-create unit is derived from this
            # exclusive attempt, never caller PID/name, original N4 or siblings.
            custody.stop_owned(process, unit, errors)
            code = process.wait(timeout=10)
    except BaseException as error:
        errors.append({"stage": "scope_spawn_or_wait", "error": repr(error)})
        if process is not None and process.poll() is None:
            try:
                custody.stop_owned(process, unit, errors)
                code = process.wait(timeout=10)
            except BaseException as cleanup:
                errors.append({"stage": "owned_new_scope_cleanup", "error": repr(cleanup)})
    finally:
        s.save_new(attempt / "scope-wait.json", {"at": s.utc_now(), "argv": command,
            "pid": process.pid if process else None, "returncode": code, "timed_out": timed_out,
            "errors_before_retention": list(errors), "actual_Popen_wait": code is not None,
            "meaning": "Only actual wait is a wait; native diagnostic exit1 is deliberately nonpassing"})
        for name, stream in (("stdout", stdout), ("stderr", stderr)):
            for step, operation in (("flush", stream.flush), ("fsync", lambda stream=stream: os.fsync(stream.fileno())), ("close", stream.close)):
                try:
                    operation()
                except BaseException as error:
                    errors.append({"stage": name + "_" + step, "error": repr(error)})
        s.save_new(attempt / "scope-retention.json", {"at": s.utc_now(), "errors": errors,
            "complete": not errors and code is not None,
            "stdout": s.pin(attempt / "scope.stdout"), "stderr": s.pin(attempt / "scope.stderr")})
    return code, timed_out, errors


def prepare(kind, review_row, ready_row, smoke_row=None):
    custody, original, value = check_frame(review_row)
    assert kind in ("native-diagnostic", "observer-control-only")
    ready = stage(value, "ready", ready_row)
    if kind == "native-diagnostic":
        smoke = s.read(s.external(smoke_row))
        assert smoke["schema"] == "worldline-N67-inner-observation-actual-terminal-collection-v1"
        assert smoke["kind"] == "observer-control-only" and smoke["release_ready"] is True
        assert smoke["actual_observer_machinery_control_pass"] is True
        assert smoke["manifest"] == s.pin(s.F / "manifest.json") and smoke["identity"] == s.pin(s.F / "identity.json")
        control_attempt = Path(smoke["attempt"])
        control_unit = unit_for(control_attempt)
        acknowledgment_path = control_attempt / "actual-release-acknowledgment.json"
        s.pin(acknowledgment_path)
        acknowledgment = s.read(acknowledgment_path)
        assert acknowledgment["schema"] == "worldline-N67-inner-observation-exact-release-acknowledgment-v1"
        assert acknowledgment["actual_terminal_collection"] == smoke_row
        assert acknowledgment["only_owned_new_diagnostic_window_released"] is True
        release = s.read(s.external(acknowledgment["actual_Main_release_confirmation"]))
        assert release["schema"] == "worldline-N67-inner-observation-Main-actual-release-confirmation-v1"
        assert release["observer"] == "Main" and release["source_tool"] == "functions.edit"
        assert release["actual_terminal_collection"] == smoke_row
        assert release["only_owned_new_diagnostic_window_released"] is True
        assert release["actual_edit_tool_response"] and release["phase_acceptance"] is False
        released = s.read(s.external(release["actual_released_window_snapshot"]))
        assert released == s.read(custody.WINDOW)
        assert released["status"] == "released" and released["candidate"] == str(s.F)
        assert released["holder_task"] == value["controller_profile"]["required_window_holder"]
        assert show_scope(custody, control_unit)["owned_unit_terminal_empty"]
    else:
        assert smoke_row is None
    root = s.F / "attempts"
    root.mkdir(exist_ok=True)
    attempt = root / uuid.uuid4().hex
    attempt.mkdir(mode=0o700)
    custody.check_storage(attempt, "prepare")
    custody.check_no_sibling_lane(attempt, "prepare")
    observed = custody.memory_kb()
    challenge = {"at": s.utc_now(), "candidate": str(s.F), "kind": "BOUNDED_CHECKED_RUNTIME_MEMORY_CHALLENGE",
        "target_kind": kind, "source_selection_sha256": original["pins"]["source_selection"]["sha256"],
        "MemAvailable_observed_kB": observed, "expression": f"{observed}*1024-8589934592-8589934592",
        "reviewed_fixed_minimum_kB": 16777217, "no_target_launch_executed": True,
        "no_acceptance": True, "emitted_frame_review": review_row, "ready_guard": ready,
        "actual_affected_control_smoke": smoke_row}
    s.save_new(attempt / "challenge.json", challenge)
    print(json.dumps({"attempt": str(attempt), "challenge": s.pin(attempt / "challenge.json"),
                      "expression": challenge["expression"], "target_execution": False}, sort_keys=True))


def execute(attempt, receipt_row, reserve_row, dispatch_row):
    unit = unit_for(attempt)
    challenge = s.read(attempt / "challenge.json")
    custody, original, value = check_frame(challenge["emitted_frame_review"])
    reserve, dispatch = stage(value, "reserve", reserve_row), stage(value, "dispatch", dispatch_row)
    assert attempt.is_dir() and not attempt.is_symlink() and not (attempt / "launch-claim.json").exists()
    custody.check_no_sibling_lane(attempt, "execute")
    window_row = window(custody, value, attempt, "execute")
    custody.checked_receipt(attempt, s.external(receipt_row))
    observed = custody.memory_kb()
    assert observed >= 16777217
    custody.check_storage(attempt, "execute")
    assert int(Path("/proc/sys/kernel/yama/ptrace_scope").read_text().strip()) in (0, 1)
    command = scope_argv(attempt, unit)
    s.save_new(attempt / "launch-claim.json", {"at": s.utc_now(), "unit": unit,
        "candidate": str(s.F), "target_kind": challenge["target_kind"], "scope_argv": command,
        "manifest": s.pin(s.F / "manifest.json"), "identity": s.pin(s.F / "identity.json"),
        "emitted_frame_review": challenge["emitted_frame_review"], "challenge": s.pin(attempt / "challenge.json"),
        "memory_receipt": s.pin(attempt / "memory-receipt.json"), "window": window_row,
        "fresh_MemAvailable_observed_kB": observed, "reserve_guard": reserve, "dispatch_guard": dispatch,
        "scope_environment": custody.environment(original), "target_environment": value["exact_target_environment"],
        "build_argv": None, "no_build_or_proof_executed": True,
        "retained_original_build_deadline_seconds": 600, "original_whole_controls_seconds": 180,
        "original_scope_seconds": 840, "required_Main_outer_seconds": 1000,
        "no_full_runtime_or_phase_acceptance": True})
    code, timed_out, errors = run_scope(custody, attempt, command, custody.environment(original), unit)
    s.save_new(attempt / "scope-terminal.json", {"at": s.utc_now(), "scope_wait": code,
        "scope_timed_out": timed_out, "retention_errors": errors,
        "actual_owned_scope_observation": show_scope(custody, unit),
        "Main_actual_outer_wait_still_required": True, "phase_acceptance": False})
    print(json.dumps({"attempt": str(attempt), "scope_wait": code, "scope_timed_out": timed_out,
        "native_diagnostic_is_nonpassing": True, "actual_collection_and_release_required": True}, sort_keys=True))
    raise SystemExit(1 if challenge["target_kind"] == "native-diagnostic" or code != 0 or timed_out or errors else 0)


def child(attempt):
    unit = unit_for(attempt)
    claim = s.read(attempt / "launch-claim.json")
    custody, original, value = check_frame(claim["emitted_frame_review"])
    assert claim["unit"] == unit and claim["scope_argv"] == scope_argv(attempt, unit)
    assert claim["manifest"] == s.pin(s.F / "manifest.json") and claim["identity"] == s.pin(s.F / "identity.json")
    assert claim["challenge"] == s.pin(attempt / "challenge.json") and claim["memory_receipt"] == s.pin(attempt / "memory-receipt.json")
    actual_argv = [item.decode() for item in Path("/proc/self/cmdline").read_bytes().split(b"\0") if item]
    assert actual_argv == claim["scope_argv"][-5:]
    window(custody, value, attempt, "child")
    env = dict(word.decode().split("=", 1) for word in Path("/proc/self/environ").read_bytes().split(b"\0") if word)
    assert env == claim["scope_environment"]
    birth = s.birth(os.getpid())
    relative = next(row[3:] for row in birth["cgroup_raw"].splitlines() if row.startswith("0::"))
    assert Path(relative).name == unit
    group = Path("/sys/fs/cgroup") / relative.lstrip("/")
    assert (group / "memory.max").read_text().strip() == "8589934592"
    assert (group / "memory.swap.max").read_text().strip() == "0"
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    s.save_new(attempt / "effective-child-limits.json", {"at": s.utc_now(), "process_birth": birth,
        "memory.max": "8589934592", "memory.swap.max": "0", "rlimit_core": list(resource.getrlimit(resource.RLIMIT_CORE))})
    capture = s.verify_capture(value["original_capture"])
    import integrity
    import runtime_inventory
    custody.closure_observation(original, attempt, "before")
    s.save_new(attempt / "before-observer-closure.json", runtime_inventory.observe(capture["debugger_closure"]["spec"]))
    assert s.read(attempt / "before-observer-closure.json") == capture["debugger_closure"]["inventory"]
    before_outputs = custody.output_inventory(original)
    s.save_new(attempt / "original-compiled-outputs-before.json", before_outputs)
    try:
        if claim["target_kind"] == "observer-control-only":
            import control_smoke
            control_pass = control_smoke.run(attempt, unit, value, custody)
        else:
            assert claim["target_kind"] == "native-diagnostic"
            import native_observation
            native_observation.run(attempt, unit, value, custody)
            control_pass = False
    finally:
        custody.closure_observation(original, attempt, "after")
        s.save_new(attempt / "after-observer-closure.json", runtime_inventory.observe(capture["debugger_closure"]["spec"]))
        assert s.read(attempt / "after-observer-closure.json") == capture["debugger_closure"]["inventory"]
        assert custody.output_inventory(original) == before_outputs == capture["original_compiled_outputs"]
        assert integrity.snapshot(s.F / "source", custody.SOURCE_OUTPUT_DIRS) == capture["source_snapshot"]
        assert integrity.snapshot(s.F / "private-sparklib", custody.DEPENDENCY_OUTPUT_DIRS) == capture["private_snapshot"]
        assert s.pin(s.F / "source/lib/libworldline_core.so") == value["diagnostic_library"]
        check_frame(claim["emitted_frame_review"])
    s.save_new(attempt / "child-outcome.json", {"at": s.utc_now(), "target_kind": claim["target_kind"],
        "actual_machinery_control_pass": control_pass, "source_and_original_compiled_outputs_unchanged": True,
        "strict_proof": False, "whole_runtime_acceptance": False, "native_abi_acceptance": False,
        "fixture_authority": False, "phase_acceptance": False, "timeout_resolution": False})
    raise SystemExit(0 if claim["target_kind"] == "observer-control-only" and control_pass else 1)


def collect(attempt, collect_row, outer_row, output_path):
    unit = unit_for(attempt)
    claim = s.read(attempt / "launch-claim.json")
    custody, original, value = check_frame(claim["emitted_frame_review"])
    guard = stage(value, "collect", collect_row)
    outer = s.read(s.external(outer_row))
    assert outer["schema"] == "worldline-N67-inner-observation-Main-actual-outer-wait-v1"
    assert outer["observer"] == "Main" and outer["source_tool"] == "functions.bash"
    assert outer["attempt"] == str(attempt) and outer["actual_argv"] == ["/usr/bin/python3", "-B", str(s.F / "native_custody.py"), "execute", str(attempt), outer["memory_receipt_argument"], outer["reserve_observation_argument"], outer["dispatch_observation_argument"]]
    assert outer["actual_timeout_seconds"] == 1000 and outer["actual_wait_observed"] is True
    assert type(outer["actual_returncode"]) is int and outer["actual_tool_response"]
    captured_wait = s.read(s.external(outer["Main_actual_wait_capture"]))
    assert captured_wait["schema"] == "worldline-N67-inner-observation-Main-actual-child-wait-v1"
    assert captured_wait["observer"] == "Main" and captured_wait["mode"] == "execute"
    expected_wrapper = ["/usr/bin/python3", "-B", str(s.F / "Main_wait.py"), "execute", str(attempt), outer["memory_receipt_argument"], outer["reserve_observation_argument"], outer["dispatch_observation_argument"], outer["Main_actual_wait_capture"]["path"]]
    assert captured_wait["actual_wrapper_argv"] == outer["actual_wrapper_argv"] == expected_wrapper
    assert captured_wait["actual_wrapper_source"] == s.pin(s.F / "Main_wait.py")
    assert captured_wait["actual_child_argv"] == outer["actual_argv"]
    assert captured_wait["original_Main_tool_timeout_seconds"] == 1000
    assert captured_wait["original_native_scope_seconds"] == 840 and captured_wait["original_whole_controls_seconds"] == 180
    assert captured_wait["owned_scope"] == unit and captured_wait["original_owned_scope_preimage"]["owned_unit_terminal_empty"] is True
    assert captured_wait["actual_Popen_wait_observed"] is True and captured_wait["actual_returncode"] == outer["actual_returncode"]
    assert captured_wait["retention_complete"] is True and captured_wait["timed_out"] is False and not captured_wait["errors"]
    assert captured_wait["provider_numeric_exit_inferred"] is False and captured_wait["actual_elapsed_seconds"] <= 1000
    invocation = outer["actual_Main_tool_invocation"]
    assert invocation["source_tool"] == "functions.bash"
    assert invocation["arguments"]["command"] == shlex.join(expected_wrapper) and invocation["arguments"]["timeout"] == 1000
    for row in captured_wait["raw_streams"].values():
        s.external(row)
    properties = show_scope(custody, unit)
    assert properties["owned_unit_terminal_empty"], "never release while exact owned scope is nonempty"
    wait = s.read(attempt / "scope-wait.json")
    retention = s.read(attempt / "scope-retention.json")
    observation = s.read(attempt / "inner-observation.json")
    assert wait["actual_Popen_wait"] is True and wait["returncode"] is not None
    assert retention["complete"] is True
    for row in (retention["stdout"], retention["stderr"], *observation["raw_streams"].values()):
        s.match(row)
    ended = []
    births = [s.read(attempt / name) for name in ("scope-runner-birth.json", "effective-child-limits.json", "observer-birth.json", "inferior-birth.json")]
    births[1] = births[1]["process_birth"]
    births.extend((captured_wait["actual_wrapper_birth"], captured_wait["actual_child_birth"]))
    for birth in births:
        root = Path("/proc") / str(birth["pid"])
        actual = s.birth(birth["pid"]) if root.exists() else None
        live_original = actual is not None and all(actual[key] == birth[key] for key in ("pid", "boot_id", "starttime_ticks"))
        assert not live_original, "an exact newly owned process birth is still live"
        ended.append({"original_birth": birth, "proc_directory_present": root.exists(),
                      "same_original_birth_still_live": live_original, "unrelated_PID_reuse_never_signalled": True})
    before, after = s.read(attempt / "before-closure.json"), s.read(attempt / "after-closure.json")
    assert {k: v for k, v in before.items() if k != "at"} == {k: v for k, v in after.items() if k != "at"}
    assert s.read(attempt / "before-observer-closure.json") == s.read(attempt / "after-observer-closure.json")
    assert custody.output_inventory(original) == s.read(attempt / "original-compiled-outputs-before.json")
    assert custody.sha(custody.WINDOW) == claim["window"]["window_sha256"]
    assert observation["terminal_retention_complete"] is True
    control_pass = claim["target_kind"] == "observer-control-only" and s.read(attempt / "observer-control-smoke.json")["actual_machinery_control_pass"] is True
    expected_code = 0 if control_pass else 1
    assert outer["actual_returncode"] == expected_code and wait["returncode"] == expected_code and not wait["timed_out"]
    assert output_path.parent == s.J and not output_path.exists() and not output_path.is_symlink()
    result = {"schema": "worldline-N67-inner-observation-actual-terminal-collection-v1",
        "observer": "Main", "at": s.utc_now(), "attempt": str(attempt), "candidate": str(s.F),
        "kind": claim["target_kind"], "manifest": s.pin(s.F / "manifest.json"), "identity": s.pin(s.F / "identity.json"),
        "actual_collect_guard": guard, "actual_Main_outer_wait": outer_row, "actual_scope_wait": s.pin(attempt / "scope-wait.json"),
        "actual_owned_scope_empty_witness": properties, "actual_owned_births_ended": ended,
        "raw_native_observation": s.pin(attempt / "inner-observation.json"),
        "actual_observer_machinery_control_pass": control_pass,
        "actual_inner_stacks_observed": observation["status"] == "ACTUAL_POST_BOUNDARY_NATIVE_STACK_SNAPSHOTS_NONPASSING_DIAGNOSTIC" and len(observation["samples"]) == 3,
        "release_ready": True, "Main_exact_new_window_release_still_required": True,
        "original_full_controls_not_a_pass": True, "whole_runtime_acceptance": False,
        "strict_proof": False, "native_abi_acceptance": False, "fixture_authority": False,
        "phase_acceptance": False, "timeout_resolution": False, "no_unrelated_process_signalled": True}
    s.save_new(output_path, result)
    print(json.dumps({"terminal_collection": s.pin(output_path), "release_ready": True,
                      "runtime_or_timeout_pass": False}, sort_keys=True))


def acknowledge_release(attempt, collection_row, release_row):
    unit = unit_for(attempt)
    claim = s.read(attempt / "launch-claim.json")
    custody, original, value = check_frame(claim["emitted_frame_review"])
    collection = s.read(s.external(collection_row))
    assert collection["attempt"] == str(attempt) and collection["release_ready"] is True
    release = s.read(s.external(release_row))
    assert release["schema"] == "worldline-N67-inner-observation-Main-actual-release-confirmation-v1"
    assert release["observer"] == "Main" and release["source_tool"] == "functions.edit"
    assert release["actual_terminal_collection"] == collection_row
    assert release["only_owned_new_diagnostic_window_released"] is True
    assert release["actual_edit_tool_response"] and release["phase_acceptance"] is False
    snapshot = s.read(s.external(release["actual_released_window_snapshot"]))
    assert snapshot == s.read(custody.WINDOW)
    assert snapshot["status"] == "released" and snapshot["candidate"] == str(s.F)
    assert snapshot["holder_task"] == value["controller_profile"]["required_window_holder"]
    assert show_scope(custody, unit)["owned_unit_terminal_empty"]
    s.save_new(attempt / "actual-release-acknowledgment.json", {
        "schema": "worldline-N67-inner-observation-exact-release-acknowledgment-v1",
        "at": s.utc_now(), "actual_terminal_collection": collection_row,
        "actual_Main_release_confirmation": release_row,
        "only_owned_new_diagnostic_window_released": True,
        "runtime_acceptance": False, "phase_acceptance": False, "timeout_resolution": False})
    print(json.dumps({"actual_release_acknowledgment": s.pin(attempt / "actual-release-acknowledgment.json"),
                      "runtime_or_timeout_pass": False}, sort_keys=True))


def cli():
    assert __debug__
    args = sys.argv[1:]
    action = args[0] if args else ""
    row = lambda text: s.pin(Path(text))
    if action == "prepare" and len(args) in (4, 5):
        prepare(args[1], row(args[2]), row(args[3]), row(args[4]) if len(args) == 5 else None)
    elif action == "execute" and len(args) == 5:
        execute(Path(args[1]), row(args[2]), row(args[3]), row(args[4]))
    elif action == "child" and len(args) == 2:
        child(Path(args[1]))
    elif action == "collect" and len(args) == 5:
        collect(Path(args[1]), row(args[2]), row(args[3]), Path(args[4]))
    elif action == "acknowledge-release" and len(args) == 4:
        acknowledge_release(Path(args[1]), row(args[2]), row(args[3]))
    else:
        raise SystemExit("exact supported actions: prepare KIND FRAME_REVIEW READY_OBSERVATION [ACTUAL_CONTROL_SMOKE_COLLECTION]; execute ATTEMPT JACKAL_RECEIPT RESERVE_OBSERVATION DISPATCH_OBSERVATION; child ATTEMPT; collect ATTEMPT COLLECT_OBSERVATION ACTUAL_OUTER_WAIT OUTPUT; acknowledge-release ATTEMPT COLLECTION ACTUAL_MAIN_RELEASE")


if __name__ == "__main__":
    cli()
