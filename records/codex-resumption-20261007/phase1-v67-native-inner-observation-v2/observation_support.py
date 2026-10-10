"""Source-only inputs. Main alone may import/run after exact independent review.

Reuse the qualified N4 native custody module; do not rebind its globals or use its
build/test entrypoints. New diagnostic namespace, controller and observer gates
are explicit and cannot supply any original runtime/proof/fixture acceptance.
"""
from __future__ import annotations

import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import stat
import sys

sys.dont_write_bytecode = True
D = Path(__file__).resolve().parent
P = D if D.name.endswith("-preparation") else D.parent / (D.name + "-preparation")
INPUTS = json.loads((P / "inputs.json").read_text())
R = Path(INPUTS["records_root"])
N4 = R / INPUTS["original_root_name"]
A4 = N4 / "attempts" / INPUTS["original_attempt_name"]
F = R / INPUTS["future_frame_name"]
J = R / INPUTS["main_observation_root_name"]
MODEL = INPUTS["current_review_model"]
AUTHOR = INPUTS["author"]
STAGES = frozenset(("preparation", "ready", "reserve", "dispatch", "collect"))
SCOPE_PREFIX = "codex-worldline-" + F.name + "-"
GDB = Path(INPUTS["debugger_locator"])


def read(path):
    return json.loads(Path(path).read_text())


def pin(path):
    p = Path(path)
    assert p.is_absolute() and p.resolve(strict=True) == p, str(p)
    first = p.lstat()
    assert stat.S_ISREG(first.st_mode) and not p.is_symlink(), str(p)
    with p.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    last = p.lstat()
    fields = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    assert fields(first) == fields(last), "changed during pin: " + str(p)
    return {"path": str(p), "sha256": digest, "bytes": last.st_size,
            "mode": stat.S_IMODE(last.st_mode)}


def match(row):
    assert set(row) == {"path", "sha256", "bytes", "mode"}
    p = Path(row["path"])
    assert pin(p) == row, str(p)
    return p


def external(row):
    p = match(row)
    assert p.is_relative_to(J) and J.resolve(strict=True) == J
    assert not set(p.relative_to(J).parts) & {"source", "private-sparklib", "__pycache__", "worker", "workers", ".cache", "tool-cache"}
    return p


def save_new(path, value):
    path = Path(path)
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    save_bytes_new(path, raw, 0o600)


