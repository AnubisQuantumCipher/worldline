"""Genuine approved-import controls for a separately provisioned root envelope.

UNRUN. Invoke through the early helper under the original outer admission.
No temporary unprotected layout, mocked loader/native authority or skipped case.
"""
import sys
_approved=sys.modules.get('_worldline_approved_source_loader')
if _approved is None:raise SystemExit('APPROVED_PROBE_EARLY_LEASE_REQUIRED')
lease=_approved.current();lease.check()
import argparse,json,unittest

class ApprovedImportControls(unittest.TestCase):
    def test_real_delayed_standard_source_and_extension_imports(self):
        import sqlite3
        import ctypes.util
        lease.check()
        self.assertTrue(any(e.get('module')=='sqlite3' and e['kind']=='SOURCE_COMPILED_BEFORE_EXEC' and e['cache_used'] is False for e in lease.events))
        self.assertTrue(any(e.get('module')=='_sqlite3' and e['kind']=='EXTENSION_BEFORE_CREATE' for e in lease.events))
    def test_control_time_import_is_checked_before_execution(self):
        def actual_late_import():
            import worldline.linux.systemd
        actual_late_import();lease.check()
        self.assertTrue(any(e.get('module')=='worldline.linux.systemd' and e['kind']=='SOURCE_COMPILED_BEFORE_EXEC' and e['cache_used'] is False for e in lease.events))
    def test_unbound_source_refuses_before_execution(self):
        # Owner-provisioned benign probe file exists on an approved directory,
        # but its source is deliberately not in this negative allowlist.
        with self.assertRaisesRegex(_approved.Refusal,'APPROVED_FILE_UNBOUND'):
            __import__('_worldline_unapproved_import_probe')
        self.assertNotIn('_worldline_unapproved_import_probe',sys.modules)
    def test_custom_finder_refuses_before_it_can_run(self):
        class Counterfeit:
            def find_spec(self,*args,**kwargs):raise AssertionError('unapproved executable finder ran')
        original=list(sys.meta_path)
        try:
            sys.meta_path.insert(0,Counterfeit())
            with self.assertRaisesRegex(_approved.Refusal,'APPROVED_IMPORT_HOOKS_CHANGED'):
                __import__('_worldline_unapproved_import_probe')
        finally:sys.meta_path[:]=original
        lease.check()
    def test_initial_candidate_cache_faithfulness_and_refusal(self):
        # Actual complete cache specimens are checked, never executed as code.
        source=lease.file(fixture['source'],('SOURCE',))
        self.assertTrue(lease._cache_faithful(fixture['faithful_cache'],fixture['source'],source)['faithful_to_complete_source'])
        with self.assertRaisesRegex(_approved.Refusal,'APPROVED_INITIAL_CACHE_NOT_FAITHFUL'):
            lease._cache_faithful(fixture['unfaithful_cache'],fixture['source'],source)
        lease.check()

def main():
    global fixture
    parser=argparse.ArgumentParser();parser.add_argument('--fixture',required=True);args=parser.parse_args()
    raw=lease.file(args.fixture,('DATA',));fixture=json.loads(raw)
    if type(fixture) is not dict or set(fixture)!={'source','faithful_cache','unfaithful_cache'}:raise _approved.Refusal('APPROVED_PROBE_COMPLETE_FIXTURE_REQUIRED')
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ApprovedImportControls)
    expected=tuple(name for name in ApprovedImportControls.__dict__ if name.startswith('test_'))
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(suite)
    closure=lease.check()
    passed=result.wasSuccessful() and result.testsRun==len(expected) and not result.skipped and not result.expectedFailures and not result.unexpectedSuccesses
    print(json.dumps({'schema':'worldline.approved-import-probe-result-v1','status':'PASS' if passed else 'FAIL','testsRun':result.testsRun,'methods':expected,'complete_executed_code':closure,'initial_execution_custody':'OUTER_REQUIRED','authority_or_phase_acceptance':False},sort_keys=True))
    raise SystemExit(0 if passed else 1)
if __name__=='__main__':main()
