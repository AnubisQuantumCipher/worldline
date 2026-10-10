"""Real-library full ledger and lifecycle controls, authored but not executed.

No mocks substitute for policy decisions. Protected packet production, native
memory correspondence, unbounded implementation costs, and SPARK proof remain
separate obligations. Numbers are retained JACKAL exact specimen values; this
finite suite establishes neither complete domain nor protected authority.
"""
import ctypes as C
from dataclasses import replace
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from worldline.errors import CoreUnavailable
from worldline.resource_run_ledger import (ResourceRunLedgerKernel,RunContext,RunBinding,
    RunRow,RunState,RunObservation,RunRequest,RawResult,STATUS,dto_record,restore_dto)

BEYOND_WORD=18446744073709551616
BEYOND_WORD_NEXT=18446744073709551617
LARGE=115792089237316195423570985008687907853269984665640564039457584007913129639937
LARGE_NEXT=115792089237316195423570985008687907853269984665640564039457584007913129639938
SCOPE=RunContext(universe=b'universe',policy=b'policy',resource=b'memory',unit=b'bytes',
    instance=b'instance',host=b'host',boot=b'boot',authority=b'authority',policy_epoch=0)

def row(name=b'row',*,epoch=0,amount=10,parent=None,kind='HELD_CAPACITY',state='RESERVED',effect=False):
    bound=RunBinding(reservation=name,operation=b'op-'+name,owner=b'owner',workload=b'work-'+name,
        universe_head=b'universe-head',capability=b'cap-'+name,grant_use=b'use-'+name,
        payload=b'payload-'+name,provenance=b'origin-'+name,resource_epoch=epoch)
    unit=b'worldline-'+name+b'.service'
    return RunRow(scope=SCOPE,bound=bound,parent=parent,kind=kind,state=state,amount=amount,
        observed_usage=None,planned_unit=unit if state!='RESERVED' else None,
        actual_unit=unit if effect else None,cgroup=b'/owned/'+name if effect else None,
        invocation=b'invoke-'+name if effect else None)

def state(epoch,*,held=0,charged=0,capacity=20,head=None):
    return RunState(scope=SCOPE,resource_epoch=epoch,universe_head=b'universe-head',
        ledger_head=head or ('head-'+str(epoch)).encode(),capacity=capacity,held_total=held,charged_total=charged)

def observation(item,epoch,live='UNKNOWN',*,actual=None):
    source=actual or item
    return RunObservation(scope=SCOPE,resource_epoch=epoch,bound=item.bound,
        actual_unit=source.actual_unit,cgroup=source.cgroup,invocation=source.invocation,
        observation_head=b'native-observation',observed=live)

def request(before,item,kind='RESERVE',*,new=None):
    return RunRequest(kind=kind,scope=SCOPE,expected_epoch=before.resource_epoch,
        expected_ledger_head=before.ledger_head,request_id=b'request',reservation=item.bound.reservation,
        operation_id=item.bound.operation,requester=item.bound.owner,bound=item.bound,
        new_row=item if kind=='RESERVE' else new)

