"""Additive genuine disposable startup controls, source-only and UNRUN.

Original controls are unchanged in their separate source. Actual durability/crash
and complete principal/caller acceptance require the additional outer campaign.
"""
import json,os,pathlib,socket,stat,struct,unittest
from worldline.protected_startup import StartupLease,StartupRefusal,canonical,private_bytes,kernel_identity

class AdditionalStartupControls(unittest.TestCase):
    def fixture(self):
        name=os.environ.get('WORLDLINE_PROTECTED_STARTUP_ADDITIVE_CASE')
        self.assertIsNotNone(name,'a genuine separately owner-provisioned control is required')
        fixture=json.loads(private_bytes(pathlib.Path(name)))
        self.assertEqual(set(fixture),{'startup_descriptor','journal_name','capability_member'})
        return fixture
    def lease_and_gate(self):
        fixture=self.fixture();lease=StartupLease(pathlib.Path(fixture['startup_descriptor']))
        try:
            from intent_gate import Gate
            lease.gate=Gate(pathlib.Path(lease.spec['paths']['authority_root'])/'authority/gate/config.json')
            return fixture,lease
        except BaseException:lease.close();raise
    def history(self,lease):return lease.db.execute('SELECT * FROM journal_history ORDER BY ordinal').fetchall()
    def selected_journal(self,fixture,lease):
        name=fixture['journal_name'];self.assertIn(name,lease.genesis['journals'])
        record=lease.genesis['journals'][name];return name,record,pathlib.Path(record['path'])
    def test_present_unused_consumes_without_replacing_exact_file(self):
        fixture,lease=self.lease_and_gate()
        try:
            name,record,path=self.selected_journal(fixture,lease)
            self.assertEqual(lease.db.execute('SELECT state FROM journal_intents WHERE name=?',(name,)).fetchone(),('UNUSED',))
            raw=private_bytes(path);before=path.lstat();self.assertEqual(raw,canonical(record['initial_envelope'])+b'\n')
            lease.open_journal(lease.gate,name,path,record['initial_envelope'])
            after=path.lstat();self.assertEqual((before.st_dev,before.st_ino),(after.st_dev,after.st_ino));self.assertEqual(raw,private_bytes(path))
            self.assertEqual(lease.db.execute('SELECT state FROM journal_intents WHERE name=?',(name,)).fetchone(),('CONSUMED',))
            retained=self.history(lease);lease.open_journal(lease.gate,name,path,record['initial_envelope']);self.assertEqual(retained,self.history(lease))
        finally:lease.close()
    def test_changed_present_intent_refuses_without_consumption(self):
        fixture,lease=self.lease_and_gate()
        try:
            name,record,path=self.selected_journal(fixture,lease)
            self.assertEqual(lease.db.execute('SELECT state FROM journal_intents WHERE name=?',(name,)).fetchone(),('INTENT',))
            raw=private_bytes(path);self.assertNotEqual(raw,canonical(record['initial_envelope'])+b'\n');history=self.history(lease)
            with self.assertRaisesRegex(StartupRefusal,'STARTUP_GENESIS_INTENT_BYTES_CHANGED'):
                lease.open_journal(lease.gate,name,path,record['initial_envelope'])
            self.assertEqual(raw,private_bytes(path));self.assertEqual(history,self.history(lease))
            self.assertEqual(lease.db.execute('SELECT state FROM journal_intents WHERE name=?',(name,)).fetchone(),('INTENT',))
        finally:lease.close()
    def unsafe_intent(self,kind):
        fixture,lease=self.lease_and_gate()
        try:
            name,record,path=self.selected_journal(fixture,lease);before=path.lstat();history=self.history(lease)
            self.assertEqual(lease.db.execute('SELECT state FROM journal_intents WHERE name=?',(name,)).fetchone(),('INTENT',))
            if kind=='SYMLINK':self.assertTrue(stat.S_ISLNK(before.st_mode))
            else:self.assertGreater(before.st_nlink,1)
            with self.assertRaises(StartupRefusal):lease.open_journal(lease.gate,name,path,record['initial_envelope'])
            after=path.lstat();self.assertEqual((before.st_dev,before.st_ino,before.st_mode,before.st_nlink),(after.st_dev,after.st_ino,after.st_mode,after.st_nlink))
            self.assertEqual(history,self.history(lease));self.assertEqual(lease.db.execute('SELECT state FROM journal_intents WHERE name=?',(name,)).fetchone(),('INTENT',))
        finally:lease.close()
    def test_symlink_intent_refuses_without_replacement(self):self.unsafe_intent('SYMLINK')
    def test_multilink_intent_refuses_without_consumption(self):self.unsafe_intent('MULTILINK')
    def layout(self,paths):
        selected=(paths.data,paths.state,paths.runtime,paths.config,paths.live,paths.generations,paths.worlds,paths.overlays,paths.events,paths.receipts,paths.transactions,paths.logs)
        records={}
        for root in selected:
            nodes=[root,*sorted(root.rglob('*'))] if root.is_dir() and not root.is_symlink() else [root]
            for path in nodes:
                if not os.path.lexists(path):records[str(path)]={'absent':True};continue
                info=path.lstat();record={'identity':(info.st_dev,info.st_ino),'mode':info.st_mode,'links':info.st_nlink}
                if stat.S_ISREG(info.st_mode):record['bytes']=path.read_bytes()
                if stat.S_ISLNK(info.st_mode):record['link']=os.readlink(path)
                records[str(path)]=record
        return records
    def capability_case(self,kind):
        fixture=self.fixture();lease=StartupLease(pathlib.Path(fixture['startup_descriptor']))
        try:
            from worldline.paths import WorldlinePaths
            from worldline.capabilities import CapabilityRegistry
            paths=WorldlinePaths(**{name:pathlib.Path(lease.spec['paths'][name]) for name in ('home','data','state','runtime','config')})
            before=self.layout(paths)
            if kind=='PRESENT':
                registry=CapabilityRegistry(paths,startup_lease=lease);self.assertIs(registry.startup_lease,lease);self.assertIsNone(registry._cached)
            else:
                member=pathlib.Path(fixture['capability_member'])
                if kind=='MISSING':self.assertFalse(os.path.lexists(member));exception=FileNotFoundError
                else:self.assertTrue(os.path.lexists(member));exception=StartupRefusal
                with self.assertRaises(exception):CapabilityRegistry(paths,startup_lease=lease)
            self.assertEqual(before,self.layout(paths));self.assertIsNone(lease.controller)
        finally:lease.close()
    def test_present_capability_layout_has_no_provisioning_effect(self):self.capability_case('PRESENT')
    def test_missing_capability_member_refuses_without_creation(self):self.capability_case('MISSING')
    def test_unsafe_capability_member_refuses_without_chmod(self):self.capability_case('UNSAFE')
    def test_configured_zero_uid_matches_actual_kernel_peer_without_authorizing(self):
        fixture=self.fixture();lease=StartupLease(pathlib.Path(fixture['startup_descriptor']))
        try:
            self.assertEqual(lease.spec['endpoint']['requester_uid'],0)
            left,right=socket.socketpair(socket.AF_UNIX,socket.SOCK_STREAM)
            try:
                wire=struct.Struct('@iII');raw=left.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,wire.size)
                pid,uid,gid=wire.unpack(raw)
                self.assertEqual(pid,os.getpid());self.assertEqual(uid,os.geteuid());self.assertEqual(gid,os.getegid())
                self.assertEqual(uid,lease.spec['endpoint']['requester_uid'])
                self.assertTrue(kernel_identity(uid));self.assertTrue(kernel_identity(gid))
                self.assertIsNone(lease.controller)
            finally:left.close();right.close()
        finally:lease.close()
