"""PK-0 C-06: the native diagnostic control and exact WORLDLINE_NATIVE_DIAGNOSTIC byte streams.

Packet PK-0 of the C-API boundary design (v4 DESIGN.md section 9.6, carried into the
endorsed v6; control C-06 in v3 DESIGN.md section 15), revision v3. The expectations are the
diagnostic_cases of tests/capi_characterization.json.

Each case runs in a fresh child interpreter, so the library starts in its elaborated state
(diagnostics inactive, no latched failure). The child's fd 2 is captured whole, as bytes, and
is compared with the expected byte stream exactly (PK0-RC4): nothing is decoded with
replacement, and line order, empty lines and every terminator are part of the comparison.

* A recorded expectation is either a list of lines or {"hex": "..."} (exact bytes, for a
  stream that is not a sequence of complete ASCII lines, such as D06 after a baseline run).
* A line list is rendered to bytes: each line is ASCII, followed by one LF. A mark is
  "WORLDLINE_NATIVE_DIAGNOSTIC " & Site (core/evaluation_completion_c.adb:42-50, written by
  Ada.Text_IO.Put_Line on Standard_Error and flushed); a value is Site & "=" &
  Integer_64'Image (Value), which has a leading space for a non-negative value (:52-59; Ada RM
  3.5(32)). The LF terminator is the GNAT Text_IO line terminator on this platform; it is a
  prediction checked by the comparison, not a fact read from S5.
* Exception lines carry Exception_Information, which is implementation-defined; no case here
  raises one (class H is asserted only by the optional C-12, which PK-0 does not author).

Process boundary (PK0-RC5): the parent starts each child with subprocess.run and no deadline;
a hung child blocks the parent. In the child, Python's sys.stderr object is replaced by
/dev/null before any other import, so fd 2 carries native output only; the report goes to
stdout. The child loads the library, applies capi_guard_pages' fatal-fault policy, builds and
mutates every scenario a call step names before the first step runs (so producer calls made
while building cannot write diagnostic lines), and then runs the steps in order. A call step
runs the export in this child process through capi_guard_pages.execute, not in a further fork.

An expectation written RECORD_ON_L0 never passes. `--record` prints, for every case holding a
placeholder, the observed returns and the raw fd 2 bytes (hex, and split after each LF with
latin-1 code points, which is lossless) on standard output. It writes no file and refuses to
start unless bytecode writing is disabled for the launch (-B or PYTHONDONTWRITEBYTECODE); its
child interpreters are started with PYTHONDONTWRITEBYTECODE=1.
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
TERMINATOR = b"\n"

CHILD = (
    "import os, sys\n"
    "sys.stderr = open(os.devnull, 'w', encoding='utf-8')\n"
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


def expected_bytes(lines, oracle):
    """The exact fd 2 byte stream a recorded expectation stands for."""
    if isinstance(lines, dict) and set(lines) == {"hex"}:
        return bytes.fromhex(lines["hex"])
    return b"".join(render(line, oracle).encode("ascii") + TERMINATOR for line in lines)


def segments(raw):
    """Split after each LF, keeping every terminator; a final unterminated piece stays last."""
    parts = raw.split(TERMINATOR)
    pieces = [part + TERMINATOR for part in parts[:-1]]
    if parts[-1]:
        pieces.append(parts[-1])
    return pieces


def lossless_view(raw):
    return {"fd2_hex": raw.hex(), "fd2_segments_latin1": [piece.decode("latin-1")
                                                          for piece in segments(raw)]}


def child_main(case_id):
    """Runs in the fresh child interpreter (sys.stderr already points to /dev/null)."""
    sys.stderr = open(os.devnull, "w", encoding="utf-8")
    try:
        case = CASES[case_id]
        sys.path.insert(0, str(HERE))
        import capi_guard_pages as G
        import test_capi_characterization as T
        from worldline.core import Core

        core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))
        library = core._lib
        G.establish_fatal_faults()
        control = library["wl_native_diagnostic_control_v1"]
        control.restype, control.argtypes = C.c_uint32, [C.c_uint32]
        built = {}
        for index, step in enumerate(case["steps"]):
            if step[0] == "call":
                target = CHARACTERIZATION[step[1]]
                scenario = T.build_scenario(core, target)
                T.mutate(scenario, target.get("mut", ()), library)
                built[index] = (target, scenario)
        returns, oracles, saved = [], [], None
        for index, step in enumerate(case["steps"]):
            kind = step[0]
            if kind == "control":
                value = CONSTANTS[step[1]] if isinstance(step[1], str) else step[1]
                G.verify_fatal_faults()
                returns.append(int(control(value)))
                G.verify_fatal_faults()
            elif kind == "call":
                target, scenario = built[index]
                oracle = T.ORACLES.get(target.get("oracle"))
                prelude = None
                if oracle is not None:
                    prelude = (lambda region, base, address, oracle=oracle, scenario=scenario:
                               oracle(scenario, library))
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
    """(report, raw fd 2 bytes). The report is strict UTF-8 JSON or a stdout_hex record."""
    try:
        report = json.loads(proc.stdout.decode("utf-8")) if proc.stdout else {}
    except ValueError:
        report = {"unreadable_report": True, "stdout_hex": proc.stdout.hex()}
    return report, proc.stderr


class CapiDiagnostics(unittest.TestCase):
    """C-06. One generated test per diagnostic case."""

    @classmethod
    def setUpClass(cls):
        # The library is selected the S5 way; the children load the same path.
        cls.library_path = Path(os.environ['WORLDLINE_CORE_LIB'])

    def check_case(self, case):
        proc = run_child(case["id"])
        report, raw = observed(proc)
        label = case["id"]
        self.assertEqual(proc.returncode, 0,
                         f"{label}: child exit {proc.returncode}; report {report}; "
                         f"fd 2 {lossless_view(raw[:2048])}")
        self.assertNotIn("unreadable_report", report, f"{label}: {report}")
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
            pending.append(f"fd 2 {lossless_view(raw)}")
        else:
            want = expected_bytes(case["lines"], oracle)
            self.assertEqual(raw, want, f"{label}: exact fd 2 byte stream; observed "
                                        f"{lossless_view(raw)}")
        if pending:
            self.fail(f"{label}: {PLACEHOLDER} expectation needs a baseline run on L0; observed {pending}")

    def test_record_shape(self):
        """Every call step names a characterization case; the record is well formed."""
        for case in CASES.values():
            self.assertEqual(len(case["steps"]), len(case["returns"]), case["id"])
            lines = case["lines"]
            self.assertTrue(lines == PLACEHOLDER or isinstance(lines, list)
                            or (isinstance(lines, dict) and set(lines) == {"hex"}), case["id"])
            for step in case["steps"]:
                if step[0] == "call":
                    self.assertIn(step[1], CHARACTERIZATION, case["id"])
                    self.assertFalse(CHARACTERIZATION[step[1]].get("guard"),
                                     f"{case['id']}: diagnostic calls use unguarded cases")

    def test_rendering_is_exact_bytes(self):
        """The renderer keeps order, empty streams and one LF per line (no library needed)."""
        self.assertEqual(expected_bytes([], None), b"")
        self.assertEqual(expected_bytes(["a", {"site": "b", "value": 0}, {"site": "c", "value": -1}],
                                        None),
                         b"WORLDLINE_NATIVE_DIAGNOSTIC a\n"
                         b"WORLDLINE_NATIVE_DIAGNOSTIC b= 0\n"
                         b"WORLDLINE_NATIVE_DIAGNOSTIC c=-1\n")
        self.assertEqual(expected_bytes({"hex": "0a00ff"}, None), b"\n\x00\xff")
        self.assertEqual(segments(b"a\n\nb"), [b"a\n", b"\n", b"b"])
        self.assertNotEqual(lossless_view(b"\xff\n"), lossless_view(b"\xfe\n"))


def _case_test(case):
    def test(self):
        self.check_case(case)
    test.__doc__ = f"{case['id']}: {case.get('title', '')}"
    return test


for _case in RECORD["diagnostic_cases"]:
    setattr(CapiDiagnostics, "test_" + _case["id"], _case_test(_case))


def record_main():
    if not sys.flags.dont_write_bytecode:
        sys.stderr.write("--record refused: launch the interpreter with -B or "
                         "PYTHONDONTWRITEBYTECODE=1 so that no bytecode file is written\n")
        sys.exit(2)
    observations = {}
    for case in RECORD["diagnostic_cases"]:
        if PLACEHOLDER not in json.dumps(case):
            continue
        proc = run_child(case["id"])
        report, raw = observed(proc)
        entry = {"exit": proc.returncode, "report": report}
        entry.update(lossless_view(raw))
        observations[case["id"]] = entry
    json.dump({"record": "capi-diagnostics observed values (L0 baseline)",
               "observed": observations}, sys.stdout, indent=1, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    if "--record" in sys.argv[1:]:
        record_main()
    else:
        unittest.main()
