"""Actual qualified isolated startup controls. Source-only; execution UNRUN.

Requires separate original owner-provisioned disposable fixtures under the
selected early source loader. No fixture provisioning, mocks, skips, or copied
native Ready/LIVE outputs are supplied by this control module.
"""
import os
from pathlib import Path
import sqlite3
import sys
import unittest

CONTROL_CASES = {
    'FRONTIER': ('test_native_complete_startup_replaces_frontier',
                 'WORLDLINE_PROTECTED_BOOTSTRAP_CONTROL_COMPOSED_NATIVE_PROOF'),
    'FULL_ROSTER': ('test_no_write_capture_preserves_complete_scoped_history',
                    'WORLDLINE_CUSTODY_STARTUP_CONTROL_FULL_ROSTER'),
    'STABLE': ('test_stable_full_operation_redecision_has_no_write_effect',
               'WORLDLINE_CUSTODY_STARTUP_CONTROL_STABLE'),
    'SURVIVING_NEXT_INTENT': ('test_surviving_next_intent_has_native_redecision_and_readback',
                             'WORLDLINE_CUSTODY_STARTUP_CONTROL_SURVIVING_NEXT_INTENT'),
    'RETAIN_UNKNOWN': ('test_unknown_retains_accounting_without_fresh_front',
                       'WORLDLINE_CUSTODY_STARTUP_CONTROL_RETAIN_UNKNOWN'),
}


def assert_complete_no_write_capture(test, resources):
    """Also callable by the real LIVE/received-descriptor outer campaign."""
    from worldline.custody_startup_capture import capture
    from worldline.root_worker_codec import raw_restore_archive
    from worldline.root_worker_current_state import _database
    from worldline.protected_scoped_resource_runtime import ProtectedScopedResourcePrincipal
    test.assertIs(type(resources), ProtectedScopedResourcePrincipal)
    with resources.gate.mutex, resources.order:
        paths = (resources.scoped_service.db_path, resources.observations.path,
                 resources.journal.path)
        before = tuple(_database(path) for path in paths)
        original = resources.current_snapshot()
        captured = capture(resources)
        packet = captured['material']
        test.assertEqual(packet.rows, original.rows)
        test.assertEqual(packet.history, original.history)
        test.assertEqual(packet.before, original.state)
        test.assertEqual(packet.proposed_rows, original.rows)
        test.assertEqual(packet.proposed_history, original.history)
        test.assertEqual(len(packet.rows), len(packet.facts))
        test.assertEqual(len(packet.rows), len(packet.observed))
        test.assertEqual(len(packet.rows), len(captured['physical']))
        test.assertEqual(len(packet.rows), len(captured['classification']))
        test.assertEqual(len(packet.rows), len(captured['classification_material']))
        complete = captured['complete_scoped_capture']
        test.assertEqual(complete['packet'], packet)
        test.assertEqual(complete['scoped_projection'], resources.scoped_projection)
        test.assertEqual(len(complete['rows']), len(packet.rows))
        decoded = raw_restore_archive(captured['capture'])
        test.assertEqual(decoded['observation'], captured['observation'])
        test.assertEqual(decoded['provenance'], complete)
        test.assertEqual(decoded['packet'], packet)
        test.assertEqual(decoded['projection'], resources.scoped_projection)
        test.assertEqual(decoded['owner'], captured['owner_state'])
        for full, row, fact, observed, raw, native, material in zip(
                complete['rows'], packet.rows, packet.facts, packet.observed,
                captured['physical'], captured['classification'], captured['classification_material']):
            test.assertEqual(full, {'row': row, 'physical': fact, 'observed': observed,
                'source': raw, 'native_classification': native, 'classification_material': material})
        for row, fact, observed, raw, native, material in zip(
                packet.rows, packet.facts, packet.observed, captured['physical'],
                captured['classification'], captured['classification_material']):
            test.assertEqual(row.bound, fact.retained)
            test.assertEqual(row.bound, observed.bound)
            test.assertEqual(raw['reservation'], row.bound.reservation.hex())
            test.assertEqual(material.rows, packet.rows)
            test.assertEqual(material.facts, packet.facts)
            test.assertEqual(resources.scoped_kernel.classify(material), native)
            test.assertEqual(native.status, observed.observed)
            test.assertTrue(all(item.observed == 'UNKNOWN' for item in material.observed))
        test.assertEqual(resources.scoped_kernel.validate(packet), captured['observation'])
        test.assertEqual(tuple(_database(path) for path in paths), before)
        test.assertEqual(resources.current_snapshot(), original)
        return captured


