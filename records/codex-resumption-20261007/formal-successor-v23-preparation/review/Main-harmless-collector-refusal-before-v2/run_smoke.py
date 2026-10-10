"""Main-owned harmless collector counterexample; no proof or admission action."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import os
import signal
import subprocess
import sys
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
SUPPORT = ROOT.parents[1] / "successor_support.py"
COLLECTOR = ROOT.parents[1] / "deadline-machinery-templates/review/root-terminal-v1/collect_terminal.py"


def load_support():
    spec = importlib.util.spec_from_file_location("harmless_collector_support", SUPPORT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def retain(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def pin(path):
    raw = path.read_bytes()
    return {"path": str(path), "bytes": len(raw), "mode": path.stat().st_mode & 0o7777,
            "sha256": hashlib.sha256(raw).hexdigest()}


if len(sys.argv) == 3 and sys.argv[1] == "--inner":
    support = load_support()
    case = Path(sys.argv[2])
    actual = support.capture_owned(
        [sys.executable, "-B", "-c", "print('harmless prover stand-in; not GNAT')"],
        case, "child", 2, term_seconds=1, kill_seconds=1,
        hard_deadline=__import__("time").monotonic() + 4)
    raise SystemExit(support.owner_exit_code(actual))

support = load_support()
case = ROOT / "actual-zero-scope-with-refused-wait-receipt"
case.mkdir(mode=0o700)
(case / "scope-wait.json").mkdir(mode=0o700)
unit = "codex-worldline-c23-collector-zero-refusal-" + uuid.uuid4().hex + ".scope"
environment = dict(os.environ, XDG_RUNTIME_DIR="/run/user/1000",
                   DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/1000/bus")
argv = ["/usr/bin/systemd-run", "--user", "--scope", "--collect",
        "--unit=" + unit, "-p", "MemoryMax=8G", "-p", "MemorySwapMax=0",
        "-p", "RuntimeMaxSec=4s", "-p", "TimeoutStopSec=1s", "--",
        sys.executable, "-B", str(Path(__file__).resolve()), "--inner", str(case)]
scope = support.capture_owned(argv, case, "scope", 5, env=environment,
                              term_seconds=1, kill_seconds=1,
                              hard_deadline=__import__("time").monotonic() + 8)
child = json.loads((case / "child-wait.json").read_text())
owner_code = support.owner_exit_code(scope)
handshake = support.capture_owned(
    [sys.executable, "-B", "-c", "import sys; sys.exit(int(sys.argv[1]))", str(owner_code)],
    case, "handshake", 2, term_seconds=1, kill_seconds=1,
    hard_deadline=__import__("time").monotonic() + 4)
observation = subprocess.run(
    ["/usr/bin/systemctl", "--user", "show", unit,
     "-p", "LoadState", "-p", "ActiveState", "-p", "SubState", "-p", "ControlGroup", "-p", "Result"],
    env=environment, capture_output=True, text=True, timeout=5)
properties = dict(line.split("=", 1) for line in observation.stdout.splitlines() if "=" in line)
assert child["returncode"] == 0 and child["actual_wait_observed"] is True, child
assert scope["returncode"] == 0 and scope["actual_wait_observed"] is True, scope
assert scope["retention_success"] is False and scope["retention_errors"], scope
assert owner_code == 1 and handshake["returncode"] == 1, handshake
assert (case / "scope-retention-refusal.json").is_file()
assert not any((Path("/proc") / str(row["pid"])).exists() for row in (child, scope, handshake))
assert observation.returncode == 0 and not properties.get("ControlGroup"), properties

# Execute only the actual pure consumer expression, not collector module globals,
# adoption checks, system inspection, publication or reserved-window mutation.
module = ast.parse(COLLECTOR.read_text(), filename=str(COLLECTOR))
assignment = next(node for node in module.body if isinstance(node, ast.Assign)
                  and any(isinstance(target, ast.Name) and target.id == "passed" for target in node.targets))
expression = ast.Expression(assignment.value)
namespace = {"source_match": True, "unrun": [], "unknown": [],
             "records": [{"actual_result": {"child_wait": child, "scope_wait": scope["returncode"],
                                            "scope_owner_control": scope, "inputs_unchanged": True}}]}
passed = eval(compile(expression, str(COLLECTOR), "eval"), {"__builtins__": {"all": all}}, namespace)
result = {"schema": "Main-real-zero-waits-failed-custody-consumer-counterexample-v1",
          "status": "FAIL_REPRODUCED_REAL_ZERO_WAITS_RETENTION_REFUSAL" if passed else "REFUSAL_REJECTED",
          "collector": pin(COLLECTOR), "support": pin(SUPPORT),
          "actual_child_wait": child, "actual_scope_owner_control": scope,
          "actual_owner_exit_code": owner_code, "actual_handshake_wait": handshake,
          "all_required_actual_pass": passed, "required_expected_pass": False,
          "actual_scope_terminal_observation": {"argv": observation.args, "returncode": observation.returncode,
                                                "stdout": observation.stdout, "stderr": observation.stderr},
          "consumer_expression_line": assignment.lineno,
          "counterexample_inputs": "Actual harmless nested systemd scope/prover waits and actual failed primary wait-receipt write; no fabricated return code.",
          "consumer_boundary": "Only the pure original pass expression; source_match means unchanged stand-in source, not Phase One source admission.",
          "target_execution": "HARMLESS_STAND_INS_ONLY_NO_GNAT_OR_ACCEPTANCE_TARGET",
          "phase_acceptance": False, "window_or_adoption_mutation": False}
retain(ROOT / "actual-smoke-results.json", result)
print(json.dumps({"status": result["status"], "child": child["returncode"], "scope": scope["returncode"],
                  "owner": owner_code, "handshake": handshake["returncode"],
                  "collector_passed": passed, "results": str(ROOT / "actual-smoke-results.json")}))
assert passed is False, "Actual zero waits plus refused custody incorrectly classified as all_required_actual_pass"
