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

    def test_simulate_preserves_exact_argv(self) -> None:
        simulation = parser().parse_args(["simulate", "--", "/usr/bin/pacman", "-Q"])
        exact = list(simulation.argv)
        if exact[0] == "--":
            exact.pop(0)
        self.assertEqual(exact, ["/usr/bin/pacman", "-Q"])


if __name__ == "__main__":
    unittest.main()
