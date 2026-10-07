"""Ordinary parser fixtures: dummy source is parsed, never imported or executed."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "engine_codes.py"
SPEC = importlib.util.spec_from_file_location("worldline_code_inventory", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
INVENTORY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INVENTORY)


class EngineCodeInventory(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-inventory-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / "runtime" / "worldline"
        self.package.mkdir(parents=True)
        (self.root / "core").mkdir()
        (self.root / "core" / "worldline_core.h").write_text(
            "#define WL_COLLAPSE_AUTHORIZED 0u\n"
            "#define WL_COLLAPSE_FIXTURE_DENIED 1u\n"
            "#define WL_ERR_FIXTURE_IO 1\n", encoding="utf-8")

    def source(self, module: str, content: str) -> None:
        path = self.package / module
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_literals_alternatives_named_imports_and_record_codes(self) -> None:
        self.source("codes.py", 'NAMED: str = "NAMED_REFUSAL"\n')
        self.source("ordinary.py", '''
from .codes import NAMED as IMPORTED
def report(flag):
    code = "CHOICE_A" if flag else "CHOICE_B"
    WorldlineError(code, "fixture")
    WorldlineError(IMPORTED, "fixture")
    WorldlineError(code="KEYWORD_REFUSAL", message="fixture")
    record = {"code": "RECORDED_WARNING"}
    record_error(error_code="CALL_WARNING")
''')
        self.assertEqual(set(INVENTORY.collect(self.root)), {
            "FIXTURE_DENIED", "CORE_FIXTURE_IO", "CHOICE_A", "CHOICE_B",
            "NAMED_REFUSAL", "KEYWORD_REFUSAL", "RECORDED_WARNING", "CALL_WARNING",
        })

    def test_known_boundary_sources_are_included(self) -> None:
        self.source("admission.py", '''
ADMITTED = "ADMITTED"
DECLINED = "FIXTURE_CAPACITY_UNKNOWN"
OUTCOMES = (ADMITTED, DECLINED)
def admit(decision):
    raise WorldlineError(decision.outcome, "fixture")
''')
        self.source("core.py", '''
_ERROR_NAMES = {1: "FIXTURE_INTERNAL"}
def report(name):
    raise WorldlineError(f"CORE_{name}", "fixture")
''')
        self.source("transaction.py", '''
def finish(self):
    decision = self._authorize()
    raise WorldlineError(decision, "fixture")
''')
        self.source("linux/private_evaluator.py", '''
class BackendFailure(Exception):
    pass
def _refuse(message, code="FIXTURE_BACKEND_DEFAULT"):
    raise BackendFailure(code, message)
def run(exc):
    _refuse("fixture", "FIXTURE_BACKEND_EXPLICIT")
    raise WorldlineError(getattr(exc, "code", "FIXTURE_BACKEND_FAILED"), "fixture")
''')
        self.assertEqual(set(INVENTORY.collect(self.root)), {
            "FIXTURE_DENIED", "CORE_FIXTURE_IO", "CORE_FIXTURE_INTERNAL",
            "FIXTURE_CAPACITY_UNKNOWN", "FIXTURE_BACKEND_DEFAULT",
            "FIXTURE_BACKEND_EXPLICIT", "FIXTURE_BACKEND_FAILED",
        })

    def test_named_error_return_and_fixed_subclass_are_included(self) -> None:
        self.source("errors.py", '''
class FixtureFailure(WorldlineError):
    def __init__(self):
        super().__init__("FIXTURE_FIXED", "fixture")
def storage_error(exc):
    code = "FIXTURE_STORAGE_FULL" if exc else "FIXTURE_STORAGE_ERROR"
    return WorldlineError(code, "fixture")
''')
        self.source("transaction.py", '''
from .errors import storage_error
def report(exc):
    named = storage_error(exc)
    raise WorldlineError(named.code, "fixture")
''')
        self.assertTrue({"FIXTURE_FIXED", "FIXTURE_STORAGE_FULL", "FIXTURE_STORAGE_ERROR"}
                        <= set(INVENTORY.collect(self.root)))

    def test_unresolved_code_is_refused(self) -> None:
        for source in (
            'def report(code):\n    raise WorldlineError(code, "fixture")\n',
            'def report():\n    code = choose("INCIDENTAL_LITERAL")\n    raise WorldlineError(code, "fixture")\n',
            'def report():\n    raise WorldlineError(**details)\n',
            'CODE = OTHER\nOTHER = CODE\ndef report():\n    raise WorldlineError(CODE, "fixture")\n',
        ):
            with self.subTest(source=source):
                self.source("ordinary.py", source)
                with self.assertRaises(INVENTORY.Unresolved):
                    INVENTORY.collect(self.root)

    def test_cli_refusal_preserves_existing_generated_file(self) -> None:
        self.source("ordinary.py", 'def report(code):\n    raise WorldlineError(code, "fixture")\n')
        generated = self.package / "engine_codes.py"
        generated.write_text("# existing generated file\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), "--write"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot resolve", result.stderr)
        self.assertEqual(generated.read_text(encoding="utf-8"), "# existing generated file\n")

    def test_cli_write_check_and_json_agree(self) -> None:
        import json
        self.source("ordinary.py", 'raise WorldlineError("FIXTURE_REFUSAL", "fixture")\n')
        for mode in ("--write", "--check"):
            result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), mode],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), "--json"],
                                capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        self.assertEqual(data["codes"], INVENTORY.collect(self.root))
        self.assertEqual(data["codeSetSha256"], INVENTORY.digest(data["codes"]))
        self.assertRegex(data["codeSetSha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
