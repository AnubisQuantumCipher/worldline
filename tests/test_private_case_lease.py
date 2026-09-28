"""Real user-systemd integration for worker-owned scoped case leases.

A trusted worker (mapped UID 1) opens a lease on a directory in its copy. The backend
starts candidate commands (mapped UID 2) against a separate candidate view of that
directory, copies worker edits in and candidate outputs out, and refuses the whole run
on any protocol violation.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest
import uuid

from worldline.errors import WorldlineError
from worldline.linux.private_evaluator import (
    PrivateEvaluationSpec, PrivateEvaluator, VERIFIER_MOUNT,
)
from worldline.linux.systemd import SystemdAdapter
from worldline.trusted import TRUSTED_INTERPRETER


LOGICAL = "/logical/lease-check"
CASE = LOGICAL + "/cases/one"

_WORKER = r'''import base64, json, os, socket, sys
from pathlib import Path
MODE = sys.argv[1]
CASE = Path(%(case)r)

def broker(request):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(60)
        client.connect("/run/worldline-worker-broker.sock")
        client.sendall(json.dumps(request).encode() + b"\n")
        response = json.loads(client.makefile("rb").readline(16 * 1024 * 1024))
    if "error" in response:
        raise RuntimeError(response["error"])
    return response

def run(handle, program, stdin=b"", env=None):
    request = {"op": "case_start", "caseHandle": handle,
               "argv": ["/usr/bin/python3", "-c", program], "cwd": %(logical)r,
               "timeout": 30, "stdinB64": base64.b64encode(stdin).decode()}
    if env is not None:
        request["env"] = env
    started = broker(request)
    while True:
        waited = broker({"op": "case_wait", "caseHandle": handle,
                         "handle": started["handle"], "waitMs": 1000})
        if waited["done"]:
            break
    broker({"op": "case_teardown", "caseHandle": handle, "handle": started["handle"]})
    copied = broker({"op": "case_copy_out", "caseHandle": handle})
    return started["observation"], waited, copied

CASE.mkdir(parents=True)
(CASE / "input.txt").write_text("worker input\n")
if MODE == "outside":
    broker({"op": "case_open", "caseRoot": "/etc"})
handle = broker({"op": "case_open", "caseRoot": str(CASE)})["caseHandle"]
payload = b"stdin \xff bytes\n"
echo = ("import os, sys, pathlib\n"
        "data = sys.stdin.buffer.read()\n"
        "case = pathlib.Path(%(case)r)\n"
        "(case / 'echo.bin').write_bytes(data)\n"
        "print(os.getuid(), os.environ.get('PYTHONHASHSEED'), (case / 'input.txt').read_text().strip(),"
        " os.path.exists('/run/worldline-worker-broker.sock'), os.path.exists('/run/worldline-report'))\n")
if MODE == "env":
    run(handle, echo, payload, {"LD_PRELOAD": "/tmp/x.so"})
if MODE == "escape":
    run(handle, "import os; os.symlink('/etc/passwd', %(case)r + '/escape')")
observation, first, copied = run(handle, echo, payload, {"PYTHONHASHSEED": "0"})
received = (CASE / "echo.bin").read_bytes()
(CASE / "input.txt").write_text("edited by worker\n")
status = broker({"op": "case_status", "caseHandle": handle})
broker({"op": "case_sync_in", "caseHandle": handle, "expectedGeneration": status["generation"]})
_, second, _ = run(handle, "import pathlib; print(pathlib.Path(%(case)r + '/input.txt').read_text().strip())")
closed = broker({"op": "case_close", "caseHandle": handle})
print(json.dumps({
    "observation": {key: observation.get(key) for key in ("role", "uid", "gid", "reportMounted",
                                                          "brokerMounted", "workerBrokerMounted")},
    "first_stdout": base64.b64decode(first["stdoutB64"]).decode(),
    "echo_exact": received == payload,
    "worker_changed": status["workerChanged"],
    "second_stdout": base64.b64decode(second["stdoutB64"]).decode(),
    "closed": closed,
}, sort_keys=True))
''' % {"case": CASE, "logical": LOGICAL}

_EXAMINER = '''import candidate, json
from pathlib import Path
result = candidate.run(['/usr/bin/python3', '-I', 'lease_worker.py', MODE], timeout=90)
value = json.loads(result.stdout) if result.returncode == 0 else {}
ok = (result.returncode == 0
      and value.get("observation") == {"role": "candidate", "uid": 2, "gid": 2, "reportMounted": False,
                                       "brokerMounted": False, "workerBrokerMounted": False}
      and value.get("first_stdout") == "2 0 worker input False False\\n"
      and value.get("echo_exact") is True
      and value.get("worker_changed") is True
      and value.get("second_stdout") == "edited by worker\\n"
      and value.get("closed") == {"closed": True})
Path('/run/worldline-report/report').write_text(
    '<testsuite tests="1" failures="' + ('0' if ok else '1') + '" errors="0"/>')
print(json.dumps(value, sort_keys=True))
raise SystemExit(0 if ok else 1)
'''


@unittest.skipUnless(os.environ.get("WORLDLINE_PRIVATE_EVALUATOR_TEST") == "1",
                     "set WORLDLINE_PRIVATE_EVALUATOR_TEST=1 for real user-systemd integration")
class PrivateCaseLeaseIntegration(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-private-lease-",
                                                     dir=str(Path.home()))
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / "source"
        self.source.mkdir(mode=0o755)
        (self.source / "lease_worker.py").write_text(_WORKER)
        self.verifier = self.base / "verifier"
        self.verifier.mkdir()
        self.adapter = SystemdAdapter()

    def run_mode(self, mode: str):
        (self.verifier / "exam.py").write_text("MODE = " + repr(mode) + "\n" + _EXAMINER)
        report = self.base / (mode + "-report")
        report.mkdir(mode=0o700)
        spec = PrivateEvaluationSpec(
            str(uuid.uuid4()), {LOGICAL: self.source}, self.verifier,
            (TRUSTED_INTERPRETER, VERIFIER_MOUNT + "/exam.py"), LOGICAL, report,
            self.base / mode, timeout_seconds=120)
        return spec, PrivateEvaluator(self.adapter).run(spec, resource_properties=(
            "MemoryMax=1G", "TasksMax=64"))

    def test_lease_runs_candidate_principal_with_exact_stdin_and_scoped_copies(self):
        spec, result = self.run_mode("positive")
        self.assertEqual(result["exitCode"], 0, result["stdout"] + result["stderr"])
        self.assertIn(b'failures="0"', (result["reportDirectory"] / "report").read_bytes())
        boundary = result["boundary"]
        leased = [item for item in boundary["workers"] if item.get("caseHandle")]
        self.assertEqual(len(leased), 2)
        for item in leased:
            self.assertEqual(item["principal"], "candidate")
            self.assertEqual((item["observation"]["uid"], item["observation"]["gid"]), (2, 2))
        workers = [item for item in boundary["workers"] if item.get("principal", "worker") == "worker"]
        self.assertEqual([item["observation"]["uid"] for item in workers], [1])
        self.assertEqual(len(boundary["caseLeases"]), 1)
        self.assertEqual(boundary["caseLeases"][0]["events"][0], "open")
        self.assertEqual(boundary["caseLeases"][0]["events"][-1], "close")
        self.assertIn("copy-in", boundary["caseLeases"][0]["events"][1:])

    def test_protocol_violations_refuse_the_entire_run(self):
        for mode, fragment in (("outside", "not strictly inside the active worker copy"),
                               ("env", "determinism allowlist"),
                               ("escape", "escapes the case tree")):
            with self.subTest(mode=mode):
                with self.assertRaises(WorldlineError) as raised:
                    self.run_mode(mode)
                self.assertEqual(raised.exception.code, "PRIVATE_EVALUATOR_BOUNDARY_FAILED")
                spec_runtime = self.base / mode
                boundary = json.loads((spec_runtime / "boundary.json").read_text())
                self.assertIn(fragment, boundary["error"])
                self.assertFalse(boundary.get("rolesCompleted", False))


if __name__ == "__main__":
    unittest.main()
