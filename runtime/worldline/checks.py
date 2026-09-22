from __future__ import annotations

import base64
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
import subprocess
import time
from typing import Any, Mapping, Sequence
import uuid
import xml.etree.ElementTree as ET

from .trusted import trusted_inline
from .canonical import atomic_write_json
from .executed import UNIDENTIFIED, VERIFIER_MOUNT, ExecutionVerifierSet
from .errors import WorldlineError
from .linux.namespaces import BubblewrapSandbox, OverlayRoot, SandboxSpec
from .admission import Gate
from .linux.systemd import SystemdAdapter
from .project import CheckSpec
from .environment import safe_environment
from .paths import WorldlinePaths, secure_directory

# The authoritative result channel.
#
# The record used to be written to a file in /run/worldline-runtime. That directory is
# bind-mounted read-write and is the world's XDG_RUNTIME_DIR, so the very processes under
# examination could create, replace or symlink the file that reports on them. Isolating the
# harness's imports closed the route to OWNING the harness and left open the route to simply
# writing its conclusion.
#
# A nonce would not have fixed it: the examiner's children run as the same user in the same PID
# namespace, so anything passed in argv, the environment or the spec is readable through procfs.
# What they cannot do is append to this stream undetected. The harness writes ONE framed record
# to its own stdout -- a pipe held by the supervisor, never inherited by the examiner, whose own
# stdout and stderr are pipes the harness reads -- and writes nothing else. The supervisor
# therefore requires the entire stream to be exactly one frame: a prefix, a suffix or a second
# frame is interference, not a result.
#
# The harness also exits with the examiner's status, so the SERVICE MANAGER records the verdict
# independently of anything inside the sandbox. Suppressing the frame means killing the harness,
# which the manager reports as a signal. The two observations must agree or the check refuses.
RECORD_MARKER = "\x1e--worldline-check-record-v1--\x1e"

_CHECK_RUNNER = """
import base64
import json
from pathlib import Path
import subprocess
import sys
import time
MARKER = '\x1e--worldline-check-record-v1--\x1e'
specification = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
started = time.monotonic_ns()
completed = subprocess.run(specification['argv'], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
result = None
if specification['result'] is not None:
    path = Path(specification['result'])
    if path.is_file():
        result = base64.b64encode(path.read_bytes()).decode('ascii')
code = completed.returncode
record = json.dumps({
    'schemaVersion': 2,
    'exitCode': code,
    'durationNs': time.monotonic_ns() - started,
    'stdoutB64': base64.b64encode(completed.stdout).decode('ascii'),
    'stderrB64': base64.b64encode(completed.stderr).decode('ascii'),
    'resultB64': result,
}, sort_keys=True, separators=(',', ':'))
sys.stdout.write(MARKER + record + MARKER)
sys.stdout.flush()
# Exit with the examiner's status so the service manager records the verdict too. Signals follow
# the shell convention; the supervisor computes the same mapping and compares.
sys.exit(code & 0xFF if code >= 0 else min(255, 128 - code))
""".strip()


def expected_unit_exit(examiner_exit: int) -> int:
    """The unit exit status the harness produces for a given examiner status.

    Mirrors the harness exactly. Python reports a signalled child as a negative number, which
    `sys.exit` cannot express, so signals follow the shell convention.
    """
    return examiner_exit & 0xFF if examiner_exit >= 0 else min(255, 128 - examiner_exit)


def parse_record_stream(stream: bytes) -> tuple[dict[str, Any] | None, str | None]:
    """The framed record, or None and a named reason.

    The whole stream must be one frame. Anything else means something other than the harness
    wrote to the harness's stdout, and a result that cannot be attributed is not a result.
    """
    text = stream.decode("utf-8", "replace")
    parts = text.split(RECORD_MARKER)
    if len(parts) == 1:
        return None, "the harness produced no result record"
    if len(parts) != 3:
        return None, f"the result stream carries {(len(parts) - 1) // 2} frames, so the record cannot be attributed to the harness"
    if parts[0] != "" or parts[2].strip() != "":
        return None, "the result stream carries bytes outside the record frame, so it was written to by more than the harness"
    try:
        record = json.loads(parts[1])
    except json.JSONDecodeError as exc:
        return None, f"the result record is not valid JSON: {exc}"
    if not isinstance(record, dict) or record.get("schemaVersion") != 2:
        return None, "the result record does not have the expected schema"
    return record, None


