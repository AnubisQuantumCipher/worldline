"""Additive ordinary controls for the first Item 7 recovery repair.

These are finite real-library/real-store controls. They do not establish the
authenticated one-shot producer, protected custody, full fault campaign or
required universal body/caller/native-storage proofs.
"""
from __future__ import annotations

import errno
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from worldline import SCHEMA_VERSION
from worldline.canonical import atomic_write_json
from worldline.core import Core
from worldline.errors import WorldlineError
from worldline.model import WorldState
from worldline.transaction import CollapseTransaction

import test_transaction as original_transaction


class RecoveryAuthorityStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))

    def test_original_transaction_table_is_exact_in_the_real_library(self):
        table = {
            'PREPARED': {'AUTHORIZED', 'DENIED', 'ABORTED'},
            'AUTHORIZED': {'COMMITTED', 'ABORTED'},
            'DENIED': {'ABORTED'},
            'COMMITTED': set(),
            'ABORTED': set(),
        }
        for source, allowed in table.items():
            for target in table:
                with self.subTest(source=source, target=target):
                    self.assertEqual(
                        self.core.transaction_transition_allowed(source, target),
                        target in allowed,
                    )

    def test_finish_refuses_without_authorization_before_any_effect(self):
        for state in ('PREPARED', 'DENIED', 'ABORTED'):
            with self.subTest(state=state):
                context = SimpleNamespace(core=self.core, store=Mock(),
                    _capture_staged=Mock(), _recovered_manifests=Mock(),
                    _set_state=Mock(), receipts=Mock(), prime=Mock())
                record = {'transactionId': 'ungranted', 'state': state}
                with self.assertRaises(WorldlineError) as caught:
                    CollapseTransaction._finish_committed(context, record)
                self.assertEqual(caught.exception.code, 'RECOVERY_UNAUTHORIZED')
                self.assertEqual(record['state'], state)
                self.assertEqual(context.store.mock_calls, [])
                context._capture_staged.assert_not_called()
                context._recovered_manifests.assert_not_called()
                context._set_state.assert_not_called()
                self.assertEqual(context.receipts.mock_calls, [])
                self.assertEqual(context.prime.mock_calls, [])

    def test_original_world_table_is_exact_in_the_real_library(self):
        table = {
            'MUTABLE': {'FINALIZING', 'DEAD'},
            'FINALIZING': {'VALID', 'DEGRADED', 'DEAD'},
            'VALID': {'COLLAPSED', 'ARCHIVED'},
            'DEGRADED': {'DEAD', 'ARCHIVED'},
            'DEAD': {'ARCHIVED'},
            'COLLAPSED': {'ARCHIVED'},
            'ARCHIVED': set(),
        }
        for source, allowed in table.items():
            for target in table:
                with self.subTest(source=source, target=target):
                    self.assertEqual(self.core.transition_allowed(source, target), target in allowed)

    def test_authorized_finish_and_committed_evidence_replay_retain_admission(self):
        for state in ('AUTHORIZED', 'COMMITTED'):
            with self.subTest(state=state):
                reached = RuntimeError('the lifecycle gate admitted the original case')
                store = Mock()
                store.world.side_effect = reached
                context = SimpleNamespace(core=self.core, store=store)
                record = {'transactionId': 'granted', 'state': state, 'candidateWorld': 'candidate'}
                with self.assertRaises(RuntimeError) as caught:
                    CollapseTransaction._finish_committed(context, record)
                self.assertIs(caught.exception, reached)
                store.world.assert_called_once_with('candidate')


