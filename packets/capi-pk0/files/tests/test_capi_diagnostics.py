"""PK-0 C-06: the native diagnostic control and exact WORLDLINE_NATIVE_DIAGNOSTIC sequences.

Packet PK-0 of the C-API boundary design (v4 DESIGN.md section 9.6, carried into the
endorsed v6; control C-06 in v3 DESIGN.md section 15). The expectations are the
diagnostic_cases of tests/capi_characterization.json. Each case runs in a fresh child
interpreter, so the library starts in its elaborated state (diagnostics inactive, no latched
failure), and the child's fd 2 is captured whole. Lines are compared exactly, in order:

* a mark is "WORLDLINE_NATIVE_DIAGNOSTIC " & Site (core/evaluation_completion_c.adb:42-50);
* a value is Site & "=" & Integer_64'Image (Value), which has a leading space for a
  non-negative value (:52-59; Ada RM 3.5(32));
* exception lines carry Exception_Information, which is implementation-defined; no case
  here raises one (class H is asserted only by the optional C-12, which PK-0 does not author).

A step that calls an export reuses a characterization case by id (builder and mutations
from test_capi_characterization.py). An expectation written RECORD_ON_L0 never passes.
`--record` prints observed returns and lines for placeholder cases and writes no file.
"""
from __future__ import annotations

import ctypes as C
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECORD = json.loads((HERE / "capi_characterization.json").read_text(encoding="utf-8"))
PLACEHOLDER = RECORD["placeholder_token"]
CONSTANTS = {name: entry["value"] for name, entry in RECORD["constants"].items()}
CASES = {case["id"]: case for case in RECORD["diagnostic_cases"]}
CHARACTERIZATION = {case["id"]: case for case in RECORD["cases"]}
PREFIX = "WORLDLINE_NATIVE_DIAGNOSTIC "

CHILD = (
    "import sys\n"
    "sys.path.insert(0, sys.argv[1])\n"
    "import test_capi_diagnostics as D\n"
    "D.child_main(sys.argv[2])\n"
)


def image(value):
    """Integer_64'Image: a leading space for a non-negative value."""
    return (" " + str(value)) if value >= 0 else str(value)


def render(line, oracle):
    if isinstance(line, str):
        return PREFIX + line
    value = oracle if line["value"] == "oracle" else line["value"]
    return PREFIX + line["site"] + "=" + image(value)


def child_main(case_id):
    """Runs in the fresh child interpreter. Python-level stderr goes to /dev/null so that
    fd 2 carries native output only; the report goes to stdout."""
    sys.stderr = open(os.devnull, "w", encoding="utf-8")
    try:
        case = CASES[case_id]
        sys.path.insert(0, str(HERE))
        import capi_guard_pages as G
        import test_capi_characterization as T
        from worldline.core import Core

        core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))
        library = core._lib
        control = library["wl_native_diagnostic_control_v1"]
        control.restype, control.argtypes = C.c_uint32, [C.c_uint32]
        returns, oracles, saved = [], [], None
        for step in case["steps"]:
            kind = step[0]
            if kind == "control":
                value = CONSTANTS[step[1]] if isinstance(step[1], str) else step[1]
                returns.append(int(control(value)))
            elif kind == "call":
                target = CHARACTERIZATION[step[1]]
                builder, kwargs = target["build"]
                scenario = T.BUILDERS[builder](core, **kwargs)
                T.mutate(scenario, target.get("mut", ()), library)
                oracle = T.ORACLES.get(target.get("oracle"))
                prelude = None
                if oracle is not None:
                    prelude = lambda region, base, address: oracle(scenario, library)  # noqa: E731
                report = G.execute(library, scenario, target.get("guard") or {}, prelude)
                returns.append(report["code"])
                oracles.append(report["oracle"])
            elif kind == "fd2" and step[1] == "full":
                saved = os.dup(2)
                full = os.open("/dev/full", os.O_WRONLY)
                os.dup2(full, 2)
                os.close(full)
                returns.append(None)
            elif kind == "fd2" and step[1] == "restore":
                os.dup2(saved, 2)
                os.close(saved)
                returns.append(None)
            else:
                raise ValueError(f"unknown step {step!r}")
        sys.stdout.write(json.dumps({"returns": returns, "oracles": oracles}))
        sys.stdout.flush()
    except BaseException as exc:  # reported on stdout; the parent fails the case
        sys.stdout.write(json.dumps({"child_error": f"{type(exc).__name__}: {exc}"}))
        sys.stdout.flush()
        os._exit(70)


