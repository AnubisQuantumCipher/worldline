"""Actual library value/transport controls; source authored, all UNRUN.

These complete fixture facts exercise the value relation. They never establish
protected OS custody. Genuine protected supervisor controls are separate, and
all original full-ledger fixtures remain unchanged and required.
"""
import ctypes as C
from dataclasses import fields,replace
import os
from types import SimpleNamespace
import unittest
from worldline.resource_os_observation import PhysicalFacts,ResourceObservationKernel
from worldline.resource_run_ledger import RunBinding,RawResult,LIVENESS
from test_resource_run_ledger_v1 import SCOPE,row,state,BEYOND_WORD

def captured(before,item,**changes):
    values={field.name:None for field in fields(PhysicalFacts)}
    values.update(current=SCOPE,current_epoch=before.resource_epoch,retained=item.bound,
        current_universe_head=before.universe_head,current_ledger_head=before.ledger_head,
        intent=b'actual-exclusive-intent',observation_head=b'full-owned-observation',phase='UNAVAILABLE')
    values.update(changes);return PhysicalFacts(**values)

def held(before,item,**changes):
    values=dict(dispatch=b'exact-dispatch',actual_unit=item.planned_unit,cgroup=b'/owned/row',invocation=b'actual-invocation',
        namespace=b'owned-namespace',held_namespace=b'owned-namespace',peer=b'kernel-peer',held_peer=b'kernel-peer',
        helper_image=b'actual-image',expected_helper_image=b'actual-image',challenge=b'full-held-challenge',held_challenge=b'full-held-challenge',
        protocol=b'HELD',namespace_wait=b'PIDFD_LIVE',helper_wait=b'PIDFD_LIVE',cgroup_events=b'populated 1\nfrozen 0\n',
        cgroup_type=b'domain\n',manager_delegate=b'no',cgroup_owner=0,cgroup_group_write=0,cgroup_other_write=0,phase='NAMESPACE_HELD')
    values.update(changes);return captured(before,item,**values)

