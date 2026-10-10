"""Additive real selected-library value controls. No protected acceptance claim."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import json,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
from worldline.errors import CoreUnavailable
from worldline.owner_transitions import OwnerGrant,OwnerRequest,authorize_owner
from worldline.evaluation_history import EvaluationRecord as Row,EvaluationCursor as Cursor,EvaluationQuery as Query,select_history

class OwnerTransitionControls(unittest.TestCase):
    def fixture(self):
        final=Row('subject','content','policy','final-run',0,'COMPLETED','PASS')
        failed=Row('subject','content','policy','run-one',1,'COMPLETED','FAIL')
        passed=Row('subject','content','policy','run-two',2,'COMPLETED','PASS')
        head=Cursor(2,'run-two');attempt=Cursor(3,'owner-retry')
        grant=OwnerGrant('RETRY_EVALUATION','RESERVED','grant','use','issuer','owner','subject','content','tx',
          'policy','policy','explicit reason','grant','grant','use',Cursor(1,'run-one'),head,attempt,0)
        req=OwnerRequest('RETRY_EVALUATION','owner','owner','issuer','subject','content','tx','policy','policy',head,attempt,0,grant)
        return [failed,passed],final,req
    def test_original_terminal_fail_and_reserved_retry_value(self):
        history,final,req=self.fixture()
        self.assertEqual(select_history(history,final,Query('subject','content','policy',req.current_head,req.current_head)).reason,'EVIDENCE_FAIL_TERMINAL')
        self.assertEqual(authorize_owner(history,final,req),'READY')
        self.assertEqual([r.outcome for r in history],['FAIL','PASS'])
        self.assertEqual(authorize_owner(history,final,replace(req,grant=replace(req.grant,state='ISSUED'))),'GRANT_UNAVAILABLE')
    def test_full_grant_scope_and_reservation_refusals(self):
        history,final,req=self.fixture()
        cases=[('principal','another','REQUESTER_NOT_OWNER'),('issuer','another','ISSUER_MISMATCH'),
          ('state','CONSUMED','GRANT_UNAVAILABLE'),('state','REVOKED','GRANT_UNAVAILABLE'),
          ('action','ADOPT_REQUIREMENT','OPERATION_MISMATCH'),('subject','another','SUBJECT_MISMATCH'),
          ('content','another','CONTENT_MISMATCH'),('transaction','another','TRANSACTION_MISMATCH'),
          ('current_requirement','another','REQUIREMENT_MISMATCH'),('expected_requirement','another','REQUIREMENT_MISMATCH'),
          ('reason','','REASON_ABSENT'),('reason',None,'REASON_ABSENT'),('issued_grant','another','RESERVATION_MISMATCH'),
          ('reserved_grant','another','RESERVATION_MISMATCH'),('reserved_use','another','RESERVATION_MISMATCH'),
          ('epoch',1,'EPOCH_MISMATCH'),('failed_run',Cursor(2,'run-two'),'FAILED_HEAD_MISMATCH'),
          ('prior_head',Cursor(1,'run-one'),'FAILED_HEAD_MISMATCH'),('next_run',Cursor(3,'another'),'ATTEMPT_MISMATCH')]
        for name,value,reason in cases:
            with self.subTest(field=name,value=value):
                self.assertEqual(authorize_owner(history,final,replace(req,grant=replace(req.grant,**{name:value}))),reason)
    def test_complete_roster_and_exact_new_attempt(self):
        history,final,req=self.fixture()
        self.assertEqual(authorize_owner([replace(history[0],subject='another'),history[1]],final,req),'HISTORY_INVALID')
        self.assertEqual(authorize_owner(history+[replace(history[1],epoch=3,run='unobserved')],final,req),'FAILED_HEAD_MISMATCH')
        self.assertEqual(authorize_owner(history,final,replace(req,attempt=Cursor(3,'run-one'),grant=replace(req.grant,next_run=Cursor(3,'run-one')))),'ATTEMPT_MISMATCH')
        self.assertEqual(authorize_owner(history,final,replace(req,attempt=Cursor(2,'owner-retry'),grant=replace(req.grant,next_run=Cursor(2,'owner-retry')))),'ATTEMPT_MISMATCH')
        self.assertEqual(authorize_owner([replace(history[0],outcome='PASS'),history[1]],final,req),'FAILED_HEAD_MISMATCH')
    def test_native_adopt_value_and_expected_resulting_requirement(self):
        history,final,req=self.fixture()
        g=replace(req.grant,action='ADOPT_REQUIREMENT',expected_requirement='new-policy')
        adopted=replace(req,action='ADOPT_REQUIREMENT',resulting_requirement='new-policy',grant=g)
        self.assertEqual(authorize_owner(history,final,adopted),'READY')
        self.assertEqual(authorize_owner(history,final,replace(adopted,resulting_requirement='wrong-policy')),'REQUIREMENT_MISMATCH')
        self.assertEqual(authorize_owner(history,final,replace(adopted,peer='non-owner')),'REQUESTER_NOT_OWNER')
    def test_arbitrary_capability_epoch_and_complete_identity_bytes(self):
        history,final,req=self.fixture()
        fixture=json.loads((Path(__file__).parent/'fixtures/owner-epoch-exact-v1.json').read_text())
        epoch=int(fixture['current']['exact']);next_epoch=int(fixture['changed']['exact'])
        wide=replace(req,current_epoch=epoch,grant=replace(req.grant,epoch=epoch))
        self.assertEqual(authorize_owner(history,final,wide),'READY')
        self.assertEqual(authorize_owner(history,final,replace(wide,grant=replace(wide.grant,epoch=next_epoch))),'EPOCH_MISMATCH')
        for value in ('','a\x00b','é','e\u0301','\ud800','世界🌍'):
            q=replace(wide,transaction=value,grant=replace(wide.grant,transaction=value))
            self.assertEqual(authorize_owner(history,final,q),'READY')
            self.assertEqual(authorize_owner(history,final,replace(q,transaction=value+'suffix')),'TRANSACTION_MISMATCH')
    def test_absence_transport_and_no_native_fallback(self):
        history,final,req=self.fixture()
        self.assertEqual(authorize_owner(history,final,replace(req,current_epoch=None)),'INPUT_ABSENT')
        self.assertEqual(authorize_owner(history,final,replace(req,owner=None)),'INPUT_ABSENT')
        with self.assertRaises(CoreUnavailable):authorize_owner(history,final,replace(req,current_epoch=True))
        with self.assertRaises(CoreUnavailable):authorize_owner(history,final,req,core=object())

if __name__=='__main__':unittest.main()