class CheckRunner:
    def __init__(
        self,
        paths: WorldlinePaths,
        sandbox: BubblewrapSandbox,
        systemd: SystemdAdapter,
        gate: "Gate",
    ) -> None:
        self.paths = paths
        self.sandbox = sandbox
        self.systemd = systemd
        self.gate = gate

    def run(
        self,
        *,
        world_instance: str,
        overlays: Sequence[OverlayRoot],
        primary_target: Path,
        checks: Sequence[CheckSpec],
        verifiers: Sequence[Mapping[str, Any]] = (),
        logical_roots: Mapping[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """`verifiers` is the resolved verifier set for this policy, as `resolve_verifiers`
        returns it; each check takes the members that name it. Passing it is what lets a check be
        identified by the bytes it runs rather than by the path it was given."""
        by_check: dict[str, list[Mapping[str, Any]]] = {}
        for entry in verifiers:
            by_check.setdefault(str(entry.get("checkId")), []).append(entry)
        results: list[dict[str, Any]] = []
        for check in checks:
            results.append(
                self._run_one(
                    world_instance=world_instance,
                    overlays=overlays,
                    primary_target=primary_target,
                    check=check,
                    verifier_entries=by_check.get(check.id, ()),
                    logical_roots=logical_roots,
                )
            )
        return results

    def _run_one(
        self,
        *,
        world_instance: str,
        overlays: Sequence[OverlayRoot],
        primary_target: Path,
        check: CheckSpec,
        verifier_entries: Sequence[Mapping[str, Any]] = (),
        logical_roots: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
        run_id = str(uuid.uuid4())
        runtime = self.paths.overlays / world_instance / "checks" / check.id
        if runtime.exists():
            import shutil

            shutil.rmtree(runtime)
        secure_directory(runtime)
        cwd = primary_target if check.cwd is None else primary_target / check.cwd
        result_path = None if check.result is None else str(cwd / check.result)

        # The declared verifier set is copied out of the overlays and identified by descriptor
        # BEFORE anything runs, and the check is pointed at the staged copies. Until this, a
        # check executed its verifier from inside the world's writable overlay — the file it ran
        # was a file the candidate owned.
        staged: ExecutionVerifierSet | None = None
        argv = list(check.argv)
        rewrites: list[dict[str, str]] = []
        # From the LOWER layer, which is PRIME as the world was forked from it — not from the
        # candidate's merged overlay. The examiner that judges a candidate must not be one the
        # candidate supplied, so tampering with a verifier inside a world now changes nothing
        # about what runs. It is still reported at finalization as VERIFIER_MODIFIED_BY_CANDIDATE;
        # it simply no longer decides anything.
        sources = {root.root_key: root.lower for root in overlays}
        if verifier_entries:
            # A set that cannot be identified is a refusal. Running the check anyway would
            # produce exactly the result this milestone exists to make impossible: a PASS whose
            # provenance nobody can state.
            staged = ExecutionVerifierSet.stage(
                check_id=check.id, entries=verifier_entries, sources=sources,
                staging=runtime.parent / f"{check.id}.verifiers")
            primary_key = next((root.root_key for root in overlays
                                if str(root.target) == str(primary_target)), None)
            argv, rewrites = staged.rewrite_argv(
                argv, dict(logical_roots or {}),
                primary_root_key=primary_key, cwd=check.cwd or "")
            # FAIL CLOSED. rewrite_argv matches an argv token by exact string against the
            # logical path, and a policy may legitimately spell the same verifier another way —
            # a cwd-relative token, a path with a "./" segment, or a `verifiers:` glob argv never
            # names at all. In every one of those the interpreter was handed the path it was
            # always handed, which resolves into the candidate's own overlay, while the evidence
            # happily recorded PRIME's bundle identity as stable and BOUND. A campaign found that
            # and it is worse than having no feature: it reports an authorised, execution-bound
            # evaluation of the examiner the candidate supplied.
            #
            # So: a bundle was staged and nothing was pointed at it means we cannot show the
            # interpreter ran what we measured. That is not a passing check and not a failing
            # one — it is a check whose provenance cannot be stated, and it refuses.
            if not rewrites:
                raise WorldlineError(
                    UNIDENTIFIED,
                    f"check {check.id} declares a verifier bundle but none of its argv tokens"
                    " names one, so the bytes it would execute cannot be shown to be the bytes"
                    " that were identified. Name the verifier by the absolute path of its"
                    " registered root.",
                    {"argv": list(check.argv),
                     "staged": [item.staged for item in staged.items]})

        specification = {
            "schemaVersion": 1,
            "argv": argv,
            "result": result_path,
        }
        atomic_write_json(runtime / "spec.json", specification)
        spec = SandboxSpec(
            instance_id=world_instance,
            # Trusted: this process attests that an examination happened, and its cwd is a
            # managed root, hence candidate-writable by construction. A candidate that planted
            # base64.py there owned this harness on its first import and fabricated a passing
            # result. The policy and the measurements behind it are in trusted.py.
            #
            # This isolates the HARNESS only. The verifier it launches is a separate process and
            # keeps ordinary semantics, because examining candidate code legitimately needs
            # candidate cwd and candidate imports. What the candidate must not get is authority
            # over the process that attests the examination happened.
            argv=trusted_inline(
                _CHECK_RUNNER,
                "/run/worldline-runtime/spec.json",
                "/run/worldline-runtime/result.json",
            ),
            cwd=cwd,
            environment=safe_environment(),
            roots=tuple(overlays),
            runtime=runtime,
            readonly_mounts=((staged.staging, VERIFIER_MOUNT),) if staged is not None else (),
        )
        with self.gate.guard(f"check:{check.id}") as _decision:
            process = self.systemd.launch(
                run_id,
                self.sandbox.build_argv(spec),
                description=f"WORLDLINE check {check.id}",
                resource_properties=self.gate.unit_properties(),
            )
            record_stream, launch_stderr = process.launcher.communicate(timeout=600)
            # Supervisor-owned facts, from the service manager's own journal entries for this
            # unit. The candidate cannot write these: they are the manager's record of a process
            # it supervised, not anything reported from inside the sandbox.
            supervision = self.systemd.outcome(process, process.launcher.returncode)
        executed: dict[str, Any] | None = None
        if staged is not None:
            try:
                after, changes = staged.reread()
                executed = staged.as_evidence()
                executed["identityAfterExecution"] = after
                executed["changedDuringExecution"] = changes
                executed["argvRewrites"] = rewrites
                # The descriptors were held open across the evaluation, so this compares the bytes
                # that ran against themselves rather than asking whether a name still resolves to
                # what it used to.
                executed["stable"] = after == executed["identity"] and not changes
            finally:
                staged.close()
        observed = self._observed_exit(supervision, process.launcher.returncode)
        identity = {
            "id": check.id,
            "kind": check.kind,
            "required": check.required,
            "format": check.format,
            "covers": list(check.covers),
        }

        def refuse(stage: str, reason: str) -> dict[str, Any]:
            # A check that did not complete is NOT a failed check: nothing was evaluated. The
            # stage is named only where supervisor-owned facts establish it.
            return {
                **identity,
                "status": "FAIL",
                "reason": reason,
                "executedVerifierSet": executed,
                "resultChannel": {"accepted": False, "stage": stage, "reason": reason},
                "supervision": supervision,
                "origin": "supervisor",
            }

        raw, channel_error = parse_record_stream(record_stream)
        if raw is None:
            launcher_text = launch_stderr.decode("utf-8", "replace").strip()
            if supervision.get("kind") == "SUPERVISED" and supervision.get("stoppedByManager"):
                stage = "STOPPED_BY_MANAGER"
            elif supervision.get("kind") == "LAUNCH_FAILED":
                stage = "SANDBOX_NEVER_STARTED"
            elif observed["signalled"]:
                stage = "HARNESS_SIGNALLED"
            else:
                # The harness started and produced no attributable record. Which side of the
                # examiner it stopped on is NOT established by anything trusted here, and
                # naming a stage would be inventing one.
                stage = "NO_ATTRIBUTABLE_RECORD"
            return refuse(stage, f"{channel_error}{': ' + launcher_text if launcher_text else ''}")

        # Two independent observations of the same verdict: the harness's own report, and the
        # service manager's record of the unit's exit. They must agree.
        reported = raw["exitCode"]
        if not isinstance(reported, int):
            return refuse("RECORD_MALFORMED", "the result record does not carry an integer exit status")
        if observed["exitStatus"] is None:
            # One observation is not a cross-check. Unknown is not permission.
            return refuse(
                "UNCORROBORATED",
                f"the supervisor could not observe how the check unit ended ({observed['source']}),"
                " so the harness's own report is the only account of the evaluation",
            )
        if observed["exitStatus"] != expected_unit_exit(reported):
            return refuse(
                "CHANNEL_DISAGREEMENT",
                f"the harness reported examiner status {reported} but the service manager"
                f" recorded unit status {observed['exitStatus']}; the two observations of the"
                " same evaluation do not agree",
            )

        # If the staged bundle could not satisfy the examiner's own imports, say so on the
        # result itself. `worldline show` is where an operator reads this, and "FAIL" with no
        # reason sends them to debug their candidate for a defect in the policy.
        gaps = (executed or {}).get("unsatisfiedImports") if executed else None
        stdout = base64.b64decode(raw["stdoutB64"].encode("ascii"), validate=True)
        stderr = base64.b64decode(raw["stderrB64"].encode("ascii"), validate=True)
        result_bytes = None if raw["resultB64"] is None else base64.b64decode(raw["resultB64"].encode("ascii"), validate=True)
        parsed = self._parse(check, reported, stdout, stderr, result_bytes)
        return {
            **identity,
            "argv": list(check.argv),
            "exitCode": reported,
            "durationNs": raw["durationNs"],
            "stdoutB64": raw["stdoutB64"],
            "stderrB64": raw["stderrB64"],
            # The identity of the bytes this evaluation actually ran. Compared at finalization
            # against what the policy declares; a difference is VERIFIER_EXECUTION_IDENTITY_MISMATCH
            # and cannot satisfy the acceptance gate.
            "executedVerifierSet": executed,
            # Three kinds of fact that were being carried as one. Keeping them apart is what
            # stops a judgment inheriting the authority of an observation, or a candidate's
            # own bytes inheriting the authority of a judgment.
            "origin": "supervisor",
            "resultChannel": {
                "accepted": True,
                "frames": 1,
                "exitStatusAgreement": {
                    "status": "AGREED",
                    "harnessReported": reported,
                    "supervisorObserved": observed["exitStatus"],
                    "source": observed["source"],
                    "journal": observed.get("journal"),
                    "launcher": observed.get("launcher"),
                },
            },
            "supervision": supervision,
            "evaluatorCompleteness": (
                {"complete": False,
                 "unsatisfiedImports": gaps,
                 "reason": "the staged verifier bundle cannot satisfy "
                           + ", ".join(sorted({f"{g['verifier']} -> {g['module']}" for g in gaps}))
                           + "; declare the helper in this check's `verifiers` so it is staged"
                             " from PRIME. WORLDLINE will not fall back to the candidate's copy."}
                if gaps else {"complete": True, "unsatisfiedImports": []}
            ),
            "candidateReachable": {
                # Produced by processes under examination. Parsed because a check must be read,
                # never because these bytes are trusted.
                "stdoutB64": raw["stdoutB64"],
                "stderrB64": raw["stderrB64"],
                "resultFilePresent": raw["resultB64"] is not None,
            },
            **parsed,
        }

    @staticmethod
    def _observed_exit(supervision: Mapping[str, Any], launcher_exit: int | None) -> dict[str, Any]:
        """How the unit ended, according to the SUPERVISOR rather than to the sandbox.

        Two supervisor-owned sources, and the difference between them matters:

        launcher     `systemd-run --pipe` propagates the service's exit status as its own, and
                     this process reaped it. Always available. The candidate cannot reach it:
                     systemd-run runs outside the sandbox, and the only way to influence it is
                     to change how the service actually ended.
        journal      the manager's own entry for the main process exiting. Stronger, because it
                     is the manager's record rather than an exit code relayed through a pipe --
                     but systemd writes that entry for a FAILING unit and not for a successful
                     one, so it is absent exactly where a claimed PASS would most want
                     corroborating. It is used when present and never waited for.

        Preferring the journal and stopping there left `exitStatus` None for every passing
        check, which made the cross-check below pass by not asking.
        """
        journal_status = supervision.get("exitStatus")
        journal_status = journal_status if isinstance(journal_status, int) else None
        launcher_status = launcher_exit if isinstance(launcher_exit, int) else None
        if journal_status is not None and launcher_status is not None and journal_status != launcher_status:
            # The two supervisor-owned sources disagree with EACH OTHER. Nothing here is the
            # candidate's doing, but the supervisor cannot state how the unit ended.
            return {"exitStatus": None, "source": "supervisor-sources-disagree",
                    "journal": journal_status, "launcher": launcher_status, "signalled": False}
        status = journal_status if journal_status is not None else launcher_status
        if status is None:
            return {"exitStatus": None, "source": "unobserved", "journal": None,
                    "launcher": None, "signalled": False}
        return {
            "exitStatus": status,
            "source": "service-manager-journal" if journal_status is not None else "launcher-propagated",
            "journal": journal_status,
            "launcher": launcher_status,
            "signalled": status > 128,
        }

    def _parse(
        self,
        check: CheckSpec,
        exit_code: int,
        stdout: bytes,
        stderr: bytes,
        result: bytes | None,
    ) -> dict[str, Any]:
        payload = result if result is not None else stdout
        if check.format == "exit":
            return {"status": "PASS" if exit_code == 0 else "FAIL"}
        if check.format == "junit":
            if result is None:
                return {"status": "FAIL", "reason": "JUnit result file is missing", "tests": None}
            try:
                root = ET.fromstring(result)
                suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
                totals = {
                    name: sum(int(suite.attrib.get(name, "0")) for suite in suites)
                    for name in ("tests", "failures", "errors", "skipped")
                }
            except (ET.ParseError, ValueError) as exc:
                return {"status": "FAIL", "reason": f"invalid JUnit XML: {exc}", "tests": None}
            status = "PASS" if exit_code == 0 and totals["failures"] == 0 and totals["errors"] == 0 else "FAIL"
            return {"status": status, **totals}
        if check.format == "gnatprove":
            text = payload.decode("utf-8", "replace")
            total_line = next((line for line in text.splitlines() if line.startswith("Total")), None)
            if total_line is None:
                return {"status": "FAIL", "reason": "gnatprove Total row is missing", "total": None}
            fields = re.sub(r"\([0-9]+%\)", "", total_line).split()
            if len(fields) != 6:
                return {"status": "FAIL", "reason": "gnatprove Total row is invalid", "total": None}
            count = lambda value: 0 if value == "." else int(value)
            total, justified, unproved = count(fields[1]), count(fields[4]), count(fields[5])
            return {
                "status": "PASS" if exit_code == 0 and justified == 0 and unproved == 0 else "FAIL",
                "total": total,
                "justified": justified,
                "unproved": unproved,
            }
        if check.format == "worldline-benchmark-v1":
            if result is None:
                return {"status": "FAIL", "reason": "benchmark result file is missing"}
            try:
                value = json.loads(result.decode("utf-8", "strict"))
            except (UnicodeError, json.JSONDecodeError) as exc:
                return {"status": "FAIL", "reason": f"invalid benchmark JSON: {exc}"}
            required = {"metric", "unit", "baseline", "candidate", "direction"}
            if not isinstance(value, dict) or set(value) != required or value["direction"] not in {"higher-is-better", "lower-is-better"}:
                return {"status": "FAIL", "reason": "benchmark schema is invalid"}
            try:
                baseline = Decimal(str(value["baseline"]))
                candidate = Decimal(str(value["candidate"]))
            except InvalidOperation:
                return {"status": "FAIL", "reason": "benchmark values are not numeric"}
            improvement = (
                candidate > baseline
                if value["direction"] == "higher-is-better"
                else candidate < baseline
            )
            percentage = None if baseline == 0 else str(((candidate - baseline) / abs(baseline) * Decimal(100)).normalize())
            return {
                "status": "PASS" if exit_code == 0 else "FAIL",
                "metric": value["metric"],
                "unit": value["unit"],
                "baseline": str(value["baseline"]),
                "candidate": str(value["candidate"]),
                "direction": value["direction"],
                "improved": improvement,
                "percentage": percentage,
            }
        raise WorldlineError("INVALID_CHECK_FORMAT", f"unsupported check format: {check.format}")
