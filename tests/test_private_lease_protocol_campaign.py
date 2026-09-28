"""Adversarial campaign against the stateful worker-broker candidate-lease protocol.

Pre-merge requirement for WORLDLINE PR #6 (release 1.6.0). An external reviewer asked:
"Attack state transitions and concurrency around the broker. Verify every scenario ends
either in a clean valid state or an explicit refusal, never half-synchronized evidence."

Every test drives the REAL private evaluator (user systemd + bubblewrap + mapped
subordinate ids), like tests/test_private_case_lease.py. A single trusted worker program
(``lease_worker.py``, mapped uid 1) is the only principal that can reach
``/run/worldline-worker-broker.sock``; it issues the adversarial request sequences. The
examiner (uid 0) merely launches the worker and reports pass/fail.

Two run-level invariant shapes, asserted deterministically (never which side of a race
wins):

* LEGITIMATE scenario  -> the evaluation returns cleanly: exitCode 0, boundary
  ``rolesCompleted`` True, report ``failures="0"``.
* ILLEGITIMATE scenario -> the WHOLE run refuses: ``WorldlineError`` with code
  ``PRIVATE_EVALUATOR_BOUNDARY_FAILED``; ``boundary["error"]`` carries the named refusal;
  ``rolesCompleted`` is never set.

For EVERY scenario we also assert two host-observable boundary invariants:

* the operator's real source tree is byte-for-byte unchanged (full manifest: path, type,
  mode, bytes, symlink target) -- no half-synchronized evidence ever reaches it; and
* the supervising systemd unit is gone afterwards, so no candidate process or sandbox is
  left running (all sandboxes are descendants of that one unit).

The worker-copy-internal "either exact pre-op state or exact fully-copied state" guarantee
is shown positively in ``test_positive_full_lifecycle_preserves_exact_manifests`` (the
fully-copied side, with full manifests) and holds structurally for the pre-op side: every
copy_out/sync_in/close checks its preconditions and re-verifies the worker generation
before any ``os.rename``, and rolls back a failed swap, so a refused mutation never leaves
a partial tree.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import tempfile
import time
import unittest
import uuid

from worldline.errors import WorldlineError
from worldline.linux.private_evaluator import (
    PrivateEvaluationSpec, PrivateEvaluator, VERIFIER_MOUNT,
)
from worldline.linux.systemd import SystemdAdapter
from worldline.trusted import TRUSTED_INTERPRETER


LOGICAL = "/logical/lease-campaign"
# Optional: WORLDLINE_CAMPAIGN_LOG=/path.jsonl records the exact observed refusal strings.
_LOG = os.environ.get("WORLDLINE_CAMPAIGN_LOG")


# The single worker program. LOGICAL is baked in as a literal so no string formatting can
# corrupt the many braces/percent signs below. MODE (argv[1]) selects the attack sequence.
_WORKER = r'''
import base64, hashlib, json, os, socket, stat, sys, time
from pathlib import Path

LOGICAL = "/logical/lease-campaign"
CROOT = LOGICAL + "/cases"
SOCK = "/run/worldline-worker-broker.sock"
MODE = sys.argv[1]


def broker(request):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(90)
        client.connect(SOCK)
        client.sendall(json.dumps(request).encode() + b"\n")
        line = client.makefile("rb").readline(16 * 1024 * 1024)
    response = json.loads(line) if line.strip() else {}
    if "error" in response:
        raise RuntimeError(response["error"])
    return response


def raw_broker(raw):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(90)
        client.connect(SOCK)
        client.sendall(raw)
        line = client.makefile("rb").readline(16 * 1024 * 1024)
    response = json.loads(line) if line.strip() else {}
    if "error" in response:
        raise RuntimeError(response["error"])
    return response


def open_case(root):
    return broker({"op": "case_open", "caseRoot": root})["caseHandle"]


def start(ch, program, stdin=b"", env=None, cwd=LOGICAL, timeout=30):
    request = {"op": "case_start", "caseHandle": ch,
               "argv": ["/usr/bin/python3", "-c", program], "cwd": cwd,
               "timeout": timeout, "stdinB64": base64.b64encode(stdin).decode()}
    if env is not None:
        request["env"] = env
    return broker(request)["handle"]


def wait_done(ch, h):
    while True:
        waited = broker({"op": "case_wait", "caseHandle": ch, "handle": h, "waitMs": 1000})
        if waited["done"]:
            return waited


def teardown(ch, h):
    return broker({"op": "case_teardown", "caseHandle": ch, "handle": h})


def status(ch):
    return broker({"op": "case_status", "caseHandle": ch})


def copy_out(ch):
    return broker({"op": "case_copy_out", "caseHandle": ch})


def sync_in(ch, expected):
    return broker({"op": "case_sync_in", "caseHandle": ch, "expectedGeneration": expected})


def close_case(ch):
    return broker({"op": "case_close", "caseHandle": ch})


def manifest(root):
    root = Path(root)
    out = {}

    def rec(directory, prefix):
        for name in sorted(os.listdir(directory)):
            path = directory / name
            rel = prefix + name
            info = os.lstat(path)
            mode = stat.S_IMODE(info.st_mode)
            if stat.S_ISLNK(info.st_mode):
                out[rel] = ["link", os.readlink(path)]
            elif stat.S_ISDIR(info.st_mode):
                out[rel] = ["dir", mode]
                rec(path, rel + "/")
            elif stat.S_ISREG(info.st_mode):
                out[rel] = ["file", mode, hashlib.sha256(path.read_bytes()).hexdigest()]
            else:
                out[rel] = ["other"]
    rec(root, "")
    return out


def build_case(path, input_text="v0\n"):
    p = Path(path)
    p.mkdir(parents=True)
    os.chmod(p, 0o755)
    f = p / "input.txt"
    f.write_text(input_text)
    os.chmod(f, 0o644)
    sub = p / "sub"
    sub.mkdir()
    os.chmod(sub, 0o755)
    d = sub / "data.bin"
    d.write_bytes(b"\x00\x01\x02")
    os.chmod(d, 0o600)


def sha(data):
    return hashlib.sha256(data).hexdigest()


WRITER = ("import os, pathlib\n"
          "c = pathlib.Path('%s')\n"
          "p = c / 'output.txt'\n"
          "p.write_text('candidate out\\n')\n"
          "os.chmod(p, 0o644)\n"
          "os.symlink('input.txt', c / 'link')\n")

READER = ("import os, pathlib\n"
          "c = pathlib.Path('%s')\n"
          "v = (c / 'input.txt').read_text()\n"
          "s = c / 'seen.txt'\n"
          "s.write_text(v)\n"
          "os.chmod(s, 0o644)\n")

EMIT = "import sys\nsys.stdout.buffer.write(b'x' * %d)\nsys.stdout.flush()\n"
SLEEP_EXIT = "import time, sys\ntime.sleep(%f)\nsys.exit(0)\n"

BIG = 900000
OVER = 2000000


def done(ok, **extra):
    print("RESULT:" + json.dumps({"ok": bool(ok), **extra}, sort_keys=True))


def mode_positive_full_lifecycle():
    main = CROOT + "/main"
    build_case(main)
    init = manifest(main)
    ch = open_case(main)
    checks = {"manifest_after_open_is_init": manifest(main) == init}

    h1 = start(ch, WRITER % main)
    wait_done(ch, h1)
    teardown(ch, h1)
    st = status(ch)
    checks["dirty_after_candidate_write"] = st["dirty"] is True
    checks["no_handle_after_teardown"] = st["handles"] == 0
    copy_out(ch)
    expect1 = dict(init)
    expect1["output.txt"] = ["file", 0o644, sha(b"candidate out\n")]
    expect1["link"] = ["link", "input.txt"]
    checks["copy_out_is_exact_fully_copied_state"] = manifest(main) == expect1

    # Worker edits, then copies its edit INTO the candidate view; a candidate then observes it.
    edited = Path(main) / "input.txt"
    edited.write_text("v1\n")
    os.chmod(edited, 0o644)
    st2 = status(ch)
    checks["worker_changed_detected"] = st2["workerChanged"] is True
    sync_in(ch, st2["generation"])
    h2 = start(ch, READER % main)
    wait_done(ch, h2)
    teardown(ch, h2)
    copy_out(ch)
    after = manifest(main)
    checks["sync_in_delivered_worker_edit_to_candidate"] = (
        after.get("seen.txt") == ["file", 0o644, sha(b"v1\n")])
    checks["input_edit_survived_roundtrip"] = (
        after.get("input.txt") == ["file", 0o644, sha(b"v1\n")])
    close_case(ch)

    # Sibling case roots (neither inside the other) must both be leasable at once.
    build_case(CROOT + "/sib_a")
    build_case(CROOT + "/sib_b")
    ca = open_case(CROOT + "/sib_a")
    cb = open_case(CROOT + "/sib_b")
    checks["sibling_leases_distinct"] = ca != cb
    close_case(ca)
    close_case(cb)
    done(all(checks.values()), checks=checks)


def mode_streaming_under_cap_is_consistent():
    big = CROOT + "/big"
    build_case(big)
    ch = open_case(big)
    h = start(ch, EMIT % BIG)
    waited = wait_done(ch, h)
    wait_stdout = base64.b64decode(waited["stdoutB64"])
    acc = b""
    offset = 0
    for _ in range(200):
        streamed = broker({"op": "case_stream", "caseHandle": ch, "handle": h,
                           "stdoutOffset": offset, "stderrOffset": 0})
        chunk = base64.b64decode(streamed["stdoutB64"])
        acc += chunk
        offset = streamed["stdoutNext"]
        if streamed["done"] and not chunk:
            break
    teardown(ch, h)
    copy_out(ch)
    close_case(ch)
    expected = sha(b"x" * BIG)
    checks = {
        "wait_output_complete": sha(wait_stdout) == expected,
        "stream_output_complete": sha(acc) == expected,
        "stream_equals_wait": sha(acc) == sha(wait_stdout),
        "length_exact": len(acc) == BIG and len(wait_stdout) == BIG,
    }
    done(all(checks.values()), checks=checks)


# ---- refusal sequences: each performs its offending op last; the RuntimeError propagates.

def open_two():
    build_case(CROOT + "/main")
    return CROOT + "/main"


def mode_open_same_dir():
    main = open_two()
    open_case(main)
    open_case(main)


def mode_open_parent_then_child():
    build_case(CROOT + "/p")
    (Path(CROOT + "/p") / "child").mkdir()
    open_case(CROOT + "/p")
    open_case(CROOT + "/p/child")


def mode_open_child_then_parent():
    build_case(CROOT + "/p")
    (Path(CROOT + "/p") / "child").mkdir()
    open_case(CROOT + "/p/child")
    open_case(CROOT + "/p")


def mode_open_outside():
    open_case("/etc")


def mode_open_symlink():
    build_case(CROOT + "/main")
    os.symlink(CROOT + "/main", CROOT + "/linkcase")
    open_case(CROOT + "/linkcase")


def mode_open_nondir():
    Path(CROOT).mkdir(parents=True)
    (Path(CROOT) / "afile").write_text("not a dir\n")
    open_case(CROOT + "/afile")


def mode_close_active_handle():
    main = open_two()
    ch = open_case(main)
    h = start(ch, SLEEP_EXIT % 20.0)
    close_case(ch)  # handle still live -> refuse


def mode_close_dirty():
    main = open_two()
    ch = open_case(main)
    h = start(ch, "import sys; sys.exit(0)")
    wait_done(ch, h)
    teardown(ch, h)
    close_case(ch)  # torn down but dirty -> refuse


def mode_copyout_active_handle():
    main = open_two()
    ch = open_case(main)
    h = start(ch, SLEEP_EXIT % 20.0)
    copy_out(ch)  # handle live -> refuse


def mode_copyout_not_dirty():
    main = open_two()
    ch = open_case(main)
    copy_out(ch)  # nothing ran -> refuse


def mode_syncin_active_handle():
    main = open_two()
    ch = open_case(main)
    st = status(ch)
    h = start(ch, SLEEP_EXIT % 20.0)
    sync_in(ch, st["generation"])  # handle live -> refuse


def mode_syncin_stale_generation():
    # Legit sync_in, then REPLAY the same request verbatim with the now-stale generation.
    main = open_two()
    ch = open_case(main)
    g0 = status(ch)["generation"]
    (Path(main) / "input.txt").write_text("v1\n")
    sync_in(ch, g0)                       # ok; generation advances
    (Path(main) / "input.txt").write_text("v2\n")
    sync_in(ch, g0)                       # replay of an earlier generation -> refuse


def mode_syncin_dirty():
    main = open_two()
    ch = open_case(main)
    g0 = status(ch)["generation"]
    h = start(ch, "import sys; sys.exit(0)")
    wait_done(ch, h)
    teardown(ch, h)
    sync_in(ch, g0)  # dirty -> refuse


def mode_case_handle_after_close():
    main = open_two()
    ch = open_case(main)
    close_case(ch)
    status(ch)  # closed lease -> refuse


def mode_candidate_handle_after_teardown():
    main = open_two()
    ch = open_case(main)
    h = start(ch, "import sys; sys.exit(0)")
    wait_done(ch, h)
    teardown(ch, h)
    broker({"op": "case_stream", "caseHandle": ch, "handle": h,
            "stdoutOffset": 0, "stderrOffset": 0})  # torn-down handle -> refuse


def mode_handle_from_another_case():
    build_case(CROOT + "/a")
    build_case(CROOT + "/b")
    ca = open_case(CROOT + "/a")
    cb = open_case(CROOT + "/b")
    ha = start(ca, SLEEP_EXIT % 20.0)
    broker({"op": "case_stream", "caseHandle": cb, "handle": ha,
            "stdoutOffset": 0, "stderrOffset": 0})  # handle belongs to case a -> refuse


def mode_forged_case_handle():
    open_two()
    status("0" * 32)  # never issued -> refuse


def mode_wrong_type_case_handle():
    open_two()
    broker({"op": "case_status", "caseHandle": [1, 2, 3]})  # wrong type -> refuse


def mode_start_on_closed_handle():
    main = open_two()
    ch = open_case(main)
    close_case(ch)
    start(ch, "import sys; sys.exit(0)")  # start on closed handle -> refuse


def mode_exited_handle_still_active():
    # A short-lived candidate exits on its own; without teardown its handle is still
    # "active", so copy_out must refuse regardless of the exit/op race.
    main = open_two()
    ch = open_case(main)
    h = start(ch, SLEEP_EXIT % 0.02)
    copy_out(ch)  # handle present (exited or not) -> refuse


def mode_output_over_cap():
    big = CROOT + "/big"
    build_case(big)
    ch = open_case(big)
    h = start(ch, EMIT % OVER)
    wait_done(ch, h)  # candidate exceeded 1 MiB output cap -> refuse


def mode_shape_open_extra_key():
    open_two()
    broker({"op": "case_open", "caseRoot": CROOT + "/main", "extra": 1})


def mode_shape_start_missing_key():
    main = open_two()
    ch = open_case(main)
    broker({"op": "case_start", "caseHandle": ch,
            "argv": ["/usr/bin/python3", "-c", "pass"], "cwd": LOGICAL, "timeout": 30})


def mode_shape_status_extra_key():
    main = open_two()
    ch = open_case(main)
    broker({"op": "case_status", "caseHandle": ch, "extra": 1})


def mode_oversized_request():
    broker({"op": "case_open", "caseRoot": "/" + "a" * 70000})


def mode_non_json():
    raw_broker(b"this is not json at all\n")


def mode_unknown_op():
    broker({"op": "case_frobnicate"})


def mode_env_ld_preload():
    main = open_two()
    ch = open_case(main)
    start(ch, "pass", env={"LD_PRELOAD": "/tmp/x.so"})


def mode_env_hashseed_abc():
    main = open_two()
    ch = open_case(main)
    start(ch, "pass", env={"PYTHONHASHSEED": "abc"})


def mode_env_dontwrite_zero():
    main = open_two()
    ch = open_case(main)
    start(ch, "pass", env={"PYTHONDONTWRITEBYTECODE": "0"})


def mode_argv_outside_roots():
    main = open_two()
    ch = open_case(main)
    broker({"op": "case_start", "caseHandle": ch, "argv": ["/sbin/badexe"],
            "cwd": LOGICAL, "timeout": 30, "stdinB64": ""})


def mode_cwd_dotdot():
    main = open_two()
    ch = open_case(main)
    broker({"op": "case_start", "caseHandle": ch,
            "argv": ["/usr/bin/python3", "-c", "pass"], "cwd": LOGICAL + "/../etc",
            "timeout": 30, "stdinB64": ""})


def mode_waitms_over():
    main = open_two()
    ch = open_case(main)
    h = start(ch, SLEEP_EXIT % 20.0)
    broker({"op": "case_wait", "caseHandle": ch, "handle": h, "waitMs": 3000})


def mode_negative_timeout():
    main = open_two()
    ch = open_case(main)
    broker({"op": "case_start", "caseHandle": ch,
            "argv": ["/usr/bin/python3", "-c", "pass"], "cwd": LOGICAL,
            "timeout": -1, "stdinB64": ""})


DISPATCH = {name[len("mode_"):]: value for name, value in dict(globals()).items()
            if name.startswith("mode_")}
DISPATCH[MODE]()
'''


_EXAMINER = '''import candidate, json
from pathlib import Path
result = candidate.run(['/usr/bin/python3', '-I', 'lease_worker.py', MODE], timeout=110)
text = result.stdout.decode('utf-8', 'replace')
ok = False
for line in text.splitlines():
    if line.startswith('RESULT:'):
        try:
            ok = json.loads(line[len('RESULT:'):]).get('ok') is True
        except Exception:
            ok = False
ok = ok and result.returncode == 0
Path('/run/worldline-report/report').write_text(
    '<testsuite tests="1" failures="' + ('0' if ok else '1') + '" errors="0"/>')
print(text[-6000:])
print(result.stderr.decode('utf-8', 'replace')[-2000:])
raise SystemExit(0 if ok else 1)
'''


REFUSAL_CASES = (
    ("open_same_dir", "overlaps an active lease"),
    ("open_parent_then_child", "overlaps an active lease"),
    ("open_child_then_parent", "overlaps an active lease"),
    ("open_outside", "not strictly inside the active worker copy"),
    ("open_symlink", "not a real directory in the worker copy"),
    ("open_nondir", "not a real directory in the worker copy"),
    ("close_active_handle", "requires copy-out and torn-down handles"),
    ("close_dirty", "requires copy-out and torn-down handles"),
    ("copyout_active_handle", "requires torn-down candidate handles"),
    ("copyout_not_dirty", "no candidate output to copy"),
    ("syncin_active_handle", "requires a quiescent matching generation"),
    ("syncin_stale_generation", "requires a quiescent matching generation"),
    ("syncin_dirty", "requires a quiescent matching generation"),
    ("case_handle_after_close", "unknown scoped case lease"),
    ("candidate_handle_after_teardown", "candidate process handle is outside scoped case"),
    ("handle_from_another_case", "candidate process handle is outside scoped case"),
    ("forged_case_handle", "unknown scoped case lease"),
    ("wrong_type_case_handle", "unknown scoped case lease"),
    ("start_on_closed_handle", "unknown scoped case lease"),
    ("output_over_cap", "exceeded output limit"),
    ("shape_open_extra_key", "scoped case open has wrong shape"),
    ("shape_start_missing_key", "scoped case start has wrong shape"),
    ("shape_status_extra_key", "scoped status has wrong shape"),
    ("oversized_request", "broker message exceeds limit"),
    ("non_json", "broker failed or did not become quiescent"),
    ("unknown_op", "worker broker operation is unsupported"),
    ("env_ld_preload", "determinism allowlist"),
    ("env_hashseed_abc", "determinism allowlist"),
    ("env_dontwrite_zero", "determinism allowlist"),
    ("argv_outside_roots", "outside system binaries/candidate roots"),
    ("cwd_dotdot", "must be an absolute normalized path"),
    ("waitms_over", "wait budget is outside the allowed range"),
    ("negative_timeout", "invalid worker timeout"),
)


def _host_manifest(root: Path) -> dict:
    out: dict[str, list] = {}

    def rec(directory: Path, prefix: str) -> None:
        for name in sorted(os.listdir(directory)):
            path = directory / name
            rel = prefix + name
            info = os.lstat(path)
            mode = stat.S_IMODE(info.st_mode)
            if stat.S_ISLNK(info.st_mode):
                out[rel] = ["link", os.readlink(path)]
            elif stat.S_ISDIR(info.st_mode):
                out[rel] = ["dir", mode]
                rec(path, rel + "/")
            elif stat.S_ISREG(info.st_mode):
                import hashlib
                out[rel] = ["file", mode, hashlib.sha256(path.read_bytes()).hexdigest()]
            else:
                out[rel] = ["other"]
    rec(root, "")
    return out


@unittest.skipUnless(os.environ.get("WORLDLINE_PRIVATE_EVALUATOR_TEST") == "1",
                     "set WORLDLINE_PRIVATE_EVALUATOR_TEST=1 for real user-systemd integration")
class PrivateLeaseProtocolCampaign(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-lease-campaign-",
                                                      dir=str(Path.home()))
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / "source"
        self.source.mkdir(mode=0o755)
        (self.source / "lease_worker.py").write_text(_WORKER)
        self.source_manifest = _host_manifest(self.source)
        self.verifier = self.base / "verifier"
        self.verifier.mkdir()
        self.adapter = SystemdAdapter()

    def _run_mode(self, mode: str):
        (self.verifier / "exam.py").write_text("MODE = " + repr(mode) + "\n" + _EXAMINER)
        run_id = str(uuid.uuid4())
        token = mode + "-" + run_id[:8]
        report = self.base / (token + "-report")
        report.mkdir(mode=0o700)
        spec = PrivateEvaluationSpec(
            run_id, {LOGICAL: self.source}, self.verifier,
            (TRUSTED_INTERPRETER, VERIFIER_MOUNT + "/exam.py"), LOGICAL, report,
            self.base / (token + "-runtime"), timeout_seconds=120)
        # Retained so a refusal (which raises out of .run) can still be located precisely.
        self._last_spec = spec
        return spec, PrivateEvaluator(self.adapter).run(
            spec, resource_properties=("MemoryMax=2G", "TasksMax=128"))

    def _assert_unit_gone(self, run_id: str) -> None:
        unit = SystemdAdapter.unit_name(run_id)
        for _ in range(150):
            shown = self.adapter._show(unit, ("ActiveState", "SubState", "LoadState"))
            if shown is None or shown.get("ActiveState") in (None, "", "inactive", "failed") \
                    or shown.get("LoadState") in (None, "", "not-found"):
                return
            time.sleep(0.1)
        self.fail(f"supervising unit {unit} still active: {shown}")

    def _assert_source_pristine(self) -> None:
        self.assertEqual(_host_manifest(self.source), self.source_manifest,
                         "operator source tree was mutated by the evaluation")

    # ---- legitimate scenarios: the run completes cleanly.

    def test_positive_full_lifecycle_preserves_exact_manifests(self):
        spec, result = self._run_mode("positive_full_lifecycle")
        self.assertEqual(result["exitCode"], 0, result["stdout"] + result["stderr"])
        self.assertIn(b'failures="0"', (result["reportDirectory"] / "report").read_bytes())
        boundary = result["boundary"]
        self.assertTrue(boundary["rolesCompleted"])
        leases = boundary["caseLeases"]
        self.assertEqual(leases[0]["events"][0], "open")
        self.assertEqual(leases[0]["events"][-1], "close")
        self.assertIn("copy-out", leases[0]["events"])
        self.assertIn("copy-in", leases[0]["events"])
        self._assert_source_pristine()
        self._assert_unit_gone(spec.run_id)

    def test_streaming_under_cap_is_complete_and_consistent(self):
        spec, result = self._run_mode("streaming_under_cap_is_consistent")
        self.assertEqual(result["exitCode"], 0, result["stdout"] + result["stderr"])
        self.assertIn(b'failures="0"', (result["reportDirectory"] / "report").read_bytes())
        self.assertTrue(result["boundary"]["rolesCompleted"])
        self._assert_source_pristine()
        self._assert_unit_gone(spec.run_id)

    # ---- illegitimate scenarios: the whole run refuses with a named reason.

    def _assert_run_refused(self, mode: str, fragment: str) -> str:
        with self.assertRaises(WorldlineError) as raised:
            self._run_mode(mode)
        self.assertEqual(raised.exception.code, "PRIVATE_EVALUATOR_BOUNDARY_FAILED",
                         f"{mode}: {raised.exception}")
        boundary = json.loads((self._last_spec.runtime / "boundary.json").read_text())
        error = boundary.get("error", "")
        self.assertIn("broker failed or did not become quiescent", error, f"{mode}: {error}")
        self.assertIn(fragment, error, f"{mode}: {error}")
        self.assertFalse(boundary.get("rolesCompleted", False), mode)
        if _LOG:
            with open(_LOG, "a") as handle:
                handle.write(json.dumps({"mode": mode, "error": error}) + "\n")
        return error

    def test_protocol_violations_refuse_the_whole_run(self):
        for mode, fragment in REFUSAL_CASES:
            with self.subTest(mode=mode):
                self._assert_run_refused(mode, fragment)
                self._assert_source_pristine()

    def test_exited_but_untorndown_handle_is_still_active_across_the_exit_race(self):
        # Bounded loop: the candidate exits on its own; the copy_out may land before or
        # after that exit. The handle stays in the lease until teardown either way, so the
        # invariant (copy_out refuses) never depends on which side wins.
        for attempt in range(3):
            with self.subTest(attempt=attempt):
                self._assert_run_refused("exited_handle_still_active",
                                         "requires torn-down candidate handles")
                self._assert_source_pristine()


if __name__ == "__main__":
    unittest.main()
