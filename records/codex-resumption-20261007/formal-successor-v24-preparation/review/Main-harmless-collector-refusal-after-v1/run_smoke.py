"""Main-only harmless four-level terminal consumer smoke; no GNAT or window action."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
FRAME = ROOT.parents[1]
SUPPORT = FRAME / "successor_support.py"
COLLECTOR = FRAME / "deadline-machinery-templates/review/root-terminal-v1/collect_terminal.py"
THIS = Path(__file__).resolve()
ENVIRONMENT = dict(os.environ, XDG_RUNTIME_DIR="/run/user/1000",
                   DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/1000/bus")


def pin(path):
    raw = path.read_bytes()
    return {"path": str(path), "bytes": len(raw), "mode": path.stat().st_mode & 0o7777,
            "sha256": hashlib.sha256(raw).hexdigest()}


def save(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def load(path):
    return json.loads(path.read_text()) if path.is_file() and not path.is_symlink() else None


spec = importlib.util.spec_from_file_location("harmless_c24_consumer_support", SUPPORT)
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)

if len(sys.argv) >= 3:
    stage, case = sys.argv[1], Path(sys.argv[2])
    if stage == "--prover-owner":
        row = support.capture_owned(
            [sys.executable, "-B", "-c", "print('harmless prover stand-in; no GNAT')"],
            case, "child", 2, term_seconds=1, kill_seconds=1,
            hard_deadline=time.monotonic() + 4)
        raise SystemExit(support.owner_exit_code(row))
    if stage == "--scope-owner":
        unit = sys.argv[3]
        original = {"driver": pin(THIS), "support": pin(SUPPORT)}
        argv = ["/usr/bin/systemd-run", "--user", "--scope", "--collect", "--unit=" + unit,
                "-p", "MemoryMax=8G", "-p", "MemorySwapMax=0", "-p", "RuntimeMaxSec=4s",
                "-p", "TimeoutStopSec=1s", "--", sys.executable, "-B", str(THIS),
                "--prover-owner", str(case)]
        row = support.capture_owned(argv, case, "scope", 5, env=ENVIRONMENT,
                                    term_seconds=1, kill_seconds=1,
                                    hard_deadline=time.monotonic() + 8)
        result = {"scope_wait": row["returncode"], "scope_owner_control": row,
                  "child_wait": load(case / "child-wait.json"),
                  "inputs_unchanged": original == {"driver": pin(THIS), "support": pin(SUPPORT)}}
        save(case / "result.json", result)
        raise SystemExit(support.owner_exit_code(row))
    if stage == "--handshake-owner":
        unit = sys.argv[3]
        row = support.capture_owned(
            [sys.executable, "-B", str(THIS), "--scope-owner", str(case), unit],
            case, "launcher", 10, env=ENVIRONMENT, term_seconds=1, kill_seconds=1,
            hard_deadline=time.monotonic() + 13)
        raise SystemExit(support.owner_exit_code(row))
    raise ValueError(stage)

original = {"driver": pin(THIS), "support": pin(SUPPORT), "collector": pin(COLLECTOR)}
module = ast.parse(COLLECTOR.read_text(), filename=str(COLLECTOR))
assignment = next(node for node in module.body if isinstance(node, ast.Assign)
                  and any(isinstance(target, ast.Name) and target.id == "passed" for target in node.targets))
consumer = compile(ast.Expression(assignment.value), str(COLLECTOR), "eval")
rows = []

for name, inject_refusal in (("normal-four-level-zero", False), ("zero-waits-refused-scope-receipt", True)):
    case = ROOT / name
    case.mkdir(mode=0o700)
    if inject_refusal:
        (case / "scope-wait.json").mkdir(mode=0o700)
    unit = "codex-worldline-c24-collector-" + uuid.uuid4().hex + ".scope"
    argv = [sys.executable, "-B", str(THIS), "--handshake-owner", str(case), unit]
    with (case / "outer.stdout").open("xb") as stdout, (case / "outer.stderr").open("xb") as stderr:
        process = subprocess.Popen(argv, env=ENVIRONMENT, stdout=stdout, stderr=stderr,
                                   start_new_session=True)
        owner = support.wait_owned(process, 15, term_seconds=1, kill_seconds=1,
                                   hard_deadline=time.monotonic() + 18)
        stdout.flush(); os.fsync(stdout.fileno())
        stderr.flush(); os.fsync(stderr.fileno())
    unchanged = original == {"driver": pin(THIS), "support": pin(SUPPORT), "collector": pin(COLLECTOR)}
    outer = {"argv": argv, "pid": process.pid, "wrapper_pid": os.getpid(),
             "actual_handshake_Popen_wait_returncode": owner["returncode"],
             "owner_control": owner, "inputs_unchanged": unchanged,
             "retention_success": True, "retention_errors": [],
             "raw_files": [pin(case / "outer.stdout"), pin(case / "outer.stderr")]}
    save(case / "outer-child-wait.json", outer)
    result, child, scope, launcher = (load(case / file) for file in
                                    ("result.json", "child-wait.json", "scope-wait.json", "launcher-wait.json"))
    refusals = [pin(case / file) for file in ("scope-retention-refusal.json", "child-retention-refusal.json",
                                             "launcher-retention-refusal.json") if (case / file).is_file()]
    classification = support.strict_terminal_classification(
        result, child_wait=child, scope_wait=scope, launcher_wait=launcher,
        outer_wait=outer, refusals=refusals, execution_observed=True)
    namespace = {"source_match": unchanged, "records": [{"actual_result": result}],
                 "proposal": {"launches": [{"scope_unit": unit, "launcher_argv": argv}]},
                 "terminal_classifications": [{"classification": classification}]}
    passed = eval(consumer, {"__builtins__": {"all": all, "len": len, "bool": bool}}, namespace)
    observed = subprocess.run(
        ["/usr/bin/systemctl", "--user", "show", unit, "-p", "LoadState", "-p", "ActiveState",
         "-p", "SubState", "-p", "ControlGroup", "-p", "Result"],
        env=ENVIRONMENT, capture_output=True, text=True, timeout=5)
    properties = dict(line.split("=", 1) for line in observed.stdout.splitlines() if "=" in line)
    actual_rows = [child, result["scope_owner_control"], launcher, owner]
    assert child["returncode"] == result["scope_wait"] == 0
    assert all(row["actual_wait_observed"] is True for row in actual_rows)
    assert not any((Path("/proc") / str(row["pid"])).exists() for row in actual_rows)
    assert observed.returncode == 0 and not properties.get("ControlGroup"), properties
    row = {"case": name, "classification": classification, "all_required_actual_pass": passed,
           "actual_child_wait": child, "actual_scope_wait_receipt": scope,
           "actual_scope_owner_control": result["scope_owner_control"],
           "actual_launcher_wait": launcher, "actual_outer_wait": outer,
           "retained_refusals": refusals,
           "actual_scope_terminal_observation": {"argv": observed.args, "returncode": observed.returncode,
                                                 "stdout": observed.stdout, "stderr": observed.stderr}}
    save(case / "actual-consumer-result.json", row)
    rows.append(row)
    assert passed is (not inject_refusal), row
    assert classification["state"] == ("FAILED_TERMINAL" if inject_refusal else "NORMAL_TERMINAL_ACTUAL_WAIT_ZERO")
    if inject_refusal:
        assert result["scope_owner_control"]["retention_success"] is False
        assert launcher["returncode"] == owner["returncode"] == 1
    else:
        assert launcher["returncode"] == owner["returncode"] == 0

before_path = FRAME.parent / "formal-successor-v23-preparation/review/Main-harmless-collector-refusal-before-v2/actual-smoke-results.json"
before = load(before_path)
replayed = support.strict_terminal_classification(
    {"scope_wait": before["actual_scope_owner_control"]["returncode"],
     "scope_owner_control": before["actual_scope_owner_control"],
     "child_wait": before["actual_child_wait"], "inputs_unchanged": True},
    child_wait=before["actual_child_wait"], scope_wait=None,
    launcher_wait=before["actual_handshake_wait"], outer_wait=None,
    refusals=[pin(before_path.parent / "actual-zero-scope-with-refused-wait-receipt/scope-retention-refusal.json")],
    execution_observed=True)
assert replayed["state"] == "FAILED_TERMINAL" and replayed["all_required_actual_pass"] is False
assert before["all_required_actual_pass"] is True
empty = ROOT / "genuinely-never-launched"
empty.mkdir(mode=0o700)
never = support.strict_terminal_classification(None)
assert never["state"] == "NEVER_LAUNCHED" and never["all_required_actual_pass"] is False
unknown = support.strict_terminal_classification(None, child_wait=rows[0]["actual_child_wait"], execution_observed=True)
assert unknown["state"] == "EXECUTED_WITH_UNKNOWN_RESULT" and unknown["all_required_actual_pass"] is False
result = {"schema": "Main-real-four-level-waits-terminal-consumer-smoke-v1",
          "status": "PASS_HARMLESS_CUSTODY_CONSUMER_ONLY_NOT_PROOF_OR_PHASE_ACCEPTANCE",
          "actual_production_support": pin(SUPPORT), "actual_production_collector": pin(COLLECTOR),
          "actual_cases": rows, "actual_unchanged_before_evidence": pin(before_path),
          "same_actual_before_receipts_after_classification": replayed,
          "genuinely_never_launched_classification": never, "executed_missing_ancestor_classification": unknown,
          "all_actual_waits_retained_without_rewriting": True,
          "collector_import_adoption_or_window_mutation": False,
          "target_execution": "HARMLESS_STAND_INS_ONLY_NO_GNAT_OR_ACCEPTANCE_TARGET",
          "phase_acceptance": False}
save(ROOT / "actual-smoke-results.json", result)
print(json.dumps({"status": result["status"], "normal_pass": rows[0]["all_required_actual_pass"],
                  "refusal_pass": rows[1]["all_required_actual_pass"], "replayed_before": replayed["state"],
                  "unknown": unknown["state"], "never": never["state"],
                  "results": str(ROOT / "actual-smoke-results.json")}))
