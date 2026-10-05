"""PK-0 C-07 and C-13: layout sentinels and the baseline layout identity.

Packet PK-0 of the C-API boundary design (v4 DESIGN.md section 9.6.6, carried into the
endorsed v6; C-07 and C-13 in v3 DESIGN.md section 15, constraints C4 and C5 in section
10.3), revision v3. The record is tests/capi_layout_baseline.json.

* Version exports: the values are constants read from S5 and are asserted now.
* C-07: for every probed kind or field that a staying layout export does not define, the
  value is the sentinel its source returns (I64'Last, SIZE_MAX or -1). Read from S5; asserted
  now.
* C-13: every layout export value over its probe domain, every runtime ctypes size,
  alignment and field offset, and every C header sizeof, _Alignof and offsetof, compared with
  the values recorded on L0. Nothing is recorded yet: every entry is RECORD_ON_L0 and fails
  until a baseline run on L0 records it through a reviewed change.

Three entry points, with different effects (PK0-RC2):

* unittest (normal run). The header test compiles and runs a probe. Its source, binary and
  any compiler scratch are confined to a fresh directory inside the admitted test scratch
  named by WORLDLINE_PK0_SCRATCH, which must be an existing absolute directory; a missing or
  unusable binding is a failure, never a fallback to the ambient temporary directory. That
  the run writes nothing else holds only under launch obligation 1 (bytecode writing disabled
  for the launch): a unittest run imports runtime modules before any test can gate it, so this
  source does not enforce it (RC-v2-3).
* `--measure-headers`: the separately labelled header measurement. Before any import outside
  the standard library, it refuses to start unless bytecode writing is disabled for the launch
  (-B or PYTHONDONTWRITEBYTECODE) (RC-v2-3). It then writes only inside
  WORLDLINE_PK0_SCRATCH, as the test does, and prints the measurement (with the compiler's
  argv, status and complete output, kept as bytes in hex) as JSON on standard output. It is
  not a record path.
* `--record`: output-only. It prints the observed layout export values and ctypes layouts as
  JSON on standard output, compiles nothing and writes no file. It reads a header measurement
  only when given one with `--headers PATH SHA256`, and only after checking that the file's
  SHA-256 equals the bound value. Without that argument the header values are reported as
  not measured. Before any import outside the standard library, it refuses to
  start unless bytecode writing is disabled for the launch (-B or PYTHONDONTWRITEBYTECODE).

The header probe follows tests/test_abi_layout.py: a C compiler is required, and a missing
compiler is a failure, never a skip. The probe is a measurement, so it is compiled without
-Werror; any warning stays in the compiler's output, which is retained (re-emitted on this
process's stderr in a test run, and carried in the --measure-headers JSON). The original strict
test, tests/test_abi_layout.py, keeps its -Werror and is not edited.

This module does not compare the three spellings with each other: PK-0 records each one
as L0 has it, and any measured disagreement is an original defect to be reviewed, never a
reason to edit a record. No automatic agreement of the ctypes layouts is assumed: Core
validates only its own _LAYOUTS when it is constructed (runtime/worldline/core.py), and the
component kernels (pending, completion, finalization, recovery) check their layouts only in
their own constructors, which this module does not call. Every native call in this module
(version, layout and sentinel queries) runs in this process, not in a fork.
"""
from __future__ import annotations

import collections
import ctypes as C
import hashlib
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASELINE = json.loads((HERE / "capi_layout_baseline.json").read_text(encoding="utf-8"))
PLACEHOLDER = BASELINE["placeholder_token"]
SENTINELS = {name: entry["value"] for name, entry in BASELINE["sentinels"].items()}
TYPES = {"uint8": C.c_uint8, "uint32": C.c_uint32, "int64": C.c_int64, "long": C.c_long,
         "size_t": C.c_size_t}
U32_LAST = C.c_uint32(-1).value
SCRATCH_VARIABLE = "WORLDLINE_PK0_SCRATCH"
MEASUREMENT_SCHEMA = "worldline/capi-header-measurement/1"


def key(point):
    return ",".join(str(item) for item in point)


def domain(entry):
    args = entry["args"]
    if not args:
        return [()]
    defined = entry["defined"]
    if len(args) == 1:
        if args[0] == "uint8":
            return [(value,) for value in range(256)]
        top = max(bounds[1] for bounds in defined.values())
        return [(value,) for value in range(top + 2)] + [(U32_LAST,)]
    if args[0] == "uint8":
        return [(kind, field) for kind in range(256) for field in range(256)]
    top_kind = max(int(kind) for kind in defined)
    top_field = max(bounds[1] for bounds in defined.values())
    kinds = list(range(top_kind + 2)) + [U32_LAST]
    fields = list(range(top_field + 2)) + [U32_LAST]
    return [(kind, field) for kind in kinds for field in fields]


def is_defined(entry, point):
    defined = entry["defined"]
    if defined is None:
        return True
    if len(point) == 1:
        low, high = defined[""]
        return low <= point[0] <= high
    bounds = defined.get(str(point[0]))
    return bounds is not None and bounds[0] <= point[1] <= bounds[1]


