"""PK-0 C-07 and C-13: layout sentinels and the baseline layout identity.

Packet PK-0 of the C-API boundary design (v4 DESIGN.md section 9.6.6, carried into the
endorsed v6; C-07 and C-13 in v3 DESIGN.md section 15, constraints C4 and C5 in section
10.3). The record is tests/capi_layout_baseline.json.

* Version exports: the values are constants read from S5 and are asserted now.
* C-07: for every probed kind or field that a staying layout export does not define, the
  value is the sentinel its source returns (I64'Last, SIZE_MAX or -1). Read from S5; asserted
  now.
* C-13: every layout export value over its probe domain, every runtime ctypes size,
  alignment and field offset, and every C header sizeof, _Alignof and offsetof, compared with
  the values recorded on L0. Nothing is recorded yet: every entry is RECORD_ON_L0 and fails
  until a baseline run on L0 records it through a reviewed change. `--record` prints the
  observed values as JSON on standard output and writes no file.

The header probe follows tests/test_abi_layout.py: a C compiler is required, and a missing
compiler is a failure, never a skip. The probe is a measurement, so it is compiled without
-Werror; any warning stays in the compiler's output.

This module does not compare the three spellings with each other: PK-0 records each one
as L0 has it. The runtime bindings compare ctypes with the library at load time.
"""
from __future__ import annotations

import collections
import ctypes as C
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


def header_layouts(entries):
    """Compile and run a probe over the listed header types; return {type: layout}."""
    compiler = shutil.which("cc") or shutil.which("gcc")
    if compiler is None:
        raise AssertionError("no C compiler: the header layouts cannot be measured")
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
    with tempfile.TemporaryDirectory(prefix="worldline-capi-pk0-") as temporary:
        source = Path(temporary) / "probe.c"
        binary = Path(temporary) / "probe"
        source.write_text("\n".join(lines) + "\n", encoding="utf-8")
        subprocess.run([compiler, "-std=c11", "-Wall", "-o", str(binary), str(source)], check=True)
        output = subprocess.run([str(binary)], check=True, capture_output=True, text=True).stdout
    answer = {}
    for line in output.splitlines():
        ctype, field, value = line.rsplit("|", 2)
        entry = answer.setdefault(ctype, {"size": None, "alignment": None, "offsets": {}})
        if field in ("size", "alignment"):
            entry[field] = int(value)
        else:
            entry["offsets"][field] = int(value)
    return answer


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
        measured = header_layouts(BASELINE["headers"])
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


def record_main():
    from worldline.core import Core
    core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))
    report = {"record": "capi-layout-baseline observed values (L0 baseline)",
              "layout_exports": {}, "ctypes": {}, "headers": {}}
    for entry in BASELINE["layout_exports"]:
        report["layout_exports"][entry["export"]] = compress(observe_layout(core._lib, entry))
    for entry in BASELINE["ctypes"]:
        report["ctypes"][entry["class"]] = ctypes_layout(ctypes_class(entry["class"]))
    measured = header_layouts(BASELINE["headers"])
    for entry in BASELINE["headers"]:
        report["headers"][entry["type"]] = measured.get(entry["type"])
    json.dump(report, sys.stdout, indent=1, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    if "--record" in sys.argv[1:]:
        record_main()
    else:
        unittest.main()
