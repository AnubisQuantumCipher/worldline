"""Same-source original actor11 and whole envelope controls, authored UNRUN."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class ActorArchiveReplayV35(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.executable = os.environ['WORLDLINE_ACTOR_ARCHIVE_CONTROL']
        cls.directory = tempfile.TemporaryDirectory(prefix='worldline-actor-archive-v35-')
        cls.path = Path(cls.directory.name)
        from export_actor_archive_v35 import export_actor_values
        cls.cases = export_actor_values(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def decide(self, mode, path):
        result = subprocess.run([self.executable, mode, str(path)], check=True,
                                capture_output=True, text=True, timeout=120)
        return result.stdout.strip()

    def test_all_original_full_inputs_arenas_rosters_counts_and_output(self):
        for case in self.cases:
            with self.subTest(case=case['name']):
                actual = self.decide('actor', self.path / case['observation'])
                if case['replay'] is not None:
                    self.assertEqual(actual, case['replay'])
                else:
                    self.assertIn(actual.split(':')[0],
                                  ('DECODE_REFUSED', 'NATIVE_REDECIDED', 'OUTPUT_CONFLICT'))
                self.assertEqual(self.decide('actor-material', self.path / case['material']),
                                 str(case['correspondence']).upper())

    def test_authentic_original_actor_committed_captures(self):
        directory = Path(os.environ['WORLDLINE_AUTHENTIC_ENVELOPE_FIXTURES'])
        cases = json.loads((directory / 'authentic-actors.json').read_text())
        self.assertTrue(cases)
        for case in cases:
            self.assertEqual(self.decide('actor', directory / case['observation']), case['replay'])
            self.assertEqual(self.decide('actor-material', directory / case['material']), 'TRUE')

    def test_genuine_whole_original_envelopes_and_corruptions(self):
        from worldline.root_worker_codec import archive, restore_archive
        from worldline.operation_capture import archive as original_archive, restore_archive as original_restore
        directory = Path(os.environ['WORLDLINE_AUTHENTIC_ENVELOPE_FIXTURES'])
        cases = json.loads((directory / 'boundaries.json').read_text())
        self.assertEqual({case['kind'] for case in cases}, {'ACTOR_EXECUTION', 'FOLLOWUP', 'FULL_BROKER'})
        for case in cases:
            value = restore_archive((directory / case['path']).read_bytes())
            original = self.path / 'original.boundary'; original.write_bytes(archive(value))
            self.assertEqual(self.decide(case['kind'], original), 'TRUE')
            # Whole immutable source and exact event custody are not success flags.
            for context_field in ('native_context',):
                changed = restore_archive(archive(value))
                native = original_restore(changed['context'][context_field])
                native['library_bytes'] += b'corruption'
                changed['context'][context_field] = original_archive(native)
                path = self.path / 'source-corrupt.boundary'; path.write_bytes(archive(changed))
                self.assertEqual(self.decide(case['kind'], path), 'FALSE')
            changed = restore_archive(archive(value)); changed['event']['operation'] = '00'
            path = self.path / 'operation-corrupt.boundary'; path.write_bytes(archive(changed))
            self.assertEqual(self.decide(case['kind'], path), 'FALSE')
            if case['kind'] == 'FULL_BROKER':
                body = original_restore(bytes.fromhex(value['material']))
                for field in tuple(body):
                    changed = restore_archive(archive(value)); corrupt = original_restore(bytes.fromhex(changed['material']))
                    del corrupt[field]; changed['material'] = original_archive(corrupt).hex()
                    path = self.path / 'broker-field-corrupt.boundary'; path.write_bytes(archive(changed))
                    self.assertEqual(self.decide(case['kind'], path), 'FALSE')
                for field in ('input', 'arena', 'output'):
                    changed = restore_archive(archive(value)); corrupt = original_restore(bytes.fromhex(changed['material']))
                    corrupt['native'][field] += '00'
                    changed['material'] = original_archive(corrupt).hex()
                    path = self.path / 'broker-native-corrupt.boundary'; path.write_bytes(archive(changed))
                    self.assertEqual(self.decide(case['kind'], path), 'FALSE')
                for ordinal in range(len(body['native']['rosters'])):
                    changed = restore_archive(archive(value)); corrupt = original_restore(bytes.fromhex(changed['material']))
                    corrupt['native']['rosters'][ordinal] += '00'
                    changed['material'] = original_archive(corrupt).hex()
                    path = self.path / 'broker-roster-corrupt.boundary'; path.write_bytes(archive(changed))
                    self.assertEqual(self.decide(case['kind'], path), 'FALSE')
                for field in ('worker', 'canonical'):
                    changed = restore_archive(archive(value)); corrupt = original_restore(bytes.fromhex(changed['material']))
                    corrupt['facts'][field] = None
                    changed['material'] = original_archive(corrupt).hex()
                    path = self.path / 'broker-observation-corrupt.boundary'; path.write_bytes(archive(changed))
                    self.assertEqual(self.decide(case['kind'], path), 'FALSE')
            else:
                material = value['material']
                full = original_restore(bytes.fromhex(material['full_current']))
                for field in tuple(full):
                    changed = restore_archive(archive(value)); corrupt = original_restore(bytes.fromhex(changed['material']['full_current']))
                    del corrupt[field]; changed['material']['full_current'] = original_archive(corrupt).hex()
                    path = self.path / 'current-field-corrupt.boundary'; path.write_bytes(archive(changed))
                    self.assertEqual(self.decide(case['kind'], path), 'FALSE')
                snapshot_field = ('full_current_rows' if case['kind'] == 'FOLLOWUP' else 'complete_snapshot')
                captured_snapshot = full[snapshot_field]
                if captured_snapshot.get('type') == 'dict':
                    for field in ('state', 'history', 'rows', 'projection', 'buckets'):
                        self.assertIn(field, captured_snapshot['fields'])
                        changed = restore_archive(archive(value))
                        corrupt = original_restore(bytes.fromhex(changed['material']['full_current']))
                        del corrupt[snapshot_field]['fields'][field]
                        changed['material']['full_current'] = original_archive(corrupt).hex()
                        path = self.path / 'complete-snapshot-roster-corrupt.boundary'
                        path.write_bytes(archive(changed))
                        self.assertEqual(self.decide(case['kind'], path), 'FALSE')
                changed = restore_archive(archive(value))
                snapshot = original_restore(bytes.fromhex(changed['material']['snapshot']))
                snapshot['evidence']['owner_resolution']['id']['policy'] = '00' * 32
                changed['material']['snapshot'] = original_archive(snapshot).hex()
                path = self.path / 'current-binding-corrupt.boundary'; path.write_bytes(archive(changed))
                self.assertEqual(self.decide(case['kind'], path), 'FALSE')
                for field in ('input', 'arena', 'output'):
                    changed = restore_archive(archive(value))
                    changed['material']['native'][field] += '00'
                    path = self.path / 'native-corrupt.boundary'; path.write_bytes(archive(changed))
                    self.assertEqual(self.decide(case['kind'], path), 'FALSE')
                for ordinal in range(len(material['native']['rosters'])):
                    changed = restore_archive(archive(value)); changed['material']['native']['rosters'][ordinal] += '00'
                    path = self.path / 'roster-corrupt.boundary'; path.write_bytes(archive(changed))
                    self.assertEqual(self.decide(case['kind'], path), 'FALSE')


if __name__ == '__main__':
    unittest.main()
