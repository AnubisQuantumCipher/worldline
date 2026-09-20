from __future__ import annotations

import unittest

from worldline.cli_main import parser


class CliParserTests(unittest.TestCase):
    def test_fork_delimiter_race_and_switch_forms(self) -> None:
        fork = parser().parse_args(
            ["fork", "alpha", "--mission-text", "change it", "--wait", "--", "codex"]
        )
        self.assertEqual(fork.name, "alpha")
        self.assertEqual(fork.agent, "codex")
        self.assertTrue(fork.wait)
        race = parser().parse_args(
            [
                "race", "--detach", "--mission-text", "compare", "--agent", "codex",
                "--agent", "claude", "--agent", "omp",
            ]
        )
        self.assertEqual(race.agent, ["codex", "claude", "omp"])
        self.assertTrue(race.detach)
        switch = parser().parse_args(["switch", "--next"])
        self.assertTrue(switch.next)
        direct = parser().parse_args(["switch", "beta"])
        self.assertEqual(direct.world, "beta")

    def test_prepared_transaction_cancel_and_dry_run_forms(self) -> None:
        prepare = parser().parse_args(["collapse", "beta", "--prepare", "--json"])
        self.assertTrue(prepare.prepare)
        self.assertFalse(prepare.yes)
        returning = parser().parse_args(["return", "--prepare"])
        self.assertTrue(returning.prepare)
        self.assertIsNone(returning.world)
        commit = parser().parse_args(["transaction", "commit", "tx-1", "--yes"])
        self.assertEqual((commit.transaction_command, commit.transaction_id, commit.yes), ("commit", "tx-1", True))
        abort = parser().parse_args(["transaction", "abort", "tx-1"])
        self.assertEqual(abort.transaction_command, "abort")
        self.assertEqual(parser().parse_args(["transaction", "list"]).transaction_command, "list")
        self.assertEqual(parser().parse_args(["transaction", "show", "tx-1"]).transaction_id, "tx-1")
        self.assertEqual(parser().parse_args(["cancel", "beta"]).world, "beta")
        dry = parser().parse_args(["init", "--dry-run", "/tmp/x"])
        self.assertTrue(dry.dry_run)
        self.assertTrue(parser().parse_args(["root", "remove", "--dry-run", "/tmp/x"]).dry_run)

    def test_simulate_preserves_exact_argv(self) -> None:
        simulation = parser().parse_args(["simulate", "--", "/usr/bin/pacman", "-Q"])
        exact = list(simulation.argv)
        if exact[0] == "--":
            exact.pop(0)
        self.assertEqual(exact, ["/usr/bin/pacman", "-Q"])


if __name__ == "__main__":
    unittest.main()
