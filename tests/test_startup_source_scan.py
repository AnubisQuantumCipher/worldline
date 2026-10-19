"""Native scan regressions using ordinary fixtures, never protected witnesses."""
from pathlib import Path
import subprocess
import unittest

from worldline.root_worker_codec import scoped_archive


class StartupSourceScanTests(unittest.TestCase):
    def test_complete_and_malformed_envelopes(self):
        header = b"WORLDLINE-APPROVED-SOURCE-ENVELOPE-V1\n"
        helper = b"FILE\tHELPER\t2f68\t500\t78\n"
        interpreter = b"FILE\tINTERPRETER\t2f69\t500\t79\n"
        data = b"FILE\tDATA\t2f61\t600\t78\n"
        prefix = header + helper + interpreter
        # Expected role, exact DATA bytes, any-role image bytes, unselected path.
        cases = [
            ("complete", prefix + data, "/a", b"x", (True, True, True, False)),
            ("missing-final-newline", prefix + data[:-1], "/a", b"x", (False,) * 4),
            ("too-many-fields", prefix + data[:-1] + b"\textra\n", "/a", b"x", (False,) * 4),
            ("duplicate-path", prefix + data + data, "/a", b"x", (False,) * 4),
            ("wrong-bytes", prefix + data, "/a", b"z", (True, False, False, False)),
            ("different-role", prefix + data.replace(b"DATA", b"SOURCE"), "/a", b"x",
             (False, False, True, False)),
            ("unselected", prefix + data, "/missing", b"x", (False, False, False, True)),
            ("explicit-absent", prefix + b"ABSENT\t2f61\n", "/a", b"x", (False,) * 4),
            ("empty", b"", "/a", b"x", (False,) * 4),
            ("unterminated-header", header[:-1], "/a", b"x", (False,) * 4),
            ("empty-line", prefix + b"\n" + data, "/a", b"x", (False, True, True, False)),
            ("empty-file-bytes", prefix + data.replace(b"\t78\n", b"\t\n"), "/a", b"",
             (True, True, True, False)),
        ]
        inputs = []
        for _, envelope, path, raw, _ in cases:
            encoded = scoped_archive({"source": {"envelope_bytes_hex": envelope.hex()},
                                      "path": path, "raw": raw})
            self.assertTrue(encoded.isascii())
            self.assertNotIn(b"\n", encoded)
            inputs.append(encoded + b"\n")
        probe = Path(__file__).resolve().parents[1] / "bin/startup_source_probe"
        result = subprocess.run([str(probe)], input=b"".join(inputs),
                                capture_output=True, timeout=30, check=False)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), len(cases), result.stdout)
        for (name, _, _, _, expected), line in zip(cases, lines):
            with self.subTest(case=name):
                self.assertEqual(line.split(), [b"TRUE" if bit else b"FALSE" for bit in expected])


if __name__ == "__main__":
    unittest.main()
