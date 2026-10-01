from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from worldline.cli_main import main, VERIFICATION_FAILED
from worldline.controller import RuntimeController
from worldline.engine_codes import CODE_SET_SHA256
from worldline.status import StatusPublisher


class VerificationReportingTests(unittest.TestCase):
    def invoke(self, command: list[str], response: object) -> tuple[int, str, str]:
        output, error = io.StringIO(), io.StringIO()
        with patch("worldline.cli_main.DaemonClient") as client, redirect_stdout(output), redirect_stderr(error):
            client.return_value.request.return_value = response
            code = main([*command, "--json"])
        self.assertEqual(json.loads(output.getvalue()), response)
        return code, output.getvalue(), error.getvalue()

    def test_complete_intact_verdicts_succeed(self) -> None:
        for command, response in (
            (["log", "--verify"], {"verdict": {"state": "OK", "problems": []}}),
            (["anchor"], {"state": "OK", "problems": []}),
        ):
            with self.subTest(command=command):
                code, _, error = self.invoke(command, response)
                self.assertEqual(code, 0)
                self.assertEqual(error, "")

    def test_missing_and_incomplete_verdicts_have_named_failure(self) -> None:
        for verdict in (None, [], "pending", {}, {"state": "OK"}, {"state": "OK", "problems": None}):
            for command, response in ((["log", "--verify"], {"verdict": verdict}), (["anchor"], verdict)):
                with self.subTest(command=command, verdict=verdict):
                    code, _, error = self.invoke(command, response)
                    self.assertEqual(code, VERIFICATION_FAILED)
                    self.assertIn("INVALID_VERIFICATION_VERDICT", error)

    def test_failed_verdict_preserves_named_problems(self) -> None:
        for command, response in (
            (["log", "--verify"], {"verdict": {"state": "FAILED", "problems": ["WITNESS_UNCONFIGURED"]}}),
            (["anchor"], {"state": "WITNESS_UNCONFIGURED", "problems": [{"state": "WITNESS_UNCONFIGURED"}]}),
        ):
            with self.subTest(command=command):
                code, _, error = self.invoke(command, response)
                self.assertEqual(code, VERIFICATION_FAILED)
                self.assertIn("WITNESS_UNCONFIGURED", error)

    def test_inconsistent_ok_verdict_does_not_succeed(self) -> None:
        for command, response in (
            (["log", "--verify"], {"verdict": {"state": "OK", "problems": ["PENDING"]}}),
            (["anchor"], {"state": "OK", "problems": [{"state": "PENDING"}]}),
        ):
            with self.subTest(command=command):
                code, _, error = self.invoke(command, response)
                self.assertEqual(code, VERIFICATION_FAILED)
                self.assertIn("INCONSISTENT_VERIFICATION_VERDICT", error)

    def test_incomplete_problem_records_do_not_crash(self) -> None:
        for command, response in (
            (["log", "--verify"], {"verdict": {"state": "FAILED", "problems": [None, {}]}}),
            (["anchor"], {"state": "FAILED", "problems": [None, "pending", {}]}),
        ):
            with self.subTest(command=command):
                code, _, error = self.invoke(command, response)
                self.assertEqual(code, VERIFICATION_FAILED)
                self.assertIn("INVALID_VERIFICATION_VERDICT", error)

    def test_plain_log_does_not_require_verification(self) -> None:
        code, _, error = self.invoke(["log"], {"verification": None})
        self.assertEqual(code, 0)
        self.assertEqual(error, "")

    def test_status_and_version_publish_same_code_set(self) -> None:
        output = io.StringIO()
        with patch("worldline.cli_main.DaemonClient"), redirect_stdout(output):
            self.assertEqual(main(["version", "--json"]), 0)
        version = json.loads(output.getvalue())
        store = Mock()
        store.roots.return_value = []
        store.prime.return_value = None
        store.worlds.return_value = []
        store.jobs.return_value = []
        store.last_receipt.return_value = None
        store.get_meta.return_value = None
        status = StatusPublisher(SimpleNamespace(socket="/unused/worldline.sock"), store).snapshot()
        self.assertEqual(status["daemon"]["codeSetSha256"], CODE_SET_SHA256)
        self.assertEqual(version["codeSetSha256"], status["daemon"]["codeSetSha256"])
        self.assertEqual(version["version"], status["daemon"]["version"])


class LogCollectionTests(unittest.TestCase):
    def test_unreadable_record_prevents_overall_success(self) -> None:
        controller = RuntimeController.__new__(RuntimeController)
        controller.store = Mock()
        controller.store.worlds.return_value = [SimpleNamespace(alias="fixture", instance_id="fixture-world")]
        controller.store.causal_events_for_world.side_effect = OSError("temporary read failure")
        controller.store.receipts.return_value = []
        controller.store.verify_chains.return_value = {}
        controller._anchor_verdict = Mock(return_value={"state": "OK", "problems": []})
        result = controller._log({"verify": True}, None)
        self.assertEqual(result["verdict"]["state"], "FAILED")
        self.assertIn("LOG_RECORD_UNREADABLE", result["verdict"]["problems"])
        self.assertEqual(result["unreadable"][0]["world"], "fixture")
        controller.store.verify_chains.assert_called_once_with()
        controller._anchor_verdict.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