def observe_layout(library, entry):
    function = library[entry["export"]]
    function.restype = TYPES[entry["restype"]]
    function.argtypes = [TYPES[arg] for arg in entry["args"]]
    return {key(point): int(function(*point)) for point in domain(entry)}


def compress(observed):
    default = collections.Counter(observed.values()).most_common(1)[0][0]
    return {"default": default,
            "points": {name: value for name, value in observed.items() if value != default}}


def expand(recorded, names):
    unknown = set(recorded["points"]) - set(names)
    if unknown:
        raise AssertionError(f"recorded points outside the probe domain: {sorted(unknown)[:8]}")
    return {name: recorded["points"].get(name, recorded["default"]) for name in names}


def ctypes_class(dotted):
    module, _, name = dotted.rpartition(".")
    return getattr(importlib.import_module(module), name)


def ctypes_layout(klass):
    return {"size": C.sizeof(klass), "alignment": C.alignment(klass),
            "offsets": {name: getattr(klass, name).offset for name, _ in klass._fields_}}


def admitted_scratch():
    """The admitted test scratch: an existing absolute directory, or a failure."""
    value = os.environ.get(SCRATCH_VARIABLE)
    if not value:
        raise AssertionError(f"{SCRATCH_VARIABLE} is not set: the header probe has no admitted scratch")
    path = Path(value)
    if not path.is_absolute() or not path.is_dir():
        raise AssertionError(f"{SCRATCH_VARIABLE}={value!r} is not an existing absolute directory")
    return path


def header_layouts(entries):
    """Compile and run a probe over the listed header types inside the admitted scratch.

    Returns ({type: layout}, compile record with argv, status and complete output as hex)."""
    compiler = shutil.which("cc") or shutil.which("gcc")
    if compiler is None:
        raise AssertionError("no C compiler: the header layouts cannot be measured")
    scratch = admitted_scratch()
    lines = ["#include <stddef.h>", "#include <stdio.h>"]
    lines += [f'#include "{ROOT / header}"' for header in sorted({e["header"] for e in entries})]
    lines.append("int main(void) {")
    for entry in entries:
        ctype = entry["type"]
        lines.append(f'printf("%s|size|%zu\\n", "{ctype}", sizeof({ctype}));')
        lines.append(f'printf("%s|alignment|%zu\\n", "{ctype}", (size_t) _Alignof({ctype}));')
        for name, _ in ctypes_class(entry["fields_from"])._fields_:
            lines.append(f'printf("%s|{name}|%zu\\n", "{ctype}", offsetof({ctype}, {name}));')
    lines.append("return 0; }")
    env = dict(os.environ)
    env["TMPDIR"] = str(scratch)
    with tempfile.TemporaryDirectory(prefix="worldline-capi-pk0-", dir=scratch) as temporary:
        source = Path(temporary) / "probe.c"
        binary = Path(temporary) / "probe"
        source.write_text("\n".join(lines) + "\n", encoding="utf-8")
        argv = [compiler, "-std=c11", "-Wall", "-o", str(binary), str(source)]
        compiled = subprocess.run(argv, capture_output=True, env=env, check=False)
        record = {"argv": argv, "returncode": compiled.returncode,
                  "stdout_hex": compiled.stdout.hex(), "stderr_hex": compiled.stderr.hex()}
        if compiled.returncode != 0:
            raise AssertionError(f"header probe did not compile: {record}")
        probe = subprocess.run([str(binary)], capture_output=True, env=env, check=False)
        if probe.returncode != 0:
            raise AssertionError(f"header probe exited {probe.returncode}: {probe.stderr!r}")
        output = probe.stdout.decode("ascii")
    answer = {}
    for line in output.splitlines():
        ctype, field, value = line.rsplit("|", 2)
        entry = answer.setdefault(ctype, {"size": None, "alignment": None, "offsets": {}})
        if field in ("size", "alignment"):
            entry[field] = int(value)
        else:
            entry["offsets"][field] = int(value)
    return answer, record