class RecoveryAuthorityStoreTests(unittest.TestCase):
    # Reuse the original owned-evaluation fixture unchanged. No existing method,
    # assertion, accepted positive or deterministic fixture is replaced.
    setUp = original_transaction.CollapseTransactionTests.setUp
    tearDown = original_transaction.CollapseTransactionTests.tearDown
    _candidate = original_transaction.CollapseTransactionTests._candidate

    def test_forged_markers_do_not_grant_a_prepared_transaction(self):
        candidate = self._candidate('ungranted bytes')
        prepared = self.transaction.prepare(candidate.alias)
        record = self.transaction._load_record(prepared.transaction_id)
        atomic_write_json(self.paths.live / '.worldline-generation.json', {
            'schemaVersion': SCHEMA_VERSION, 'transactionId': prepared.transaction_id,
        })
        atomic_write_json(Path(record['preparedMapping']) / '.worldline-generation.json', {
            'schemaVersion': SCHEMA_VERSION, 'transactionId': 'different-marker',
        })
        with self.assertLogs('worldline.transaction', level='ERROR'):
            recovered = self.transaction.recover_all()
        self.assertEqual(recovered[0]['state'], 'UNRECOVERABLE')
        self.assertEqual(recovered[0]['error']['code'], 'RECOVERY_UNAUTHORIZED')
        self.assertEqual(self.store.transaction_record(prepared.transaction_id)['state'], 'PREPARED')
        self.assertEqual((self.work / 'state.txt').read_text(encoding='utf-8'), 'prime')
        self.assertEqual(self.store.world(candidate.alias).state, WorldState.VALID)
        self.assertIsNone(self.store.receipt_for_transaction(prepared.transaction_id))

    def test_offline_write_without_retained_staged_tree_quarantines(self):
        candidate = self._candidate('authorized staged bytes')
        prepared = self.transaction.prepare(candidate.alias)
        record = self.transaction._load_record(prepared.transaction_id)
        self.transaction._set_state(record, 'AUTHORIZED')
        root_key = self.store.roots()[0]['root_key']
        retained = Path(record['stagingPayload']).parent / 'manifests' / (root_key + '.json')
        retained.unlink()
        self.transaction.atomic.exchange(self.paths.live, Path(record['preparedMapping']))
        (self.work / 'state.txt').write_text('unaccounted offline bytes', encoding='utf-8')
        prime_before = self.store.prime().instance_id
        with self.assertLogs('worldline.transaction', level='ERROR'):
            recovered = self.transaction.recover_all()
        self.assertEqual(recovered[0]['state'], 'UNRECOVERABLE')
        self.assertEqual(recovered[0]['error']['code'], 'TRANSACTION_RECORD_LEGACY')
        self.assertEqual(self.store.prime().instance_id, prime_before)
        self.assertEqual(self.store.world(candidate.alias).state, WorldState.VALID)
        self.assertIsNone(self.store.receipt_for_transaction(prepared.transaction_id))

    def test_directory_flush_failure_aborts_before_exchange(self):
        candidate = self._candidate('not durable')
        prepared = self.transaction.prepare(candidate.alias)
        failure = OSError(errno.ENOSPC, 'simulated directory flush failure')
        with patch.object(self.transaction, '_fsync_payload_tree', side_effect=failure), \
                patch.object(self.transaction.atomic, 'exchange') as exchange:
            with self.assertRaises(OSError) as caught:
                self.transaction._commit(prepared.transaction_id)
        self.assertIs(caught.exception, failure)
        exchange.assert_not_called()
        self.assertEqual(self.store.transaction_record(prepared.transaction_id)['state'], 'ABORTED')
        self.assertEqual((self.work / 'state.txt').read_text(encoding='utf-8'), 'prime')
        self.assertIsNone(self.store.receipt_for_transaction(prepared.transaction_id))

    def test_post_flush_staged_change_is_redecided_and_aborted(self):
        candidate = self._candidate('original staged bytes')
        prepared = self.transaction.prepare(candidate.alias)
        root_key = self.store.roots()[0]['root_key']
        flush = self.transaction._fsync_payload_tree

        def changed_after_flush(payload):
            flush(payload)
            (payload / root_key / 'state.txt').write_text('changed after flush', encoding='utf-8')

        with patch.object(self.transaction, '_fsync_payload_tree', side_effect=changed_after_flush), \
                patch.object(self.transaction.atomic, 'exchange') as exchange:
            with self.assertRaises(WorldlineError) as caught:
                self.transaction._commit(prepared.transaction_id)
        self.assertEqual(caught.exception.code, 'STAGED_ROOT_MISMATCH')
        exchange.assert_not_called()
        self.assertEqual(self.store.transaction_record(prepared.transaction_id)['state'], 'ABORTED')
        self.assertEqual((self.work / 'state.txt').read_text(encoding='utf-8'), 'prime')
        self.assertIsNone(self.store.receipt_for_transaction(prepared.transaction_id))

    def test_clean_commit_retains_complete_post_flush_inputs_and_intent(self):
        candidate = self._candidate('durable commit')
        prepared = self.transaction.prepare(candidate.alias)
        result = self.transaction.commit(prepared.transaction_id)
        self.assertEqual(result['state'], 'COMMITTED')
        record = self.transaction._load_record(prepared.transaction_id)
        self.assertTrue(set(record['decisionInputs']).issubset(record['decisionInputsAtCommit']))
        self.assertEqual(record['commitIntent'], {
            'state': 'COMMITTING', 'transactionId': prepared.transaction_id,
            'stagedRoot': prepared.staged_root,
        })
        self.assertEqual((self.work / 'state.txt').read_text(encoding='utf-8'), 'durable commit')
        self.assertIsNotNone(self.store.receipt_for_transaction(prepared.transaction_id))


