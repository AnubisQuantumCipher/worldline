"""Consumer-visible lossless v2 schema/FK/SQL cells; no simulated startup lease."""
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from worldline.root_worker_current_state import _database_connection, _database
from worldline.custody_v2_provision_values import ExplicitInputs, Target, write_empty_artifacts
from worldline.protected_startup import canonical, digest
from worldline.root_worker_codec import archive, restore_archive

class CustodyV2SQLCaptureControls(unittest.TestCase):
    def fixture(self, root):
        key = b'fixture'; descriptor = canonical({'installation_id': 'fixture'})
        plan = canonical({'schema': 'worldline.protected-root-worker-plan-v1', 'installation': 'fixture',
                          'handoff_genesis': str(root/'genesis.json'), 'handoff_journal': str(root/'custody.sqlite')})
        genesis = canonical({'schema': 'worldline.owner-provisioned-root-custody-v2', 'installation': 'fixture',
            'startup_descriptor_sha256': digest(descriptor), 'owner_plan_sha256': digest(plan),
            'issuer_key_sha256': digest(key), 'initial_event': None, 'prior_custody': None})
        fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
        try:
            write_empty_artifacts(ExplicitInputs(descriptor, plan, genesis, key), Target(fd, 'custody.sqlite'),
                                  Target(fd, 'genesis.json'), Target(fd, 'custody.sqlite.lock'))
        finally: os.close(fd)
        return root/'custody.sqlite'
    def test_empty_origin_null_fk_and_exact_whole_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.fixture(Path(tmp)); raw = _database(path)
            tables = {row['name']: row for row in raw['tables']}
            self.assertEqual(raw['foreign_keys'], ((1,),))
            self.assertEqual(raw['foreign_key_check'], ())
            self.assertEqual(set(tables), {'genesis', 'events', 'head', 'root_state', 'subject_state', 'alternatives', 'blobs'})
            self.assertIsNone(tables['head']['rows'][0][3])
            self.assertEqual(restore_archive(archive(raw)), raw)
    def test_consumer_captures_real_dangling_fk_not_authorization_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.fixture(Path(tmp)); db = sqlite3.connect(path)
            try:
                # Deliberately damaged authoritative-fixture row is observable
                # when a corrupting writer disabled FK enforcement. The loader
                # never replaces this raw violation with a copied success bit.
                db.execute('PRAGMA foreign_keys=OFF')
                db.execute("UPDATE head SET head_kind='EVENT',event_id=?,origin=NULL", ('0'*64,)); db.commit()
            finally: db.close()
            observed = _database(path)
            self.assertEqual(observed['foreign_keys'], ((1,),))
            self.assertTrue(observed['foreign_key_check'])
            self.assertEqual(observed['foreign_key_check'][0][0], 'head')
    def test_native_quantity_domain_not_sql_integer(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.fixture(Path(tmp)); db = sqlite3.connect(path)
            try:
                base = b'raw'; fields = ('1'*64, '2'*64, 1, 'op', 'ROOT', '', b'', 'PREPARED', 'FRONT', base, base, '3'*64)
                with self.assertRaises(sqlite3.IntegrityError):
                    db.execute('INSERT INTO events(event_id,previous,generation,operation,subject_kind,subject,subgeneration,kind,actor,record,base,mac) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', fields)
                fields = list(fields); fields[2] = b'\x01\x00'
                with self.assertRaises(sqlite3.IntegrityError):
                    db.execute('INSERT INTO events(event_id,previous,generation,operation,subject_kind,subject,subgeneration,kind,actor,record,base,mac) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', fields)
                fields[2] = b'\x01' + b'\x00'*4096 + b'\x01'
                db.execute('INSERT INTO events(event_id,previous,generation,operation,subject_kind,subject,subgeneration,kind,actor,record,base,mac) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', fields)
                db.commit()
                self.assertEqual(db.execute('SELECT generation FROM events').fetchone()[0], fields[2])
            finally: db.close()
    def test_caller_transaction_required_and_no_missing_database_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); absent = root/'missing.sqlite'
            with self.assertRaises(sqlite3.OperationalError): _database(absent)
            self.assertFalse(absent.exists())
            db = sqlite3.connect(':memory:')
            try:
                from worldline.protected_startup import StartupRefusal
                with self.assertRaises(StartupRefusal): _database_connection(db)
            finally: db.close()
if __name__ == '__main__': unittest.main()
