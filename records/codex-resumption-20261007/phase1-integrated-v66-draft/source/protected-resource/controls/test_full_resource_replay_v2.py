"""Actual protected service/Gate/native controls, source authored and NOT run.

Requires separately owner-provisioned disposable root layouts, authentic native
roster producer, complete native source/library and genuine controlled fault
fixtures. No fake Gate/peer/Systemd/native/authority Boolean supplies a positive.
"""
import json,os,pathlib,unittest
from run_service import RunLedgerService,Refusal
from gate_bridge import FullResourceGateBridge
from intent_gate import Gate
from worldline.resource_run_ledger import restore_dto,dto_record

class FullResourceReplayV2Controls(unittest.TestCase):
    def fixture(self,name):
        path=os.environ.get('WORLDLINE_FULL_RESOURCE_CONTROL_'+name)
        self.assertIsNotNone(path,'a genuine separately provisioned protected disposable control is required')
        value=json.loads(pathlib.Path(path).read_bytes())
        gate=Gate(pathlib.Path(value['gate_config']))
        service=RunLedgerService(pathlib.Path(value['resource_root']))
        return value,gate,service
    def snapshot(self,service):
        with service.connect() as db:
            db.execute('BEGIN')
            try:
                service._snapshot(db)
                return {table:[tuple(row) for row in db.execute('SELECT * FROM '+table+' ORDER BY '+order)]
                        for table,order in (('run_meta','config_sha'),('run_rows','ordinal'),('run_events','ordinal'))}
            finally:db.rollback()
    def args(self,packet):
        return {'proposed':restore_dto(packet['proposed']),
                'rows':tuple(restore_dto(row) for row in packet['rows']),
                'request':restore_dto(packet['request'])}

    def test_successful_same_pending_operation_advances_all_lifecycle_steps(self):
        fixture,gate,service=self.fixture('SEQUENTIAL')
        bridge=FullResourceGateBridge(gate)
        expected=('RESERVE','RECORD_LAUNCH_INTENT','RECORD_RUNNING','RECORD_TERMINATING','RECORD_TERMINAL','RELEASE_HOLD')
        self.assertEqual(tuple(restore_dto(packet['request']).kind for packet in fixture['packets']),expected)
        for packet in fixture['packets']:
            answer=bridge.submit(**self.args(packet))
            self.assertEqual(answer['status'],'READY');self.assertEqual(answer['state'],packet['proposed'])
            self.assertEqual(answer['rows'],packet['rows'])
        self.assertEqual(gate.journal['pending']['operation_id'],fixture['operation_id'])
        self.assertTrue(all(event['cause'] in ('SUBMIT','ACKNOWLEDGE') for event in gate.journal['full_resource_history_v2']))
        self.snapshot(service)

    def test_exact_committed_duplicate_and_recover_return_original_result_without_append(self):
        fixture,gate,service=self.fixture('DUPLICATE')
        bridge=FullResourceGateBridge(gate);packet=fixture['packets'][0]
        answer=bridge.submit(**self.args(packet));before=self.snapshot(service)
        gate_before=json.dumps(gate.journal,sort_keys=True)
        self.assertEqual(bridge.submit(**self.args(packet)),answer)
        self.assertEqual(bridge.recover(**self.args(packet)),answer)
        self.assertEqual(service.mutate(packet,os.geteuid()),answer)
        self.assertEqual(service.recover(packet,os.geteuid()),answer)
        self.assertEqual(before,self.snapshot(service));self.assertEqual(gate_before,json.dumps(gate.journal,sort_keys=True))

    def test_committed_lost_ack_after_restart_reconciles_once(self):
        fixture,gate,service=self.fixture('LOST_ACK_RESTART')
        # The actual controlled fault already committed the event and left the
        # genuine Gate SUBMIT without ACK. Its owner key/peer/native record is
        # retained. This test never fabricates that authorization history.
        packet=fixture['packets'][0];before=self.snapshot(service)
        expected=service.recover(packet,os.geteuid());self.assertEqual(expected['status'],'READY')
        bridge=FullResourceGateBridge(gate);self.assertEqual(bridge.recover(**self.args(packet)),expected)
        after_gate=json.dumps(gate.journal,sort_keys=True)
        self.assertEqual(bridge.recover(**self.args(packet)),expected)
        self.assertEqual(before,self.snapshot(service));self.assertEqual(after_gate,json.dumps(gate.journal,sort_keys=True))

    def test_same_id_changed_complete_packet_or_owner_refuses_without_mutation(self):
        fixture,gate,service=self.fixture('CONFLICT')
        packet=fixture['packets'][0];service.mutate(packet,os.geteuid());before=self.snapshot(service)
        changed=json.loads(json.dumps(packet));changed['request']['requester']={'bytes':b'foreign-owner'.hex()}
        with self.assertRaisesRegex(Refusal,'FULL_LEDGER_REQUEST_ID_CONFLICT'):service.mutate(changed,os.geteuid())
        with self.assertRaisesRegex(Refusal,'FULL_LEDGER_REQUEST_ID_CONFLICT'):service.recover(changed,os.geteuid())
        with self.assertRaisesRegex(Refusal,'PEER_NOT_ROOT_GATE'):service.recover(packet,gate.config['requester_uid'])
        self.assertEqual(before,self.snapshot(service))

    def test_historical_exact_response_survives_later_native_state_and_closed_gate(self):
        fixture,gate,service=self.fixture('CLOSED_AFTER_COMMIT')
        self.assertIsNone(gate.journal['pending'])
        packet=fixture['packets'][0];before=self.snapshot(service)
        expected=service.recover(packet,os.geteuid())
        self.assertEqual(FullResourceGateBridge(gate).recover(**self.args(packet)),expected)
        self.assertEqual(before,self.snapshot(service))

    def test_not_committed_recovery_does_not_create_an_event(self):
        fixture,gate,service=self.fixture('NOT_COMMITTED')
        packet=fixture['packets'][0];before=self.snapshot(service)
        self.assertEqual(service.recover(packet,os.geteuid()),{'status':'NOT_COMMITTED'})
        self.assertEqual(before,self.snapshot(service))

    def test_repeated_dispatch_intent_never_launches_again(self):
        fixture,gate,service=self.fixture('DISPATCH_UNKNOWN')
        from worldline.linux.systemd import SystemdAdapter
        bridge=FullResourceGateBridge(gate);packet=fixture['packets'][0];before=self.snapshot(service)
        manager=SystemdAdapter()
        with self.assertRaisesRegex(Exception,'FULL_RESOURCE_LAUNCH_ALREADY_INTENDED_RECONCILIATION_REQUIRED'):
            bridge.launch_after_intent(**self.args(packet),manager=manager,
                instance_id=fixture['instance_id'],argv=fixture['argv'],description=fixture['description'])
        self.assertEqual(before,self.snapshot(service))

    def test_legacy_result_import_preserves_complete_original_row(self):
        fixture,gate,service=self.fixture('LEGACY_COMMITTED')
        packet=fixture['packets'][0];legacy=json.dumps(gate.journal['pending']['full_resource_intent_v1'],sort_keys=True)
        before=self.snapshot(service);answer=FullResourceGateBridge(gate).recover(**self.args(packet))
        self.assertEqual(answer,service.recover(packet,os.geteuid()))
        self.assertEqual(legacy,json.dumps(gate.journal['pending']['full_resource_intent_v1'],sort_keys=True))
        self.assertEqual(before,self.snapshot(service))

if __name__=='__main__':unittest.main()