def save_bytes_new(path, raw, mode):
    path = Path(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    folder = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(folder)
    finally:
        os.close(folder)


def inherited():
    assert __debug__, "assertions may not be disabled"
    for name, expected in INPUTS["original_pins"].items():
        assert {key: value for key, value in pin(N4 / name).items() if key != "path"} == expected, name
    original = read(N4 / "manifest.json")
    # Import only exact qualified custody code. No target, build, test or provider
    # is imported by this function. N4 remains the original immutable namespace.
    spec = importlib.util.spec_from_file_location("qualified_N4_custody", N4 / "validate.py")
    custody = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(custody)
    custody.check_identity(original)
    before, after = read(A4 / "before-closure.json"), read(A4 / "after-closure.json")
    assert {k: v for k, v in before.items() if k != "at"} == {k: v for k, v in after.items() if k != "at"}
    terminal = read(A4 / "terminal-collection.json")
    assert terminal["actual_build_wait"]["returncode"] == 0
    assert terminal["actual_build_wait"]["timed_out"] is False
    assert terminal["actual_test_wait"]["returncode"] == -15 and terminal["actual_test_wait"]["timed_out"] is True
    assert terminal["actual_failing_original_total_control_timeout_seconds"] == 180
    assert terminal["actual_owned_unit_terminal_empty"] is True
    assert terminal["actual_compiled_outputs_unchanged"] is True
    assert terminal["exact_native_internal_root_cause_unproven"] is True
    release = read(A4 / "window-release-actual-confirmation.json")
    assert release["only_owned_N67_v4_window_released"] is True and release["target_or_phase_acceptance"] is False
    for row in terminal["evidence"].values():
        match(row)
    for row in (release["actual_release_evidence"], release["actual_released_window_snapshot"], release["actual_terminal_collection"]):
        match(row)
    return custody, original


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def reviewed(row, kind, artifacts, inputs):
    """Consume actual independently authored opinion AND actual model companion."""
    record = read(external(row))
    assert record["schema"] == "worldline-N67-inner-observation-independent-review-v1"
    assert record["kind"] == kind and record["disposition"] == "QUALIFIED_EXACT_SOURCE_ONLY_SCOPE"
    assert record["author"] == AUTHOR and record["reviewer"] not in (AUTHOR, "Main", "")
    assert record["record_author"] == record["reviewer"] and record["reviewer_authored"] is True
    assert record["actual_model_selection"] == MODEL and record["blocking_findings"] == []
    assert record["artifacts"] == artifacts and record["inputs"] == inputs
    model = read(external(record["actual_model_companion"]))
    assert model["actual_model_selection"] == MODEL and model["resolved_model_is_fallback"] is False
    assert model["thinking_level"] == "max" and model["service_tier"] == "default" and model["advisor_enabled"] is False
    assert model["agent"] == record["reviewer"] and model["session_id"]
    assert model["actual_session_observation"] and model["actual_reply_observation"]
    required = read(P / "review-contracts.json")["required_checks"][kind]
    assert set(record["checks"]) == set(required)
    assert all(record["checks"][key] == "QUALIFIED_EXACT_BYTES" for key in required)
    for key in ("target_execution", "strict_proof", "runtime_acceptance", "phase_acceptance", "fixture_authority", "timeout_resolution"):
        assert record[key] is False, key
    return record


def recipe_artifacts():
    provenance = read(P / "author-provenance.json")
    actual = read(external(provenance["actual_Main_model_receipt"]))
    assert actual["author"] == AUTHOR and actual["actual_session_header"]["id"] == provenance["actual_session_id"]
    assert actual["resolvedModelIdentity"] + ":" + actual["resolvedThinkingLevel"] == MODEL
    assert actual["fallback_used"] is False and actual["actual_observed_provider_tiers"] == ["default"]
    assert actual["literal_Standard_wire_observation"] is False and actual["unknown_tier_relabelled"] is False
    current = read(external(provenance["actual_current_Main_model_receipt"]))
    assert current["author"] == AUTHOR and current["same_owned_worker_not_restarted"] is True
    assert current["actual_model_selection"] == MODEL and current["thinking_level"] == "max"
    assert current["resolved_model_is_fallback"] is False and current["service_tier"] == "default"
    assert current["advisor_enabled"] is False and current["required_configured_speed"] == "Standard"
    assert current["literal_Standard_wire_observed"] is False
    assert current["actual_session_and_model_thinking_events"][0]["id"] == provenance["actual_session_id"]
    assert current["actual_current_provider_replies"]
    assert all(row["message"]["provider"] == "openai-codex" and row["message"]["model"] == "gpt-6.1-sol"
               and row["message"]["serviceTier"] == "default" and row["message"]["errorMessage"] is None
               for row in current["actual_current_provider_replies"])
    names = read(P / "author-handoff.json")["recipe_artifact_names"]
    return {name: pin(P / name) for name in names}


def namespace_values(value, prefix, path=()):
    """Enumerate the complete declared namespace join, not a new observation."""
    if isinstance(value, dict):
        for key, member in value.items():
            assert prefix not in key, "unqualified captured namespace dictionary key"
            yield from namespace_values(member, prefix, path + (key,))
    elif isinstance(value, list):
        for index, member in enumerate(value):
            yield from namespace_values(member, prefix, path + (index,))
    elif isinstance(value, str) and prefix in value:
        yield path, value


def capture_namespace_view(capture, row):
    assert row == INPUTS["retained_original_capture"], "reuse only the exact actual original capture"
    binding_path = match(INPUTS["capture_reuse_binding"])
    assert binding_path == P / "capture-reuse-binding.json"
    binding = read(binding_path)
    previous = R / INPUTS["predecessor_frame_name"]
    assert binding["schema"] == "worldline-N67-inner-observation-authenticated-capture-namespace-reuse-v1"
    assert binding["original_capture"] == row and binding["predecessor_frame"] == str(previous)
    assert binding["successor_frame"] == str(F) and binding["namespace_dictionary_keys"] == []
    assert binding["new_capture_result"] is False and binding["target_execution"] is False
    assert capture["gdb_initialization"] == gdb_initialization(previous)
    joins = binding["scalar_relocations"]
    expected = {tuple(item["path"]): item["before"] for item in joins}
    assert len(expected) == len(joins) and dict(namespace_values(capture, str(previous))) == expected
    for item in joins:
        parent = capture
        for key in item["path"][:-1]:
            parent = parent[key]
        key = item["path"][-1]
        assert parent[key] == item["before"]
        assert item["after"] == item["before"].replace(str(previous), str(F))
        parent[key] = item["after"]
    assert not list(namespace_values(capture, str(previous)))
    assert capture["gdb_initialization"] == gdb_initialization(F)
    return capture


def verify_capture(row):
    assert row == INPUTS["retained_original_capture"]
    capture = read(external(row))
    assert capture["schema"] == "worldline-N67-inner-observation-original-capture-v1"
    assert capture["observer"] == "Main" and capture["target_execution"] is False
    assert capture["original_manifest"] == pin(N4 / "manifest.json")
    assert capture["original_identity"] == pin(N4 / "identity.json")
    assert capture["retained_library"] == pin(A4 / "built-libworldline_core.so")
    assert capture["original_terminal"] == pin(A4 / "terminal-collection.json")
    assert capture["original_release"] == pin(A4 / "window-release-actual-confirmation.json")
    assert capture["actual_debugger_metadata"] == read(P / "author-provenance.json")["actual_Main_debugger_metadata_receipt"]
    metadata = read(external(capture["actual_debugger_metadata"]))
    assert metadata["configuration_and_version_successful_tool_completion_observed"] is True
    assert metadata["actual_target_or_debug_session_launched"] is False
    assert all(option in metadata["actual_completion_event"]["content"] for option in ("--without-python", "--without-guile", "--without-debuginfod"))
    assert capture["debugger"]["sha256"] == INPUTS["retained_debugger_sha256"]
    match(capture["debugger"])
    assert capture["ptrace_scope"] in (0, 1), "no policy relaxation; parent tracing must already be allowed"
    for metadata_row in capture["metadata_outputs"].values():
        external(metadata_row)
    closure = capture["debugger_closure"]
    assert str(GDB) in closure["inventory"]["required_native_closed_graph"]
    assert str(A4 / "built-libworldline_core.so") in closure["inventory"]["required_native_closed_graph"]
    assert closure["inventory"]["unresolved_optional_native_dependencies"] == closure["inherited_unresolved_optional_native_dependencies"], "new unresolved observer input"
    assert capture["gdb_initialization"] == gdb_initialization(R / INPUTS["predecessor_frame_name"])
    assert capture["source_snapshot_digest"] == digest(capture["source_snapshot"])
    assert capture["private_snapshot_digest"] == digest(capture["private_snapshot"])
    return capture_namespace_view(capture, row)


def gdb_initialization(frame):
    return ["set auto-load off", "set auto-load safe-path /nonexistent-N67-observer-autoload",
            "set index-cache enabled off",
            "set startup-with-shell off", "set pagination off", "set confirm off",
            "set print frame-arguments none", "set print entry-values no",
            "set backtrace limit 64", "set language c", "set detach-on-fork on",
            "set follow-fork-mode parent", "set follow-exec-mode same",
            "set disable-randomization off", "set debug-file-directory " + str(frame / "empty-debug"),
            "set libthread-db-search-path " + str(frame / "empty-debug"),
            "handle SIGINT stop noprint nopass", "handle SIGTERM nostop noprint pass"]


def gdb_prefix(frame):
    argv = [str(GDB), "--nh", "--nx", "--quiet", "--interpreter=mi2",
            "--data-directory=" + str(GDB.parent.parent / "share/gdb")]
    for command in gdb_initialization(frame):
        argv.extend(("-iex", command))
    return argv


def target_environment(custody, original):
    env = custody.environment(original)
    old_source = str(N4 / "source")
    old_private = str(N4 / "private-sparklib")
    result = {key: value.replace(old_source, str(F / "source")).replace(old_private, str(F / "private-sparklib"))
              for key, value in env.items()}
    assert result["WORLDLINE_BUILD"] == "checks"
    assert result["WORLDLINE_CORE_LIB"] == str(F / "source/lib/libworldline_core.so")
    for key in ("LD_AUDIT", "LD_PRELOAD", "LD_LIBRARY_PATH", "PYTHONHOME", "PYTHONOPTIMIZE", "PYTHONPYCACHEPREFIX", "PYTHONUSERBASE"):
        assert key not in result, key
    return result


def birth(pid):
    root = Path("/proc") / str(pid)
    raw = (root / "stat").read_text()
    close = raw.rfind(")")
    assert int(raw.split(" ", 1)[0]) == pid and close > 0
    fields = raw[close + 2:].split()
    status = (root / "status").read_text()
    return {"pid": pid, "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
            "starttime_ticks": int(fields[19]), "ppid": int(fields[1]),
            "state": fields[0], "utime_ticks": int(fields[11]), "stime_ticks": int(fields[12]),
            "clock_ticks_per_second": os.sysconf("SC_CLK_TCK"), "stat_raw": raw,
            "status_raw": status, "cgroup_raw": (root / "cgroup").read_text(),
            "cmdline_hex": (root / "cmdline").read_bytes().hex()}


def same_birth(expected):
    actual = birth(expected["pid"])
    assert all(actual[k] == expected[k] for k in ("pid", "boot_id", "starttime_ticks")), "PID recycled"
    return actual


def owned_pidfd(expected, unit, parent=None):
    actual = same_birth(expected)
    relative = next(row[3:] for row in actual["cgroup_raw"].splitlines() if row.startswith("0::"))
    assert Path(relative).name == unit and unit.startswith(SCOPE_PREFIX)
    if parent is not None:
        assert actual["ppid"] == parent, "not this observer's newly created child"
    fd = os.pidfd_open(expected["pid"])
    try:
        same_birth(expected)
        return fd
    except BaseException:
        os.close(fd)
        raise


def signal_owned(fd, expected, unit, signo):
    assert signo in (signal.SIGTERM, signal.SIGKILL)
    actual = same_birth(expected)
    relative = next(row[3:] for row in actual["cgroup_raw"].splitlines() if row.startswith("0::"))
    assert Path(relative).name == unit and unit.startswith(SCOPE_PREFIX)
    signal.pidfd_send_signal(fd, signo)


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def control_argv():
    return ["/usr/bin/python3", "-I", "-S", "-c",
            "import os,stat,sys; fd=int(os.environ['WORLDLINE_NATIVE_TRANSACTION_OBSERVATION_PENDING_FD']); "
            "assert fd>2 and stat.S_ISREG(os.fstat(fd).st_mode); "
            "os.write(fd,b'OBSERVER_CONTROL_ONLY_REGULAR_FD\\n'); "
            "print('OBSERVER_CONTROL_ONLY'); print('OBSERVER_CONTROL_STDERR_ONLY',file=sys.stderr)"]
