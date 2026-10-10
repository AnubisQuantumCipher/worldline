"""Real selected native-library controls; source-only authoring leaves them UNRUN.

No fake DLL, Python authorization oracle, filtered history or replacement fixture
is used. These controls must run against the composed exact selected library.
"""
from dataclasses import replace
import ctypes
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
from worldline.core import Core,CollapseInput,CCollapseRequest,COptionalHash
from worldline.canonical import canonical_bytes
from worldline.errors import CoreUnavailable
from worldline.owner_transitions import OwnerGrant,OwnerRequest
from worldline.owner_retry_audit import (RetryAudit,UseReceipt,FullScope,decide_retry,
    authorize_retry_collapse,authorize_checkpoint,authorize_adopt_receipt,Owned,_api,_Scope,AUDIT_REASONS)
from worldline.evaluation_history import EvaluationRecord as Row,EvaluationCursor as Cursor,EvaluationQuery as Query,select_history

def h(value):return bytes([value])*32

def subject_digest(instance,checkpoint=False):
    core=Core.shared()
    binding=identity(core.hash_bytes(b'worldline-return-v1'+instance.encode('ascii'))) if checkpoint else ''
    return core.hash_bytes(b'worldline-subject-v1'+canonical_bytes([instance,binding]))

def original(instance='instance-world'):
    return CollapseInput(candidate_state='VALID',phase='COMMIT',mode='CANDIDATE_EVALUATION',conflicts='NONE_FOUND',
        foreign_writes='NONE_FOUND',roster_complete=True,staged_roster_complete=False,
        expected_parent=h(1),candidate_parent=h(1),expected_subject=subject_digest(instance),evidence_subject=subject_digest(instance),
        expected_base=h(3),candidate_base=h(3),expected_delta=h(4),candidate_delta=h(4),
        expected_root_set=h(5),candidate_root_set=h(5),expected_staged_root=h(6),actual_staged_root=h(6),
        staged_content_root=h(7),tested_root=h(7),current_requirement=h(8),resulting_requirement=h(8),
        evaluated_requirement=h(8),declared_verifiers=h(9),executed_verifiers=h(9),staged_evaluated_requirement=None,
        staged_executed_verifiers=None,staged_examined_root=None,expected_checkpoint=None,witnessed_checkpoint=None,
        registered_watch_set=h(10),watched_set=h(10),generation_before=41,generation_after=41)

def identity(value):return 'sha256:'+value.hex()

def fixture():
    subject,content,requirement='instance-world',identity(h(11)),identity(h(8))
    final=Row(subject,content,requirement,'final',0,'COMPLETED','PASS')
    failed=Row(subject,content,requirement,'failed',1,'COMPLETED','FAIL')
    passed=Row(subject,content,requirement,'old-pass',2,'COMPLETED','PASS')
    head,attempt=Cursor(2,'old-pass'),Cursor(3,'owner-retry')
    g=OwnerGrant('RETRY_EVALUATION','RESERVED','grant','use','issuer','owner',subject,content,'tx',requirement,requirement,
        'explicit retained failed-head reason','grant','grant','use',Cursor(1,'failed'),head,attempt,0)
    q=OwnerRequest('RETRY_EVALUATION','owner','owner','issuer',subject,content,'tx',requirement,requirement,head,attempt,0,g)
    receipt=UseReceipt(replace(g,state='CONSUMED'),'issue-event','reserve-event','consume-event','issue-event','reserve-event')
    audit=RetryAudit(q,receipt,attempt,attempt,0)
    after=[failed,passed,Row(subject,content,requirement,'owner-retry',3,'COMPLETED','PASS')]
    return [failed,passed],after,final,audit,FullScope(subject,content,'tx')

