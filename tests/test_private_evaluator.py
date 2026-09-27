"""Filesystem/protocol contract and opt-in real user-systemd role separation."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile
import unittest
from unittest.mock import patch
import uuid

from worldline.errors import WorldlineError
from worldline.linux.private_evaluator import (
    BackendFailure, PrivateEvaluationSpec, PrivateEvaluator, REPORT_MOUNT,
    TOOLCHAIN_MOUNT, VERIFIER_MOUNT, _request, copy_frozen_tree,
    _bubblewrap_identity,
)
from worldline.linux.systemd import SystemdAdapter
from worldline.trusted import TRUSTED_INTERPRETER


class PrivateTreeContract(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-private-tree-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / "source"
        self.source.mkdir()
        self.file = self.source / "source.txt"
        self.file.write_text("ordinary source\n")
        self.destination = self.base / "copy"

    def test_copy_preserves_content_mode_timestamp_and_has_stable_identity(self):
        self.file.chmod(0o640)
        (self.source / "nested").mkdir(mode=0o750)
        before = self.file.stat()
        identity = copy_frozen_tree(self.source, self.destination)
        self.assertEqual((self.destination / "source.txt").read_bytes(), self.file.read_bytes())
        self.assertEqual(stat.S_IMODE((self.destination / "source.txt").stat().st_mode), 0o640)
        self.assertEqual((self.destination / "source.txt").stat().st_mtime_ns, before.st_mtime_ns)
        self.assertEqual(identity, copy_frozen_tree(self.source, self.base / "again"))

    def test_links_special_objects_metadata_and_mountlike_inputs_are_refused(self):
        cases = ("symlink", "hardlink", "fifo", "setid", "xattr")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory(dir=self.base) as temporary:
                source = Path(temporary) / "source"
                source.mkdir()
                if case == "symlink":
                    (source / "entry").symlink_to(self.file)
                elif case == "hardlink":
                    os.link(self.file, source / "entry")
                elif case == "fifo":
                    os.mkfifo(source / "entry")
                elif case == "setid":
                    (source / "entry").write_text("file")
                    (source / "entry").chmod(0o4755)
                else:
                    os.setxattr(source, b"user.private-evaluator-test", b"present")
                with self.assertRaises(BackendFailure) as raised:
                    copy_frozen_tree(source, Path(temporary) / "out")
                self.assertEqual(raised.exception.code, "PRIVATE_TREE_UNSUPPORTED")

    def test_parent_symlink_and_byte_budget_are_refused(self):
        alias = self.base / "alias"
        alias.symlink_to(self.base, target_is_directory=True)
        with self.assertRaises(OSError):
            copy_frozen_tree(alias / "source", self.destination)
        with patch("worldline.linux.private_evaluator.MAX_TREE_BYTES", 1):
            with self.assertRaises(BackendFailure) as raised:
                copy_frozen_tree(self.source, self.destination)
            self.assertEqual(raised.exception.code, "PRIVATE_TREE_LIMIT")

    def test_constrained_request_accepts_command_and_refuses_authority_options(self):
        roots = [{"target": "/work"}]
        request = {"argv": ["/usr/bin/true"], "cwd": None, "timeout": 10}
        self.assertEqual(_request(request, roots, "/work"), (["/usr/bin/true"], "/work", 10))
        for changed in ({**request, "uid": 0}, {**request, "cwd": "/etc"},
                        {**request, "cwd": "/work/../etc"}, {**request, "timeout": True},
                        {**request, "argv": ["relative"]}, {**request, "argv": ["/run/helper"]}):
            with self.subTest(request=changed), self.assertRaises(BackendFailure):
                _request(changed, roots, "/work")

    def test_private_role_binary_uses_the_resolved_approved_installation(self):
        installed = self.base / "private-bwrap"
        installed.write_bytes(b"controlled bubblewrap fixture\n")
        installed.chmod(0o755)
        identity = _bubblewrap_identity(installed)
        self.assertEqual(identity["path"], str(installed.resolve()))
        self.assertEqual(identity["sha256"], hashlib.sha256(installed.read_bytes()).hexdigest())
        installed.chmod(0o775)
        with self.assertRaises(BackendFailure):
            _bubblewrap_identity(installed)


_WORKER = '''import json, os
from pathlib import Path
source = Path('source.txt')
assert source.read_text() == 'ordinary source\\n'
source.write_text('worker edit\\n')
Path('nested/created.txt').write_text('worker creation\\n')
assert not Path('/run/worldline-report').exists()
assert not Path('/run/worldline-broker.sock').exists()
assert not Path('/opt/worldline-gnat').exists()
print('ordinary worker complete')
'''

_EXAMINER = '''import candidate
from pathlib import Path
result = candidate.run(['/usr/bin/python3', 'worker.py'], timeout=20)
assert Path('source.txt').read_text() == 'ordinary source\\n'
assert not Path('nested/created.txt').exists()
ok = result.returncode == 0 and result.stdout == EXPECTED
Path('/run/worldline-report/report').write_text(
    '<testsuite tests="1" failures="' + ('0' if ok else '1') + '" errors="0"/>')
print('trusted assertion passed' if ok else 'trusted assertion failed')
raise SystemExit(0 if ok else 1)
'''


@unittest.skipUnless(os.environ.get("WORLDLINE_PRIVATE_EVALUATOR_TEST") == "1",
                     "set WORLDLINE_PRIVATE_EVALUATOR_TEST=1 for real user-systemd integration")
class PrivateEvaluatorIntegration(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-private-evaluator-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / "source"
        self.source.mkdir(mode=0o755)
        (self.source / "nested").mkdir(mode=0o755)
        (self.source / "source.txt").write_text("ordinary source\n")
        (self.source / "worker.py").write_text(_WORKER)
        self.verifier = self.base / "verifier"
        self.verifier.mkdir()
        self.adapter = SystemdAdapter()

    def run_examiner(self, expected: bytes, name: str):
        (self.verifier / "exam.py").write_text("EXPECTED = " + repr(expected) + "\n" + _EXAMINER)
        report = self.base / (name + "-report")
        report.mkdir(mode=0o700)
        spec = PrivateEvaluationSpec(
            str(uuid.uuid4()), {"/logical/private-check": self.source}, self.verifier,
            (TRUSTED_INTERPRETER, VERIFIER_MOUNT + "/exam.py"), "/logical/private-check", report,
            self.base / name, timeout_seconds=60)
        result = PrivateEvaluator(self.adapter).run(spec, resource_properties=(
            "MemoryMax=1G", "TasksMax=64", "CPUQuota=100%", "IOAccounting=yes"))
        evidence = os.environ.get("WORLDLINE_PRIVATE_EVALUATOR_EVIDENCE")
        if evidence:
            destination = Path(evidence)
            destination.mkdir(parents=True, exist_ok=True)
            (destination / (name + "-boundary.json")).write_text(json.dumps(result["boundary"], indent=2))
            (destination / (name + "-report.xml")).write_bytes((report / "report").read_bytes())
            (destination / (name + "-stdout.log")).write_bytes(result["stdout"])
            (destination / (name + "-stderr.log")).write_bytes(result["stderr"])
            (destination / (name + "-supervision.json")).write_text(json.dumps(result["supervision"], indent=2))
        return result

    def test_genuine_positive_and_negative_assertions_under_observed_separate_roles(self):
        passing = self.run_examiner(b"ordinary worker complete\n", "positive")
        failing = self.run_examiner(b"wrong expected value\n", "negative")
        self.assertEqual(passing["exitCode"], 0)
        self.assertIn(b'failures="0"', (passing["reportDirectory"] / "report").read_bytes())
        self.assertEqual(failing["exitCode"], 1)
        self.assertIn(b'failures="1"', (failing["reportDirectory"] / "report").read_bytes())
        self.assertEqual((self.source / "source.txt").read_text(), "ordinary source\n")
        self.assertFalse((self.source / "nested/created.txt").exists())
        for result in (passing, failing):
            boundary = result["boundary"]
            self.assertEqual(boundary["bubblewrap"]["path"],
                             str(Path(shutil.which("bwrap")).resolve()))
            self.assertEqual(boundary["managerBootstrapProperties"]["NoNewPrivileges"], "no")
            self.assertTrue(boundary["rolesCompleted"])
            examiner = boundary["examiner"]
            worker = boundary["workers"][0]["observation"]
            self.assertEqual(examiner["uid"], 0)
            self.assertEqual(worker["uid"], 1)
            self.assertEqual(examiner["uidMap"], worker["uidMap"])
            for namespace in ("pid", "mnt"):
                self.assertNotEqual(examiner["namespaces"][namespace], worker["namespaces"][namespace])
            for observation in (examiner, worker):
                self.assertEqual(observation["status"]["NoNewPrivs"], "1")
                self.assertEqual(observation["status"]["CapEff"], "0000000000000000")
            self.assertTrue(examiner["reportMounted"])
            self.assertTrue(examiner["brokerMounted"])
            self.assertTrue(examiner["toolchainMounted"])
            self.assertTrue(any(name.endswith("/bin/gnatprove")
                                for name in boundary["toolchain"]["executables"]))
            self.assertFalse(worker["reportMounted"])
            self.assertFalse(worker["brokerMounted"])
            self.assertFalse(worker["toolchainMounted"])
            self.assertEqual(boundary["workers"][0]["stdoutSha256"],
                             hashlib.sha256(b"ordinary worker complete\n").hexdigest())

    def test_worker_timeout_and_output_limit_refuse_the_entire_run(self):
        for name, argv, timeout in (
            ("timeout", ["/usr/bin/sleep", "10"], 1),
            ("output", ["/usr/bin/python3", "-c", "print('x' * 2097152)"], 20),
        ):
            with self.subTest(name=name):
                script = "import candidate\nfrom pathlib import Path\ntry:\n"
                script += "    candidate.run(" + repr(argv) + ", timeout=" + str(timeout) + ")\n"
                script += "except RuntimeError:\n    pass\n"
                script += "Path('/run/worldline-report/report').write_text('caught worker failure')\n"
                (self.verifier / "exam.py").write_text(script)
                report = self.base / (name + "-report")
                report.mkdir(mode=0o700)
                spec = PrivateEvaluationSpec(
                    str(uuid.uuid4()), {"/work": self.source}, self.verifier,
                    (TRUSTED_INTERPRETER, VERIFIER_MOUNT + "/exam.py"), "/work", report,
                    self.base / name, timeout_seconds=30)
                with self.assertRaises(WorldlineError) as raised:
                    PrivateEvaluator(self.adapter).run(spec, resource_properties=("MemoryMax=1G", "TasksMax=64"))
                self.assertEqual(raised.exception.code, "PRIVATE_EVALUATOR_BOUNDARY_FAILED")
                boundary = json.loads((spec.runtime / "boundary.json").read_text())
                self.assertIn("exceeded", boundary["error"])
                self.assertFalse(boundary.get("rolesCompleted", False))
                evidence = os.environ.get("WORLDLINE_PRIVATE_EVALUATOR_EVIDENCE")
                if evidence:
                    Path(evidence, name + "-boundary.json").write_text(json.dumps(boundary, indent=2))


if __name__ == "__main__":
    unittest.main()
