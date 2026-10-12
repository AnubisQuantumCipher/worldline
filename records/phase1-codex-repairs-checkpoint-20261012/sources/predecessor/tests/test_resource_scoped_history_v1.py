"""Actual-library scoped value/transport controls; source only, all UNRUN.

Fixtures here are data, never protected custody or genuine OS observations.
Complete protected runtime, historical replay, native actor policy/caller/cost
proof and genuine positive all-operation/parent/follow-up campaigns stay OPEN.
Numeric specimen values are the unchanged original JACKAL exact fixtures.
"""
import ctypes as C
from dataclasses import replace
import os
from types import SimpleNamespace
import unittest
from worldline import resource_scoped_run_ledger as S
from worldline import resource_run_ledger as L
from test_resource_run_ledger_v1 import SCOPE,row,state,request,BEYOND_WORD,BEYOND_WORD_NEXT,LARGE,LARGE_NEXT
from test_resource_os_observation_v1 import captured,held

NEW_SCOPE=replace(SCOPE,policy=b'new-policy',policy_epoch=1)
KEY=S.PhysicalKey(machine=SCOPE.host,resource=SCOPE.resource,unit=SCOPE.unit)


def frame(scope=SCOPE,*,epoch=0,head=b'frame-original',prior=None,uhead=b'universe-head',roots=0,roothead=b'roots-genesis'):
    return S.ScopeFrame(scope=scope,first_epoch=epoch,universe_head=uhead,frame_head=head,prior_frame=prior,
        store_genesis=b'owner-store-genesis',store_id=b'finalization-store',root_head=roothead,prime=None,
        root_count=roots,cause=b'authentic-cause-fixture',requester=b'owner',receipt=b'authentic-receipt-fixture',
        catalogue_head=b'catalogue-original',observation_head=b'complete-current-source-fixture')


def scoped(epoch,*,scope=SCOPE,head=b'ledger-before',hhead=b'frame-original',uhead=b'universe-head',physical=b'physical-source'):
    return S.ScopedState(current=scope,resource_epoch=epoch,universe_head=uhead,ledger_head=head,
                         history_head=hhead,physical_head=physical)


def current(before,latest,*,scope=None,uhead=None,hhead=None,physical=None):
    return S.CurrentObservation(scope=scope or before.current,resource_epoch=before.resource_epoch,
        universe_head=uhead or before.universe_head,ledger_head=before.ledger_head,
        history_head=hhead or before.history_head,physical_head=physical or before.physical_head,
        store_genesis=latest.store_genesis,store_id=latest.store_id,root_head=latest.root_head,
        prime=latest.prime,root_count=latest.root_count,cause=latest.cause,requester=latest.requester,
        receipt=latest.receipt,catalogue_head=latest.catalogue_head,observation_head=latest.observation_head)


def projection(item,amount=None):
    return S.PhysicalProjection(key=KEY,bound=item.bound,origin=item.scope,catalogue_head=b'catalogue-original',
        numerator=1,denominator=1,amount=item.amount if amount is None else amount)


def bucket(held=0,capacity=20):
    return S.PhysicalBucket(key=KEY,capacity=capacity,held_total=held,charged_total=0,
        capacity_source=b'actual-capacity-source-fixture',catalogue_head=b'catalogue-original',
        observation_head=b'complete-current-source-fixture')


def intent(before,original,*,kind='ORDINARY',cause=None):
    return S.ScopedIntent(kind=kind,original=original,expected_epoch=before.resource_epoch,
        expected_ledger_head=before.ledger_head,request_id=original.request_id,
        cause=cause or original.operation_id,requester=original.requester,receipt=b'authentic-receipt-fixture')


def packet(before,history,rows,p,b,after,ph,pr,pp,pb,c,r,facts,observed):
    return S.ScopedPacket(before=before,history=tuple(history),rows=tuple(rows),projection=tuple(p),buckets=tuple(b),
        proposed=after,proposed_history=tuple(ph),proposed_rows=tuple(pr),proposed_projection=tuple(pp),
        proposed_buckets=tuple(pb),actual_buckets=tuple(pb),facts=tuple(facts),observed=tuple(observed),
        current=c,request=r)