class OwnerRetryAuditControls(unittest.TestCase):
    def setUp(self):self.core=Core.shared()
    def audit(self,before,after,final,q,after_final=None):
        return decide_retry(before,after,final,final if after_final is None else after_final,q,core=self.core)
    def test_complete_pass_fail_pass_keeps_original_veto_and_owner_positive(self):
        before,after,final,q,scope=fixture()
        query=Query(scope.subject,scope.content,q.before_request.current_requirement,q.current_head,q.prepared_evidence)
        self.assertEqual([final.outcome]+[row.outcome for row in after],['PASS','FAIL','PASS','PASS'])
        self.assertEqual(select_history(after,final,query,core=self.core).reason,'EVIDENCE_FAIL_TERMINAL')
        self.assertEqual(self.audit(before,after,final,q),'READY')
        self.assertEqual(authorize_retry_collapse(before,after,final,final,q,original(),scope,core=self.core),'READY')
    def test_exact_complete_prefix_and_extra_current_history(self):
        before,after,final,q,_scope=fixture()
        for changed in (after[1:],after+[replace(after[-1],epoch=4,run='extra')],
            [replace(after[0],outcome='PASS')]+after[1:], [after[1],after[0],after[2]], []):
            with self.subTest(history=changed):self.assertEqual(self.audit(before,changed,final,q),'PREFIX_CHANGED')
        self.assertEqual(self.audit(before,after,final,q,replace(final,run='different-final')),'PREFIX_CHANGED')
        for state in ('PENDING','ERROR'):
            b=[before[0],replace(before[1],state=state,outcome=None)]
            a=b+[after[-1]]
            self.assertEqual(self.audit(b,a,final,q),'BEFORE_NOT_AUTHORIZED')
        for state,outcome in (('PENDING',None),('ERROR',None),('COMPLETED','FAIL')):
            changed=after[:-1]+[replace(after[-1],state=state,outcome=outcome)]
            self.assertNotEqual(self.audit(before,changed,final,q),'READY')
        changed=after[:-1]+[replace(after[-1],subject='another')]
        self.assertEqual(self.audit(before,changed,final,q),'AFTER_INVALID')
        changed=after[:-1]+[replace(after[-1],requirement='another')]
        self.assertNotEqual(self.audit(before,changed,final,q),'READY')
    def test_independent_complete_consumed_receipt_and_live_cursors(self):
        before,after,final,q,_scope=fixture()
        for name in ('issued_event','reserved_event','consumed_event','consumed_issue','consumed_reservation'):
            altered=replace(q,receipt=replace(q.receipt,**{name:None}))
            self.assertEqual(self.audit(before,after,final,altered),'USE_NOT_CONSUMED')
        for name in ('consumed_issue','consumed_reservation'):
            self.assertEqual(self.audit(before,after,final,replace(q,receipt=replace(q.receipt,**{name:'wrong'}))),'USE_NOT_CONSUMED')
        self.assertEqual(self.audit(before,after,final,replace(q,receipt=replace(q.receipt,consumed_event=q.receipt.issued_event))),'USE_NOT_CONSUMED')
        for name in ('grant','use_id','issuer','principal','subject','content','transaction','current_requirement','expected_requirement','reason','issued_grant','reserved_grant','reserved_use'):
            bad=replace(q.receipt.consumed,**{name:'wrong'})
            self.assertEqual(self.audit(before,after,final,replace(q,receipt=replace(q.receipt,consumed=bad))),'USE_NOT_CONSUMED')
        for state in ('ISSUED','RESERVED','REVOKED'):
            self.assertEqual(self.audit(before,after,final,replace(q,receipt=replace(q.receipt,consumed=replace(q.receipt.consumed,state=state)))),'USE_NOT_CONSUMED')
        for name in ('current_head','prepared_evidence'):
            self.assertNotEqual(self.audit(before,after,final,replace(q,**{name:Cursor(2,'old-pass')})),'READY')
        self.assertEqual(self.audit(before,after,final,replace(q,current_epoch=None)),'CURRENT_BINDING_CHANGED')
    def test_arbitrary_original_epoch_and_genesis_transport(self):
        before,after,final,q,_scope=fixture()
        data=json.loads((Path(__file__).parent/'fixtures/owner-epoch-exact-v1.json').read_text())
        epoch=int(data['current']['exact']);different=int(data['changed']['exact'])
        request=replace(q.before_request,current_epoch=epoch,grant=replace(q.before_request.grant,epoch=epoch))
        receipt=replace(q.receipt,consumed=replace(q.receipt.consumed,epoch=epoch))
        wide=replace(q,before_request=request,receipt=receipt,current_epoch=epoch)
        self.assertEqual(self.audit(before,after,final,wide),'READY')
        self.assertEqual(self.audit(before,after,final,replace(wide,current_epoch=different)),'CURRENT_BINDING_CHANGED')
        self.assertEqual(self.audit(before,after,final,q),'READY')
        with self.assertRaises(CoreUnavailable):self.audit(before,after,final,replace(q,current_epoch=True))
    def test_all_original_r_a_conjuncts_and_full_owner_scope(self):
        before,after,final,q,scope=fixture();values=original()
        cases=(replace(values,candidate_state='DEAD'),replace(values,candidate_parent=h(12)),
            replace(values,evidence_subject=h(12)),replace(values,candidate_base=h(12)),replace(values,candidate_delta=h(12)),
            replace(values,candidate_root_set=h(12)),replace(values,actual_staged_root=h(12)),replace(values,evaluated_requirement=h(12)),
            replace(values,executed_verifiers=h(12)),replace(values,roster_complete=False),replace(values,tested_root=h(12)),
            replace(values,conflicts='FOUND'),replace(values,foreign_writes='FOUND'),replace(values,generation_after=42),
            replace(values,watched_set=h(12)))
        for changed in cases:
            self.assertEqual(authorize_retry_collapse(before,after,final,final,q,changed,scope,core=self.core),'ORIGINAL_COLLAPSE_DENIED')
        for name in ('subject','content','transaction'):
            self.assertEqual(authorize_retry_collapse(before,after,final,final,q,values,replace(scope,**{name:'wrong'}),core=self.core),'OWNER_SCOPE_MISMATCH')
        # Lowercase complete digest prefix and every final byte are bound.
        subject=replace(scope,subject=scope.subject[:-1]+'f')
        self.assertEqual(authorize_retry_collapse(before,after,final,final,q,values,subject,core=self.core),'OWNER_SCOPE_MISMATCH')
    def test_original_full_subject_hash_grammar_not_asserted_projection(self):
        before,after,final,q,scope=fixture()
        for subject in ('instance-world','世界🌍','a\x00b','a"b','a\\b','\b\t\n\f\r','é','e\u0301'):
            b=[replace(row,subject=subject) for row in before]
            a=[replace(row,subject=subject) for row in after]
            f=replace(final,subject=subject)
            req=replace(q.before_request,subject=subject,grant=replace(q.before_request.grant,subject=subject))
            receipt=replace(q.receipt,consumed=replace(q.receipt.consumed,subject=subject))
            audit=replace(q,before_request=req,receipt=receipt)
            whole=replace(scope,subject=subject)
            values=original(subject)
            self.assertEqual(authorize_retry_collapse(b,a,f,f,audit,values,whole,core=self.core),'READY')
            # Both original sides move together so original R-A still holds;
            # the owner projection independently computes the real preimage.
            changed=replace(values,expected_subject=h(12),evidence_subject=h(12))
            self.assertEqual(self.core.collapse_decide(changed),'AUTHORIZED')
            self.assertEqual(authorize_retry_collapse(b,a,f,f,audit,changed,whole,core=self.core),'OWNER_SCOPE_MISMATCH')

    def test_checkpoint_independent_result_and_actual_adopt_consumed_relation(self):
        before,_after,final,retry,scope=fixture()
        digest=subject_digest(scope.subject,True)
        values=replace(original(),mode='CHECKPOINT_RETURN',expected_subject=digest,evidence_subject=digest,roster_complete=False,resulting_requirement=None,
            evaluated_requirement=None,executed_verifiers=None,expected_checkpoint=h(11),witnessed_checkpoint=h(11))
        self.assertEqual(authorize_checkpoint((),None,values,h(8),scope,None,core=self.core),'READY')
        self.assertEqual(authorize_checkpoint((),None,values,None,scope,None,core=self.core),'RESULTING_REQUIREMENT_ABSENT')
        self.assertEqual(authorize_checkpoint((),None,values,h(12),scope,None,core=self.core),'REQUIREMENT_CHANGED')
        grant=replace(retry.before_request.grant,action='ADOPT_REQUIREMENT',expected_requirement=identity(h(12)),failed_run=None,next_run=None)
        adopt=replace(retry.before_request,action='ADOPT_REQUIREMENT',attempt=None,resulting_requirement=identity(h(12)),grant=grant)
        self.assertEqual(authorize_checkpoint(before,final,values,h(12),scope,adopt,core=self.core),'READY')
        self.assertEqual(authorize_checkpoint(before,final,values,h(8),scope,adopt,core=self.core),'OWNER_SCOPE_MISMATCH')
        consumed=replace(grant,state='CONSUMED')
        receipt=replace(retry.receipt,consumed=consumed)
        audit=RetryAudit(adopt,receipt,None,None,0)
        self.assertEqual(authorize_adopt_receipt(before,final,audit,values,scope,h(12),core=self.core),'READY')
        self.assertEqual(authorize_adopt_receipt(before,final,replace(audit,receipt=replace(receipt,consumed=grant)),values,scope,h(12),core=self.core),'OWNER_NOT_AUTHORIZED')
        self.assertEqual(authorize_adopt_receipt(before,final,replace(audit,receipt=replace(receipt,consumed_issue='another')),values,scope,h(12),core=self.core),'OWNER_NOT_AUTHORIZED')
    def test_real_native_wire_presence_and_owned_alias(self):
        before,after,final,audit,_scope=fixture()
        from worldline.owner_transitions import _Row,_Request
        def call(*,malformed=False,alias=False):
            owned=Owned();b=(_Row*len(before))(*(owned.row(row) for row in before))
            a=(_Row*len(after))(*(owned.row(row) for row in after));f=owned.row(final);q=owned.audit(audit)
            if malformed:q.current_epoch.present=2
            arena=(ctypes.c_uint8*len(owned.arena)).from_buffer_copy(owned.arena)
            result=ctypes.c_uint8();output=ctypes.cast(arena,ctypes.POINTER(ctypes.c_uint8)) if alias else ctypes.byref(result)
            status=_api(self.core)(0,arena,len(arena),b,len(before),a,len(after),1,ctypes.byref(f),1,ctypes.byref(f),
                ctypes.byref(q),ctypes.byref(CCollapseRequest()),ctypes.byref(_Scope()),ctypes.byref(COptionalHash()),0,
                ctypes.byref(_Request()),output)
            return status,AUDIT_REASONS[arena[0] if alias else result.value]
        self.assertEqual(call(malformed=True),(0,'INPUT_INVALID'))
        self.assertEqual(call(alias=True),(0,'READY'))

    def test_no_absent_native_or_python_fallback(self):
        before,after,final,q,_scope=fixture()
        with self.assertRaises(CoreUnavailable):decide_retry(before,after,final,final,q,core=object())

if __name__=='__main__':unittest.main()
