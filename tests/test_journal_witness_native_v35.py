"""Replay exact original-fixture full raw witnesses against the selected native core."""
import hashlib
import json
import os
from pathlib import Path
import unittest
from worldline.core import Core
from worldline.errors import CoreUnavailable
from worldline.journal_witness_kernel import invoke
from worldline.root_worker_codec import scoped_archive, scoped_restore_archive
from worldline.operation_capture import archive, restore_archive


class JournalWitnessNativeControls(unittest.TestCase):
    @unittest.skipUnless(os.environ.get('WORLDLINE_JOURNAL_WITNESS_CORPUS') and os.environ.get('WORLDLINE_SOURCE_IDENTITY'),
                         'original journal witness corpus is selected by the campaign environment')
    def test_full_original_fixture_corpus(self):
        root = Path(os.environ['WORLDLINE_JOURNAL_WITNESS_CORPUS'])
        identity = os.environ['WORLDLINE_SOURCE_IDENTITY']
        core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))
        rows = [json.loads(line) for line in
                (root / 'invocations.jsonl').read_text(encoding='ascii').splitlines()]
        self.assertTrue(rows, 'the authentic original fixture exporter must run first')
        positives = set()
        for row in rows:
            with self.subTest(current=row['current'], kind=row['kind']):
                self.assertEqual(row['source_identity'], identity)
                current = (root / row['current']).read_bytes()
                input_bytes = (root / row['input']).read_bytes()
                self.assertEqual(hashlib.sha256(current).hexdigest(), row['current_sha256'])
                self.assertEqual(hashlib.sha256(input_bytes).hexdigest(), row['input_sha256'])
                self.assertEqual(invoke(core._lib, row['kind'], current, input_bytes), row['decision'])
                if row['decision'] == 0:
                    positives.add(row['kind'])
                    # Same complete authentic original fixture, with only its
                    # custody genesis authentication cell corrupted. Parsing or
                    # authentic resource shape alone cannot authorize a witness.
                    damaged = scoped_restore_archive(current)
                    mac = damaged['genesis_mac']
                    damaged['genesis_mac'] = ('1' if mac[0] == '0' else '0') + mac[1:]
                    self.assertNotEqual(invoke(core._lib, row['kind'],
                                              scoped_archive(damaged), input_bytes), 0)
                    if row['kind'] == 0:
                        authentic = scoped_restore_archive(current)
                        owner = authentic['owner_roster']['operation_context']['owner_context']
                        capsules_raw = owner['native_replay_capsules_raw']
                        self.assertIs(type(capsules_raw), bytes)
                        capsules = restore_archive(capsules_raw)
                        self.assertIs(type(capsules), list)
                        for capsule in capsules:
                            self.assertIs(type(capsule), dict)
                            self.assertEqual(set(capsule), {'result', 'declaration', 'capsule'})
                            for value in capsule.values():
                                self.assertIs(type(value), bytes)
                                # Inspect JSON syntax without narrowing the
                                # native arbitrary-integer operand domain.
                                json.loads(value.decode('utf8'), parse_int=str)
                        # Preserve all original custody/history/material and
                        # remove only the independently acquired factual route.
                        del owner['native_replay_capsules_raw']
                        self.assertNotEqual(invoke(core._lib, row['kind'],
                                                  scoped_archive(authentic), input_bytes), 0)
                        if capsules:
                            # Keep every authentic original result/declaration;
                            # only replace its physical capture by a verdict.
                            owner['native_replay_capsules_raw'] = archive([
                                dict(capsule, capsule=b'{"AST":true}')
                                for capsule in capsules])
                            self.assertNotEqual(invoke(core._lib, row['kind'],
                                                      scoped_archive(authentic), input_bytes), 0)
                # Malformed loss of original retained bytes cannot acquire either
                # authority; this does not replace authentic stale/conflict cases.
                with self.assertRaises(CoreUnavailable):
                    invoke(core._lib, row['kind'], current, b'')
        self.assertEqual(positives, {0, 1}, 'both original fixture accepted authorities must remain reachable')


if __name__ == '__main__':
    unittest.main()
