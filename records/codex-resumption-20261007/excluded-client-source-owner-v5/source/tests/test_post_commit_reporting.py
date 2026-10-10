from __future__ import annotations

from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from worldline.controller import RuntimeController
from worldline.errors import WorldlineError


class PostCommitReportingTests(unittest.TestCase):
    def controller(self) -> RuntimeController:
        controller = RuntimeController.__new__(RuntimeController)
        controller.store = Mock()
        controller.store.transaction_record.return_value = {"kind": "collapse"}
        controller.transactions = Mock()
        controller._rebuild_watcher_and_retry = Mock(return_value=[{"step": "watcher-rebuild"}])
        controller._after_commit = Mock(return_value=[{"step": "automatic-ghosts"}])
        return controller

    def test_committed_result_retains_followup_warnings(self) -> None:
        controller = self.controller()
        controller.transactions.commit.return_value = {
            "state": "COMMITTED", "transactionId": "fixture-transaction",
            "anchor": {"warnings": [{"step": "anchor-export"}]},
        }
        result = controller._collapse_commit({"transactionId": "fixture-transaction"}, SimpleNamespace(daemon=Mock()))
        self.assertEqual(result["state"], "COMMITTED")
        self.assertEqual(result["transactionId"], "fixture-transaction")
        self.assertEqual(result["postCommit"]["warnings"], [
            {"step": "watcher-rebuild"}, {"step": "automatic-ghosts"}, {"step": "anchor-export"}])

    def test_committed_error_retains_original_warning_details(self) -> None:
        controller = self.controller()
        error = WorldlineError("COMMIT_DURABILITY_UNCERTAIN", "fixture", {
            "state": "COMMITTED", "transactionId": "fixture-transaction",
            "postCommit": {"warnings": [{"step": "receipt"}], "retryRequired": True},
        })
        controller.transactions.commit.side_effect = error
        with self.assertRaises(WorldlineError) as caught:
            controller._collapse_commit({"transactionId": "fixture-transaction"}, SimpleNamespace(daemon=Mock()))
        self.assertIs(caught.exception, error)
        self.assertEqual(error.details["state"], "COMMITTED")
        self.assertTrue(error.details["postCommit"]["retryRequired"])
        self.assertEqual(error.details["postCommit"]["warnings"], [
            {"step": "receipt"}, {"step": "watcher-rebuild"}, {"step": "automatic-ghosts"}])

    def test_committed_result_preserves_existing_post_commit_fields(self) -> None:
        controller = self.controller()
        controller.transactions.commit.return_value = {
            "state": "COMMITTED", "transactionId": "fixture-transaction",
            "postCommit": {"warnings": [{"step": "receipt"}], "retryRequired": True},
        }
        result = controller._collapse_commit({"transactionId": "fixture-transaction"}, SimpleNamespace(daemon=Mock()))
        self.assertEqual(result["state"], "COMMITTED")
        self.assertTrue(result["postCommit"]["retryRequired"])
        self.assertEqual(result["postCommit"]["warnings"], [
            {"step": "receipt"}, {"step": "watcher-rebuild"}, {"step": "automatic-ghosts"}])

    def test_scheduling_and_pending_read_failure_preserve_committed_result(self) -> None:
        controller = self.controller()
        del controller._after_commit  # exercise the real follow-up reporting method
        controller._schedule_automatic_ghosts = Mock(side_effect=OSError("fixture scheduling unavailable"))
        controller.store.get_meta.side_effect = OSError("fixture pending status unavailable")
        controller.transactions.commit.return_value = {
            "state": "COMMITTED", "transactionId": "fixture-transaction",
        }
        with self.assertLogs("worldline.controller", level="ERROR"):
            result = controller._collapse_commit({"transactionId": "fixture-transaction"}, SimpleNamespace(daemon=Mock()))
        self.assertEqual(result["state"], "COMMITTED")
        self.assertEqual(result["transactionId"], "fixture-transaction")
        warnings = result["postCommit"]["warnings"]
        self.assertEqual([warning["step"] for warning in warnings], [
            "watcher-rebuild", "automatic-ghosts", "automatic-ghosts-status"])
        self.assertNotIn("pending", warnings[1])
        self.assertIn("fixture scheduling unavailable", warnings[1]["message"])
        self.assertIn("fixture pending status unavailable", warnings[2]["message"])

    def test_prepare_refusal_does_not_schedule_post_commit_work(self) -> None:
        controller = self.controller()
        error = WorldlineError("PROOF_STATUS_UNEVALUABLE", "fixture", {"state": "PREPARED"})
        controller.transactions.commit.side_effect = error
        with self.assertRaises(WorldlineError) as caught:
            controller._collapse_commit({"transactionId": "fixture-transaction"}, SimpleNamespace(daemon=Mock()))
        self.assertIs(caught.exception, error)
        controller._after_commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
