from __future__ import annotations

import os

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

from .executed import UNIDENTIFIED, VERIFIER_MOUNT, ExecutionVerifierSet
from .resolution import resolve_token, root_prefixes
from .errors import WorldlineError
from .linux.namespaces import BubblewrapSandbox, OverlayRoot, SandboxSpec
from .admission import Gate
from .linux.systemd import SystemdAdapter
from .project import CheckSpec
from .environment import safe_environment
from .paths import WorldlinePaths, secure_directory

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
        verifier_sources: Mapping[str, Path],
        verifiers: Sequence[Mapping[str, Any]] = (),
        logical_roots: Mapping[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """`verifiers` is the resolved verifier set for this policy, as `resolve_verifiers`
        returns it; each check takes the members that name it. Passing it is what lets a check be
        identified by the bytes it runs rather than by the path it was given.

        `verifier_sources` (root_key -> directory) is the TRUSTED EVALUATOR SNAPSHOT the examiner
        bytes are staged from. It is passed explicitly, never inferred from the overlay `lower`:
        for a fork the lower happens to be PRIME, but for a revalidation it is the candidate's own
        payload, and staging the examiner from there would let the candidate supply the examiner
        that judges it. The tree the check examines (the overlays) and the bytes that examine it
        (these sources) are two different snapshots and must be named separately."""
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
                    verifier_sources=verifier_sources,
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
        verifier_sources: Mapping[str, Path],
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

        # The declared verifier set is copied out of the overlays and identified by descriptor
        # BEFORE anything runs, and the check is pointed at the staged copies. Until this, a
        # check executed its verifier from inside the world's writable overlay — the file it ran
        # was a file the candidate owned.
        staged: ExecutionVerifierSet | None = None
        argv = list(check.argv)
        rewrites: list[dict[str, str]] = []
        primary_key = next((root.root_key for root in overlays
                            if str(root.target) == str(primary_target)), None)

        # FAIL CLOSED, and BEFORE staging: an argv token that addresses a managed root but binds
        # to no clean member inside it -- an absolute remainder (`/root//gate.py`), a `..` that
        # climbs out (`/root/../root/x`), or the root directory itself -- is never executed. The
        # earlier code resolved these to nothing and silently ran the candidate's overlay copy
        # while recording PRIME's bundle as BOUND; a campaign walked straight through it. Whether
        # or not a bundle was staged, such a token means the bytes this check would run cannot be
        # attributed, so the check refuses instead of running them.
        escapes = [token for token in check.argv
                   if resolve_token(token, root_prefixes(dict(logical_roots or {})),
                                    primary_root_key=primary_key, cwd=check.cwd or "")[0] == "escape"]
        if escapes:
            raise WorldlineError(
                UNIDENTIFIED,
                f"check {check.id} has argv tokens that address a managed root but bind to no"
                " verifier inside it, so what they would execute cannot be attributed:"
                f" {escapes}. Name each verifier by a clean path inside its registered root.",
                {"argv": list(check.argv), "escapes": escapes})

        # The TRUSTED EVALUATOR SNAPSHOT, passed in explicitly. The examiner that judges a
        # candidate must not be one the candidate supplied, so tampering with a verifier inside a
        # world changes nothing about what runs (it is still reported at finalization as
        # VERIFIER_MODIFIED_BY_CANDIDATE; it simply no longer decides anything). This is NOT read
        # from the overlay lower, because for a revalidation the lower is the candidate's payload.
        sources = dict(verifier_sources)
        if verifier_entries:
            # A set that cannot be identified is a refusal. Running the check anyway would
            # produce exactly the result this milestone exists to make impossible: a PASS whose
            # provenance nobody can state.
            staged = ExecutionVerifierSet.stage(
                check_id=check.id, entries=verifier_entries, sources=sources,
                staging=runtime.parent / f"{check.id}.verifiers")
            plan = staged.rewrite_argv(
                argv, dict(logical_roots or {}),
                primary_root_key=primary_key, cwd=check.cwd or "")
            argv, rewrites = plan.argv, plan.rewrites
            # A bundle was staged and no argv token points at it: the entrypoint is named only
            # by a `verifiers:` glob or a `-m module` the interpreter resolves itself, so the
            # bytes that run cannot be shown to be the bytes that were identified. Not a passing
            # check and not a failing one -- a check whose provenance cannot be stated.
            if not rewrites:
                raise WorldlineError(
                    UNIDENTIFIED,
                    f"check {check.id} declares a verifier bundle but none of its argv tokens"
                    " names one, so the bytes it would execute cannot be shown to be the bytes"
                    " that were identified. Name the verifier by the absolute path of its"
                    " registered root.",
                    {"argv": list(check.argv),
                     "staged": [item.staged for item in staged.items]})

        # THE RECORD PRODUCER IS THE DAEMON, OUTSIDE THE SANDBOX.
        #
        # The examiner is exec'd directly under bwrap; there is no in-sandbox harness process
        # writing a framed record to a pipe. A campaign showed why that mattered: the examiner's
        # own descendants share its uid and PID namespace and can open /proc/<harness>/fd/1, so
        # they could take the harness's frame off its stdout and put back a forged one, or write
        # a frame while the harness was mid-write. The producer is now this process -- in a
        # different PID and mount namespace from everything in the sandbox -- so there is no
        # in-sandbox producer fd to reach, and the authoritative facts are measured out here:
        #
        #   verdict (exit status)   the SERVICE MANAGER's record of how the unit ended. The
        #                           candidate can change it only by changing how the examiner
        #                           actually exits, which is the examiner's decision, not its
        #                           children's.
        #   stdout / stderr         the examiner's own streams, read by the daemon. These are
        #                           CANDIDATE-DOMAIN output: the examiner runs candidate cwd and
        #                           may run candidate code, so they are recorded, never trusted.
        #   result file             read host-side from the overlay upper AFTER the run. For a
        #                           format whose verdict is the file contents this is
        #                           candidate-reachable -- a sibling under the same uid can write
        #                           it -- so the profile records that and does not claim the
        #                           report is isolated from the candidate.
        #
        # The examiner keeps ordinary startup (NOT -I -S): examining candidate code legitimately
        # needs candidate cwd and imports. Only the removed harness ever needed isolation.
        spec = SandboxSpec(
            instance_id=world_instance,
            argv=tuple(argv),
            cwd=cwd,
            environment=safe_environment(),
            roots=tuple(overlays),
            runtime=runtime,
            readonly_mounts=((staged.staging, VERIFIER_MOUNT),) if staged is not None else (),
        )
        started_ns = time.monotonic_ns()
        with self.gate.guard(f"check:{check.id}") as _decision:
            process = self.systemd.launch(
                run_id,
                self.sandbox.build_argv(spec),
                description=f"WORLDLINE check {check.id}",
                resource_properties=self.gate.unit_properties(),
            )
            examiner_stdout, examiner_stderr = process.launcher.communicate(timeout=600)
            # Supervisor-owned facts, from the service manager's own journal entries for this
            # unit. The candidate cannot write these: they are the manager's record of a process
            # it supervised, not anything reported from inside the sandbox.
            supervision = self.systemd.outcome(process, process.launcher.returncode)
        duration_ns = time.monotonic_ns() - started_ns
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

        # The verdict is the SERVICE MANAGER's observation of how the unit ended -- measured
        # outside the sandbox, not reported from within it.
        if supervision.get("kind") == "LAUNCH_FAILED":
            return refuse("SANDBOX_NEVER_STARTED",
                          (examiner_stderr.decode("utf-8", "replace").strip() or "the sandbox never started"))
        if supervision.get("kind") == "SUPERVISED" and supervision.get("stoppedByManager"):
            return refuse("STOPPED_BY_MANAGER",
                          "the check unit was stopped by the service manager before it completed")
        if observed["exitStatus"] is None:
            # No supervisor-owned exit observation: the daemon cannot state how the unit ended,
            # and the examiner's own streams are candidate-domain. Unknown is not permission.
            return refuse("UNCORROBORATED",
                          f"the supervisor could not observe how the check unit ended ({observed['source']})")

        exit_status = observed["exitStatus"]

        # The examiner's own streams: candidate-domain output. Recorded, parsed where a check
        # format reads them, never trusted as the authoritative record.
        stdout = examiner_stdout or b""
        stderr = examiner_stderr or b""

        # The result file, read host-side from the overlay upper after the run. Candidate-
        # reachable: a sibling under the same uid could have written it. For a format whose
        # verdict is the file contents (junit, gnatprove, benchmark) this is the report-trust
        # boundary, recorded honestly below.
        result_bytes = self._read_result_file(check, overlays, primary_target)

        gaps = (executed or {}).get("unsatisfiedImports") if executed else None
        parsed = self._parse(check, exit_status, stdout, stderr, result_bytes)

        verdict_from_file = check.format in ("junit", "gnatprove", "worldline-benchmark-v1")
        return {
            **identity,
            "argv": list(check.argv),
            "exitCode": exit_status,
            "durationNs": duration_ns,
            "stdoutB64": base64.b64encode(stdout).decode("ascii"),
            "stderrB64": base64.b64encode(stderr).decode("ascii"),
            # The identity of the bytes this evaluation actually ran. Compared at finalization
            # against what the policy declares; a difference is VERIFIER_EXECUTION_IDENTITY_MISMATCH
            # and cannot satisfy the acceptance gate.
            "executedVerifierSet": executed,
            "origin": "supervisor",
            # The producer is the daemon, outside the sandbox. `accepted` here means the unit
            # was supervised and its exit observed -- NOT that an in-sandbox frame was validated
            # (there is no frame any more).
            "resultChannel": {
                "accepted": True,
                "recordProducer": "daemon-outside-sandbox",
                "exitStatus": {
                    "observed": exit_status,
                    "source": observed["source"],
                    "journal": observed.get("journal"),
                    "launcher": observed.get("launcher"),
                },
            },
            # What the verdict actually rests on, stated so nothing over-claims. The exit status
            # is supervisor-owned and unforgeable by the examiner's children; a result-file
            # verdict additionally rests on bytes the candidate could reach, and does NOT get the
            # "isolated from the candidate" claim for those bytes.
            "evaluationProfile": {
                "recordProducer": "supervisor",
                "verdictAuthority": "candidate-reachable-report" if verdict_from_file else "supervisor-exit-status",
                "reportTrust": "candidate-reachable" if verdict_from_file else "not-applicable",
                "nonClaims": ([
                    "The verdict of a result-file format rests on file bytes written inside the"
                    " sandbox, which a candidate subprocess under the same uid could replace. The"
                    " exit status is supervisor-owned; the report contents are not. This check's"
                    " report is not isolated from the candidate.",
                ] if verdict_from_file else [
                    "The verdict is the exit status the service manager observed for the unit,"
                    " outside the sandbox. A candidate can change it only by changing how the"
                    " examiner actually exits -- which is not the same as claiming the examiner's"
                    " JUDGMENT is independent of candidate code it may run in-process.",
                ]),
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
                "stdoutB64": base64.b64encode(stdout).decode("ascii"),
                "stderrB64": base64.b64encode(stderr).decode("ascii"),
                "resultFilePresent": result_bytes is not None,
            },
            **parsed,
        }

    def _read_result_file(self, check: "CheckSpec", overlays: Sequence[OverlayRoot],
                          primary_target: Path) -> bytes | None:
        """Read the check's declared result file host-side, from the primary overlay's upper
        layer, after the run. This is where a file the examiner CREATES lands (and where an
        existing file it modifies is copied up). It is candidate-reachable: the caller records
        that. Returns None when no result file is declared or none was produced."""
        if check.result is None:
            return None
        primary = next((root for root in overlays if str(root.target) == str(primary_target)), None)
        if primary is None:
            return None
        relative = check.result if check.cwd is None else os.path.join(check.cwd, check.result)
        relative = os.path.normpath(relative)
        if relative.startswith("..") or os.path.isabs(relative):
            return None
        host_path = primary.upper / relative
        try:
            if host_path.is_symlink() or not host_path.is_file():
                return None
            return host_path.read_bytes()
        except OSError:
            return None

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