class ResourceScopedHistoryV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kernel=S.ScopedRunLedgerKernel(SimpleNamespace(_lib=C.CDLL(os.environ['WORLDLINE_CORE_LIB'])))

    def rollover(self):
        old=row();before=scoped(BEYOND_WORD);oldf=frame()
        newf=frame(NEW_SCOPE,epoch=BEYOND_WORD_NEXT,head=b'frame-new',prior=oldf.frame_head,
                   uhead=b'universe-new',roots=1,roothead=b'roots-after-original-init')
        after=scoped(BEYOND_WORD_NEXT,scope=NEW_SCOPE,head=b'ledger-after',hhead=newf.frame_head,uhead=newf.universe_head)
        c=current(before,newf,scope=NEW_SCOPE,uhead=newf.universe_head,hhead=newf.frame_head)
        orig=request(state(BEYOND_WORD),old,'RETAIN_UNCERTAIN')
        r=intent(before,orig,kind='ADVANCE_CONTEXT',cause=newf.cause)
        facts=captured(state(BEYOND_WORD),old,current=NEW_SCOPE,current_epoch=BEYOND_WORD,
            current_universe_head=newf.universe_head,current_ledger_head=before.ledger_head)
        observed=L.RunObservation(scope=old.scope,resource_epoch=before.resource_epoch,bound=old.bound,
            actual_unit=None,cgroup=None,invocation=None,observation_head=facts.observation_head,observed='UNKNOWN')
        return packet(before,(oldf,),(old,),(projection(old),),(bucket(held=10),),after,(oldf,newf),
            (old,),(projection(old),),(bucket(held=10),),c,r,(facts,),(observed,))

    def test_rollover_keeps_reserved_row_full_amount_old_scope_and_no_prime_nonempty_roots(self):
        p=self.rollover()
        self.assertEqual(self.kernel.decide(p).status,'READY')
        self.assertIsNone(p.current.prime)
        self.assertEqual(p.proposed_rows,p.rows)
        self.assertNotEqual(p.rows[0].scope,p.proposed.current)

    def test_full_quantity_magnitude_survives_rollover_physical_charge_without_word_narrowing(self):
        p=self.rollover();large=replace(p.rows[0],amount=LARGE)
        physical=replace(p.buckets[0],capacity=LARGE,held_total=LARGE)
        q=replace(p,rows=(large,),proposed_rows=(large,),projection=(projection(large),),
            proposed_projection=(projection(large),),buckets=(physical,),proposed_buckets=(physical,),
            actual_buckets=(physical,))
        self.assertEqual(self.kernel.decide(q).status,'READY')

    def test_whole_physical_projection_refuses_hidden_retained_charge(self):
        p=self.rollover();other=row(b'other-retained')
        q=replace(p,rows=(*p.rows,other),proposed_rows=(*p.rows,other),
            projection=(*p.projection,projection(other)),proposed_projection=(*p.projection,projection(other)),
            observed=(*p.observed,replace(p.observed[0],bound=other.bound)),
            facts=(*p.facts,replace(p.facts[0],retained=other.bound)))
        self.assertEqual(self.kernel.decide(q).status,'INVALID_BEFORE')

    def test_missing_frame_epoch_is_named_invalid_snapshot_without_variant_exception(self):
        p=self.rollover();h=(replace(p.history[0],first_epoch=None),)
        p=replace(p,history=h)
        self.assertEqual(self.kernel.decide(p).status,'INVALID_BEFORE')

    def test_history_frame_cannot_reuse_immutable_head_or_rewrite_old_root(self):
        p=self.rollover()
        self.assertEqual(self.kernel.decide(replace(p,proposed_history=(p.history[0],
            replace(p.proposed_history[-1],frame_head=p.history[0].frame_head)),
            proposed=replace(p.proposed,history_head=p.history[0].frame_head))).status,'INVALID_PROPOSED')
        changed=replace(p.history[0],root_head=b'changed-old-roots')
        self.assertEqual(self.kernel.decide(replace(p,proposed_history=(changed,p.proposed_history[-1]))).status,
                         'CONTEXT_ADVANCE_INVALID')

    def test_rollover_cannot_drop_physical_hold_or_replace_original_projection(self):
        p=self.rollover()
        self.assertEqual(self.kernel.decide(replace(p,proposed_rows=(),proposed_projection=(),
            proposed_buckets=(bucket(),),actual_buckets=(bucket(),))).status,'HISTORICAL_ROW_CHANGED')
        changed=replace(p.proposed_projection[0],catalogue_head=b'new-unbound-catalogue')
        self.assertEqual(self.kernel.decide(replace(p,proposed_projection=(changed,))).status,
                         'PHYSICAL_PROJECTION_INVALID')

    def release(self):
        old=row(state='TERMINAL',effect=True);oldf=frame()
        newf=frame(NEW_SCOPE,epoch=BEYOND_WORD_NEXT,head=b'frame-new',prior=oldf.frame_head,
                   uhead=b'universe-new',roots=1,roothead=b'roots-after-original-init')
        before=scoped(LARGE,scope=NEW_SCOPE,hhead=newf.frame_head,uhead=newf.universe_head)
        after=replace(before,resource_epoch=LARGE_NEXT,ledger_head=b'after-historical-release')
        c=current(before,newf);released=replace(old,state='RELEASED')
        orig=replace(request(state(LARGE),old,'RELEASE_HOLD'),expected_ledger_head=before.ledger_head)
        r=intent(before,orig)
        facts=held(replace(state(LARGE),scope=NEW_SCOPE,universe_head=before.universe_head,
            ledger_head=before.ledger_head),old,phase='NAMESPACE_CLOSED',dispatch=b'protected-dispatch',
            current=NEW_SCOPE,
            actual_unit=old.actual_unit,cgroup=old.cgroup,invocation=old.invocation,
            protocol=b'CLOSED_ECHILD',closed_event=b'complete-closed-event',namespace_wait=b'PIDFD_TERMINAL',
            helper_wait=b'PIDFD_TERMINAL',cgroup_events=b'populated 0\nfrozen 0\n')
        observed=L.RunObservation(scope=old.scope,resource_epoch=before.resource_epoch,bound=old.bound,
            actual_unit=old.actual_unit,cgroup=old.cgroup,invocation=old.invocation,
            observation_head=facts.observation_head,observed='REAPED')
        return packet(before,(oldf,newf),(old,),(projection(old),),(bucket(held=10),),
            after,(oldf,newf),(released,),(projection(released,amount=0),),(bucket(),),c,r,(facts,),(observed,))

    def test_historical_terminal_release_under_different_current_policy_uses_exact_old_binding(self):
        p=self.release()
        self.assertEqual(self.kernel.decide(p).status,'READY')
        self.assertNotEqual(p.request.original.scope,p.before.current)
        self.assertEqual(p.request.original.bound,p.rows[0].bound)

    def test_unknown_descendants_do_not_release_old_hold(self):
        p=self.release()
        bad=replace(p.facts[0],phase='UNAVAILABLE',protocol=None,closed_event=None)
        unknown=replace(p.observed[0],observed='UNKNOWN')
        self.assertEqual(self.kernel.decide(replace(p,facts=(bad,),observed=(unknown,))).status,'ILLEGAL_LIFECYCLE')

    def test_fresh_launch_cannot_borrow_an_old_context(self):
        p=self.release();old=replace(p.rows[0],state='RESERVED',planned_unit=None,actual_unit=None,cgroup=None,invocation=None)
        launched=replace(old,state='LAUNCH_INTENT',planned_unit=b'new-child.service')
        orig=replace(p.request.original,kind='RECORD_LAUNCH_INTENT')
        f=replace(p.facts[0],retained=old.bound,phase='UNAVAILABLE')
        obs=replace(p.observed[0],bound=old.bound,observed='UNKNOWN',actual_unit=None,cgroup=None,invocation=None)
        q=replace(p,rows=(old,),projection=(projection(old),),proposed_rows=(launched,),
            proposed_projection=(projection(launched),),proposed_buckets=p.buckets,actual_buckets=p.buckets,
            request=replace(p.request,original=orig),facts=(f,),observed=(obs,))
        self.assertEqual(self.kernel.decide(q).status,'CONTEXT_CHANGED')

    def test_complete_native_input_rosters_are_copied_before_output_alias(self):
        p=self.rollover();raw,arena,length,rosters=self.kernel.prepare(p)
        args=[C.byref(raw),C.sizeof(raw),arena,length]
        for _name,owned,count in rosters:args.extend((owned,count))
        args.extend((C.byref(raw),C.sizeof(L.RawResult)))
        code=self.kernel.call(*args)
        self.assertEqual(code,0)
        result=C.cast(C.byref(raw),C.POINTER(L.RawResult)).contents
        self.assertEqual(S.SCOPED_STATUSES[result.status],'READY')
