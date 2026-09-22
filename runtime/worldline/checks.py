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

from .canonical import atomic_write_json
from .executed import UNIDENTIFIED, VERIFIER_MOUNT, ExecutionVerifierSet
from .errors import WorldlineError
from .linux.namespaces import BubblewrapSandbox, OverlayRoot, SandboxSpec
from .admission import Gate
from .linux.systemd import SystemdAdapter
from .project import CheckSpec
from .environment import safe_environment
from .paths import WorldlinePaths, secure_directory

_CHECK_RUNNER = """
import base64
import json
from pathlib import Path
import subprocess
import sys
import time
specification = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
started = time.monotonic_ns()
completed = subprocess.run(specification['argv'], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
result = None
if specification['result'] is not None:
    path = Path(specification['result'])
    if path.is_file():
        result = base64.b64encode(path.read_bytes()).decode('ascii')
Path(sys.argv[2]).write_text(json.dumps({
    'schemaVersion': 1,
    'exitCode': completed.returncode,
    'durationNs': time.monotonic_ns() - started,
    'stdoutB64': base64.b64encode(completed.stdout).decode('ascii'),
    'stderrB64': base64.b64encode(completed.stderr).decode('ascii'),
    'resultB64': result,
}, sort_keys=True, separators=(',', ':')) + '\\n', encoding='utf-8')
""".strip()


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
            argv=(
                "/usr/bin/python3",
                # Isolated startup, and this is a security boundary rather than tidiness. The
                # check's working directory must be inside a managed root, so it is
                # candidate-writable BY CONSTRUCTION — and `python3 -c` puts the working
                # directory first on sys.path. The harness's very first import, `import base64`,
                # was answered from a file the workload wrote; a correctly written shadow owns
                # the harness outright and fabricates the result.
                #
                # -I removes that insertion (it implies -P), ignores every PYTHON* variable and
                # drops the user site directory. -S additionally suppresses site initialisation,
                # which is what processes .pth files and sitecustomize — controlling PYTHONPATH
                # alone would not reach those. Measured on this host with CPython 3.14.7: with no
                # flags and with -S alone the candidate's base64.py is imported; with -I and with
                # -I -S the standard library's is.
                #
                # This isolates the HARNESS only. The verifier it launches is a separate process
                # and keeps ordinary semantics, because examining candidate code legitimately
                # needs candidate cwd and candidate imports. What the candidate must not get is
                # authority over the process that attests the examination happened.
                "-I",
                "-S",
                "-c",
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
            _stdout, launch_stderr = process.launcher.communicate(timeout=600)
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
        record_path = runtime / "result.json"
        if process.launcher.returncode != 0 or not record_path.is_file():
            return {
                "id": check.id,
                "kind": check.kind,
                "required": check.required,
                "format": check.format,
                "covers": list(check.covers),
                "status": "FAIL",
                "reason": launch_stderr.decode("utf-8", "replace").strip() or "check sandbox failed",
                "executedVerifierSet": executed,
            }
        raw = json.loads(record_path.read_text(encoding="utf-8"))
        stdout = base64.b64decode(raw["stdoutB64"].encode("ascii"), validate=True)
        stderr = base64.b64decode(raw["stderrB64"].encode("ascii"), validate=True)
        result_bytes = None if raw["resultB64"] is None else base64.b64decode(raw["resultB64"].encode("ascii"), validate=True)
        parsed = self._parse(check, raw["exitCode"], stdout, stderr, result_bytes)
        return {
            "id": check.id,
            "kind": check.kind,
            "required": check.required,
            "format": check.format,
            "covers": list(check.covers),
            "argv": list(check.argv),
            "exitCode": raw["exitCode"],
            "durationNs": raw["durationNs"],
            "stdoutB64": raw["stdoutB64"],
            "stderrB64": raw["stderrB64"],
            # The identity of the bytes this evaluation actually ran. Compared at finalization
            # against what the policy declares; a difference is VERIFIER_EXECUTION_IDENTITY_MISMATCH
            # and cannot satisfy the acceptance gate.
            "executedVerifierSet": executed,
            **parsed,
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
