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

    # ---- descriptor stability is NOT execution identity ---------------------------------------------
    def test_a_rebound_pathname_is_detected_even_though_the_descriptor_is_unchanged(self) -> None:
        """The control this replaces was insufficient, and the reason is worth keeping.

        A held descriptor keeps referring to its original open file description after the
        pathname is re-pointed, so "the descriptor's hash did not move" is perfectly compatible
        with the interpreter having opened a different file through the same name. Proving the
        bytes we measured did not change is not proving they are the bytes that ran.

        The substitution here is performed by the test harness as the OWNER of the staging
        directory, from the host. That is a privileged action and is not a sandbox escape; it is
        done to exercise the detector, not to claim the workload could do it.
        """
        staging = self.base / "staged"
        (self.lower / "exam/run.py").write_text("print('GENUINE')\n", encoding="utf-8")
        entries = [{"rootKey": ROOT_KEY, "path": "exam/run.py", "source": "argv"}]
        with ExecutionVerifierSet.stage(check_id="exam", entries=entries,
                                        sources={ROOT_KEY: self.lower}, staging=staging) as staged:
            before = staged.identity()
            member = staged.items[0]
            target = Path(member.host_path)
            os.chmod(staging, 0o700)
            os.chmod(target.parent, 0o700)
            target.unlink()
            target.write_text("print('SUBSTITUTED')\n", encoding="utf-8")

            # What an interpreter launched against that NAME would actually run:
            import subprocess
            ran = subprocess.run([sys.executable, str(target)], capture_output=True, text=True).stdout
            self.assertIn("SUBSTITUTED", ran, "the harness substitution did not take effect")

            after, changes = staged.reread()
            # The descriptor is still perfectly stable. That is the trap.
            self.assertEqual(after, before, "the descriptor content should be unchanged")
            kinds = {c.get("kind") for c in changes}
            self.assertIn("pathname-rebound", kinds,
                          "a re-pointed pathname was not detected, so descriptor stability was"
                          f" being mistaken for execution identity: {changes}")

    def test_the_runner_marks_an_evaluation_unstable_when_the_staged_name_was_rebound(self) -> None:
        """Acceptance condition: the intended examiner runs, or the evaluation is refused."""
        self.write_examiner("print('GENUINE')\n")
        staging_parent = self.paths.overlays
        check = CheckSpec("exam", "tests", ("/usr/bin/python3", f"{LOGICAL}/exam/run.py"),
                          None, True, "exit", None, (), ())
        entries = [{"checkId": "exam", "rootKey": ROOT_KEY, "path": "exam/run.py", "source": "argv"}]
        instance = str(uuid.uuid4())

        original_stage = ExecutionVerifierSet.stage
        substituted: dict = {}

        def stage_then_substitute(**kwargs):
            staged = original_stage(**kwargs)
            member = staged.items[0]
            target = Path(member.host_path)
            os.chmod(staged.staging, 0o700)
            os.chmod(target.parent, 0o700)
            target.unlink()
            target.write_text("print('SUBSTITUTED')\n", encoding="utf-8")
            os.chmod(target, 0o444)
            substituted["path"] = str(target)
            return staged

        ExecutionVerifierSet.stage = staticmethod(stage_then_substitute)
        try:
            result = self.runner.run(world_instance=instance, overlays=[self.overlay],
                                     primary_target=Path(LOGICAL), checks=[check],
                                     verifiers=entries, logical_roots={ROOT_KEY: LOGICAL})[0]
        finally:
            ExecutionVerifierSet.stage = original_stage
        self.assertTrue(substituted, "the substitution never ran")
        executed = result["executedVerifierSet"]
        self.assertFalse(executed["stable"],
                         "a substituted examiner ran and the evaluation was still reported stable")
        self.assertIn("pathname-rebound", {c.get("kind") for c in executed["changedDuringExecution"]})

    # ---- validate the instrument before trusting a green result -------------------------------------
    def test_argv_can_only_ever_name_something_that_was_measured(self) -> None:
        """The deliberately broken instrument is "hash one file, launch another". Nothing in a
        content or inode comparison catches that, because both files are individually unchanged.
        What prevents it is structural: the paths the check is given are derived from the same
        entries that were measured, and this asserts exactly that."""
        self.write_examiner("print('x')\n")
        (self.lower / "exam/helper.py").write_text("VALUE = 1\n", encoding="utf-8")
        result = self.run_check(argv=("/usr/bin/python3", f"{LOGICAL}/exam/run.py"),
                                members=("exam/run.py", "exam/helper.py"))
        executed = result["executedVerifierSet"]
        measured = {m["executedAs"] for m in executed["members"]}
        self.assertTrue(executed["argvRewrites"], "nothing was rewritten, so nothing was proved")
        for rewrite in executed["argvRewrites"]:
            self.assertIn(rewrite["to"], measured,
                          "the check was pointed at a path that was never measured")
            member = next(m for m in executed["members"] if m["executedAs"] == rewrite["to"])
            self.assertEqual(rewrite["sha256"], member["sha256"],
                             "the digest recorded for the rewrite is not the digest of the"
                             " member it names")


def _stdout(result: dict) -> str:
    import base64
    return base64.b64decode(result.get("stdoutB64", "").encode("ascii")).decode("utf-8", "replace")


if __name__ == "__main__":
    unittest.main()


class AcceptanceBinding(unittest.TestCase):
    """The roster lesson, applied to promotion.

    An evaluation WORLDLINE cannot attach to the examiner it authorised must not become an
    ordinary pass, and a check outside coverage must not be advertised as bound.
    """

    def test_the_three_outcomes_are_distinct(self) -> None:
        from worldline.finalize import execution_binding
        self.assertEqual(execution_binding(
            {"executedVerifierSet": {"stable": True, "changedDuringExecution": []}}), "BOUND")
        self.assertEqual(execution_binding(
            {"executedVerifierSet": {"stable": False,
                                     "changedDuringExecution": [{"kind": "pathname-rebound"}]}}),
            "UNESTABLISHED")
        self.assertEqual(execution_binding({}), "NOT_COVERED")
        self.assertEqual(execution_binding({"executedVerifierSet": None}), "NOT_COVERED")

    def test_an_unparseable_record_is_unestablished_not_covered(self) -> None:
        """A record we cannot read is not a check that needed no binding."""
        from worldline.finalize import execution_binding
        for shape in ("yes", 7, ["stable"]):
            with self.subTest(shape=shape):
                self.assertEqual(execution_binding({"executedVerifierSet": shape}), "UNESTABLISHED")

    def test_a_bundle_that_moved_is_unestablished_even_when_stable_says_true(self) -> None:
        """Two sources of truth must agree; the pessimistic one wins."""
        from worldline.finalize import execution_binding
        self.assertEqual(execution_binding({"executedVerifierSet": {
            "stable": True, "changedDuringExecution": [{"kind": "content"}]}}), "UNESTABLISHED")
