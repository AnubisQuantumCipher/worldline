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
    COptionalCounter,
    COptionalHash,
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
    "wl_optional_hash": (4, COptionalHash),
    "wl_optional_counter": (5, COptionalCounter),
}


def header_fields(struct: str) -> list[str]:
    text = HEADER.read_text(encoding="utf-8")
    body = re.search(r"struct %s \{(.*?)\};" % re.escape(struct), text, re.S)
    if body is None:
        raise AssertionError(f"struct {struct} is not in the header")
    without_comments = re.sub(r"/\*.*?\*/", "", body.group(1), flags=re.S)
    return re.findall(r"(?:uint8_t|struct\s+\w+)\s+(\w+)\s*(?:\[[^]]*\])?\s*;", without_comments)


class AbiLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.core = Core(REPO / "lib/libworldline_core.so")

    def test_header_and_ctypes_name_the_same_fields_in_the_same_order(self) -> None:
        for struct, (_selector, record) in STRUCTS.items():
            with self.subTest(struct=struct):
                self.assertEqual(header_fields(struct), [name for name, _ in record._fields_])

    def test_the_library_lays_out_every_record_as_ctypes_does(self) -> None:
        unknown = ctypes.c_size_t(-1).value
        for struct, (selector, record) in STRUCTS.items():
            with self.subTest(struct=struct):
                self.assertEqual(self.core._lib.wl_layout_size(selector), ctypes.sizeof(record))
                for name, _type in record._fields_:
                    self.assertEqual(self.core._lib.wl_layout_offset(selector, name.encode(), len(name)),
                                     getattr(record, name).offset, name)
                self.assertEqual(self.core._lib.wl_layout_offset(selector, b"nonexistent", 11), unknown)
        self.assertEqual(self.core._lib.wl_layout_offset(9, b"candidate_state", 15), unknown)
        self.assertEqual(self.core._lib.wl_layout_offset(0, None, 0), unknown)

    def test_a_library_whose_fields_are_ordered_differently_is_refused_at_load(self) -> None:
        # Two equal-sized fields swapped keep every record size; only the offsets differ.
        from unittest import mock
        from worldline.errors import CoreUnavailable
        import worldline.core as core_module
        fields = list(CCollapseRequest._fields_)
        mode = next(i for i, (name, _t) in enumerate(fields) if name == "evaluation_mode")
        fields[mode], fields[mode + 1] = fields[mode + 1], fields[mode]  # evaluation_mode <-> conflicts
        swapped = type("SwappedCollapseRequest", (ctypes.Structure,), {"_fields_": fields})
        self.assertEqual(ctypes.sizeof(swapped), ctypes.sizeof(CCollapseRequest))
        layouts = tuple((selector, swapped if record is CCollapseRequest else record)
                        for selector, record in core_module._LAYOUTS)
        with mock.patch.object(core_module, "_LAYOUTS", layouts):
            with self.assertRaises(CoreUnavailable):
                Core(REPO / "lib/libworldline_core.so")

    def test_every_observation_code_table_matches_the_header(self) -> None:
        from worldline import core as core_module
        text = HEADER.read_text(encoding="utf-8")
        tables = {
            "wl_evaluation_origin": ("WL_ORIGIN_", {k.upper(): v for k, v in core_module.EVALUATION_ORIGINS.items()}),
            "wl_evaluation_status": ("WL_STATUS_", core_module.EVALUATION_STATUSES),
            "wl_evaluation_channel": ("WL_CHANNEL_", core_module.EVALUATION_CHANNELS),
            "wl_evaluation_stage": ("WL_STAGE_", core_module.EVALUATION_STAGES),
            "wl_evaluation_supervision": ("WL_SUPERVISION_", core_module.EVALUATION_SUPERVISION),
        }
        for enum, (prefix, table) in tables.items():
            with self.subTest(enum=enum):
                body = re.search(r"enum %s \{(.*?)\};" % enum, text, re.S).group(1)
                names = [item.strip().removeprefix(prefix) for item in body.split(",") if item.strip()]
                self.assertEqual(names, [name for name, _code in sorted(table.items(), key=lambda kv: kv[1])])
                self.assertEqual(sorted(table.values()), list(range(len(names))))

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
        self.assertEqual(int(seen["collapse-layout"]), 5)

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
