"""Adversarial fault campaign against the private evaluator's case-lease machinery.

Pre-merge requirement for WORLDLINE 1.6.0 (PR #6). An external reviewer asked us to
"verify every scenario ends either in a clean valid state or an explicit refusal, never
half-synchronized evidence", and to actually attack nested user namespaces rather than
leave them an untested sentence.

Every test here asserts an INVARIANT, never which side of a race wins:

  * The whole run ends VALID and clean (a legitimate scenario), or it ends as one explicit
    whole-run refusal (a boundary error, never admissible). It is never half-synchronized:
    the worker's authoritative case directory is exactly its pre-operation state or exactly
    the fully-copied candidate output, never a partial mixture.
  * No candidate process or role sandbox outlives the evaluation, and no worldline transient
    unit lingers.

The nested-user-namespace probes RECORD what the kernel permitted or refused (this differs
between the local Arch kernel and the hosted ubuntu-24.04 runner, which sets
kernel.apparmor_restrict_unprivileged_userns=0). The kernel's choice is data in the test
output; the assertion is only that no privileged surface became reachable either way.

Run (from the worktree root):
  WORLDLINE_PRIVATE_EVALUATOR_TEST=1 PYTHONPATH=runtime PYTHONDONTWRITEBYTECODE=1 \
    ~/.cache/anubis-item21/capped.sh python3 -m unittest -v tests.test_private_lease_fault_campaign
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
import unittest
import uuid
from pathlib import Path

from worldline.errors import WorldlineError
from worldline.linux.private_case_copy import (
    CaseCopyError, MAX_CASE_BYTES, MAX_CASE_DEPTH, MAX_CASE_ENTRIES, copy_case_tree,
)
from worldline.linux.private_evaluator import PrivateEvaluationSpec, PrivateEvaluator, VERIFIER_MOUNT
from worldline.linux.systemd import SystemdAdapter, manager_environment
from worldline.trusted import TRUSTED_INTERPRETER


_GATE = unittest.skipUnless(
    os.environ.get("WORLDLINE_PRIVATE_EVALUATOR_TEST") == "1",
    "set WORLDLINE_PRIVATE_EVALUATOR_TEST=1 for real user-systemd/bubblewrap integration")

LOGICAL = "/logical/fault-campaign"
CASE = LOGICAL + "/cases/one"
# Optional: WORLDLINE_CAMPAIGN_LOG=/path.jsonl records what the kernel decided. Nothing is
# printed: the assurance instrument reads unittest's own verdict as the last line of output.
_LOG = os.environ.get("WORLDLINE_CAMPAIGN_LOG")


def _record(scenario: str, **observed) -> None:
    if _LOG:
        with open(_LOG, "a", encoding="utf-8") as handle:
            handle.write(json.dumps({"scenario": scenario, **observed}, sort_keys=True, default=str) + "\n")


def _fill(source: str) -> str:
    """Substitute the two path tokens. Token replacement (not %-formatting) so embedded
    candidate programs may freely use %d/%s runtime formatting."""
    return source.replace("@CASE@", repr(CASE)).replace("@LOGICAL@", repr(LOGICAL))


# A permission-tolerant recursive manifest, shared by the worker scripts. It never raises on
# an unreadable entry; it records the fact instead, so a copy-out that legitimately preserves
# a candidate's 0o000 file does not turn the invariant check into a crash.
_MANIFEST = r'''
def manifest(root):
    import os, stat, hashlib
    out = {}
    def walk(directory, rel):
        try:
            names = sorted(os.listdir(directory))
        except OSError as exc:
            out[rel or "."] = ["dir-unreadable", getattr(exc, "errno", 0)]
            return
        for name in names:
            path = os.path.join(directory, name)
            key = name if not rel else rel + "/" + name
            try:
                info = os.lstat(path)
            except OSError as exc:
                out[key] = ["lstat-error", getattr(exc, "errno", 0)]
                continue
            mode = stat.S_IMODE(info.st_mode)
            if stat.S_ISDIR(info.st_mode):
                out[key] = ["dir", mode]
                walk(path, key)
            elif stat.S_ISLNK(info.st_mode):
                out[key] = ["symlink", os.readlink(path)]
            elif stat.S_ISREG(info.st_mode):
                try:
                    with open(path, "rb") as handle:
                        out[key] = ["file", mode, info.st_size,
                                    hashlib.sha256(handle.read()).hexdigest()]
                except OSError as exc:
                    out[key] = ["file-unreadable", mode, info.st_size, getattr(exc, "errno", 0)]
            else:
                out[key] = ["special", mode]
    walk(root, "")
    return out
'''


# The worker talks to the worker-broker over /run/worldline-worker-broker.sock. MODE selects
# the attack. It prints exactly one JSON object as its final stdout line (consumed by the
# examiner) unless it is deliberately killing itself or its opener mid-lease.
_WORKER = _fill(r'''
import base64, json, os, socket, sys, stat, hashlib
from pathlib import Path
MODE = sys.argv[1]
CASE = Path(@CASE@)
''' + _MANIFEST + r'''

def broker(request):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(150)
        client.connect("/run/worldline-worker-broker.sock")
        client.sendall(json.dumps(request).encode() + b"\n")
        response = json.loads(client.makefile("rb").readline(16 * 1024 * 1024))
    if "error" in response:
        raise RuntimeError(response["error"])
    return response

def open_case():
    CASE.mkdir(parents=True, exist_ok=True)
    (CASE / "input.txt").write_text("worker input\n")
    (CASE / "keep").mkdir(exist_ok=True)
    (CASE / "keep" / "data.bin").write_bytes(b"payload\n")
    return broker({"op": "case_open", "caseRoot": str(CASE)})["caseHandle"]

def start(handle, program, timeout=60):
    return broker({"op": "case_start", "caseHandle": handle,
                   "argv": ["/usr/bin/python3", "-c", program], "cwd": @LOGICAL@,
                   "timeout": timeout, "stdinB64": ""})

def wait_done(handle, inner, budget_seconds=150):
    import time as _t
    deadline = _t.monotonic() + budget_seconds
    while True:
        waited = broker({"op": "case_wait", "caseHandle": handle,
                         "handle": inner, "waitMs": 1000})
        if waited["done"]:
            return waited
        if _t.monotonic() >= deadline:
            raise RuntimeError("candidate did not finish within worker budget")

def run_candidate(handle, program, timeout=60):
    started = start(handle, program, timeout)
    waited = wait_done(handle, started["handle"])
    broker({"op": "case_teardown", "caseHandle": handle, "handle": started["handle"]})
    return started["observation"], waited

# ------------------------------------------------------------------ scenario 1
if MODE == "handshake":
    handle = open_case()
    # Candidates that die at, or immediately after, the frame/GO acknowledgement window.
    dying = [
        "import os, signal\nos.killpg(0, signal.SIGKILL)\n",   # self-SIGKILL first line
        "raise SystemExit(0)\n",                                # clean immediate exit
        "import os\nos._exit(0)\n",                             # abrupt immediate exit
    ]
    uids = []
    for index in range(6):
        program = dying[index % len(dying)]
        started = start(handle, program, timeout=20)
        # Sample the just-after-GO window with an idempotent signal, then reap deterministically.
        broker({"op": "case_signal", "caseHandle": handle,
                "handle": started["handle"], "signal": "SIGKILL"})
        wait_done(handle, started["handle"])
        broker({"op": "case_teardown", "caseHandle": handle, "handle": started["handle"]})
        uids.append(started["observation"]["uid"])
    copied = broker({"op": "case_copy_out", "caseHandle": handle})
    closed = broker({"op": "case_close", "caseHandle": handle})
    print(json.dumps({"candidate_uids": uids, "copied_out": True, "closed": closed}))
    sys.exit(0)

# ------------------------------------------------------------------ scenario 2
if MODE == "worker_death":
    handle = open_case()
    # Long candidate, then abrupt worker death leaving the lease open and the candidate live.
    start(handle, "import time\ntime.sleep(600)\n", timeout=120)
    os._exit(7)

# ------------------------------------------------------------------ scenario 3
if MODE == "examiner_death":
    handle = open_case()
    started = start(handle, "import time\ntime.sleep(600)\n", timeout=120)
    # Worker returns cleanly, deliberately WITHOUT tearing down or closing. The examiner will
    # exit abruptly next, so at bootstrap teardown a live candidate and an open case remain.
    print(json.dumps({"left_open": started["handle"][:8]}))
    sys.exit(0)

# ------------------------------------------------------------------ scenario 4
if MODE.startswith("copyout:"):
    kind = MODE.split(":", 1)[1]
    handle = open_case()
    before = manifest(str(CASE))
    make = {
        "fifo": "import os\nos.mkfifo(os.path.join(@CASE@, 'pipe'))\n",
        "hardlink": ("import os\np = os.path.join(@CASE@, 'a'); open(p,'w').write('x')\n"
                     "os.link(p, os.path.join(@CASE@, 'b'))\n"),
        "xattr": ("import os\np = os.path.join(@CASE@, 'x'); open(p,'w').write('x')\n"
                  "try:\n    os.setxattr(p, b'user.attack', b'1')\nexcept OSError as e:\n"
                  "    open(os.path.join(@CASE@, 'xattr_unsupported'),'w').write(str(e.errno))\n"),
        "setuid": ("import os\np = os.path.join(@CASE@, 's'); open(p,'w').write('x')\n"
                   "os.chmod(p, 0o4755)\n"),
        "chmod000": ("import os\np = os.path.join(@CASE@, 'secret'); open(p,'w').write('classified\\n')\n"
                     "os.chmod(p, 0o000)\n"),
    }[kind]
    run_candidate(handle, make, timeout=30)
    err = None
    copied = False
    try:
        broker({"op": "case_copy_out", "caseHandle": handle})
        copied = True
    except RuntimeError as exc:
        err = str(exc)
    after = manifest(str(CASE))
    if copied:
        broker({"op": "case_close", "caseHandle": handle})
    result = {"kind": kind, "copied_out": copied, "copy_out_error": err,
              "worker_dir_unchanged": before == after}
    print(json.dumps(result, sort_keys=True))
    # Invariant: refused => worker dir is exactly pre-operation; copied => a real (fully) copy
    # happened (its content differs). Never half: refused-but-mutated is a failure.
    if not copied and before != after:
        sys.exit(11)
    sys.exit(0)

# ------------------------------------------------------------- scenarios 6 & 7
if MODE == "isolation":
    handle = open_case()
    observation, waited = run_candidate(handle, ISOLATION_PROBE, timeout=90)
    probe = json.loads(base64.b64decode(waited["stdoutB64"]))
    broker({"op": "case_copy_out", "caseHandle": handle})
    broker({"op": "case_close", "caseHandle": handle})
    print(json.dumps({"observation": {k: observation.get(k) for k in ("role", "uid", "gid")},
                      "candidate_returncode": waited.get("returncode"), "probe": probe}))
    sys.exit(0)

# ------------------------------------------------------------------ scenario 8
if MODE == "mountid":
    handle = open_case()
    observation, waited = run_candidate(handle, MOUNTID_PROBE, timeout=90)
    probe = json.loads(base64.b64decode(waited["stdoutB64"]))
    refused = None
    copied = False
    try:
        broker({"op": "case_copy_out", "caseHandle": handle})
        copied = True
    except RuntimeError as exc:
        refused = str(exc)
    have_underlying = have_ghost = None
    if copied:
        sub = CASE / "sub"
        have_underlying = (sub / "underlying.txt").exists()
        have_ghost = (sub / "ghost.txt").exists()
        broker({"op": "case_close", "caseHandle": handle})
    print(json.dumps({"probe": probe, "copied_out": copied, "copy_out_error": refused,
                      "have_underlying": have_underlying, "have_ghost": have_ghost}))
    # Invariant: host-side copy-out collects the UNDERLYING content (never the candidate's
    # nested-namespace ghost), OR the copier refuses. A copy that captured the ghost is a leak.
    if copied and (have_ghost or not have_underlying):
        sys.exit(12)
    sys.exit(0)

raise SystemExit("unknown fault mode: " + MODE)
''')


# The candidate (mapped UID 2, all capabilities dropped, NoNewPrivs=1) probes every privileged
# surface, then attempts to escape via a nested user namespace, recording exactly what the
# kernel allowed or refused. It writes one JSON object to stdout.
ISOLATION_PROBE = _fill(r'''
import ctypes, errno, json, os, socket, sys

def code(number):
    return errno.errorcode.get(number, number)

res = {"uid": os.getuid(), "gid": os.getgid()}
SURFACES = ["/run/worldline-broker.sock", "/run/worldline-worker-broker.sock",
            "/run/worldline-report", "/run/worldline-verifiers", "/opt/worldline-gnat"]

def reachability():
    seen = {surface: os.path.exists(surface) for surface in SURFACES}
    connects = {}
    for surface in ["/run/worldline-broker.sock", "/run/worldline-worker-broker.sock"]:
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.settimeout(1)
            client.connect(surface)
            connects[surface] = "CONNECTED"
            client.close()
        except OSError as exc:
            connects[surface] = code(exc.errno)
    return seen, connects

res["reach"], res["connect"] = reachability()

# --- scenario 7: /proc across roles -----------------------------------------
pids = [int(name) for name in os.listdir("/proc") if name.isdigit()]
uids = set()
for pid in pids:
    try:
        with open("/proc/%d/status" % pid) as handle:
            for line in handle:
                if line.startswith("Uid:"):
                    uids.add(line.split()[1])
                    break
    except OSError:
        pass
res["proc_pid_count"] = len(pids)
res["proc_visible_uids"] = sorted(uids)
# pid 1 in the candidate's PID namespace is bwrap's own sandbox supervisor (mapped uid 0),
# NOT the examiner (a different PID namespace). Its root and environ must stay unreachable.
pid1 = {}
try:
    with open("/proc/1/status") as handle:
        for line in handle:
            if line.startswith("Uid:"):
                pid1["uid"] = line.split()[1]
                break
except OSError as exc:
    pid1["status_error"] = code(exc.errno)
try:
    with open("/proc/1/environ", "rb") as handle:
        handle.read(1)
    pid1["environ_readable"] = True
except OSError as exc:
    pid1["environ_readable"] = False
    pid1["environ_error"] = code(exc.errno)
try:
    os.kill(1, 0)
    pid1["kill0"] = "PERMITTED"
except OSError as exc:
    pid1["kill0"] = code(exc.errno)
res["pid1"] = pid1
try:
    res["proc1_root_run"] = sorted(os.listdir("/proc/1/root/run"))
except OSError as exc:
    res["proc1_root_run"] = "error:" + str(code(exc.errno))
# Signal-probe PIDs that would belong to other roles if this PID namespace were shared.
signal_probe = {}
for pid in (1000000, 900001, 450001, 250001):
    try:
        os.kill(pid, 0)
        signal_probe[pid] = "EXISTS"
    except OSError as exc:
        signal_probe[pid] = code(exc.errno)
res["kill_probe"] = signal_probe
# /proc/<pid>/environ and /proc/<pid>/fd of every visible PID: readable ones are all our own.
foreign_readable = []
for pid in pids:
    try:
        with open("/proc/%d/environ" % pid, "rb") as handle:
            handle.read(64)
        with open("/proc/%d/status" % pid) as handle:
            first_uid = None
            for line in handle:
                if line.startswith("Uid:"):
                    first_uid = line.split()[1]
                    break
        if first_uid not in (None, str(os.getuid())):
            foreign_readable.append([pid, first_uid])
    except OSError:
        pass
res["foreign_readable_environ"] = foreign_readable

# --- scenario 6: nested user namespace --------------------------------------
nested = {}
my_uid = os.getuid()
try:
    os.unshare(os.CLONE_NEWUSER)
    nested["userns"] = "ALLOWED"
    nested["euid_before_map"] = os.geteuid()
    try:
        with open("/proc/self/setgroups", "w") as handle:
            handle.write("deny")
    except OSError as exc:
        nested["setgroups"] = code(exc.errno)
    try:
        with open("/proc/self/uid_map", "w") as handle:
            handle.write("0 %d 1" % my_uid)
        with open("/proc/self/gid_map", "w") as handle:
            handle.write("0 %d 1" % my_uid)
        nested["mapped_to_root"] = (os.geteuid() == 0)
    except OSError as exc:
        nested["map_error"] = code(exc.errno)
    try:
        os.unshare(os.CLONE_NEWNS)
        nested["mountns"] = "ALLOWED"
        libc = ctypes.CDLL("libc.so.6", use_errno=True)
        rc = libc.mount(b"tmpfs", b"/tmp", b"tmpfs", 0, None)
        nested["mount_tmpfs_over_tmp"] = "OK" if rc == 0 else code(ctypes.get_errno())
        rc = libc.mount(b"proc", b"/proc", b"proc", 0, None)
        nested["mount_proc_over_proc"] = "OK" if rc == 0 else code(ctypes.get_errno())
        rc = libc.mount(b"tmpfs", @CASE@.encode(), b"tmpfs", 0, None)
        nested["mount_tmpfs_over_case"] = "OK" if rc == 0 else code(ctypes.get_errno())
    except OSError as exc:
        nested["mountns"] = code(exc.errno)
    # Even as nested root with a private mount table, nothing privileged should appear.
    nested["reach_after"], nested["connect_after"] = reachability()
except OSError as exc:
    nested["userns"] = code(exc.errno)
res["nested"] = nested

# Leave benign content so copy-out has something ordinary to collect.
try:
    with open(os.path.join(@CASE@, "probe-out.txt"), "w") as handle:
        handle.write("probe complete\n")
except OSError as exc:
    res["view_write_error"] = code(exc.errno)

sys.stdout.write(json.dumps(res))
sys.stdout.flush()
''')


# The candidate hides a nested-namespace mount over a subdirectory of its case view, then
# writes a "ghost" that exists only inside that nested mount namespace.
MOUNTID_PROBE = _fill(r'''
import ctypes, errno, json, os, sys

def code(number):
    return errno.errorcode.get(number, number)

res = {}
sub = os.path.join(@CASE@, "sub")
os.makedirs(sub, exist_ok=True)
with open(os.path.join(sub, "underlying.txt"), "w") as handle:
    handle.write("real underlying content\n")
my_uid = os.getuid()
try:
    os.unshare(os.CLONE_NEWUSER)
    try:
        with open("/proc/self/setgroups", "w") as handle:
            handle.write("deny")
    except OSError:
        pass
    with open("/proc/self/uid_map", "w") as handle:
        handle.write("0 %d 1" % my_uid)
    with open("/proc/self/gid_map", "w") as handle:
        handle.write("0 %d 1" % my_uid)
    os.unshare(os.CLONE_NEWNS)
    libc = ctypes.CDLL("libc.so.6", use_errno=True)
    rc = libc.mount(b"tmpfs", sub.encode(), b"tmpfs", 0, None)
    if rc == 0:
        res["mounted_over_sub"] = "OK"
        with open(os.path.join(sub, "ghost.txt"), "w") as handle:
            handle.write("ghost visible only in the nested mount namespace\n")
    else:
        res["mounted_over_sub"] = code(ctypes.get_errno())
except OSError as exc:
    res["nested"] = code(exc.errno)
sys.stdout.write(json.dumps(res))
sys.stdout.flush()
''')


# The two probe programs are module-level constants here, but the worker is a standalone
# script staged into the sandbox: it cannot see them by name. Embed them as its own literals
# (both are already token-filled, so no further substitution is needed).
_WORKER = ("ISOLATION_PROBE = " + repr(ISOLATION_PROBE) + "\n"
           + "MOUNTID_PROBE = " + repr(MOUNTID_PROBE) + "\n"
           + _WORKER)


# Generic examiner: run the worker, mirror its result, keep the report file honest. CFG is
# prepended per test. `abrupt` makes the examiner exit via os._exit without an orderly return.
_EXAMINER = r'''
import candidate, json, os
from pathlib import Path
try:
    result = candidate.run(["/usr/bin/python3", "-I", "lease_worker.py", CFG["mode"]],
                           timeout=CFG.get("timeout", 120))
    worker_rc = result.returncode
    worker_stdout = result.stdout.decode("utf-8", "replace")
except Exception as exc:
    worker_rc = -1
    worker_stdout = "candidate.run raised: " + repr(exc)
try:
    Path("/run/worldline-report/report").write_text(
        '<testsuite tests="1" failures="' + ("0" if worker_rc == 0 else "1") + '" errors="0"/>')
except OSError:
    pass
print(json.dumps({"worker_rc": worker_rc, "worker_stdout": worker_stdout}))
if CFG.get("abrupt"):
    os._exit(0)
raise SystemExit(0 if worker_rc == 0 else 1)
'''


@_GATE
class PrivateLeaseFaultCampaign(unittest.TestCase):
    """Real user-systemd + bubblewrap integration attacks on the case-lease lifecycle."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(
            prefix="worldline-fault-", dir=str(Path.home()))
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / "source"
        self.source.mkdir(mode=0o755)
        (self.source / "lease_worker.py").write_text(_WORKER)
        self.verifier = self.base / "verifier"
        self.verifier.mkdir()
        self.adapter = SystemdAdapter()

    # -- harness ---------------------------------------------------------------
    def _spec(self, name, config):
        # A Python literal (repr), not JSON: the examiner evaluates this as source, so a JSON
        # ``true``/``false``/``null`` would raise NameError before the examiner does anything.
        examiner = "CFG = " + repr(config) + "\n" + _EXAMINER
        (self.verifier / "exam.py").write_text(examiner)
        report = self.base / (name + "-report")
        report.mkdir(mode=0o700)
        return PrivateEvaluationSpec(
            str(uuid.uuid4()), {LOGICAL: self.source}, self.verifier,
            (TRUSTED_INTERPRETER, VERIFIER_MOUNT + "/exam.py"), LOGICAL, report,
            self.base / name, timeout_seconds=240)

    def _run(self, name, config, resources=("MemoryMax=1500M", "TasksMax=96")):
        spec = self._spec(name, config)
        result = PrivateEvaluator(self.adapter).run(spec, resource_properties=resources)
        return spec, result

    def _boundary(self, spec):
        return json.loads((spec.runtime / "boundary.json").read_text())

    def _examiner_json(self, result):
        return json.loads(result["stdout"].decode("utf-8", "replace"))

    def _worker_probe(self, result):
        outer = self._examiner_json(result)
        self.assertEqual(outer["worker_rc"], 0, outer["worker_stdout"])
        return json.loads(outer["worker_stdout"])

    def _assert_clean_teardown(self, spec, deadline_seconds=45):
        """No process referencing this run's runtime, and its transient unit is collected."""
        unit = "worldline-%s.service" % spec.run_id
        token = str(spec.runtime).encode()
        systemctl = shutil.which("systemctl")
        environment = manager_environment()
        deadline = time.monotonic() + deadline_seconds
        lingering, unit_state = None, None
        while time.monotonic() < deadline:
            lingering = []
            for name in os.listdir("/proc"):
                if not name.isdigit():
                    continue
                try:
                    with open("/proc/%s/cmdline" % name, "rb") as handle:
                        if token in handle.read():
                            lingering.append(name)
                except OSError:
                    continue
            unit_state = "gone"
            if systemctl is not None:
                shown = subprocess.run(
                    [systemctl, "--user", "show", unit, "--property=LoadState,ActiveState"],
                    env=environment, capture_output=True, timeout=10).stdout.decode()
                if "LoadState=not-found" not in shown and shown.strip():
                    unit_state = shown.strip().replace("\n", " ")
            if not lingering and unit_state == "gone":
                return
            time.sleep(0.2)
        self.fail("run did not become clean: lingering_pids=%r unit=%r" % (lingering, unit_state))

    def _assert_no_staging_residue(self, spec):
        stray = []
        for pattern in ("copy-out-*", "old-worker-*", "copy-in-*", "old-candidate-*", "guard-*"):
            stray.extend(str(path) for path in spec.runtime.rglob(pattern))
        self.assertEqual(stray, [], "staging/quarantine residue left behind: %r" % stray)

    # -- scenario 1 ------------------------------------------------------------
    def test_scenario1_death_in_role_acknowledgement_window(self):
        spec, result = self._run("handshake", {"mode": "handshake", "timeout": 120})
        self.assertEqual(result["exitCode"], 0, result["stdout"] + result["stderr"])
        boundary = result["boundary"]
        self.assertTrue(boundary.get("rolesCompleted"))
        self.assertNotIn("error", boundary)
        probe = self._worker_probe(result)
        self.assertEqual(probe["candidate_uids"], [2] * 6)
        lease = boundary["caseLeases"][0]
        self.assertEqual(lease["events"][0], "open")
        self.assertEqual(lease["events"][-1], "close")
        self.assertEqual(lease["events"].count("start"), 6)
        self.assertEqual(lease["events"].count("teardown"), 6)
        self.assertIn("copy-out", lease["events"])
        self._assert_no_staging_residue(spec)
        self._assert_clean_teardown(spec)

    # -- scenario 2 ------------------------------------------------------------
    def test_scenario2_worker_death_with_active_case_refuses_and_reaps(self):
        with self.assertRaises(WorldlineError) as raised:
            self._run("worker-death", {"mode": "worker_death"})
        self.assertEqual(raised.exception.code, "PRIVATE_EVALUATOR_BOUNDARY_FAILED")
        spec = self.base / "worker-death"
        boundary = json.loads((spec / "boundary.json").read_text())
        self.assertFalse(boundary.get("rolesCompleted", False))
        error = boundary["error"]
        self.assertTrue("was not closed" in error or "was not torn down" in error, error)
        self.assertEqual(len(boundary["caseLeases"]), 1)
        self.assertNotIn("close", boundary["caseLeases"][0]["events"])
        self._assert_no_staging_residue(_SpecShim(spec, boundary["runId"]))
        self._assert_clean_teardown(_SpecShim(spec, boundary["runId"]))

    # -- scenario 3 ------------------------------------------------------------
    def test_scenario3_examiner_death_with_live_case_refuses_and_reaps(self):
        with self.assertRaises(WorldlineError) as raised:
            self._run("examiner-death", {"mode": "examiner_death", "abrupt": True})
        self.assertEqual(raised.exception.code, "PRIVATE_EVALUATOR_BOUNDARY_FAILED")
        runtime = self.base / "examiner-death"
        boundary = json.loads((runtime / "boundary.json").read_text())
        self.assertFalse(boundary.get("rolesCompleted", False))
        error = boundary["error"]
        self.assertTrue("was not closed" in error or "was not torn down" in error, error)
        self._assert_clean_teardown(_SpecShim(runtime, boundary["runId"]))

    # -- scenario 4 ------------------------------------------------------------
    def test_scenario4_copyout_failure_keeps_worker_dir_pre_operation(self):
        # xattr refusal through the full stack depends on the case filesystem supporting user
        # xattrs; it is covered filesystem-independently by CaseCopyTreeShapes below. These
        # three refuse on tree shape / permission bits alone, so they are stack-deterministic.
        refusing = {
            "fifo": ("CASE_COPY_UNSUPPORTED", "special file"),
            "setuid": ("CASE_COPY_UNSUPPORTED", "special permission bits"),
            "hardlink": ("CASE_COPY_HARDLINK", "hardlinked"),
        }
        for kind, (_code, fragment) in refusing.items():
            with self.subTest(kind=kind):
                name = "copyout-" + kind
                with self.assertRaises(WorldlineError) as raised:
                    self._run(name, {"mode": "copyout:" + kind})
                self.assertEqual(raised.exception.code, "PRIVATE_EVALUATOR_BOUNDARY_FAILED")
                runtime = self.base / name
                boundary = json.loads((runtime / "boundary.json").read_text())
                self.assertFalse(boundary.get("rolesCompleted", False))
                # The worker (principal "worker") asserted before==after and exited 0.
                workers = [w for w in boundary["workers"]
                           if w.get("principal", "worker") == "worker"]
                self.assertEqual(len(workers), 1)
                self.assertEqual(workers[0]["returncode"], 0,
                                 "worker reported a half-synchronized case directory")
                self.assertIn(fragment, boundary["error"])
                self.assertTrue("was not closed" in boundary["error"], boundary["error"])
                self._assert_no_staging_residue(_SpecShim(runtime, boundary["runId"]))
                self._assert_clean_teardown(_SpecShim(runtime, boundary["runId"]))

    def test_scenario4_root_copies_candidate_locked_file_as_correct_copy(self):
        # A 0o000 file the candidate created does not block the mapped-root copier: this is a
        # legitimate, fully-completed copy-out, so the run is VALID (never half-synchronized).
        spec, result = self._run("copyout-chmod000", {"mode": "copyout:chmod000"})
        self.assertEqual(result["exitCode"], 0, result["stdout"] + result["stderr"])
        self.assertTrue(result["boundary"].get("rolesCompleted"))
        probe = self._worker_probe(result)
        self.assertTrue(probe["copied_out"])
        self.assertIsNone(probe["copy_out_error"])
        lease = result["boundary"]["caseLeases"][0]
        self.assertIn("copy-out", lease["events"])
        self.assertEqual(lease["events"][-1], "close")
        self._assert_no_staging_residue(spec)
        self._assert_clean_teardown(spec)

    # -- scenarios 6 & 7 -------------------------------------------------------
    def test_scenarios6_7_nested_userns_and_proc_reach_nothing_privileged(self):
        spec, result = self._run("isolation", {"mode": "isolation", "timeout": 120})
        self.assertEqual(result["exitCode"], 0, result["stdout"] + result["stderr"])
        outer = self._worker_probe(result)
        probe = outer["probe"]
        # Record what the kernel decided (data, not an assertion).
        self._nested_record = probe["nested"]
        _record("6/7", uid=probe["uid"], nested=probe["nested"],
                proc_visible_uids=probe["proc_visible_uids"], pid1=probe["pid1"],
                proc1_root_run=probe["proc1_root_run"], kill_probe=probe["kill_probe"])

        # Invariants that must hold whether or not the kernel allowed the nested namespace:
        # (a) no privileged surface is present or connectable, before OR after nesting.
        for label, seen, connect in (
                ("initial", probe["reach"], probe["connect"]),
                ("after-nested", probe["nested"].get("reach_after", probe["reach"]),
                 probe["nested"].get("connect_after", probe["connect"]))):
            self.assertFalse(seen["/run/worldline-broker.sock"], label)
            self.assertFalse(seen["/run/worldline-worker-broker.sock"], label)
            self.assertFalse(seen["/run/worldline-report"], label)
            self.assertFalse(seen["/run/worldline-verifiers"], label)
            self.assertFalse(seen["/opt/worldline-gnat"], label)
            for surface, outcome in connect.items():
                self.assertNotEqual(outcome, "CONNECTED",
                                    "%s: candidate reached %s" % (label, surface))
        # (b) The candidate's PID namespace contains no worker (uid 1) process, and the only
        #     uid-0 process is its own bwrap supervisor (pid 1) whose root and environ stay
        #     unreadable. It can read the environment of no process outside its own uid.
        self.assertNotIn("1", probe["proc_visible_uids"],
                         "a worker (uid 1) process was visible to the candidate")
        self.assertEqual(probe["foreign_readable_environ"], [],
                         "candidate read a foreign process's environment via /proc")
        self.assertFalse(probe["pid1"].get("environ_readable"),
                         "candidate read the sandbox supervisor's environ")
        self.assertNotEqual(probe["pid1"].get("kill0"), "PERMITTED",
                            "candidate could signal the sandbox supervisor")
        self.assertTrue(all(state in ("ESRCH", "EPERM")
                            for state in probe["kill_probe"].values()),
                        probe["kill_probe"])
        # (c) /proc/1/root is the candidate's own root; the broker sockets are not under it.
        proc1 = probe["proc1_root_run"]
        if isinstance(proc1, list):
            self.assertNotIn("worldline-broker.sock", proc1)
            self.assertNotIn("worldline-worker-broker.sock", proc1)
            self.assertNotIn("worldline-report", proc1)
        # If the kernel allowed the nested user namespace, mapping to root must not have
        # widened reach (already checked in (a)); just record that it stayed contained.
        if probe["nested"].get("userns") == "ALLOWED":
            self.assertIn("reach_after", probe["nested"])
        self._assert_clean_teardown(spec)

    # -- scenario 8 ------------------------------------------------------------
    def test_scenario8_nested_mount_does_not_change_copyout(self):
        # Two acceptable outcomes: a VALID run whose copy-out collected the underlying content,
        # or an explicit refusal from the copier. Never a copy that captured the nested ghost.
        try:
            spec, result = self._run("mountid", {"mode": "mountid", "timeout": 120})
        except WorldlineError as refused:
            self.assertEqual(refused.code, "PRIVATE_EVALUATOR_BOUNDARY_FAILED")
            runtime = self.base / "mountid"
            boundary = json.loads((runtime / "boundary.json").read_text())
            self.assertIn("CASE_COPY", boundary["error"])
            self.assertFalse(boundary.get("rolesCompleted", False))
            _record("8", refused=boundary["error"])
            self._assert_clean_teardown(_SpecShim(runtime, boundary["runId"]))
            return
        self.assertEqual(result["exitCode"], 0, result["stdout"] + result["stderr"])
        probe = self._worker_probe(result)
        _record("8", nested_mount=probe["probe"], copied=probe["copied_out"],
                underlying=probe["have_underlying"], ghost=probe["have_ghost"])
        if probe["copied_out"]:
            self.assertTrue(probe["have_underlying"])
            self.assertFalse(probe["have_ghost"])
        self._assert_clean_teardown(spec)