class ResourceRunLedgerV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Missing symbol/layout/library is an error, never a skip or Python fallback.
        cls.kernel=ResourceRunLedgerKernel(SimpleNamespace(_lib=C.CDLL(os.environ['WORLDLINE_CORE_LIB'])))
    def check(self,before,before_rows,proposed,rows,observed,req):
        return self.kernel.check(before=before,before_rows=tuple(before_rows),proposed=proposed,
            proposed_rows=tuple(rows),observed=tuple(observed),request=req)
    def test_present_genesis_zero_reserves_before_launch(self):
        before=state(0);first=row();after=state(1,held=10)
        self.assertEqual(self.check(before,(),after,(first,),(),request(before,first)),'READY')
    def test_absent_epoch_is_not_present_genesis(self):
        before=state(None);first=row()
        self.assertEqual(self.check(before,(),state(1,held=10),(first,),(),request(before,first)),'INVALID_BEFORE')
    def test_all_capacity_rows_project_into_total(self):
        one=row(b'one');two=row(b'two',epoch=1)
        before=state(1,held=10);req=request(before,two)
        self.assertEqual(self.check(before,(one,),state(2,held=20),(one,two),
             (observation(one,1),),req),'READY')
        self.assertEqual(self.check(before,(one,),state(2,held=10),(one,two),
             (observation(one,1),),req),'CONSERVATION_MISMATCH')
    def test_no_asserted_remainder_omits_a_row(self):
        one=row(b'one');two=row(b'two');before=state(1,held=20)
        changed=replace(one,state='LAUNCH_INTENT',planned_unit=b'unit')
        req=request(before,one,'RECORD_LAUNCH_INTENT')
        self.assertEqual(self.check(before,(one,two),state(2,held=10),(changed,),
            (observation(one,1),observation(two,1)),req),'HISTORICAL_ROW_REMOVED')
    def test_historical_amount_and_binding_cannot_change(self):
        one=row(b'one');before=state(1,held=10)
        changed=replace(one,state='LAUNCH_INTENT',planned_unit=b'unit',amount=11)
        self.assertEqual(self.check(before,(one,),state(2,held=11),(changed,),
             (observation(one,1),),request(before,one,'RECORD_LAUNCH_INTENT')),'ILLEGAL_LIFECYCLE')
        changed=replace(one,state='LAUNCH_INTENT',planned_unit=b'unit',bound=replace(one.bound,payload=b'other'))
        self.assertEqual(self.check(before,(one,),state(2,held=10),(changed,),
             (observation(one,1),),request(before,one,'RECORD_LAUNCH_INTENT')),'ILLEGAL_LIFECYCLE')
    def test_running_requires_prior_durable_launch_intent_and_exact_invocation(self):
        reserved=row();running=row(state='RUNNING',effect=True)
        before=state(1,held=10);after=state(2,held=10)
        observed=observation(reserved,1,'LIVE',actual=running)
        self.assertEqual(self.check(before,(reserved,),after,(running,),(observed,),
            request(before,reserved,'RECORD_RUNNING')),'ILLEGAL_LIFECYCLE')
        intent=row(state='LAUNCH_INTENT');observed=observation(intent,1,'LIVE',actual=running)
        self.assertEqual(self.check(before,(intent,),after,(running,),(observed,),
            request(before,intent,'RECORD_RUNNING')),'READY')
        self.assertEqual(self.check(before,(intent,),after,(running,),
            (replace(observed,invocation=b'wrong'),),request(before,intent,'RECORD_RUNNING')),'ILLEGAL_LIFECYCLE')
    def test_uncertain_launch_is_held_and_can_later_be_established(self):
        intent=row(state='LAUNCH_INTENT');uncertain=replace(intent,state='SETTLEMENT_UNKNOWN')
        before=state(1,held=10);after=state(2,held=10)
        self.assertEqual(self.check(before,(intent,),after,(uncertain,),(observation(intent,1),),
            request(before,intent,'RETAIN_UNCERTAIN')),'READY')
        running=row(state='RUNNING',effect=True)
        self.assertEqual(self.check(after,(uncertain,),state(3,held=10),(running,),
            (observation(uncertain,2,'LIVE',actual=running),),request(after,uncertain,'RECORD_RUNNING')),'READY')
    def test_unknown_and_live_cannot_free_capacity(self):
        running=row(state='RUNNING',effect=True);released=replace(running,state='RELEASED')
        before=state(1,held=10)
        for live in ('UNKNOWN','LIVE'):
            with self.subTest(liveness=live):
                self.assertEqual(self.check(before,(running,),state(2),(released,),
                    (observation(running,1,live),),request(before,running,'RELEASE_HOLD')),'ILLEGAL_LIFECYCLE')
    def test_terminal_release_exactly_once_and_historical_zero_retained(self):
        terminal=row(state='TERMINAL',effect=True);released=replace(terminal,state='RELEASED')
        before=state(1,held=10);after=state(2)
        self.assertEqual(self.check(before,(terminal,),after,(released,),
            (observation(terminal,1,'REAPED'),),request(before,terminal,'RELEASE_HOLD')),'READY')
        self.assertEqual(self.check(after,(released,),state(3),(released,),
            (observation(released,2,'REAPED'),),request(after,released,'RELEASE_HOLD')),'ILLEGAL_LIFECYCLE')
        other=row(b'other',epoch=2)
        self.assertEqual(self.check(after,(released,),state(3,held=10),(other,),
            (observation(released,2,'REAPED'),),request(after,other)),'HISTORICAL_ROW_REMOVED')
    def test_never_launched_release_uses_independent_observation(self):
        reserved=row();released=replace(reserved,state='RELEASED');before=state(1,held=10)
        self.assertEqual(self.check(before,(reserved,),state(2),(released,),
            (observation(reserved,1,'NEVER_LAUNCHED'),),request(before,reserved,'RELEASE_HOLD')),'READY')
        self.assertEqual(self.check(before,(reserved,),state(2),(released,),
            (observation(reserved,1),),request(before,reserved,'RELEASE_HOLD')),'ILLEGAL_LIFECYCLE')
    def test_all_sibling_children_must_fit_parent(self):
        parent=row(b'parent',amount=20);one=row(b'one',amount=12,parent=b'parent')
        two=row(b'two',amount=12,parent=b'parent',epoch=1);before=state(1,held=20)
        self.assertEqual(self.check(before,(parent,one),state(2,held=20),(parent,one,two),
            (observation(parent,1),observation(one,1)),request(before,two)),'PARENT_INVALID')
        two=replace(two,amount=7)
        self.assertEqual(self.check(before,(parent,one),state(2,held=20),(parent,one,two),
            (observation(parent,1),observation(one,1)),request(before,two)),'READY')
    def test_observed_parent_overage_does_not_enlarge_child_grant(self):
        parent=replace(row(b'parent',amount=20),observed_usage=30)
        one=row(b'one',amount=12,parent=b'parent')
        two=row(b'two',amount=12,parent=b'parent',epoch=1)
        before=state(1,held=30,capacity=40)
        self.assertEqual(self.check(before,(parent,one),state(2,held=30,capacity=40),(parent,one,two),
            (observation(parent,1),observation(one,1)),request(before,two)),'PARENT_INVALID')
    def test_parent_cannot_release_while_a_descendant_is_held(self):
        parent=row(b'parent',amount=20,state='TERMINAL',effect=True)
        child=row(b'child',amount=10,parent=b'parent',state='SETTLEMENT_UNKNOWN',effect=True)
        child=replace(child,cgroup=b'/owned/parent/child')
        before=state(1,held=20);released=replace(parent,state='RELEASED')
        self.assertEqual(self.check(before,(parent,child),state(2),(released,child),
            (observation(parent,1,'REAPED'),observation(child,1)),request(before,parent,'RELEASE_HOLD')),'PARENT_INVALID')
        done=replace(child,state='RELEASED')
        self.assertEqual(self.check(before,(parent,child),state(2,held=20),(parent,done),
            (observation(parent,1,'REAPED'),observation(child,1)),request(before,child,'RELEASE_HOLD')),'ILLEGAL_LIFECYCLE')
    def test_parent_must_exist_earlier_and_actual_cgroup_must_be_contained(self):
        parent=row(b'parent',amount=20,state='RUNNING',effect=True)
        child=row(b'child',parent=b'parent',epoch=1)
        before=state(1,held=20)
        self.assertEqual(self.check(before,(parent,),state(2,held=20),(child,parent),
            (observation(parent,1,'LIVE'),),request(before,child)),'PARENT_INVALID')
        intent=replace(child,state='LAUNCH_INTENT',planned_unit=b'worldline-child.service')
        running=replace(intent,state='RUNNING',actual_unit=b'worldline-child.service',
            cgroup=b'/owned/parent-escape',invocation=b'child-invocation')
        self.assertEqual(self.check(before,(parent,intent),state(2,held=20),(parent,running),
            (observation(parent,1,'LIVE'),observation(intent,1,'LIVE',actual=running)),
             request(before,intent,'RECORD_RUNNING')),'PARENT_INVALID')
    def test_budget_charge_stays_counted_and_never_uses_capacity_release(self):
        terminal=row(kind='IRREVERSIBLE_BUDGET',state='TERMINAL',effect=True)
        charged=replace(terminal,state='CHARGED');before=state(1,charged=10)
        after=state(2,charged=10)
        self.assertEqual(self.check(before,(terminal,),after,(charged,),
            (observation(terminal,1,'REAPED'),),request(before,terminal,'CHARGE_BUDGET')),'READY')
        self.assertEqual(self.check(after,(charged,),state(3),(replace(charged,state='RELEASED'),),
            (observation(charged,2,'REAPED'),),request(after,charged,'RELEASE_HOLD')),'INVALID_PROPOSED')
    def test_capacity_and_charged_budget_joint_limit(self):
        charged=row(b'budget',kind='IRREVERSIBLE_BUDGET',state='CHARGED',effect=True)
        hold=row(b'hold',epoch=1,amount=12);before=state(1,charged=10)
        self.assertEqual(self.check(before,(charged,),state(2,held=12,charged=10),(charged,hold),
            (observation(charged,1,'REAPED'),),request(before,hold)),'CAPACITY_EXCEEDED')
    def test_complete_native_roster_and_all_full_binding_fields(self):
        before=state(1,held=10);item=row();intent=replace(item,state='LAUNCH_INTENT',planned_unit=b'unit')
        req=request(before,item,'RECORD_LAUNCH_INTENT');obs=observation(item,1)
        self.assertEqual(self.check(before,(item,),state(2,held=10),(intent,),(),req),'NATIVE_ROSTER_INVALID')
        for field in ('reservation','operation','owner','workload','universe_head','capability','grant_use','payload','provenance'):
            with self.subTest(field=field):
                bad=replace(obs,bound=replace(obs.bound,**{field:b'wrong'}))
                self.assertEqual(self.check(before,(item,),state(2,held=10),(intent,),(bad,),req),'NATIVE_ROSTER_INVALID')
    def test_context_absence_and_mismatch_refuse(self):
        before=state(1,held=10);item=row();intent=replace(item,state='LAUNCH_INTENT',planned_unit=b'unit')
        for field in ('universe','policy','resource','unit','instance','host','boot','authority'):
            with self.subTest(field=field):
                req=replace(request(before,item,'RECORD_LAUNCH_INTENT'),scope=replace(SCOPE,**{field:None}))
                self.assertEqual(self.check(before,(item,),state(2,held=10),(intent,),(observation(item,1),),req),'REQUEST_INVALID')
                req=replace(req,scope=replace(SCOPE,**{field:b'wrong'}))
                self.assertEqual(self.check(before,(item,),state(2,held=10),(intent,),(observation(item,1),),req),'CONTEXT_CHANGED')
    def test_epoch_above_machine_word_and_large_magnitude_remain_exact(self):
        for epoch,next_epoch in ((BEYOND_WORD,BEYOND_WORD_NEXT),(LARGE,LARGE_NEXT)):
            with self.subTest(epoch=epoch):
                before=state(epoch,capacity=LARGE);item=row(epoch=epoch,amount=LARGE)
                self.assertEqual(self.check(before,(),state(next_epoch,held=LARGE,capacity=LARGE),(item,),(),request(before,item)),'READY')
                self.assertEqual(self.check(before,(),state(next_epoch,held=LARGE,capacity=LARGE),(item,),(),
                    replace(request(before,item),expected_epoch=0)),'STALE_EPOCH')
    def test_signed_zero_padding_and_typed_absence_survive_native_wire(self):
        before=state(0);item=row(amount=0);after=state(1)
        owned=self.kernel.prepare(before=before,before_rows=(),proposed=after,proposed_rows=(item,),observed=(),request=request(before,item))
        arena_bytes=bytes(owned.arena[:owned.arena_length])+bytes((0,0))
        arena=(C.c_uint8*len(arena_bytes)).from_buffer_copy(arena_bytes)
        first=owned.arena_length+1
        for epoch in (owned.packet.before_state.resource_epoch,owned.packet.intent.expected_epoch,
                      owned.packet.intent.bound.resource_epoch,owned.packet.intent.new_row.bound.resource_epoch,
                      owned.proposed_rows[0].bound.resource_epoch):
            epoch.value.negative=1;epoch.value.first=first;epoch.value.length=2
        result=RawResult()
        code=self.kernel.call(C.byref(owned.packet),C.sizeof(owned.packet),arena,len(arena_bytes),
            owned.before_rows,0,owned.proposed_rows,1,owned.native,0,C.byref(result),C.sizeof(result))
        self.assertEqual(code,0);self.assertEqual(STATUS[result.status],'READY')
        owned.packet.intent.expected_epoch.present=0
        untouched=RawResult(123)
        code=self.kernel.call(C.byref(owned.packet),C.sizeof(owned.packet),arena,len(arena_bytes),
            owned.before_rows,0,owned.proposed_rows,1,owned.native,0,C.byref(untouched),C.sizeof(untouched))
        self.assertEqual(code,-1);self.assertEqual(untouched.status,123)
    def test_owned_caller_roundtrip_has_no_decimal_size_cap_or_fallback(self):
        before=state(LARGE,capacity=LARGE)
        self.assertEqual(restore_dto(dto_record(before)),before)
        with self.assertRaises(CoreUnavailable):ResourceRunLedgerKernel(SimpleNamespace(_lib=object()))
        with self.assertRaises(ValueError):self.kernel.prepare(before=before,before_rows=[],proposed=before,
            proposed_rows=(),observed=(),request=request(before,row()))

if __name__=='__main__':unittest.main()