def run_child(case_id):
    env = dict(os.environ)
    runtime = str(HERE.parent / "runtime")
    env["PYTHONPATH"] = os.pathsep.join(p for p in (runtime, env.get("PYTHONPATH", "")) if p)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run([sys.executable, "-c", CHILD, str(HERE), case_id], env=env,
                          capture_output=True, check=False)


def observed(proc):
    report = json.loads(proc.stdout.decode("utf-8")) if proc.stdout else {}
    lines = proc.stderr.decode("utf-8", "replace").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return report, lines


class CapiDiagnostics(unittest.TestCase):
    """C-06. One generated test per diagnostic case."""

    @classmethod
    def setUpClass(cls):
        # The library is selected the S5 way; the children load the same path.
        cls.library_path = Path(os.environ['WORLDLINE_CORE_LIB'])

    def check_case(self, case):
        proc = run_child(case["id"])
        report, lines = observed(proc)
        label = case["id"]
        self.assertEqual(proc.returncode, 0,
                         f"{label}: child exit {proc.returncode}; report {report}; fd 2 {lines[:8]}")
        self.assertNotIn("child_error", report, f"{label}: {report.get('child_error')}")
        returns = report["returns"]
        oracle = next((value for value in report["oracles"] if value is not None), None)
        expected = case["returns"]
        self.assertEqual(len(returns), len(expected), f"{label}: step count")
        pending = []
        for index, (got, want) in enumerate(zip(returns, expected)):
            if want == PLACEHOLDER:
                pending.append(f"step {index + 1} returned {got}")
            elif isinstance(want, dict) and "same_as" in want:
                self.assertEqual(got, returns[want["same_as"]], f"{label}: step {index + 1} latch")
            elif want == "oracle":
                self.assertIsNotNone(oracle, f"{label}: no oracle value")
                self.assertNotEqual(oracle, 255, f"{label}: the oracle request must be well formed")
                self.assertEqual(got, oracle, f"{label}: step {index + 1}")
            else:
                self.assertEqual(got, want, f"{label}: step {index + 1} return value")
        if case["lines"] == PLACEHOLDER:
            pending.append(f"fd 2 lines {lines}")
        else:
            self.assertEqual(lines, [render(line, oracle) for line in case["lines"]],
                             f"{label}: exact fd 2 line sequence")
        if pending:
            self.fail(f"{label}: {PLACEHOLDER} expectation needs a baseline run on L0; observed {pending}")

    def test_record_shape(self):
        """Every call step names a characterization case; the record is well formed."""
        for case in CASES.values():
            self.assertEqual(len(case["steps"]), len(case["returns"]), case["id"])
            for step in case["steps"]:
                if step[0] == "call":
                    self.assertIn(step[1], CHARACTERIZATION, case["id"])
                    self.assertFalse(CHARACTERIZATION[step[1]].get("guard"),
                                     f"{case['id']}: diagnostic calls use unguarded cases")


def _case_test(case):
    def test(self):
        self.check_case(case)
    test.__doc__ = f"{case['id']}: {case.get('title', '')}"
    return test


for _case in RECORD["diagnostic_cases"]:
    setattr(CapiDiagnostics, "test_" + _case["id"], _case_test(_case))


def record_main():
    observations = {}
    for case in RECORD["diagnostic_cases"]:
        if PLACEHOLDER not in json.dumps(case):
            continue
        proc = run_child(case["id"])
        report, lines = observed(proc)
        observations[case["id"]] = {"exit": proc.returncode, "report": report, "lines": lines}
    json.dump({"record": "capi-diagnostics observed values (L0 baseline)",
               "observed": observations}, sys.stdout, indent=1, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    if "--record" in sys.argv[1:]:
        record_main()
    else:
        unittest.main()