class ResourceOSObservationV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kernel=ResourceObservationKernel(SimpleNamespace(_lib=C.CDLL(os.environ['WORLDLINE_CORE_LIB'])))
    def test_independent_present_genesis_and_full_empty_roster_current_head(self):
        before=state(0);item=row();f=captured(before,item)
        self.assertEqual(self.kernel.current(before,None,f),'CURRENT_READY')
        for name,value in (('current_epoch',None),('current_universe_head',b'other'),('current_ledger_head',b'other'),
                ('current',replace(SCOPE,boot=b'other'))):
            with self.subTest(field=name):self.assertEqual(self.kernel.current(before,None,replace(f,**{name:value})),'CURRENT_REFUSED')
    def test_authentic_empty_store_value_crosswalk_has_typed_absent_prime(self):
        before=state(0);item=row()
        f=captured(before,item,actual_store_genesis=b'actual-store-genesis',owner_store_genesis=b'actual-store-genesis',
            actual_store_id=b'actual-finalization-store-id',owner_store_id=b'actual-finalization-store-id',
            genesis_universe=SCOPE.universe,genesis_instance=SCOPE.instance,genesis_context_head=b'exact-owner-context',
            genesis_root_count=0,genesis_prime=None)
        self.assertEqual(self.kernel.genesis_current(before,None,f),'CURRENT_READY')
        for name,value in (('owner_store_genesis',b'wrong'),('owner_store_id',b'wrong'),('genesis_universe',b'wrong'),
                ('genesis_instance',b'wrong'),('genesis_context_head',None),('genesis_root_count',None),
                ('genesis_root_count',1),('genesis_prime',b'dummy-prime')):
            with self.subTest(field=name):self.assertEqual(self.kernel.genesis_current(before,None,replace(f,**{name:value})),'CURRENT_REFUSED')
    def test_complete_beyond_word_epoch_is_not_narrowed(self):
        before=state(BEYOND_WORD);item=row(epoch=BEYOND_WORD);f=captured(before,item,phase='NEVER_DISPATCHED')
        self.assertEqual(self.kernel.current(before,None,f),'CURRENT_READY')
        self.assertEqual(self.kernel.classify(before,item,f),'NEVER_LAUNCHED')
    def test_exclusive_never_dispatched_retains_independent_absence(self):
        before=state(0);item=row();f=captured(before,item,phase='NEVER_DISPATCHED')
        self.assertEqual(self.kernel.classify(before,item,f),'NEVER_LAUNCHED')
        for name,value in (('phase','UNAVAILABLE'),('dispatch',b'old-receipt'),('intent',None),('protocol',b'HELD'),
                ('actual_unit',b'claimed-unit'),('retained',replace(item.bound,owner=b'wrong'))):
            with self.subTest(field=name):self.assertEqual(self.kernel.classify(before,item,replace(f,**{name:value})),'UNKNOWN')
    def test_complete_owned_held_value_and_every_custody_mismatch(self):
        before=state(0);item=row(state='LAUNCH_INTENT');f=held(before,item)
        self.assertEqual(self.kernel.classify(before,item,f),'LIVE')
        for name,value in (('held_namespace',b'wrong'),('held_peer',b'wrong'),('expected_helper_image',b'wrong'),
                ('held_challenge',b'wrong'),('actual_unit',b'wrong'),('manager_delegate',b'yes'),('cgroup_owner',None),
                ('cgroup_group_write',1),('namespace_wait',b'PIDFD_TERMINAL'),('cgroup_events',None),('cgroup_type',b'threaded\n')):
            with self.subTest(field=name):self.assertEqual(self.kernel.classify(before,item,replace(f,**{name:value})),'UNKNOWN')
    def test_empty_cgroup_or_launcher_wait_does_not_establish_closure(self):
        before=state(0);item=row(state='LAUNCH_INTENT');f=held(before,item,cgroup_events=b'populated 0\nfrozen 0\n',helper_wait=b'PIDFD_TERMINAL')
        self.assertEqual(self.kernel.classify(before,item,f),'UNKNOWN')
        self.assertEqual(self.kernel.classify(before,item,replace(f,namespace_wait=b'PIDFD_TERMINAL')),'UNKNOWN')
    def test_closed_full_tuple_requires_echild_both_terminals_and_measured_empty(self):
        before=state(0);item=row(state='RUNNING',effect=True)
        f=held(before,item,cgroup=item.cgroup,invocation=item.invocation,phase='NAMESPACE_CLOSED',protocol=b'CLOSED_ECHILD',
            closed_event=b'authenticated-complete-closed-event',namespace_wait=b'PIDFD_TERMINAL',helper_wait=b'PIDFD_TERMINAL',
            cgroup_events=b'frozen 0\npopulated 0\n')
        self.assertEqual(self.kernel.classify(before,item,f),'REAPED')
        for name,value in (('closed_event',None),('protocol',b'CLOSED'),('helper_wait',b'PIDFD_LIVE'),
                ('namespace_wait',b'PIDFD_LIVE'),('cgroup_events',None),('cgroup_events',b'populated 1\nfrozen 0\n'),
                ('invocation',b'wrong'),('cgroup',b'wrong')):
            with self.subTest(field=name):self.assertEqual(self.kernel.classify(before,item,replace(f,**{name:value})),'UNKNOWN')
    def test_original_signed_zero_and_padding_semantics_in_real_native_current(self):
        before=state(0);item=row();f=captured(before,item);packet,arena,length=self.kernel.prepare(before,item,f)
        packet.captured.current_epoch.value.negative=1
        answer=RawResult()
        code=self.kernel.current_call(C.byref(packet),C.sizeof(packet),arena,length,C.byref(answer),C.sizeof(answer))
        self.assertEqual((code,answer.status),(0,1))
        # A separate complete padded zero span remains zero; arena ownership is
        # retained by this raw control rather than rewritten by DTO canonicalization.
        original=bytes(arena[:length]);padded=original+b'\0\0';owned=(C.c_uint8*len(padded)).from_buffer_copy(padded)
        packet.captured.current_epoch.value.first=length+1;packet.captured.current_epoch.value.length=2
        code=self.kernel.current_call(C.byref(packet),C.sizeof(packet),owned,len(padded),C.byref(answer),C.sizeof(answer))
        self.assertEqual((code,answer.status),(0,1))
    def test_actual_native_ownership_before_input_output_alias(self):
        before=state(0);item=row();f=captured(before,item,phase='NEVER_DISPATCHED');packet,arena,length=self.kernel.prepare(before,item,f)
        code=self.kernel.call(C.byref(packet),C.sizeof(packet),arena,length,C.byref(packet),C.sizeof(RawResult))
        self.assertEqual(code,0);self.assertEqual(LIVENESS[C.cast(C.byref(packet),C.POINTER(RawResult)).contents.status],'NEVER_LAUNCHED')