def assert_native_installation_correspondence(test, lease):
    """Real captured owner input, original native C ABI, full retained operands.

    No fabricated owner/enrollment or physical installation mutation is used.
    Main's original private framed stdout retains each complete native operand.
    """
    import copy
    import json
    from worldline.startup_admission_kernel import decide_owner
    core = lease._owner_admission_core()
    for name, journal in lease.genesis['journals'].items():
        roster = lease._owner_admission_roster(name, journal['initial_envelope'])
        baseline = decide_owner(lease, core, name, roster)
        print('STARTUP_INSTALLATION_NATIVE_CONTROL ' + json.dumps({
            'control': 'actual-complete-scoped-owner-baseline', 'name': name,
            'input_hex': baseline.envelope.hex(), 'status': baseline.status,
            'position': baseline.position}, sort_keys=True))
        test.assertEqual(baseline.status, 1, 'actual consumed original owner admission required')
        runtime = roster['current']['installation']['runtime']
        test.assertIn('resource_scoped_producer', runtime, 'original FRONTIER is genuinely scoped')
        inventory = roster['startup_admission']['installation_inventory']
        helper = inventory['resource_scoped_producer']['config']['helper']
        def refused(control, change):
            altered = copy.deepcopy(roster)
            change(altered)
            observed = decide_owner(lease, core, name, altered)
            print('STARTUP_INSTALLATION_NATIVE_CONTROL ' + json.dumps({
                'control': control, 'name': name, 'input_hex': observed.envelope.hex(),
                'status': observed.status, 'position': observed.position}, sort_keys=True))
            test.assertEqual(observed.status, 0, control)
        def executable_record(value, column):
            for epoch in ('before', 'current'):
                source = value[epoch]['source']
                lines = bytes.fromhex(source['envelope_bytes_hex']).splitlines(keepends=True)
                found = 0
                for index, line in enumerate(lines):
                    words = line.rstrip(b'\n').split(b'\t')
                    if len(words) == 5 and words[0:2] == [b'FILE', b'EXECUTABLE'] and bytes.fromhex(words[2].decode()).decode() == helper:
                        found += 1
                        if column == 'bytes': words[4] += b'00'
                        else: words[3] = format(int(words[3], 8) & ~0o111, 'o').encode('ascii')
                        lines[index] = b'\t'.join(words) + b'\n'
                test.assertEqual(found, 1, 'one genuine selected full-content EXECUTABLE record required')
                source['envelope_bytes_hex'] = b''.join(lines).hex()
        refused('executable-envelope-bytes-differ-from-installed-full-content',
                lambda value: executable_record(value, 'bytes'))
        refused('executable-envelope-mode-lacks-real-execute-eligibility',
                lambda value: executable_record(value, 'mode'))
        def remove_installed_helper(value):
            selected = value['startup_admission']['installation_inventory']
            found = [row for row in selected['files'] if row['path'] == helper]
            found += [row for tree in selected['trees'] for row in tree['entries'] if row['path'] == helper]
            test.assertTrue(found, 'actual installed selected native helper required')
            selected['files'] = [row for row in selected['files'] if row['path'] != helper]
            for tree in selected['trees']:
                tree['entries'] = [row for row in tree['entries'] if row['path'] != helper]
        refused('selected-v3-executable-outside-installed-inventory', remove_installed_helper)
        refused('scoped-producer-full-raw-mismatch', lambda value:
                value['startup_admission']['installation_inventory']['resource_scoped_producer'].__setitem__('raw', b''))
        refused('scoped-producer-selected-path-mismatch', lambda value:
                value['startup_admission']['installation_inventory']['resource_scoped_producer'].__setitem__('path', helper))
        refused('scoped-producer-v3-helper-mismatch', lambda value:
                value['startup_admission']['installation_inventory']['resource_scoped_producer']['config'].__setitem__('helper', runtime['tools']['systemctl']))
        refused('scoped-ten-runtime-shape-has-an-extra-field', lambda value:
                value['current']['installation']['runtime'].__setitem__('unexpected', None))


