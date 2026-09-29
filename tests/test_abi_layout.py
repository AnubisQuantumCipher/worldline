"""One ABI, three spellings: the C header, the ctypes records the runtime uses, and the library's
own Ada layout (wl_layout_size). A field added to one and not the others would make the kernel
read a decision input at the wrong offset, so all three are compared field by field."""
from __future__ import annotations

import ctypes
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from worldline.core import (
    ABI_VERSION,
    CCollapseRequest,
    CEvaluationClassification,
    CEvaluationObservations,
    CEvidencePresence,
    COLLAPSE_DECISIONS,
    Core,
    EVALUATION_EXECUTIONS,
)

REPO = Path(__file__).resolve().parents[1]
HEADER = REPO / "core" / "worldline_core.h"
STRUCTS = {
    "wl_collapse_request": (0, CCollapseRequest),
    "wl_evaluation_observations": (1, CEvaluationObservations),
    "wl_evaluation_classification": (2, CEvaluationClassification),
    "wl_evidence_presence": (3, CEvidencePresence),
}


def header_fields(struct: str) -> list[str]:
    text = HEADER.read_text(encoding="utf-8")
    body = re.search(r"struct %s \{(.*?)\};" % re.escape(struct), text, re.S)
    if body is None:
        raise AssertionError(f"struct {struct} is not in the header")
    without_comments = re.sub(r"/\*.*?\*/", "", body.group(1), flags=re.S)
    return re.findall(r"uint8_t\s+(\w+)\s*(?:\[[^]]*\])?\s*;", without_comments)


class AbiLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.core = Core(REPO / "lib/libworldline_core.so")

    def test_header_and_ctypes_name_the_same_fields_in_the_same_order(self) -> None:
        for struct, (_selector, record) in STRUCTS.items():
            with self.subTest(struct=struct):
                self.assertEqual(header_fields(struct), [name for name, _ in record._fields_])

    def test_the_library_lays_out_every_record_as_ctypes_does(self) -> None:
        for struct, (selector, record) in STRUCTS.items():
            with self.subTest(struct=struct):
                self.assertEqual(self.core._lib.wl_layout_size(selector), ctypes.sizeof(record))

    def test_a_c_compiler_reading_the_header_agrees_on_every_offset(self) -> None:
        compiler = shutil.which("cc") or shutil.which("gcc")
        if compiler is None:
            self.fail("no C compiler: the header cannot be checked, and an unchecked header is the defect this test exists for")
        lines = ["#include <stddef.h>", "#include <stdio.h>", f'#include "{HEADER}"', "int main(void) {"]
        for struct, (_selector, record) in STRUCTS.items():
            lines.append(f'printf("{struct} size %zu\\n", sizeof(struct {struct}));')
            for name, _type in record._fields_:
                lines.append(f'printf("{struct} {name} %zu\\n", offsetof(struct {struct}, {name}));')
        lines.append(f'printf("abi %u\\n", (unsigned) WL_ABI_VERSION);')
        lines.append(f'printf("collapse-layout %u\\n", (unsigned) WL_COLLAPSE_REQUEST_VERSION);')
        lines.append("return 0; }")
        with tempfile.TemporaryDirectory(prefix="worldline-abi-") as temporary:
            source = Path(temporary) / "probe.c"
            binary = Path(temporary) / "probe"
            source.write_text("\n".join(lines), encoding="utf-8")
            subprocess.run([compiler, "-std=c11", "-Wall", "-Werror", "-o", str(binary), str(source)], check=True)
            output = subprocess.run([str(binary)], check=True, capture_output=True, text=True).stdout
        seen = dict(line.rsplit(" ", 1) for line in output.splitlines())
        for struct, (_selector, record) in STRUCTS.items():
            with self.subTest(struct=struct):
                self.assertEqual(int(seen[f"{struct} size"]), ctypes.sizeof(record))
                for name, _type in record._fields_:
                    self.assertEqual(int(seen[f"{struct} {name}"]), getattr(record, name).offset, name)
        self.assertEqual(int(seen["abi"]), ABI_VERSION)
        self.assertEqual(int(seen["collapse-layout"]), 4)

    def test_header_codes_match_the_runtime_tables(self) -> None:
        text = HEADER.read_text(encoding="utf-8")
        for code, name in COLLAPSE_DECISIONS.items():
            with self.subTest(decision=name):
                match = re.search(r"#define WL_COLLAPSE_%s (\d+)u" % name, text)
                self.assertIsNotNone(match, name)
                self.assertEqual(int(match.group(1)), code)
        enum = re.search(r"enum wl_execution_state \{(.*?)\};", text, re.S).group(1)
        names = [item.strip().removeprefix("WL_EVAL_") for item in enum.split(",") if item.strip()]
        self.assertEqual(names, list(EVALUATION_EXECUTIONS))

    def test_a_library_of_another_generation_is_refused_at_load(self) -> None:
        from unittest import mock
        from worldline.errors import CoreUnavailable
        import worldline.core as core_module
        with mock.patch.object(core_module, "ABI_VERSION", ABI_VERSION + 1):
            with self.assertRaises(CoreUnavailable):
                Core(REPO / "lib/libworldline_core.so")


if __name__ == "__main__":
    unittest.main()
