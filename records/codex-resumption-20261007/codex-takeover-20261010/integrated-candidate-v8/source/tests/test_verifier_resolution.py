"""One resolution rule for verifier selection, staging, argv rewriting and the fail-closed guard.

Campaign findings F1 and F7. Two resolvers disagreed on how to read a policy argv token:
`resolve_verifiers` (which bytes are authoritative) took an absolute token's remainder verbatim,
while `rewrite_argv` (which token points at the staged copy) normalised it. A policy token
`/root/./gate.py` was recorded as the member `./gate.py` and looked up as `gate.py`; the lookup
missed, the token was never rewritten, and the check ran the candidate's overlay copy while the
evidence recorded PRIME's bundle as BOUND. `checks.py` guarded with `if not rewrites` -- at least
one token rewrote, per check -- so a single unrelated operand satisfied it.

These lock the shared rule in place. The `./gate.py + operand` case is kept permanently: it is the
one that specifically defeats a positive-rewrite-count guard.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "runtime"))

from worldline.resolution import resolve_token, root_prefixes  # noqa: E402


class SharedResolution(unittest.TestCase):
    def setUp(self) -> None:
        self.px = root_prefixes({"RK": "/logical/root"})

    def r(self, token: str):
        return resolve_token(token, self.px, primary_root_key="RK", cwd="")

    def test_a_plain_absolute_path_is_a_member(self) -> None:
        self.assertEqual(self.r("/logical/root/gate.py"), ("member", "RK", "gate.py"))

    def test_a_dot_segment_normalises_to_the_same_member(self) -> None:
        self.assertEqual(self.r("/logical/root/./gate.py"), ("member", "RK", "gate.py"))

    def test_a_doubled_separator_normalises_to_the_same_member(self) -> None:
        self.assertEqual(self.r("/logical/root//gate.py"), ("member", "RK", "gate.py"))

    def test_a_parent_climb_that_leaves_the_root_escapes(self) -> None:
        self.assertEqual(self.r("/logical/root/../root/gate.py"), ("escape", None, None))

    def test_a_parent_climb_that_stays_inside_is_a_member(self) -> None:
        # cwd sub/, token ../gate.py -> gate.py, still inside the root.
        self.assertEqual(resolve_token("../gate.py", self.px, primary_root_key="RK", cwd="sub"),
                         ("member", "RK", "gate.py"))

    def test_the_root_directory_itself_escapes(self) -> None:
        self.assertEqual(self.r("/logical/root"), ("escape", None, None))
        self.assertEqual(self.r("/logical/root/"), ("escape", None, None))

    def test_the_interpreter_and_flags_are_outside(self) -> None:
        self.assertEqual(self.r("/usr/bin/python3"), ("outside", None, None))
        self.assertEqual(self.r("-c"), ("outside", None, None))

    def test_a_cwd_relative_token_is_a_member(self) -> None:
        self.assertEqual(self.r("gate.py"), ("member", "RK", "gate.py"))

    def test_membership_and_rewriting_agree_on_every_spelling(self) -> None:
        # The correctness argument for the whole repair: the two consumers cannot disagree,
        # because there is one function.
        for token in ("/logical/root/gate.py", "/logical/root/./gate.py",
                      "/logical/root//gate.py", "gate.py"):
            self.assertEqual(self.r(token), ("member", "RK", "gate.py"), token)


class ArgvPlanRewrites(unittest.TestCase):
    """rewrite_argv points verifier tokens at the staged copies and reports escapes."""

    def setUp(self) -> None:
        from worldline.executed import ExecutionVerifierSet
        self.temporary = tempfile.TemporaryDirectory(prefix="argvplan-")
        self.addCleanup(self.temporary.cleanup)
        base = Path(self.temporary.name)
        source = base / "src"
        (source).mkdir()
        (source / "gate.py").write_text("print('gate')\n", encoding="utf-8")
        (source / "data.py").write_text("# data\n", encoding="utf-8")
        entries = [{"checkId": "c", "rootKey": "RK", "path": p, "source": "argv"}
                   for p in ("gate.py", "data.py")]
        self.staged = ExecutionVerifierSet.stage(check_id="c", entries=entries,
                                                 sources={"RK": source}, staging=base / "stg")
        self.addCleanup(self.staged.close)
        self.roots = {"RK": "/logical/root"}

    def plan(self, argv):
        return self.staged.rewrite_argv(argv, self.roots, primary_root_key="RK")

    def test_every_spelling_of_the_verifier_is_rewritten(self) -> None:
        for token in ("/logical/root/gate.py", "/logical/root/./gate.py", "/logical/root//gate.py"):
            plan = self.plan(["/usr/bin/python3", token])
            self.assertEqual(len(plan.rewrites), 1, token)
            self.assertTrue(plan.argv[1].startswith("/run/worldline-verifiers/"), token)
            self.assertEqual(plan.escapes, [], token)

    def test_the_forged_dot_slash_plus_operand_attack_is_defeated(self) -> None:
        # The permanent regression: `./gate.py` rewrites (it is not left pointing at the overlay),
        # so the positive count from the second operand is no longer what carries the check.
        plan = self.plan(["/usr/bin/python3", "/logical/root/./gate.py", "/logical/root/data.py"])
        froms = {rw["from"] for rw in plan.rewrites}
        self.assertEqual(froms, {"/logical/root/./gate.py", "/logical/root/data.py"})
        self.assertTrue(plan.argv[1].startswith("/run/worldline-verifiers/"))

    def test_an_escaping_token_is_reported_not_rewritten(self) -> None:
        plan = self.plan(["/usr/bin/python3", "/logical/root/../root/gate.py"])
        self.assertEqual(plan.escapes, ["/logical/root/../root/gate.py"])
        self.assertEqual(plan.rewrites, [])
        # The escaping token is passed through unchanged; the check runner refuses on it.
        self.assertEqual(plan.argv[1], "/logical/root/../root/gate.py")


if __name__ == "__main__":
    unittest.main()


class UnaccountedInRootTokens(unittest.TestCase):
    """An argv token inside a root that binds to no staged member and is not covers-data refuses.

    Re-run campaign finding (T1/T2): checks.py consumed plan.rewrites but ignored
    plan.unbound_members, though rewrite_argv's contract promises the runner refuses on an
    unrewritten in-root member. A script token naming a file present only in the candidate
    overlay executed while the evidence recorded PRIME's bundle as BOUND. Not directly
    candidate-reachable (it needs a policy naming a non-PRIME file), but the code claimed a
    protection it did not deliver.
    """

    def setUp(self) -> None:
        import os
        import tempfile
        import uuid
        from worldline.admission import AdmissionAuthority, Floors, Gate, Ledger, ResourcePolicy
        from worldline.checks import CheckRunner
        from worldline.linux.namespaces import BubblewrapSandbox, OverlayRoot
        from worldline.linux.systemd import SystemdAdapter
        from worldline.paths import WorldlinePaths
        self._os, self._uuid = os, uuid
        self.temporary = tempfile.TemporaryDirectory(prefix="unaccounted-")
        self.addCleanup(self.temporary.cleanup)
        base = Path(self.temporary.name)
        env = dict(os.environ, XDG_STATE_HOME=str(base / "s"), XDG_DATA_HOME=str(base / "d"),
                   XDG_RUNTIME_DIR=str(base / "r"), XDG_CONFIG_HOME=str(base / "c"))
        for n in "sdrc":
            (base / n).mkdir(parents=True, exist_ok=True)
        self.paths = WorldlinePaths.from_environment(env)
        self.paths.ensure()
        self.lower = base / "lower"
        (self.lower / "exam").mkdir(parents=True)
        (self.lower / "exam" / "run.py").write_text("print('GENUINE')\nimport sys; sys.exit(1)\n", encoding="utf-8")
        self.upper = base / "upper"
        (self.upper / "exam").mkdir(parents=True)
        self.work = base / "work"
        self.work.mkdir()
        self.overlay = OverlayRoot(root_key="a1" * 32, lower=self.lower, upper=self.upper,
                                   work=self.work, target=Path("/logical/root"))
        gate = Gate(AdmissionAuthority(Ledger(self.paths.runtime), Floors()), ResourcePolicy.from_mapping({}))
        self.runner = CheckRunner(self.paths, BubblewrapSandbox(self.paths), SystemdAdapter(), gate)

    def run_check(self, argv_extra, covers, upper_files):
        from worldline.project import CheckSpec, ProjectConfig
        from worldline.validation import resolve_verifiers
        for rel, content in upper_files.items():
            (self.upper / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.upper / rel).write_text(content, encoding="utf-8")
        argv = ("/usr/bin/python3", *argv_extra)
        check = CheckSpec("exam", "tests", argv, None, True, "exit", None, tuple(covers), ())
        proj = ProjectConfig(generated=(), checks=(check,), services=())
        roots = [{"root_key": "a1" * 32, "path": b"/logical/root", "primary_root": True}]
        entries = resolve_verifiers(proj, roots, {"a1" * 32: self.lower})
        return self.runner.run(world_instance=str(self._uuid.uuid4()), overlays=[self.overlay],
                               primary_target=Path("/logical/root"), checks=[check],
                               verifier_sources={"a1" * 32: self.lower}, verifiers=entries,
                               logical_roots={"a1" * 32: "/logical/root"})[0]

    def test_an_overlay_only_script_token_refuses(self) -> None:
        from worldline.errors import WorldlineError
        with self.assertRaises(WorldlineError) as caught:
            self.run_check(["/logical/root/exam/forged.py", "/logical/root/exam/run.py"], [],
                           {"exam/forged.py": "print('FORGED')\nimport sys; sys.exit(0)\n"})
        self.assertEqual(caught.exception.code, "VERIFIER_EXECUTION_UNIDENTIFIED")

    def test_a_declared_covers_operand_is_not_over_refused(self) -> None:
        import base64
        result = self.run_check(["/logical/root/exam/run.py", "/logical/root/out.txt"], ["out.txt"],
                                {"out.txt": "candidate output\n"})
        # PRIME's examiner ran (GENUINE, exit 1); the covers-operand did not trip the guard.
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("GENUINE", base64.b64decode(result["stdoutB64"]).decode())