class RecoveryFlushTests(unittest.TestCase):
    def test_actual_directory_flush_error_is_not_swallowed(self):
        with tempfile.TemporaryDirectory(prefix='worldline-flush-refusal-') as temporary:
            payload = Path(temporary)
            (payload / 'file').write_bytes(b'flushable')
            failure = OSError(errno.EROFS, 'simulated read-only directory flush')
            with patch('worldline.transaction.fsync_directory', side_effect=failure):
                with self.assertRaises(OSError) as caught:
                    CollapseTransaction._fsync_payload_tree(payload)
            self.assertIs(caught.exception, failure)

    def test_missing_payload_is_not_a_successful_flush(self):
        with tempfile.TemporaryDirectory(prefix='worldline-missing-staging-') as temporary:
            with self.assertRaises(FileNotFoundError):
                CollapseTransaction._fsync_payload_tree(Path(temporary) / 'missing')

    def test_file_fsync_and_close_failure_preserves_primary_object_and_closes_once(self):
        with tempfile.TemporaryDirectory(prefix='worldline-double-flush-failure-') as temporary:
            payload = Path(temporary)
            (payload / 'file').write_bytes(b'flushable')
            primary = OSError(errno.ENOSPC, 'simulated file fsync failure')
            secondary = OSError(errno.EIO, 'simulated close failure')
            close = os.close

            def release_then_refuse(descriptor):
                close(descriptor)
                raise secondary

            with patch('worldline.transaction.os.fsync', side_effect=primary), \
                    patch('worldline.transaction.os.close', side_effect=release_then_refuse) as closed:
                with self.assertRaises(OSError) as caught:
                    CollapseTransaction._fsync_payload_tree(payload)
            self.assertIs(caught.exception, primary)
            closed.assert_called_once()
            self.assertTrue(any(repr(secondary) in note for note in primary.__notes__))

    def test_successful_file_fsync_close_failure_still_refuses(self):
        with tempfile.TemporaryDirectory(prefix='worldline-close-refusal-') as temporary:
            payload = Path(temporary)
            (payload / 'file').write_bytes(b'flushable')
            secondary = OSError(errno.EIO, 'simulated close failure after successful flush')
            close = os.close

            def release_then_refuse(descriptor):
                close(descriptor)
                raise secondary

            with patch('worldline.transaction.os.close', side_effect=release_then_refuse) as closed:
                with self.assertRaises(OSError) as caught:
                    CollapseTransaction._fsync_payload_tree(payload)
            self.assertIs(caught.exception, secondary)
            closed.assert_called_once()


if __name__ == '__main__':
    unittest.main()
