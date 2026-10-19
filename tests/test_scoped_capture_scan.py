"""Native factual maps parser fixtures; not protected host/custody acceptance."""
from pathlib import Path
import subprocess
import unittest

from worldline.root_worker_codec import raw_archive

ROOT = Path(__file__).resolve().parents[1]


class ScopedCaptureMapsControls(unittest.TestCase):
    def test_native_complete_maps_and_role_selection(self):
        prefix = b'0-1 r-xp 0000 00:00 1 '
        selected = ({'path': '/usr/bin/demo', 'role': 'EXECUTABLE'},)
        cases = [
            (b'', selected, True),
            (b'\n', selected, True),
            (prefix+b'/usr/bin/demo', selected, True),
            (prefix+b'/usr/bin/demo\n', selected, True),
            (prefix+b' \t/usr/bin/demo\n', selected, True),
            (prefix+b'[heap]\n', selected, True),
            (prefix+b'/different\n', selected, False),
            (prefix+b'/usr/bin/demo\n'+prefix+b'/different', selected, False),
            (prefix+b'/usr/bin/demo', (), False),
            (prefix+b'/usr/bin/demo', ({'path': '/usr/bin/demo', 'role': 'OTHER'},), False),
        ]
        for role in ('INTERPRETER', 'EXECUTABLE', 'EXTENSION', 'DATA'):
            cases.append((prefix+b'/usr/bin/demo', ({'path': '/usr/bin/demo', 'role': role},), True))
        payload = b'\n'.join(raw_archive({'maps': raw, 'inventory': {
            'current_source_files': files}}) for raw, files, _ in cases)+b'\n'
        result = subprocess.run([str(ROOT/'bin/scoped_capture_probe')], input=payload,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=60, check=False)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace'))
        observed = result.stdout.decode().splitlines()
        self.assertEqual(len(observed), len(cases))
        for output, (raw, files, expected) in zip(observed, cases):
            with self.subTest(raw=raw, files=files):
                self.assertEqual(output.strip(), 'TRUE' if expected else 'FALSE')
