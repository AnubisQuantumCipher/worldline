"""Bounded GDB/MI observation of ONLY the newly launched owned inferior.

No attach, breakpoints in the native diagnostic, inferior function calls,
variables/arguments, writes to target memory, source changes, performance cure,
or test selection. Three real stopped stacks and actual /proc CPU ticks after
the existing native boundary; every diagnostic outcome remains nonpassing.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import select
import signal
import subprocess
import time

import observation_support as s


class MI:
    def __init__(self, process, stream, deadline):
        self.process, self.stream, self.deadline = process, stream, deadline
        self.buffer = b""
        self.lines = []
        self.results = {}
        self.number = 0
        self.volume = 0
        self.started_pid = None
        self.exited = False
        self.stopped_sequence = 0
        self.target_terminal_rows = []
        os.set_blocking(process.stdout.fileno(), False)

    def pump(self, seconds=0.05):
        assert time.monotonic() < self.deadline, "original whole-controls deadline"
        readable, _, _ = select.select([self.process.stdout], [], [], min(seconds, max(0, self.deadline - time.monotonic())))
        if not readable:
            return
        data = os.read(self.process.stdout.fileno(), 65536)
        if not data:
            assert self.process.poll() is None, "debugger exited before the requested observation"
            return
        self.stream.write(data)
        self.volume += len(data)
        assert self.volume <= 8 * 1024 * 1024, "bounded observer raw-stream volume exceeded"
        self.buffer += data
        assert len(self.buffer) <= 1024 * 1024, "unbounded MI line"
        while b"\n" in self.buffer:
            raw, self.buffer = self.buffer.split(b"\n", 1)
            line = raw.decode("utf-8", errors="strict").rstrip("\r")
            self.lines.append(line)
            assert len(self.lines) <= 32768, "bounded MI record volume exceeded"
            result = re.match(r"^(\d+)\^(done|running|exit|error)(?:,|$)", line)
            if result:
                self.results[int(result[1])] = (result[2], line)
            started = re.fullmatch(r'=thread-group-started,id="i1",pid="(\d+)"', line)
            if started:
                pid = int(started[1])
                assert self.started_pid in (None, pid), "unexpected additional inferior"
                self.started_pid = pid
            if line.startswith("*stopped,"):
                self.stopped_sequence += 1
            if line.startswith("=thread-group-exited,") or (line.startswith("*stopped,") and "reason=\"exited" in line):
                self.target_terminal_rows.append(line)
                self.exited = True

    def command(self, command, expected=("done",), timeout=5):
        assert "\n" not in command and "\r" not in command
        self.number += 1
        token = self.number
        self.process.stdin.write((str(token) + command + "\n").encode())
        self.process.stdin.flush()
        end = min(self.deadline, time.monotonic() + timeout)
        while token not in self.results:
            assert time.monotonic() < end, "bounded MI command did not finish: " + command
            self.pump()
        kind, line = self.results.pop(token)
        assert kind in expected, line
        return line

    def console(self, command):
        return self.command("-interpreter-exec console " + json.dumps(command))

    def stopped_after(self, previous):
        end = min(self.deadline, time.monotonic() + 5)
        while self.stopped_sequence == previous and not self.exited:
            assert time.monotonic() < end, "actual native stop event unavailable"
            self.pump()
        assert not self.exited, "inferior exited before native snapshot"


def mapped_files(pid, capture, *, target_library=None):
    raw = (Path("/proc") / str(pid) / "maps").read_text()
    admitted = capture["debugger_closure"]["inventory"]["files"]
    mappings = []
    for line in raw.splitlines():
        columns = line.split(None, 5)
        if len(columns) != 6 or not columns[5].startswith("/"):
            continue
        assert not columns[5].endswith(" (deleted)"), "mapped input deleted"
        path = Path(columns[5])
        resolved = str(path.resolve(strict=True))
        if target_library is not None and resolved == target_library["path"]:
            s.match(target_library)
            row = target_library
        else:
            assert resolved in admitted, "unclosed mapped debugger/target input: " + resolved
            expected = admitted[resolved]
            observed = s.pin(Path(resolved))
            assert {k: observed[k] for k in ("sha256", "bytes", "mode")} == {k: expected[k] for k in ("sha256", "bytes", "mode")}
            row = observed
        start, end = (int(item, 16) for item in columns[0].split("-"))
        major, minor = (int(item, 16) for item in columns[3].split(":"))
        st = path.stat()
        assert int(columns[4]) == st.st_ino and os.makedev(major, minor) == st.st_dev
        mappings.append({"start": start, "end": end, "permissions": columns[1],
            "offset": int(columns[2], 16), "device": columns[3], "inode": int(columns[4]), "file": row})
    if target_library is not None:
        assert any(row["file"] == target_library and "x" in row["permissions"] for row in mappings), "actual diagnostic library mapping absent"
    return {"raw": raw, "mappings": mappings}


def target_proof(expected, gdb_pid, unit, manifest, attempt):
    actual = s.same_birth(expected)
    assert actual["ppid"] == gdb_pid
    root = Path("/proc") / str(expected["pid"])
    argv = [word.decode() for word in (root / "cmdline").read_bytes().split(b"\0") if word]
    assert argv == manifest["exact_target_argv"], "actual target argv not the complete original control runner"
    assert str((root / "cwd").resolve(strict=True)) == manifest["source"]
    admission = s.read(attempt / "inferior-exec-admission.json")
    assert admission["pid"] == expected["pid"] and admission["ppid"] == gdb_pid
    expected_env = dict(manifest["exact_target_environment"])
    expected_env["WORLDLINE_NATIVE_TRANSACTION_OBSERVATION_PENDING_FD"] = str(admission["native_fd"])
    env = dict(word.decode().split("=", 1) for word in (root / "environ").read_bytes().split(b"\0") if word)
    assert env == expected_env, "actual exec environment differs; no silent GDB environment mutation"
    relative = next(row[3:] for row in actual["cgroup_raw"].splitlines() if row.startswith("0::"))
    assert Path(relative).name == unit
    assert actual["clock_ticks_per_second"] > 0
    return {"process_birth_and_cpu": actual, "actual_argv": argv, "actual_environment": env,
            "actual_cwd": str((root / "cwd").resolve(strict=True)), "pre_exec_admission": s.pin(attempt / "inferior-exec-admission.json")}


def boundary_rows(path):
    raw = path.read_bytes()
    assert len(raw) <= 65536, "native cold-boundary volume exceeded"
    complete = raw.split(b"\n")[:-1]
    rows = [json.loads(line) for line in complete if line]
    for row in rows:
        assert set(row) == {"kind", "phase", "monotonic_seconds", "monotonic_nanoseconds", "thread_id", "no_acceptance"}
        assert row["kind"] == "native_transaction_boundary" and row["no_acceptance"] is True
        assert type(row["thread_id"]) is int and row["thread_id"] > 0
        assert type(row["monotonic_seconds"]) is int and 0 <= row["monotonic_nanoseconds"] < 1000000000
    return raw, rows


def stream_identity(stream, path):
    st = os.fstat(stream.fileno())
    return {"path": str(path), "device": st.st_dev, "inode": st.st_ino}


def run(attempt, unit, manifest, custody, kind="native-diagnostic"):
    capture = s.verify_capture(manifest["original_capture"])
    started = time.monotonic()
    deadline = started + 180
    process = None
    gdb_birth = target_birth = None
    gdb_fd = target_fd = None
    result = {"schema": "worldline-N67-actual-inner-native-observation-v1", "kind": kind,
              "runtime_acceptance": False, "phase_acceptance": False, "timeout_resolution": False,
              "original_controls_pass": False, "status": "UNOBSERVED", "samples": [], "errors": []}
    paths = {name: attempt / filename for name, filename in (
        ("stdout", "tests.stdout"), ("stderr", "tests.stderr"), ("native_boundaries", "tests.native-boundaries.stdout"),
        ("MI", "observer.mi.stdout"), ("gdb_stderr", "observer.stderr"))}
    streams = {name: custody.open_raw(path, nonblocking=name == "native_boundaries") for name, path in paths.items()}
    mi = None
    try:
        launch = {"schema": "worldline-N67-owned-inferior-exec-v1", "attempt": str(attempt), "unit": unit,
            "target_kind": kind, "native_observation": True, "cwd": manifest["source"],
            "environment": manifest["exact_target_environment"],
            "argv": manifest["exact_target_argv"] if kind == "native-diagnostic" else
                s.control_argv(),
            "streams": {name: stream_identity(streams[name], paths[name]) for name in ("stdout", "stderr", "native_boundaries")}}
        s.save_new(attempt / "inferior-launch.json", launch)
        argv = s.gdb_prefix(s.F) + ["--args", "/usr/bin/python3", "-B", str(s.F / "target_stdio.py"), str(attempt / "inferior-launch.json")]
        s.save_new(attempt / "observer-command.json", {"at": s.utc_now(), "argv": argv,
            "cwd": manifest["source"], "environment": manifest["exact_target_environment"],
            "original_whole_controls_seconds": 180, "original_scope_seconds": 840,
            "fresh_owned_processes_only": True, "no_attach_existing": True,
            "target_argv": launch["argv"], "no_runtime_acceptance": True})
        process = subprocess.Popen(argv, cwd=manifest["source"], env=manifest["exact_target_environment"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=streams["gdb_stderr"], bufsize=0)
        gdb_birth = s.birth(process.pid)
        assert gdb_birth["ppid"] == os.getpid()
        gdb_fd = s.owned_pidfd(gdb_birth, unit, os.getpid())
        s.save_new(attempt / "observer-birth.json", gdb_birth)
        mi = MI(process, streams["MI"], deadline)
        mi.command("-gdb-set mi-async on")
        # Startup options are issued before any file/inferior load; read back
        # their actual state, preserving raw replies for independent collection.
        for setting in ("auto-load gdb-scripts", "auto-load local-gdbinit", "auto-load libthread-db", "index-cache enabled", "startup-with-shell"):
            actual_setting = mi.command("-gdb-show " + setting)
            assert 'value="off"' in actual_setting, "debugger setting not actually disabled: " + setting
        actual_debug_directory = mi.command("-gdb-show debug-file-directory")
        assert 'value="' + str(s.F / "empty-debug") + '"' in actual_debug_directory
        actual_thread_db_directory = mi.command("-gdb-show libthread-db-search-path")
        assert 'value="' + str(s.F / "empty-debug") + '"' in actual_thread_db_directory
        mapped_files(process.pid, capture)
        mi.command("-exec-run" if kind == "native-diagnostic" else "-exec-run --start", ("running",))
        while mi.started_pid is None:
            mi.pump()
        target_birth = s.birth(mi.started_pid)
        target_fd = s.owned_pidfd(target_birth, unit, process.pid)
        s.save_new(attempt / "inferior-birth.json", target_birth)
        if kind == "observer-control-only":
            mi.stopped_after(0)
            mi.console("thread apply all bt 64")
            mi.command("-exec-continue", ("running",))
            while not mi.exited:
                mi.pump()
            result["status"] = "ACTUAL_OBSERVER_CONTROL_ONLY_NO_NATIVE_EVIDENCE"
        else:
            boundary = None
            while not mi.exited:
                mi.pump()
                raw, rows = boundary_rows(paths["native_boundaries"])
                if rows and rows[-1]["phase"] == "archive_accepted_decide_enter":
                    boundary = rows[-1]
                    break
            assert boundary is not None, "actual archive_accepted_decide_enter not observed"
            assert boundary["thread_id"] == target_birth["pid"]
            boundary_time = boundary["monotonic_seconds"] + boundary["monotonic_nanoseconds"] / 1000000000
            assert started <= boundary_time <= time.monotonic(), "boundary clock/process mismatch"
            initial = target_proof(target_birth, process.pid, unit, manifest, attempt)
            s.save_new(attempt / "actual-boundary-admission.json", {"at": s.utc_now(), "boundary": boundary,
                "native_raw_at_boundary_hex": raw.hex(), "proof": initial,
                "debugger_actual_maps": mapped_files(process.pid, capture),
                "target_actual_maps": mapped_files(target_birth["pid"], capture, target_library=manifest["diagnostic_library"]),
                "cpu_ticks_are_process_cpu_not_native_function_cost": True,
                "status": "ACTUAL_BOUNDARY_NOT_HOTSPOT_OR_ACCEPTANCE"})
            for ordinal, delay in enumerate(s.INPUTS["sample_delays_after_actual_boundary_seconds"], 1):
                while time.monotonic() < boundary_time + delay and not mi.exited:
                    mi.pump()
                raw, rows = boundary_rows(paths["native_boundaries"])
                assert rows and rows[-1] == boundary, "native boundary advanced; not the same admitted inner interval"
                proof_before = target_proof(target_birth, process.pid, unit, manifest, attempt)
                previous = mi.stopped_sequence
                mi_start = streams["MI"].tell()
                interrupt_at = time.monotonic_ns()
                mi.command("-exec-interrupt --all")
                mi.stopped_after(previous)
                stopped_at = time.monotonic_ns()
                # These commands read native frames only, not values, inferior
                # calls, memory mutations, symbols guessed from source, or PCs
                # attributed to an unobserved function.
                mi.command("-thread-info")
                mi.console("thread apply all bt 64")
                mi.console("info sharedlibrary")
                proof_stopped = target_proof(target_birth, process.pid, unit, manifest, attempt)
                target_maps = mapped_files(target_birth["pid"], capture, target_library=manifest["diagnostic_library"])
                mi_stop = streams["MI"].tell()
                mi.command("-exec-continue", ("running",))
                resumed_at = time.monotonic_ns()
                sample = {"ordinal": ordinal, "requested_delay_after_boundary_seconds": delay,
                    "actual_interrupt_monotonic_ns": interrupt_at, "actual_stopped_monotonic_ns": stopped_at,
                    "actual_resume_monotonic_ns": resumed_at, "actual_boundary": boundary,
                    "MI_raw_byte_start": mi_start, "MI_raw_byte_end": mi_stop,
                    "proof_before_interrupt": proof_before, "proof_stopped": proof_stopped,
                    "target_actual_maps": target_maps,
                    "delta_cpu_ticks_since_boundary": {key: proof_stopped["process_birth_and_cpu"][key] - initial["process_birth_and_cpu"][key]
                                                     for key in ("utime_ticks", "stime_ticks")},
                    "per_function_cpu_cost_or_hotspot_percentage": "UNOBSERVED",
                    "frame_truncation_possible_at_64": True, "diagnostic_interruption_not_acceptance": True}
                s.save_new(attempt / ("native-sample-" + str(ordinal) + ".json"), sample)
                result["samples"].append(s.pin(attempt / ("native-sample-" + str(ordinal) + ".json")))
            result["status"] = "ACTUAL_POST_BOUNDARY_NATIVE_STACK_SNAPSHOTS_NONPASSING_DIAGNOSTIC"
            result["bounded_diagnostic_interrupted_after_samples"] = True
    except BaseException as error:
        result["errors"].append({"stage": "observation", "type": type(error).__name__, "error": repr(error)})
        if result["samples"]:
            result["status"] = "PARTIAL_ACTUAL_NATIVE_SNAPSHOTS_NO_COMPLETE_QUALIFICATION"
    finally:
        observation_error_count = len(result["errors"])
        # Only retained birth+pidfd+cgroup checked children are signalled. Never
        # derive PID from an existing target search or a caller-provided PID.
        if target_fd is not None and target_birth is not None:
            for signo, grace in ((signal.SIGTERM, 10), (signal.SIGKILL, 10)):
                if select.select([target_fd], [], [], 0)[0]:
                    break
                try:
                    s.signal_owned(target_fd, target_birth, unit, signo)
                    end = time.monotonic() + grace
                    if mi is not None:
                        mi.deadline = end
                    while time.monotonic() < end and not select.select([target_fd], [], [], 0)[0]:
                        if mi is not None and process.poll() is None:
                            mi.pump(0.05)
                        else:
                            time.sleep(0.05)
                except BaseException as error:
                    result["errors"].append({"stage": "owned_inferior_signal_reap", "signal": int(signo), "error": repr(error)})
            result["inferior_pidfd_terminal"] = bool(select.select([target_fd], [], [], 0)[0])
        else:
            result["inferior_pidfd_terminal"] = False
        if process is not None:
            try:
                if process.poll() is None and mi is not None:
                    mi.deadline = time.monotonic() + 5
                    mi.command("-gdb-exit", ("exit",))
                code = process.wait(timeout=10)
            except BaseException as error:
                result["errors"].append({"stage": "debugger_exit_wait", "error": repr(error)})
                code = None
                for signo in (signal.SIGTERM, signal.SIGKILL):
                    if process.poll() is not None:
                        break
                    try:
                        if gdb_fd is not None:
                            s.signal_owned(gdb_fd, gdb_birth, unit, signo)
                        else:
                            process.send_signal(signo)  # direct newly created Popen child only
                        code = process.wait(timeout=10)
                    except BaseException as error:
                        result["errors"].append({"stage": "owned_debugger_TERM_KILL_reap", "signal": int(signo), "error": repr(error)})
            result["actual_debugger_Popen_wait_returncode"] = code
            if process.stdout is not None:
                try:
                    # After actual wait the pipe is finite. Preserve remaining
                    # raw bytes, including final terminal records, before seal.
                    remaining = process.stdout.read()
                    if remaining:
                        streams["MI"].write(remaining)
                    process.stdout.close()
                    process.stdin.close()
                except BaseException as error:
                    result["errors"].append({"stage": "debugger_pipe_retention", "error": repr(error)})
        result["actual_debugger_inferior_terminal_wait_rows"] = list(mi.target_terminal_rows) if mi else []
        result["actual_inferior_wait_observed"] = bool(mi and mi.target_terminal_rows)
        for fd in (target_fd, gdb_fd):
            if fd is not None:
                os.close(fd)
        for name, stream in streams.items():
            for stage, operation in (("flush", stream.flush), ("fsync", lambda stream=stream: os.fsync(stream.fileno())), ("close", stream.close)):
                try:
                    operation()
                except BaseException as error:
                    result["errors"].append({"stage": name + "_" + stage, "error": repr(error)})
        result["raw_streams"] = {name: s.pin(path) for name, path in paths.items()}
        result["actual_elapsed_seconds"] = time.monotonic() - started
        result["observation_errors"] = result["errors"][:observation_error_count]
        result["retention_errors"] = result["errors"][observation_error_count:]
        result["terminal_retention_complete"] = not result["retention_errors"] and result.get("actual_debugger_Popen_wait_returncode") is not None and result["inferior_pidfd_terminal"] and result["actual_inferior_wait_observed"]
        s.save_new(attempt / "inner-observation.json", result)
    return result
