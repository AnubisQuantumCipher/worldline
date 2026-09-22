"""Does the check run the bytes WORLDLINE says it ran?

These drive the real check runner against a real sandbox. The attack they exist for is:

    expected verifier -> temporarily replace -> execute replacement -> restore -> finalize

Both ends look perfect while the thing that produced PASS was different. Until this milestone a
check executed its verifier from inside the world's writable overlay, so the file it ran was a
file the candidate owned.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "runtime"))

from worldline.admission import AdmissionAuthority, Floors, Gate, Ledger, ResourcePolicy  # noqa: E402
from worldline.checks import CheckRunner  # noqa: E402
from worldline.errors import WorldlineError  # noqa: E402
from worldline.executed import UNIDENTIFIED, ExecutionVerifierSet  # noqa: E402
from worldline.linux.namespaces import BubblewrapSandbox, OverlayRoot  # noqa: E402
from worldline.linux.systemd import SystemdAdapter  # noqa: E402
from worldline.paths import WorldlinePaths  # noqa: E402
from worldline.project import CheckSpec  # noqa: E402

ROOT_KEY = "a1" * 32
LOGICAL = "/logical/root"


class ExecutedIdentity(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-executed-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        env = dict(os.environ,
                   XDG_STATE_HOME=str(self.base / "state"), XDG_DATA_HOME=str(self.base / "data"),
                   XDG_RUNTIME_DIR=str(self.base / "run"), XDG_CONFIG_HOME=str(self.base / "cfg"))
        for name in ("state", "data", "run", "cfg"):
            (self.base / name).mkdir(parents=True, exist_ok=True)
        self.paths = WorldlinePaths.from_environment(env)
        self.paths.ensure()
        # lower is PRIME as the world was forked from it; upper is what the candidate wrote.
        self.lower = self.base / "lower"
        (self.lower / "exam").mkdir(parents=True)
        self.upper = self.base / "upper"
        self.upper.mkdir()
        self.work = self.base / "work"
        self.work.mkdir()
        self.overlay = OverlayRoot(root_key=ROOT_KEY, lower=self.lower, upper=self.upper,
                                   work=self.work, target=Path(LOGICAL))
        gate = Gate(AdmissionAuthority(Ledger(self.paths.runtime), Floors()), ResourcePolicy.from_mapping({}))
        self.runner = CheckRunner(self.paths, BubblewrapSandbox(self.paths), SystemdAdapter(), gate)

    def write_examiner(self, body: str, name: str = "run.py") -> None:
        (self.lower / "exam" / name).write_text(body, encoding="utf-8")

    def run_check(self, *, argv: tuple[str, ...], members: tuple[str, ...] = ("exam/run.py",)) -> dict:
        check = CheckSpec("exam", "tests", argv, None, True, "exit", None, (), ())
        entries = [{"checkId": "exam", "rootKey": ROOT_KEY, "path": m, "source": "argv"} for m in members]
        return self.runner.run(
            world_instance=str(uuid.uuid4()), overlays=[self.overlay],
            primary_target=Path(LOGICAL), checks=[check],
            verifiers=entries, logical_roots={ROOT_KEY: LOGICAL})[0]

    # ---- the examiner is PRIME's, not the candidate's -----------------------------------------
    def test_a_candidate_that_replaced_the_examiner_is_still_judged_by_primes(self) -> None:
        """The whole modify-run-restore attack rests on the check running the candidate's copy."""
        self.write_examiner("import sys; print('GENUINE'); sys.exit(1)\n")
        # The candidate's overlay says the examiner passes. It is not consulted.
        (self.upper / "exam").mkdir(parents=True)
        (self.upper / "exam/run.py").write_text("import sys; print('FORGED'); sys.exit(0)\n", encoding="utf-8")
        result = self.run_check(argv=("/usr/bin/python3", f"{LOGICAL}/exam/run.py"))
        self.assertEqual(result["status"], "FAIL",
                         "the candidate's forged examiner decided the outcome")
        self.assertIn("GENUINE", _stdout(result))
        self.assertNotIn("FORGED", _stdout(result))

    def test_the_identity_recorded_is_primes_examiner(self) -> None:
        self.write_examiner("print('ok')\n")
        (self.upper / "exam").mkdir(parents=True)
        (self.upper / "exam/run.py").write_text("print('other')\n", encoding="utf-8")
        executed = self.run_check(argv=("/usr/bin/python3", f"{LOGICAL}/exam/run.py"))["executedVerifierSet"]
        member = executed["members"][0]
        import hashlib
        expected = hashlib.sha256((self.lower / "exam/run.py").read_bytes()).hexdigest()
        self.assertEqual(member["sha256"], expected)
        self.assertTrue(executed["stable"])

    # ---- the check runs from somewhere the candidate cannot reach -------------------------------
    def test_the_examiner_is_executed_from_a_mount_the_workload_cannot_write(self) -> None:
        self.write_examiner(
            "import os, sys\n"
            "p = sys.argv[0]\n"
            "print('RUNNING_FROM', p)\n"
            "try:\n"
            "    open(p, 'ab').write(b'x'); print('WRITABLE')\n"
            "except OSError as e:\n"
            "    print('WRITE_REFUSED', e.errno)\n"
            "try:\n"
            "    os.rename(p, p + '.moved'); print('RENAMABLE')\n"
            "except OSError as e:\n"
            "    print('RENAME_REFUSED', e.errno)\n")
        out = _stdout(self.run_check(argv=("/usr/bin/python3", f"{LOGICAL}/exam/run.py")))
        self.assertIn("/run/worldline-verifiers/", out, f"the examiner did not run from the staged mount:\n{out}")
        self.assertIn("WRITE_REFUSED", out, out)
        self.assertIn("RENAME_REFUSED", out, out)
        self.assertNotIn("WRITABLE", out)
        self.assertNotIn("RENAMABLE", out)

    def test_swapping_the_original_while_the_check_runs_changes_nothing(self) -> None:
        """The classic: identity established, attacker swaps, execution proceeds."""
        self.write_examiner(
            "import pathlib, sys\n"
            f"original = pathlib.Path('{LOGICAL}/exam/run.py')\n"
            "original.write_text('print(\\'FORGED\\')\\n')\n"
            "print('SWAPPED_ORIGINAL')\n"
            "print('I_AM', pathlib.Path(sys.argv[0]).read_text().splitlines()[0])\n")
        result = self.run_check(argv=("/usr/bin/python3", f"{LOGICAL}/exam/run.py"))
        out = _stdout(result)
        self.assertIn("SWAPPED_ORIGINAL", out, out)
        self.assertNotIn("FORGED", out.split("I_AM")[-1], "the running examiner saw the swapped bytes")
        executed = result["executedVerifierSet"]
        self.assertTrue(executed["stable"], f"the identity moved during execution: {executed['changedDuringExecution']}")
        self.assertEqual(executed["identity"], executed["identityAfterExecution"])

    # ---- the set, not the file -------------------------------------------------------------------
    def test_a_declared_helper_is_part_of_the_identity(self) -> None:
        self.write_examiner("import helper; print(helper.VALUE)\n")
        (self.lower / "exam/helper.py").write_text("VALUE = 'first'\n", encoding="utf-8")
        first = self.run_check(argv=("/usr/bin/python3", f"{LOGICAL}/exam/run.py"),
                               members=("exam/run.py", "exam/helper.py"))
        (self.lower / "exam/helper.py").write_text("VALUE = 'second'\n", encoding="utf-8")
        second = self.run_check(argv=("/usr/bin/python3", f"{LOGICAL}/exam/run.py"),
                                members=("exam/run.py", "exam/helper.py"))
        self.assertNotEqual(first["executedVerifierSet"]["identity"],
                            second["executedVerifierSet"]["identity"],
                            "changing a declared helper left the set identity unchanged")
        self.assertIn("first", _stdout(first))
        self.assertIn("second", _stdout(second))

    def test_a_shadow_module_beside_the_examiner_cannot_be_imported(self) -> None:
        """A module the candidate added is not in the declared set, so it is not staged, so the
        examiner running from the staged mount cannot import it."""
        self.write_examiner("import sys\ntry:\n    import shadow\n    print('SHADOW_IMPORTED')\nexcept ImportError:\n    print('SHADOW_ABSENT')\n")
        (self.upper / "exam").mkdir(parents=True)
        (self.upper / "exam/shadow.py").write_text("print('pwned')\n", encoding="utf-8")
        out = _stdout(self.run_check(argv=("/usr/bin/python3", f"{LOGICAL}/exam/run.py")))
        self.assertIn("SHADOW_ABSENT", out, out)

    # ---- a set that cannot be identified is a refusal ---------------------------------------------
    def test_a_symlinked_verifier_is_refused_rather_than_followed(self) -> None:
        """A symlink is a name, and a name is what this refuses to trust."""
        (self.lower / "exam/real.py").write_text("print('x')\n", encoding="utf-8")
        (self.lower / "exam/run.py").unlink(missing_ok=True)
        (self.lower / "exam/run.py").symlink_to("real.py")
        with self.assertRaises(WorldlineError) as caught:
            self.run_check(argv=("/usr/bin/python3", f"{LOGICAL}/exam/run.py"))
        self.assertEqual(caught.exception.args[0], UNIDENTIFIED)

    def test_a_missing_verifier_is_refused(self) -> None:
        with self.assertRaises(WorldlineError) as caught:
            self.run_check(argv=("/usr/bin/python3", f"{LOGICAL}/exam/absent.py"),
                           members=("exam/absent.py",))
        self.assertEqual(caught.exception.args[0], UNIDENTIFIED)

    # ---- identity is read through descriptors, not names -------------------------------------------
    def test_identity_is_recomputed_through_the_same_descriptors(self) -> None:
        staging = self.base / "staged"
        (self.lower / "exam/run.py").write_text("print('x')\n", encoding="utf-8")
        entries = [{"rootKey": ROOT_KEY, "path": "exam/run.py", "source": "argv"}]
        with ExecutionVerifierSet.stage(check_id="exam", entries=entries,
                                        sources={ROOT_KEY: self.lower}, staging=staging) as staged:
            before = staged.identity()
            # Replace the NAME inside the staging area. The descriptor still holds the old inode.
            target = staging / ROOT_KEY / "exam/run.py"
            os.chmod(staging, 0o700)
            os.chmod(target.parent, 0o700)
            target.unlink()
            target.write_text("print('replaced')\n", encoding="utf-8")
            after, changes = staged.reread()
            self.assertEqual(after, before, "the identity followed the name instead of the bytes")
            self.assertEqual(changes, [])


def _stdout(result: dict) -> str:
    import base64
    return base64.b64decode(result.get("stdoutB64", "").encode("ascii")).decode("utf-8", "replace")


if __name__ == "__main__":
    unittest.main()
