"""Main-only honest wait capture for the original clock and native driver.

No generic command runner. Native target argv/custody/deadlines are unchanged.
The provider's absent numeric exit stays absent: this records an actual Popen
child wait, separately from the actual Main tool invocation/completion.
"""
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

import observation_support as s

CLOCK_ARGV = ["/usr/bin/date", "-u", "+%Y-%m-%d %H:%M:%S UTC"]
CLOCK_COMMAND = "/usr/bin/date -u '+%Y-%m-%d %H:%M:%S UTC'"


def main():
    assert __debug__ and sys.argv[1] in ("clock", "execute")
    mode = sys.argv[1]
    started = time.monotonic()
    outer_argv = [word.decode() for word in Path("/proc/self/cmdline").read_bytes().split(b"\0") if word]
    assert outer_argv[:3] == ["/usr/bin/python3", "-B", str(s.D / "Main_wait.py")]
    if mode == "clock":
        assert len(sys.argv) == 3
        argv, output, total_budget, unit = CLOCK_ARGV, Path(sys.argv[2]), 30, None
        custody = None
    else:
        assert len(sys.argv) == 7 and s.D == s.F
        import native_custody
        attempt = Path(sys.argv[2])
        unit = native_custody.unit_for(attempt)
        assert (attempt / "challenge.json").is_file() and not (attempt / "launch-claim.json").exists()
        custody, original = s.inherited()
        preimage = native_custody.show_scope(custody, unit)
        assert preimage["owned_unit_terminal_empty"], "never adopt an existing unit"
        argv = ["/usr/bin/python3", "-B", str(s.F / "native_custody.py"), "execute"] + sys.argv[2:6]
        output, total_budget = Path(sys.argv[6]), 1000
    assert output.is_absolute() and output.parent == s.J and not output.exists() and not output.is_symlink()
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    raw_paths = {label: output.with_name(output.name + "." + label + ".raw") for label in ("stdout", "stderr")}
    raw = {}
    process = None
    pidfd = None
    code = None
    timed_out = False
    errors = []
    stop_evidence = None
    receipt = {"schema": "worldline-N67-inner-observation-Main-actual-child-wait-v1",
        "observer": "Main", "mode": mode, "at": s.utc_now(),
        "actual_wrapper_argv": outer_argv, "actual_wrapper_source": s.pin(s.D / "Main_wait.py"),
        "actual_wrapper_birth": s.birth(os.getpid()), "actual_child_argv": argv,
        "actual_clock_command": CLOCK_COMMAND if mode == "clock" else None,
        "original_Main_tool_timeout_seconds": total_budget,
        "original_native_scope_seconds": 840 if mode == "execute" else None,
        "original_whole_controls_seconds": 180 if mode == "execute" else None,
        "owned_scope": unit, "original_owned_scope_preimage": preimage if mode == "execute" else None,
        "provider_numeric_exit_inferred": False, "phase_acceptance": False,
        "runtime_acceptance": False, "timeout_resolution": False}
    try:
        for label, path in raw_paths.items():
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
            raw[label] = os.fdopen(descriptor, "wb")
        process = subprocess.Popen(argv, stdout=raw["stdout"], stderr=raw["stderr"])
        child_birth = s.birth(process.pid)
        assert child_birth["ppid"] == os.getpid()
        receipt["actual_child_birth"] = child_birth
        pidfd = os.pidfd_open(process.pid)
        s.same_birth(child_birth)
        # The unchanged outer cap includes finite original cleanup, not a
        # second fresh 1000-second allowance. This supervisor housekeeping
        # watchdog never resets/reduces native whole180 or scope840 timers.
        reserve = 20 if mode == "clock" else 100
        remaining = started + total_budget - reserve - time.monotonic()
        assert remaining > 0, "preflight exhausted unchanged Main outer budget"
        try:
            code = process.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            timed_out = True
            if mode == "execute":
                # Exact fresh unit was absent before this newly created
                # driver. Only its actual own claim may authorize old custody.
                claim = s.read(attempt / "launch-claim.json")
                assert claim["unit"] == unit and claim["candidate"] == str(s.F)
                assert claim["scope_argv"] == native_custody.scope_argv(attempt, unit)
                runner = s.read(attempt / "scope-runner-birth.json")
                assert runner["ppid"] == child_birth["pid"]
                stop_evidence = []
                custody.stop_owned(process, unit, stop_evidence)
            else:
                s.same_birth(child_birth)
                signal.pidfd_send_signal(pidfd, signal.SIGTERM)
            try:
                code = process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                s.same_birth(child_birth)
                signal.pidfd_send_signal(pidfd, signal.SIGKILL)
                code = process.wait(timeout=10)
    except BaseException as error:
        errors.append(repr(error))
        if process is not None:
            try:
                if process.poll() is None:
                    # On an admission failure do not invent a scope claim or
                    # stop any existing target. This newly created driver only.
                    s.same_birth(child_birth)
                    signal.pidfd_send_signal(pidfd, signal.SIGTERM)
                    try:
                        code = process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        s.same_birth(child_birth)
                        signal.pidfd_send_signal(pidfd, signal.SIGKILL)
                        code = process.wait(timeout=10)
                else:
                    code = process.wait(timeout=10)
            except BaseException as cleanup_error:
                errors.append(repr(cleanup_error))
    finally:
        if pidfd is not None:
            os.close(pidfd)
        for stream in raw.values():
            for operation in (stream.flush, lambda stream=stream: os.fsync(stream.fileno()), stream.close):
                try:
                    operation()
                except BaseException as error:
                    errors.append(repr(error))
        receipt.update({"actual_Popen_wait_observed": code is not None,
            "actual_returncode": code, "actual_elapsed_seconds": time.monotonic() - started,
            "timed_out": timed_out, "errors": errors, "actual_owned_stop_evidence": stop_evidence,
            "raw_streams": {label: s.pin(path) for label, path in raw_paths.items() if path.is_file()},
            "retention_complete": code is not None and not errors and len(raw) == 2,
            "actual_Main_provider_invocation_and_completion_still_required": True})
        s.save_new(output, receipt)
    if mode == "clock" and receipt["retention_complete"] and not timed_out and code == 0:
        stdout = raw_paths["stdout"].read_bytes()
        assert stdout.endswith(b"\n") and stdout.count(b"\n") == 1 and len(stdout) < 64
        sys.stdout.write(stdout.decode())
    print(json.dumps({"actual_Main_child_wait_capture": s.pin(output),
                      "numeric_provider_exit_not_inferred": True,
                      "runtime_or_timeout_pass": False}, sort_keys=True))
    raise SystemExit(code if type(code) is int and not errors and not timed_out else 1)


if __name__ == "__main__":
    main()
