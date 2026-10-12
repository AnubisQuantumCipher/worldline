"""Real provisioned lab controls, retained as source and NOT run in preparation.

The fixture is an operator-provisioned disposable root-owned installation, not a
mock peer/key/lock/authority Boolean. These controls require that exact fixture;
absence refuses and never skips/promotes a synthetic positive.
"""
import os,pathlib,socket,sqlite3,unittest
from worldline.protected_startup import StartupLease,StartupRefusal,IntentDispatcher,canonical,private_bytes

class ProtectedStartupControls(unittest.TestCase):
    def descriptor(self,name):
        value=os.environ.get('WORLDLINE_PROTECTED_BOOTSTRAP_CONTROL_'+name)
        self.assertIsNotNone(value,'a separately owner-provisioned disposable control is required')
        return pathlib.Path(value)

    def test_second_lease_refuses_original_store_lock(self):
        lease=StartupLease(self.descriptor('EMPTY_GENESIS'))
        try:
            with self.assertRaises(BlockingIOError):StartupLease(lease.descriptor_path)
            lease.intact()
        finally:lease.close()

    def test_missing_prior_lock_does_not_regenerate(self):
        # Owner prepared a separate intact descriptor whose required original
        # store lock was intentionally absent; the runtime may not create it.
        descriptor=self.descriptor('MISSING_LOCK')
        import json
        spec=json.loads(private_bytes(descriptor));path=pathlib.Path(spec['paths']['state'])/'worldline-store.lock'
        self.assertFalse(os.path.lexists(path))
        with self.assertRaises(FileNotFoundError):StartupLease(descriptor)
        self.assertFalse(os.path.lexists(path))

    def test_legacy_endpoint_refuses_without_removing_it(self):
        descriptor=self.descriptor('LEGACY_ENDPOINT')
        import json
        spec=json.loads(private_bytes(descriptor));path=pathlib.Path(spec['paths']['runtime'])/'worldlined.sock'
        before=path.lstat()
        with self.assertRaisesRegex(StartupRefusal,'STARTUP_LEGACY_ENDPOINT_PRESENT'):StartupLease(descriptor)
        after=path.lstat();self.assertEqual((before.st_dev,before.st_ino),(after.st_dev,after.st_ino))

    def test_missing_consumed_journal_refuses_exact_existing_ledger(self):
        lease=StartupLease(self.descriptor('CONSUMED_MISSING'))
        try:
            # Actual installed Gate construction under the original held lease,
            # with existing protected issuer keys and native authority source.
            from intent_gate import Gate
            lease.gate=Gate(pathlib.Path(lease.spec['paths']['authority_root'])/'authority/gate/config.json')
            record=lease.genesis['journals']['recovery-full-journal'];path=pathlib.Path(record['path'])
            before=lease.db.execute('SELECT * FROM journal_history ORDER BY ordinal').fetchall()
            self.assertFalse(os.path.lexists(path))
            with self.assertRaisesRegex(StartupRefusal,'STARTUP_CONSUMED_JOURNAL_MISSING'):
                lease.open_journal(lease.gate,'recovery-full-journal',path,record['initial_envelope'])
            self.assertFalse(os.path.lexists(path))
            self.assertEqual(before,lease.db.execute('SELECT * FROM journal_history ORDER BY ordinal').fetchall())
        finally:lease.close()

    def test_pending_missing_intent_refuses_without_recreation(self):
        lease=StartupLease(self.descriptor('INTENT_MISSING'))
        try:
            from intent_gate import Gate
            lease.gate=Gate(pathlib.Path(lease.spec['paths']['authority_root'])/'authority/gate/config.json')
            record=lease.genesis['journals']['full-use-reservations'];path=pathlib.Path(record['path'])
            with self.assertRaisesRegex(StartupRefusal,'STARTUP_GENESIS_INTENT_MISSING_FILE_REVIEW_REQUIRED'):
                lease.open_journal(lease.gate,'full-use-reservations',path,record['initial_envelope'])
            self.assertFalse(os.path.lexists(path))
        finally:lease.close()

    def test_owner_genesis_creates_exact_bytes_once(self):
        lease=StartupLease(self.descriptor('EMPTY_GENESIS'))
        try:
            from intent_gate import Gate
            lease.gate=Gate(pathlib.Path(lease.spec['paths']['authority_root'])/'authority/gate/config.json')
            for name,record in lease.genesis['journals'].items():
                path=pathlib.Path(record['path']);self.assertFalse(os.path.lexists(path))
                lease.open_journal(lease.gate,name,path,record['initial_envelope'])
                self.assertEqual(private_bytes(path),canonical(record['initial_envelope'])+b'\n')
                history=lease.db.execute('SELECT * FROM journal_history ORDER BY ordinal').fetchall()
                lease.open_journal(lease.gate,name,path,record['initial_envelope'])
                self.assertEqual(history,lease.db.execute('SELECT * FROM journal_history ORDER BY ordinal').fetchall())
        finally:lease.close()

    def test_exact_present_intent_finishes_without_file_replacement(self):
        lease=StartupLease(self.descriptor('INTENT_PRESENT'))
        try:
            from intent_gate import Gate
            lease.gate=Gate(pathlib.Path(lease.spec['paths']['authority_root'])/'authority/gate/config.json')
            record=lease.genesis['journals']['recovery-full-journal'];path=pathlib.Path(record['path'])
            before=path.stat();raw=private_bytes(path)
            self.assertEqual(raw,canonical(record['initial_envelope'])+b'\n')
            lease.open_journal(lease.gate,'recovery-full-journal',path,record['initial_envelope'])
            after=path.stat()
            self.assertEqual((before.st_dev,before.st_ino),(after.st_dev,after.st_ino))
            self.assertEqual(raw,private_bytes(path))
            self.assertEqual(lease.db.execute('SELECT state FROM journal_intents WHERE name=?',('recovery-full-journal',)).fetchone(),('CONSUMED',))
        finally:lease.close()

    def test_current_source_frontier_names_full_ledger_startup_gap(self):
        lease=StartupLease(self.descriptor('COMPOSED_NATIVE_PROOF'))
        try:
            with self.assertRaisesRegex(StartupRefusal,'PROTECTED_FULL_LEDGER_STARTUP_RECONCILER_UNAVAILABLE'):
                lease.construct()
            self.assertIsNotNone(lease.gate)
            self.assertIsNotNone(lease.store)
            lease.intact()
            self.assertIsNone(lease.controller)
        finally:lease.close()

if __name__=='__main__':unittest.main()