class CapiLayoutIdentity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = None
        from worldline.core import Core
        cls.core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))
        cls.lib = cls.core._lib

    def test_version_exports(self):
        """The staying version exports return the constants written in S5."""
        for entry in BASELINE["version_exports"]:
            with self.subTest(export=entry["export"]):
                function = self.lib[entry["export"]]
                function.restype, function.argtypes = C.c_uint32, []
                self.assertEqual(int(function()), entry["value"], entry["s5"])

    def test_c07_layout_sentinels(self):
        """Every undefined probed kind or field returns the source sentinel."""
        for entry in BASELINE["layout_exports"]:
            if entry["sentinel"] is None:
                continue
            with self.subTest(export=entry["export"]):
                sentinel = SENTINELS[entry["sentinel"]]
                observed = observe_layout(self.lib, entry)
                wrong = [(name, value) for name, value in observed.items()
                         if not is_defined(entry, tuple(int(x) for x in name.split(",")))
                         and value != sentinel]
                self.assertEqual(wrong[:16], [], f"{entry['export']} ({entry['s5']})")

    def test_c13_layout_values(self):
        """Every layout export value over its probe domain equals the L0 record."""
        for entry in BASELINE["layout_exports"]:
            with self.subTest(export=entry["export"]):
                observed = observe_layout(self.lib, entry)
                if entry["values"] == PLACEHOLDER:
                    self.fail(f"{entry['export']}: {PLACEHOLDER}; observed {compress(observed)}")
                self.assertEqual(observed, expand(entry["values"], list(observed)))

    def test_c13_ctypes_layouts(self):
        """Every runtime ctypes record keeps its L0 size, alignment and offsets."""
        for entry in BASELINE["ctypes"]:
            with self.subTest(record=entry["class"]):
                observed = ctypes_layout(ctypes_class(entry["class"]))
                if entry["values"] == PLACEHOLDER:
                    self.fail(f"{entry['class']}: {PLACEHOLDER}; observed {observed}")
                self.assertEqual(observed, entry["values"])

    def test_c13_header_layouts(self):
        """Every C header record keeps its L0 sizeof, _Alignof and offsetof."""
        measured, compiled = header_layouts(BASELINE["headers"])
        # Retain the compiler's complete output (warnings included) in the launch's log.
        sys.stderr.write(json.dumps({"header_probe_compile": compiled}) + "\n")
        for entry in BASELINE["headers"]:
            with self.subTest(header=entry["header"], type=entry["type"]):
                observed = measured.get(entry["type"])
                self.assertIsNotNone(observed, entry["type"])
                if entry["values"] == PLACEHOLDER:
                    self.fail(f"{entry['type']}: {PLACEHOLDER}; observed {observed}")
                self.assertEqual(observed, entry["values"])

    def test_record_shape(self):
        """The baseline names 15 version exports and 25 layout exports (the 40 staying)."""
        names = [e["export"] for e in BASELINE["version_exports"]] + \
                [e["export"] for e in BASELINE["layout_exports"]]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual((len(BASELINE["version_exports"]), len(BASELINE["layout_exports"])),
                         (15, 25))
        self.assertEqual(SENTINELS["I64'Last"], (1 << (8 * C.sizeof(C.c_int64) - 1)) - 1)
        self.assertEqual(SENTINELS["SIZE_MAX"], C.c_size_t(-1).value)


def require_output_only_launch(mode):
    """RC-v2-3: refuse a --record or --measure-headers launch that could write bytecode."""
    if not sys.flags.dont_write_bytecode:
        sys.stderr.write(f"{mode} refused: launch the interpreter with -B or "
                         "PYTHONDONTWRITEBYTECODE=1 so that no bytecode file is written\n")
        sys.exit(2)


def bound_measurement(arguments):
    """Read a header measurement named by --headers PATH SHA256, only if its digest matches."""
    index = arguments.index("--headers")
    path, digest = Path(arguments[index + 1]), arguments[index + 2].lower()
    data = path.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual != digest:
        raise SystemExit(f"--headers refused: {path} has sha256 {actual}, not the bound {digest}")
    measurement = json.loads(data.decode("utf-8"))
    if measurement.get("schema") != MEASUREMENT_SCHEMA:
        raise SystemExit(f"--headers refused: {path} is not a {MEASUREMENT_SCHEMA} measurement")
    return measurement, actual


def measure_main():
    """The separately labelled header measurement; writes only in the admitted scratch."""
    require_output_only_launch("--measure-headers")
    measured, compiled = header_layouts(BASELINE["headers"])
    json.dump({"schema": MEASUREMENT_SCHEMA,
               "label": "capi-header-layouts measurement (L0 baseline), compiled without -Werror",
               "compile": compiled, "layouts": measured}, sys.stdout, indent=1, sort_keys=True)
    sys.stdout.write("\n")


def record_main(arguments):
    require_output_only_launch("--record")
    from worldline.core import Core
    core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))
    report = {"record": "capi-layout-baseline observed values (L0 baseline)",
              "layout_exports": {}, "ctypes": {}, "headers": {}}
    for entry in BASELINE["layout_exports"]:
        report["layout_exports"][entry["export"]] = compress(observe_layout(core._lib, entry))
    for entry in BASELINE["ctypes"]:
        report["ctypes"][entry["class"]] = ctypes_layout(ctypes_class(entry["class"]))
    if "--headers" in arguments:
        measurement, digest = bound_measurement(arguments)
        report["header_measurement_sha256"] = digest
        report["header_compile"] = measurement["compile"]
        for entry in BASELINE["headers"]:
            report["headers"][entry["type"]] = measurement["layouts"].get(entry["type"])
    else:
        report["headers"] = ("NOT_MEASURED: --record compiles nothing; run --measure-headers in "
                             "the admitted frame and pass its bound output with "
                             "--headers PATH SHA256")
    json.dump(report, sys.stdout, indent=1, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    if "--record" in sys.argv[1:]:
        record_main(sys.argv[1:])
    elif "--measure-headers" in sys.argv[1:]:
        measure_main()
    else:
        unittest.main()
