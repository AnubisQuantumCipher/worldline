"""Explicit-input filesystem/SQLite producer controls; no protected startup claim."""
import hashlib
import hmac
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from worldline.custody_v2_provision_values import (
    DOMAIN, ExplicitInputs, Target, write_empty_artifacts)
from worldline.protected_startup import canonical, digest, exact_json, StartupRefusal
from worldline.root_worker_codec import archive

class EmptyV2ProducerControls(unittest.TestCase):
    def inputs(self, root, prior=None):
        key = b'explicit-fixture-key'
        descriptor = canonical({'installation_id': 'fixture'})
        plan = canonical({'schema': 'worldline.protected-root-worker-plan-v1',
            'installation': 'fixture', 'handoff_journal': str(root / 'custody.sqlite'),
            'handoff_genesis': str(root / 'genesis.json')})
        genesis = {'schema': 'worldline.owner-provisioned-root-custody-v2',
            'installation': 'fixture', 'startup_descriptor_sha256': digest(descriptor),
            'owner_plan_sha256': digest(plan), 'issuer_key_sha256': digest(key),
            'initial_event': None, 'prior_custody': prior}
        # The genesis value is the one its canonical file declares (exact_json
        # order), which native Genesis_Archive_Matches requires of the row.
        raw = canonical(genesis)
        return ExplicitInputs(descriptor, plan, raw, key), exact_json(raw)

    def targets(self, fd):
        return (Target(fd, 'custody.sqlite'), Target(fd, 'genesis.json'), Target(fd, 'custody.sqlite.lock'))

    def test_durable_empty_store_origin_and_full_hmac_readback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); inputs, genesis = self.inputs(root)
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            try:
                receipt = write_empty_artifacts(inputs, *self.targets(fd))
                self.assertEqual(receipt.state, 'EMPTY_V2_WRITTEN_SOURCE_AND_MIGRATION_AUTHORITY_OPEN')
                row = archive(genesis)
                origin = hashlib.sha256(row).hexdigest()
                mac = lambda value: hmac.new(inputs.key, DOMAIN + archive(value), hashlib.sha256).hexdigest()
                db = sqlite3.connect(root / 'custody.sqlite')
                try:
                    db.execute('PRAGMA foreign_keys=ON')
                    self.assertEqual(db.execute('SELECT * FROM genesis').fetchall(),
                        [('owner-genesis', row, mac({'genesis': genesis}))])
                    self.assertEqual(db.execute('SELECT * FROM head').fetchall(),
                        [('current', 'ORIGIN', None, origin,
                          mac({'head_kind': 'ORIGIN', 'head': origin, 'genesis': genesis}))])
                    self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
                    for name in ('events', 'alternatives', 'root_state', 'subject_state', 'blobs'):
                        self.assertEqual(db.execute('SELECT * FROM ' + name).fetchall(), [])
                finally:
                    db.close()
                self.assertEqual((root / 'genesis.json').read_bytes(), inputs.genesis_raw)
                self.assertEqual(receipt.journal_sha256, digest((root / 'custody.sqlite').read_bytes()))
                self.assertEqual(receipt.origin, origin)
            finally:
                os.close(fd)

    def test_existing_output_refuses_without_replacing_other_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); inputs, _ = self.inputs(root)
            existing = root / 'genesis.json'; existing.write_bytes(b'retained')
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            try:
                with self.assertRaises(FileExistsError):
                    write_empty_artifacts(inputs, *self.targets(fd))
                self.assertEqual(existing.read_bytes(), b'retained')
                self.assertEqual(set(p.name for p in root.iterdir()), {'genesis.json'})
            finally:
                os.close(fd)

    def test_symlink_target_refuses_and_preserves_referent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); inputs, _ = self.inputs(root)
            old = root / 'old-v1'; old.write_bytes(b'old retained history')
            (root / 'custody.sqlite').symlink_to(old)
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            try:
                with self.assertRaises(FileExistsError):
                    write_empty_artifacts(inputs, *self.targets(fd))
                self.assertEqual(old.read_bytes(), b'old retained history')
                self.assertFalse((root / 'genesis.json').exists())
            finally:
                os.close(fd)

    def test_injected_failure_keeps_partial_artifacts_and_retry_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); inputs, _ = self.inputs(root)
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            try:
                with patch('worldline.custody_v2_provision_values.sqlite3.connect', side_effect=OSError('injected')):
                    with self.assertRaises(OSError):
                        write_empty_artifacts(inputs, *self.targets(fd))
                self.assertEqual((root / 'genesis.json').read_bytes(), inputs.genesis_raw)
                self.assertTrue((root / 'custody.sqlite').exists())
                self.assertTrue((root / 'custody.sqlite.lock').exists())
                with self.assertRaises(FileExistsError):
                    write_empty_artifacts(inputs, *self.targets(fd))
            finally:
                os.close(fd)

    def test_key_binding_refuses_before_creating_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); inputs, _ = self.inputs(root)
            changed = ExplicitInputs(inputs.descriptor_raw, inputs.plan_raw, inputs.genesis_raw, b'changed')
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            try:
                with self.assertRaises(StartupRefusal):
                    write_empty_artifacts(changed, *self.targets(fd))
                self.assertEqual(tuple(root.iterdir()), ())
            finally:
                os.close(fd)

if __name__ == '__main__':
    unittest.main()
