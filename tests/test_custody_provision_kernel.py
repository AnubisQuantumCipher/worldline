"""Real SQLite/value consumer controls; production operator custody is not mocked."""
import ctypes
import hashlib
import hmac
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from worldline.core import Core
from worldline.custody_provision_kernel import ProvisionInputs, invoke, _SYMBOLS
from worldline.custody_v2_provision_values import ExplicitInputs, Target, write_empty_artifacts
from worldline.custody_v2_provision_entry import PLAN_KEYS
from worldline.protected_startup import canonical, digest, exact_json
from worldline.root_worker_codec import archive, restore_archive
from worldline.root_worker_current_state import _database
from worldline.retained_v1_migration_capture import _OriginalLoaderContext

class NativeOfflineProvisionControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core()
        cls.functions = tuple(getattr(cls.core._lib, name) for name in _SYMBOLS)
    def fixture(self, root, kinds=('HISTORICAL_SETTLEMENT', 'FRONT_RECONSTRUCTION'), key=None):
        key = b'whole-key' * 10000 if key is None else key
        def plan(path, journal, genesis):
            value = {name: None for name in PLAN_KEYS}
            value.update(schema='worldline.protected-root-worker-plan-v1', installation='fixture',
                         startup_descriptor=str(path), handoff_journal=str(journal), handoff_genesis=str(genesis))
            return canonical(value)
        d1 = root / 'd1.json'; p1 = root / 'p1.json'; g1 = root / 'g1.json'; j1 = root / 'j1.sqlite'
        d2 = root / 'd2.json'; p2 = root / 'p2.json'; g2 = root / 'g2.json'; j2 = root / 'j2.sqlite'
        old_descriptor = canonical({'installation_id': 'fixture', 'paths': {'authority_root': str(root)}})
        old_plan = plan(d1, j1, g1)
        old_genesis_raw = canonical({'schema': 'worldline.owner-provisioned-root-custody-v1', 'installation': 'fixture',
                       'startup_descriptor_sha256': digest(old_descriptor), 'owner_plan_sha256': digest(old_plan),
                       'issuer_key_sha256': digest(key), 'initial_event': None})
        # A retained v1 journal holds the genesis its canonical file declares
        # (capture_retained_v1 loads exact_json(genesis_raw)); native
        # Genesis_Archive_Matches preserves that file order.
        old_genesis = exact_json(old_genesis_raw)
        for path, raw in ((d1, old_descriptor), (p1, old_plan), (g1, old_genesis_raw)):
            path.write_bytes(raw)
        db = sqlite3.connect(j1)
        db.executescript('CREATE TABLE genesis(name TEXT,value BLOB);'
                         'CREATE TABLE events(event_id TEXT,previous TEXT,operation TEXT,kind TEXT,record BLOB,mac TEXT);'
                         'CREATE TABLE head(name TEXT,event_id TEXT,mac TEXT);')
        db.execute('INSERT INTO genesis VALUES(?,?)', ('owner-genesis', archive(old_genesis)))
        mac = lambda value: hmac.new(key, b'worldline.protected-root-custody-v1\0' + archive(value), hashlib.sha256).hexdigest()
        previous = digest(archive(old_genesis))
        for index, kind in enumerate(kinds):
            operation = 'operation-' + str(index) if kind != 'UNKNOWN' else 'operation-0'
            record = {'actual_fixture': index}
            base = {'previous': previous, 'operation': operation, 'kind': kind, 'record': record}
            event_id = digest(archive(base))
            db.execute('INSERT INTO events VALUES(?,?,?,?,?,?)',
                       (event_id, previous, operation, kind, archive(record), mac(base)))
            previous = event_id
        db.execute('INSERT INTO head VALUES(?,?,?)', ('current', previous, mac({'head': previous, 'genesis': old_genesis})))
        db.commit(); db.close()
        database = _database(j1, _OriginalLoaderContext(old_genesis, key))
        prior = {'descriptor_path': str(d1), 'descriptor_sha256': digest(d1.read_bytes()),
                 'plan_path': str(p1), 'plan_sha256': digest(p1.read_bytes()),
                 'genesis_path': str(g1), 'genesis_sha256': digest(g1.read_bytes()),
                 'journal_path': str(j1), 'journal_sha256': digest(j1.read_bytes()),
                 'head_event': previous, 'issuer_key_sha256': digest(key)}
        new_descriptor = canonical({'installation_id': 'fixture', 'root_worker': {'owner_plan': str(p2)}})
        new_plan = plan(d2, j2, g2)
        new_genesis = {'schema': 'worldline.owner-provisioned-root-custody-v2', 'installation': 'fixture',
                       'startup_descriptor_sha256': digest(new_descriptor), 'owner_plan_sha256': digest(new_plan),
                       'issuer_key_sha256': digest(key), 'initial_event': None, 'prior_custody': prior}
        return {'key': key, 'new': [(new_descriptor, str(d2)), (new_plan, str(p2)), (canonical(new_genesis), str(g2))],
                'journal': str(j2), 'prior': prior, 'old': [(d1.read_bytes(), str(d1), prior['descriptor_sha256']),
                  (p1.read_bytes(), str(p1), prior['plan_sha256']), (g1.read_bytes(), str(g1), prior['genesis_sha256']),
                  (j1.read_bytes(), str(j1), prior['journal_sha256']), (key, str(root/'key.bin'), digest(key))],
                'database': database, 'old_genesis': old_genesis, 'head': previous}
    def pack(self, fixture, mode='MIGRATE'):
        arena = bytearray(); spans = []
        def put(value): spans.append((len(arena)+1, len(value))); arena.extend(value)
        def text(value): put(value.encode('utf-8'))
        for raw, path in fixture['new']: put(raw); put(archive(__import__('json').loads(raw))); text(path)
        text(fixture['journal']); put(fixture['key']); text(mode)
        counts = (0, 0, 0)
        if mode == 'NEW':
            for _ in range(25): put(b'')
        else:
            for raw, path, expected in fixture['old']: put(raw); text(path); text(path); text(expected)
            put(archive(__import__('json').loads(fixture['old'][0][0])))
            put(archive(__import__('json').loads(fixture['old'][1][0])))
            put(archive(fixture['old_genesis']))
            put(archive({'head': fixture['head'], 'genesis': fixture['old_genesis']})); text(fixture['head'])
            tables = {table['name']: table['rows'] for table in fixture['database']['tables']}
            counts = tuple(len(tables[name]) for name in ('genesis', 'events', 'head'))
            for _, name, raw in tables['genesis']: text(name); put(raw)
            for _, event_id, previous, operation, kind, raw, mac in tables['events']:
                for word in (event_id, previous, operation, kind): text(word)
                put(raw); text(mac); put(archive({'previous': previous, 'operation': operation,
                                                'kind': kind, 'record': restore_archive(raw)}))
            for _, name, event_id, mac in tables['head']: text(name); text(event_id); text(mac)
        return ProvisionInputs(bytes(arena), tuple(spans), *counts)
    def test_closed_sqlite_v1_native_migration_new_paths_old_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); fixture = self.fixture(root)
            before = {path: Path(path).read_bytes() for _, path, _ in fixture['old'][:-1]}
            self.assertEqual(invoke(self.functions, self.pack(fixture)).state, 'Closed_V1_Migration_Eligible')
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            try:
                inputs = ExplicitInputs(*(raw for raw, _ in fixture['new']), fixture['key'])
                receipt = write_empty_artifacts(inputs, Target(fd, 'j2.sqlite'), Target(fd, 'g2.json'), Target(fd, 'j2.sqlite.lock'))
                self.assertEqual(receipt.genesis_sha256, digest(inputs.genesis_raw))
                db = sqlite3.connect(root/'j2.sqlite')
                try:
                    db.execute('PRAGMA foreign_keys=ON')
                    self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
                    self.assertEqual(db.execute('SELECT head_kind,event_id FROM head').fetchall(), [('ORIGIN', None)])
                finally: db.close()
            finally: os.close(fd)
            self.assertEqual(before, {path: Path(path).read_bytes() for path in before})
    def test_unknown_later_operation_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.fixture(Path(tmp), ('HISTORICAL_SETTLEMENT', 'FRONT_RECONSTRUCTION', 'UNKNOWN'))
            self.assertEqual(invoke(self.functions, self.pack(fixture)).state, 'Operation_Not_Closed')
    def test_open_operation_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.fixture(Path(tmp), ('PREPARED',))
            self.assertEqual(invoke(self.functions, self.pack(fixture)).state, 'Operation_Not_Closed')
    def test_retained_descriptor_digest_mutation_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.fixture(Path(tmp)); raw, path, sha = fixture['old'][0]
            fixture['old'][0] = (raw + b'\n', path, sha)
            self.assertEqual(invoke(self.functions, self.pack(fixture)).state, 'Prior_Context_Refused')
    def test_selected_key_rotation_refuses_without_remac(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.fixture(Path(tmp)); fixture['key'] = b'rotated'
            self.assertEqual(invoke(self.functions, self.pack(fixture)).state, 'Selected_Context_Refused')
    def test_explicit_new_mode_null_prior_is_not_missing_journal_inference(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.fixture(Path(tmp)); raw, path = fixture['new'][2]
            value = __import__('json').loads(raw); value['prior_custody'] = None
            fixture['new'][2] = (canonical(value), path)
            self.assertEqual(invoke(self.functions, self.pack(fixture, 'NEW')).state, 'New_Origin_Eligible')
    def test_new_mode_cannot_discard_retained_prior(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.fixture(Path(tmp))
            self.assertEqual(invoke(self.functions, self.pack(fixture, 'NEW')).state, 'Prior_Context_Refused')
    def test_empty_key_remains_original_hmac_domain(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.fixture(Path(tmp), key=b'')
            self.assertEqual(invoke(self.functions, self.pack(fixture)).state, 'Closed_V1_Migration_Eligible')
    def test_null_zero_arena_retains_semantic_refusal_not_transport_domain_cap(self):
        from worldline.retained_chain_kernel import _Span
        from worldline.custody_provision_kernel import _Output
        # Configure the actual function/layout first, then exercise the original
        # zero-count native memory case with real allocated metadata/output.
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self.fixture(Path(tmp))
            invoke(self.functions, self.pack(fixture))
        spans = (_Span * 37)(*(_Span(1, 0) for _ in range(37)))
        output = _Output()
        code = self.functions[2](None, 0, spans, len(spans), 0, 0, 0,
                                 ctypes.byref(output), ctypes.sizeof(output))
        self.assertEqual(code, 0)
        self.assertEqual(output.status, 0)
        self.assertEqual(output.failing_row, 0)
if __name__ == '__main__': unittest.main()
