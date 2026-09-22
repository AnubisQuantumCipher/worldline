from __future__ import annotations

import base64
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
import subprocess
import time
from typing import Any, Sequence
import uuid
import xml.etree.ElementTree as ET

from .canonical import atomic_write_json
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
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for check in checks:
            results.append(
                self._run_one(
                    world_instance=world_instance,
                    overlays=overlays,
                    primary_target=primary_target,
                    check=check,
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
    ) -> dict[str, Any]:
        run_id = str(uuid.uuid4())
        runtime = self.paths.overlays / world_instance / "checks" / check.id
        if runtime.exists():
            import shutil

            shutil.rmtree(runtime)
        secure_directory(runtime)
        cwd = primary_target if check.cwd is None else primary_target / check.cwd
        result_path = None if check.result is None else str(cwd / check.result)
        specification = {
            "schemaVersion": 1,
            "argv": list(check.argv),
            "result": result_path,
        }
        atomic_write_json(runtime / "spec.json", specification)
        spec = SandboxSpec(
            instance_id=world_instance,
            argv=(
                "/usr/bin/python3",
                "-c",
                _CHECK_RUNNER,
                "/run/worldline-runtime/spec.json",
                "/run/worldline-runtime/result.json",
            ),
            cwd=cwd,
            environment=safe_environment(),
            roots=tuple(overlays),
            runtime=runtime,
        )
        with self.gate.guard(f"check:{check.id}") as _decision:
            process = self.systemd.launch(
                run_id,
                self.sandbox.build_argv(spec),
                description=f"WORLDLINE check {check.id}",
                resource_properties=self.gate.unit_properties(),
            )
            _stdout, launch_stderr = process.launcher.communicate(timeout=600)
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