class _SpecShim:
    """Minimal stand-in exposing the two attributes the clean-teardown/residue audits read,
    for scenarios where the WorldlineError refusal means we never receive a spec object."""

    def __init__(self, runtime, run_id):
        self.runtime = Path(runtime)
        self.run_id = run_id


@_GATE
class CaseCopyTreeShapes(unittest.TestCase):
    """Scenario 5: huge, deep and strange trees drive copy_case_tree to a clean refusal or a
    correct copy, never a crash or hang. Tree-shape logic is exercised directly (no sandbox)."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-case-shape-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.logical = "/logical/shape"

    def _copy(self, **kwargs):
        return copy_case_tree(self.source, self.root / ("dst-" + uuid.uuid4().hex),
                              logical_root=self.logical, **kwargs)

    def test_entry_count_over_limit_refuses(self):
        # The one genuinely large tree in the module: just over the 100,000-entry default.
        overflow = self.source / "flat"
        overflow.mkdir()
        count = MAX_CASE_ENTRIES + 1
        opener = os.open
        for index in range(count):
            fd = opener(str(overflow / str(index)), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.close(fd)
        with self.assertRaises(CaseCopyError) as caught:
            self._copy()
        self.assertEqual(caught.exception.code, "CASE_COPY_LIMIT")

    def test_depth_over_limit_refuses(self):
        node = self.source
        for _ in range(MAX_CASE_DEPTH + 2):
            node = node / "d"
            node.mkdir()
        with self.assertRaises(CaseCopyError) as caught:
            self._copy()
        self.assertEqual(caught.exception.code, "CASE_COPY_LIMIT")

    def test_apparent_size_over_limit_refuses_via_sparse_file(self):
        big = self.source / "sparse.bin"
        with open(big, "wb") as handle:
            handle.truncate(MAX_CASE_BYTES + 1)
        self.assertGreater(big.stat().st_size, MAX_CASE_BYTES)
        with self.assertRaises(CaseCopyError) as caught:
            self._copy()
        self.assertEqual(caught.exception.code, "CASE_COPY_LIMIT")

    def test_long_newline_and_non_utf8_names_copy_without_crashing(self):
        (self.source / ("n" * 255)).write_bytes(b"long name\n")
        (self.source / "with\nnewline").write_bytes(b"newline name\n")
        raw_dir = os.path.join(os.fsencode(self.source), b"raw_\xff\xfe")
        os.mkdir(raw_dir)
        with open(os.path.join(raw_dir, b"child.txt"), "wb") as handle:
            handle.write(b"non utf8 parent\n")
        manifest = self._copy()
        self.assertGreaterEqual(manifest["entries"], 4)
        self.assertEqual(manifest, self._copy())

    def test_symlink_loops_and_self_reference_do_not_hang(self):
        (self.source / "a").symlink_to("b")
        (self.source / "b").symlink_to("a")
        (self.source / "to_root").symlink_to(".")
        (self.source / "sub").mkdir()
        (self.source / "sub" / "abs_internal").symlink_to(self.logical + "/sub")
        manifest = self._copy()
        self.assertEqual(manifest, self._copy())
        links = 0
        second = copy_case_tree(self.source, self.root / "verify",
                                logical_root=self.logical)
        self.assertEqual(manifest["sha256"], second["sha256"])
        self.assertTrue((self.root / "verify" / "a").is_symlink())

    def test_absolute_external_symlink_refused(self):
        (self.source / "escape").symlink_to("/etc/passwd")
        with self.assertRaises(CaseCopyError) as caught:
            self._copy()
        self.assertEqual(caught.exception.code, "CASE_COPY_LINK_ESCAPE")

    def test_special_permission_bits_refused(self):
        for label, mode in (("setuid", 0o4755), ("setgid", 0o2755), ("sticky", 0o1755)):
            with self.subTest(label=label), tempfile.TemporaryDirectory(dir=self.root) as tmp:
                src = Path(tmp) / "source"
                src.mkdir()
                target = src / "entry"
                target.mkdir()
                target.chmod(mode)
                with self.assertRaises(CaseCopyError) as caught:
                    copy_case_tree(src, Path(tmp) / "dst", logical_root=self.logical)
                self.assertEqual(caught.exception.code, "CASE_COPY_UNSUPPORTED")

    def test_user_xattr_refused_when_supported(self):
        target = self.source / "attributed"
        target.write_bytes(b"content\n")
        try:
            os.setxattr(target, b"user.attack", b"1")
        except OSError as exc:
            self.skipTest("filesystem does not support user xattrs: %s" % exc)
        with self.assertRaises(CaseCopyError) as caught:
            self._copy()
        self.assertEqual(caught.exception.code, "CASE_COPY_UNSUPPORTED")


if __name__ == "__main__":
    unittest.main()