class CustodyStartupNativeControls(unittest.TestCase):
    def descriptor(self, case):
        self.assertEqual(os.geteuid(), 0, 'actual admitted isolated root control required')
        self.assertTrue(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode)
        source = sys.modules.get('_worldline_approved_source_loader')
        self.assertIsNotNone(source, 'qualified actual early source lease required')
        self.assertIs(type(source.current()), source.ApprovedSourceLease)
        source.current().check()
        value = os.environ.get(CONTROL_CASES[case][1])
        self.assertIsNotNone(value, 'separate genuine disposable original fixture required')
        return Path(value)

    def construct(self, case):
        from worldline.protected_startup import StartupLease
        lease = StartupLease(self.descriptor(case))
        try:
            recovery = lease.construct()
        except BaseException:
            lease.close()
            raise
        self.assertIs(recovery, lease.principal)
        self.addCleanup(lease.close)
        return lease, lease.canonical_operation_principal

    def test_native_complete_startup_replaces_frontier(self):
        from worldline.protected_operations import CanonicalOperationPrincipal
        from worldline.protected_scoped_resource_runtime import ProtectedScopedResourcePrincipal
        lease, principal = self.construct('FRONTIER')
        self.assertIs(type(principal), CanonicalOperationPrincipal)
        self.assertIs(type(lease.resource_principal), ProtectedScopedResourcePrincipal)
        self.assertIs(principal.resources, lease.resource_principal)
        self.assertIs(principal.controller, lease.controller)
        self.assertIs(principal.store, lease.store)
        self.assertIs(principal.recovery, lease.principal)
        self.assertEqual(lease.require_front_startup().state, 'FrontStartup')
        self.assertEqual(lease.controller._reconciled_at_start, [])
        self.assertIsNone(lease.controller._reconcile_error)
        self.assertEqual(lease.pending_journal_admissions, {})
        self.assertTrue(all(row[0] == 'CONSUMED' for row in
            lease.db.execute('SELECT state FROM journal_intents ORDER BY name')))
        lease.intact()
        profiles = lease.capture_admission_profiles()
        self.assertEqual({profile['name'] for profile in profiles}, set(lease.genesis['journals']))
        for profile in profiles:
            self.assertEqual(profile['issuer_intent']['path'], str(lease.gate.issuer.state / 'intent.json'))
            self.assertEqual(profile['issuer_intent']['presence'], 'ABSENT')
            self.assertIsNone(profile['issuer_intent']['raw'])
            self.assertEqual(profile['issuer_head_temporaries'], [])
            self.assertEqual(profile['store_initial_snapshot'], lease.store_initial_snapshot)
            self.assertEqual(profile['store_initial_snapshot_raw'], lease.store_initial_snapshot_raw)
            self.assertIs(type(profile['installation_inventory']), dict)
            self.assertEqual(len(profile['installation_inventory']['trees']), len(lease.spec['trees']))
            self.assertEqual(len(profile['installation_inventory']['files']), len(lease.spec['files']))
            self.assertEqual(profile['gate_config_raw'], profile['gate_config_source']['raw'])
            self.assertIs(type(profile['gate_journal_source']['raw']), bytes)
            self.assertIs(type(profile['issuer_head_source']['raw']), bytes)
            self.assertIs(type(profile['store_source']['raw']), bytes)
            self.assertIsNone(profile['gate_journal_source']['error'])
            self.assertIsNone(profile['issuer_head_source']['error'])
            self.assertIsNone(profile['store_source']['error'])
        assert_native_installation_correspondence(self, lease)

    def test_no_write_capture_preserves_complete_scoped_history(self):
        lease, principal = self.construct('FULL_ROSTER')
        self.assertTrue(principal.resources.current_snapshot().rows,
                        'nonempty full original row fixture required')
        captured = assert_complete_no_write_capture(self, principal.resources)
        self.assertEqual(captured['source'], lease.source_lease.check())

    def test_stable_full_operation_redecision_has_no_write_effect(self):
        from worldline.protected_startup import private_bytes
        from worldline.root_worker_current_state import _database
        lease, principal = self.construct('STABLE')
        before_raw = private_bytes(principal.journal.path)
        before_head = _database(Path(principal.policy['head_database']))
        result = principal.journal.load()
        self.assertEqual(result.state, 'Stable')
        self.assertTrue(result.envelope)
        self.assertEqual(private_bytes(principal.journal.path), before_raw)
        self.assertEqual(_database(Path(principal.policy['head_database'])), before_head)
        lease.intact()

    def test_surviving_next_intent_has_native_redecision_and_readback(self):
        from worldline.protected_startup import StartupLease, private_bytes, digest
        descriptor = self.descriptor('SURVIVING_NEXT_INTENT')
        lease = StartupLease(descriptor)
        self.addCleanup(lease.close)
        state = Path(lease.spec['paths']['authority_root']) / 'authority/issuer/state'
        head_path = state / 'worldline-operation-head.sqlite'
        journal_path = state / 'worldline-operations.json'
        db = sqlite3.connect(head_path.as_uri() + '?mode=ro', uri=True)
        try:
            before = db.execute('SELECT head,state,prior_envelope,next_envelope '
                'FROM canonical_operation_head WHERE name=?', ('worldline-operations',)).fetchone()
        finally:
            db.close()
        self.assertIsNotNone(before)
        self.assertEqual(before[1], 'INTENT')
        self.assertEqual(before[0], digest(before[2]))
        original_raw = private_bytes(journal_path)
        self.assertEqual(original_raw, before[3])
        original_identity = (journal_path.stat().st_dev, journal_path.stat().st_ino)
        lease.construct()
        principal = lease.canonical_operation_principal
        self.assertEqual(principal.journal.startup_redecision.state, 'Finalize_Surviving_Next')
        self.assertTrue(principal.journal.startup_redecision.envelope)
        self.assertEqual(principal.journal.startup_readback.state, 'Stable')
        self.assertEqual(private_bytes(journal_path), original_raw)
        self.assertEqual((journal_path.stat().st_dev, journal_path.stat().st_ino), original_identity)
        row = principal.journal.head_row()
        self.assertEqual(row[2:6], (digest(original_raw), 'STABLE', None, None))
        lease.intact()

    def test_unknown_retains_accounting_without_fresh_front(self):
        from worldline.protected_startup import StartupRefusal
        from worldline.root_worker_current_state import _database
        lease, principal = self.construct('RETAIN_UNKNOWN')
        before = _database(principal.resources.scoped_service.db_path)
        action = lease.recovery_startup_action(principal)
        self.assertEqual(action.state, 'RetainUnknown')
        self.assertIsNone(lease.controller._reconciled_at_start)
        self.assertEqual(lease.controller._reconcile_error, 'PROTECTED_STARTUP_NATIVE_RetainUnknown')
        with self.assertRaisesRegex(StartupRefusal, 'STARTUP_NATIVE_FRESH_FRONT_RetainUnknown'):
            lease.require_front_startup()
        self.assertEqual(_database(principal.resources.scoped_service.db_path), before)
        self.assertEqual(lease.recovery_startup_action(principal).state, 'RetainUnknown')
        lease.intact()


if __name__ == '__main__':
    unittest.main()
