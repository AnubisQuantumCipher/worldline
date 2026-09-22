"""Trusted processes must not take their imports from a directory the candidate writes.

WORLDLINE runs several Python processes on its own behalf: the check harness that attests an
examination happened, the materializer that snapshots a candidate, the simulation runner, the
netguard forwarder. Their output is treated as WORLDLINE's own observation. CPython puts either
the working directory (`-c`) or the script's directory (a script path) first on sys.path, and in
normal operation both of those are candidate-writable — a check's cwd is inside a managed root,
and /run/worldline-runtime is bind-mounted read-write as the world's XDG_RUNTIME_DIR.

These tests establish three things, in increasing strength:

    1. every trusted launch site carries the policy  (so a new one cannot quietly skip it)
    2. the policy actually works on the interpreter WORLDLINE launches  (not assumed)
    3. the materializer produces the intended candidate snapshot even under attack, AND the
       same attack succeeds without the policy  (so a pass here means something)
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "runtime"))

from worldline.finalize import _COPY_SCRIPT  # noqa: E402
from worldline.trusted import (  # noqa: E402
    ISOLATION_FLAGS,
    TRUSTED_INTERPRETER,
    trusted_inline,
    trusted_script,
)

RUNTIME = REPO / "runtime" / "worldline"


def _tree_digest(root: Path) -> str:
    """Content identity of a directory tree: names, modes and bytes."""
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8") + b"\0")
        if path.is_symlink():
            digest.update(b"L" + os.readlink(path).encode("utf-8"))
        elif path.is_dir():
            digest.update(b"D")
        else:
            digest.update(b"F" + oct(path.stat().st_mode & 0o777).encode("ascii") + path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


class PolicyCoverage(unittest.TestCase):
    """Nothing launches the interpreter except through the one policy."""

    def test_no_launch_site_spells_the_interpreter_itself(self) -> None:
        offenders = []
        for path in sorted(RUNTIME.rglob("*.py")):
            if path.name == "trusted.py":
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if '"/usr/bin/python3"' not in line and "'/usr/bin/python3'" not in line:
                    continue
                # Recording the interpreter as evidence is not launching it.
                if "TRUSTED_INTERPRETER" in line:
                    continue
                offenders.append(f"{path.relative_to(REPO)}:{number}: {line.strip()}")
        self.assertEqual(offenders, [], "trusted launches must go through worldline.trusted")

    def test_every_trusted_helper_is_launched_through_the_policy(self) -> None:
        # The four sites, named, so that deleting one's isolation is a test failure rather than
        # a silent regression in whichever file nobody re-read.
        expected = {
            "checks.py": "trusted_inline(",          # the check harness
            "finalize.py": "trusted_inline(",        # the materializer
            "simulation.py": "trusted_inline(",      # the simulation runner
            "linux/namespaces.py": "trusted_script(",  # the netguard forwarder
        }
        for relative, call in expected.items():
            text = (RUNTIME / relative).read_text(encoding="utf-8")
            self.assertIn(call, text, f"{relative} does not launch through worldline.trusted")

    def test_the_policy_is_recorded_in_the_validation_context(self) -> None:
        # A weaker startup policy is not the same evidence, so changing it must stale what came
        # before rather than silently reinterpreting it.
        from worldline.validation import execution_context

        config = type("C", (), {"network_policy": None, "network_allow": (),
                                "readonly_home_paths": (), "resource_policy": None})()
        context = execution_context(config)
        self.assertEqual(context["trustedStartupFlags"], list(ISOLATION_FLAGS))
        self.assertEqual(context["checkRunnerInterpreter"], TRUSTED_INTERPRETER)


class ThePolicyActuallyWorks(unittest.TestCase):
    """Measured against the real interpreter, in both launch forms.

    Asserting the flags are present proves only that someone typed them. These run the
    interpreter WORLDLINE will launch, with a hostile module planted where CPython would look.
    """

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-trusted-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.working = self.base / "candidate-cwd"
        self.scripts = self.base / "script-dir"
        self.working.mkdir()
        self.scripts.mkdir()
        self.probe = "import base64; print('BASE64:' + (base64.__file__ or 'builtin'))"

    def _plant(self, directory: Path) -> None:
        (directory / "base64.py").write_text("__file__ = 'HOSTILE'\n", encoding="utf-8")

    def _run(self, argv, cwd: Path) -> str:
        proc = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, timeout=60)
        return proc.stdout

    def test_inline_source_is_hijacked_without_the_policy(self) -> None:
        # The complementary arm. Without it, a pass below could mean the attack simply does not
        # work on this interpreter, which would make the whole test vacuous.
        self._plant(self.working)
        out = self._run([TRUSTED_INTERPRETER, "-c", self.probe], self.working)
        self.assertIn("HOSTILE", out)

    def test_inline_source_is_clean_under_the_policy(self) -> None:
        self._plant(self.working)
        out = self._run(trusted_inline(self.probe), self.working)
        self.assertNotIn("HOSTILE", out)
        self.assertIn("BASE64:", out)

    def test_a_script_is_hijacked_from_its_own_directory_without_the_policy(self) -> None:
        # A different directory from the -c case, which is why the policy has two entry points.
        script = self.scripts / "helper.py"
        script.write_text(self.probe + "\n", encoding="utf-8")
        self._plant(self.scripts)
        out = self._run([TRUSTED_INTERPRETER, str(script)], self.working)
        self.assertIn("HOSTILE", out)

    def test_a_script_is_clean_under_the_policy(self) -> None:
        script = self.scripts / "helper.py"
        script.write_text(self.probe + "\n", encoding="utf-8")
        self._plant(self.scripts)
        self._plant(self.working)
        out = self._run(trusted_script(str(script)), self.working)
        self.assertNotIn("HOSTILE", out)
        self.assertIn("BASE64:", out)

    def test_the_policy_survives_a_pth_file(self) -> None:
        # -I alone would not reach this: .pth files are processed by site initialisation, which
        # is what -S suppresses. This is why the policy is two flags and not one.
        site = self.base / "sitedir"
        site.mkdir()
        (site / "evil.pth").write_text("import sys; sys.stdout.write('PTH-RAN\\n')\n", encoding="utf-8")
        environment = {**os.environ, "PYTHONPATH": str(site)}
        proc = subprocess.run(trusted_inline("pass"), cwd=self.working, env=environment,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=60)
        self.assertNotIn("PTH-RAN", proc.stdout)


class MaterializationProducesTheCandidateSnapshot(unittest.TestCase):
    """The materializer's output IS the candidate snapshot every later measurement is taken from.

    Two positive facts are required, not one absence:

        1. the intended trusted helper ran      (the copy completed)
        2. its output matches the candidate      (byte-for-byte, modes included)

    The attack is quiet by design: a hostile `subprocess` shim makes the copy a no-op and lets
    the helper exit 0, so the payload becomes an empty directory that every later step measures
    as the candidate's content.
    """

    HOSTILE_SUBPROCESS = (
        "class _Result:\n"
        "    returncode = 0\n"
        "    stdout = b''\n"
        "    stderr = b''\n"
        "def run(*arguments, **keywords):\n"
        "    open('/tmp/unused-marker', 'a').close() if False else None\n"
        "    return _Result()\n"
        "class CalledProcessError(Exception):\n"
        "    pass\n"
    )

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-materialize-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.candidate = self.base / "candidate-root"
        (self.candidate / "src").mkdir(parents=True)
        (self.candidate / "src" / "main.py").write_text("print('the candidate\\'s work')\n", encoding="utf-8")
        (self.candidate / "README.md").write_text("# delivered\n", encoding="utf-8")
        executable = self.candidate / "build.sh"
        executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        executable.chmod(0o755)
        self.expected = _tree_digest(self.candidate)

    def _materialize(self, argv_builder, *, hostile: bool) -> tuple[int, Path]:
        if hostile:
            # Planted in the helper's working directory, which is the primary candidate root —
            # a directory the candidate writes by construction.
            (self.candidate / "subprocess.py").write_text(self.HOSTILE_SUBPROCESS, encoding="utf-8")
            self.expected = _tree_digest(self.candidate)
        destination = self.base / ("hostile" if hostile else "clean") / "materialized"
        destination.parent.mkdir(parents=True, exist_ok=True)
        argv = argv_builder(_COPY_SCRIPT, str(self.candidate), str(destination))
        proc = subprocess.run(argv, cwd=self.candidate, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, timeout=120)
        return proc.returncode, destination

    def test_the_snapshot_matches_the_candidate_under_attack(self) -> None:
        code, destination = self._materialize(trusted_inline, hostile=True)
        # Positive fact 1: the intended helper ran to completion.
        self.assertEqual(code, 0)
        self.assertTrue(destination.is_dir())
        self.assertTrue((destination / "src" / "main.py").is_file(),
                        "the copy did not happen: the helper was subverted or never ran")
        # Positive fact 2: what it produced IS the candidate, modes and all.
        self.assertEqual(_tree_digest(destination), self.expected)
        self.assertEqual((destination / "build.sh").stat().st_mode & 0o777, 0o755)

    def test_the_same_attack_succeeds_without_the_policy(self) -> None:
        # The complementary arm: the attack is real, so the test above is not vacuous.
        def unisolated(source, *arguments):
            return (TRUSTED_INTERPRETER, "-c", source, *arguments)

        code, destination = self._materialize(unisolated, hostile=True)
        self.assertEqual(code, 0, "the hostile shim is supposed to let the helper exit cleanly")
        self.assertFalse((destination / "src" / "main.py").exists(),
                         "the hostile subprocess shim did not take effect; this arm proves nothing")
        self.assertNotEqual(_tree_digest(destination), self.expected)

    def test_an_unattacked_snapshot_still_matches(self) -> None:
        code, destination = self._materialize(trusted_inline, hostile=False)
        self.assertEqual(code, 0)
        self.assertEqual(_tree_digest(destination), self.expected)


if __name__ == "__main__":
    unittest.main()
