"""Real SQLite lower-producer controls, not a protected-owner/startup claim."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from worldline.root_worker_current_state import _database

class CustodyForeignKeyCaptureControls(unittest.TestCase):
    def make_database(self, root, dangling=False):
        path = root / 'custody.sqlite'
        db = sqlite3.connect(path)
        try:
            db.execute('PRAGMA foreign_keys=ON')
            db.execute('CREATE TABLE events (event_id TEXT PRIMARY KEY)')
            db.execute('CREATE TABLE head (name TEXT PRIMARY KEY, event_id TEXT REFERENCES events(event_id), origin BLOB)')
            db.execute('INSERT INTO events VALUES (?)', ('retained-event',))
            db.execute('INSERT INTO head VALUES (?,?,?)', ('origin', None, b''))
            db.execute('INSERT INTO head VALUES (?,?,?)', ('current', 'retained-event', None))
            db.commit()
            if dangling:
                db.execute('PRAGMA foreign_keys=OFF')
                db.execute('INSERT INTO head VALUES (?,?,?)', ('dangling', 'absent-event', None))
                db.commit()
        finally:
            db.close()
        return path

    def test_complete_fk_observation_preserves_null_and_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_database(Path(tmp))
            before = path.read_bytes()
            observed = _database(path)
            self.assertEqual(observed['foreign_keys'], ((1,),))
            self.assertEqual(observed['foreign_key_check'], ())
            tables = {table['name']: table for table in observed['tables']}
            self.assertEqual(tables['events']['foreign_key_list'], ())
            self.assertEqual(tables['head']['foreign_key_list'],
                ((0, 0, 'events', 'event_id', 'event_id', 'NO ACTION', 'NO ACTION', 'NONE'),))
            self.assertEqual(tuple(row[1:] for row in tables['head']['rows']),
                (('origin', None, b''), ('current', 'retained-event', None)))
            self.assertEqual(path.read_bytes(), before)

    def test_dangling_fk_retained_for_native_refusal_not_filtered(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_database(Path(tmp), dangling=True)
            before = path.read_bytes()
            observed = _database(path)
            tables = {table['name']: table for table in observed['tables']}
            dangling = next(row for row in tables['head']['rows'] if row[1] == 'dangling')
            self.assertEqual(observed['foreign_keys'], ((1,),))
            self.assertEqual(observed['foreign_key_check'], (('head', dangling[0], 'events', 0),))
            self.assertIn(dangling, tables['head']['rows'])
            self.assertEqual(path.read_bytes(), before)

    def test_real_journal_hook_receives_same_read_transaction(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_database(Path(tmp))
            class Observer:
                def _load(self, db):
                    self.in_transaction = db.in_transaction
                    self.fk = tuple(db.execute('PRAGMA foreign_keys'))
                    self.rows = tuple(db.execute('SELECT rowid,* FROM head ORDER BY rowid'))
                    return (), 'fixture-observation-only'
            hook = Observer()
            observed = _database(path, hook)
            tables = {table['name']: table for table in observed['tables']}
            self.assertTrue(hook.in_transaction)
            self.assertEqual(hook.fk, observed['foreign_keys'])
            self.assertEqual(hook.rows, tables['head']['rows'])
            # The hook is instrumented, not HMAC/protected-producer evidence.
            self.assertEqual(observed['authenticated_root_events'], ())

if __name__ == '__main__':
    unittest.main()
