"""Complete real-library value controls, authored only and UNRUN.

Independent fixture values are never kernel observations or protected grants.
The complete canonical frozen dependency must be explicitly composed before
these controls can be run. Genuine actor/physical/custody campaigns remain
separate required positive and fault obligations.
"""
import copy
import ctypes as C
from dataclasses import fields,replace
import os
from types import SimpleNamespace
import unittest
from worldline.core import HASH_BYTES
from worldline import resource_scoped_run_ledger as S
from worldline import resource_actor_admission as K
from worldline import resource_actor_execution as E
from worldline.operation_authority_kernel import FIELDS,OPS
from worldline.protected_operations import empty_evidence,quantity
from test_resource_run_ledger_v1 import SCOPE,row,state,request,BEYOND_WORD
from test_resource_scoped_history_v1 import frame,scoped,current,projection,bucket,intent,packet
from test_resource_os_observation_v1 import held


def specimen(requester=0):
    # Hash extent is the original observed ABI constant. These are deliberately
    # synthetic full value fixtures, not issuer signatures or a READY flag.
    identity=b'\x01'*HASH_BYTES;scope=replace(SCOPE,instance=identity)
    item=row(state='RUNNING',effect=True,epoch=BEYOND_WORD)
    bound=replace(item.bound,reservation=identity,operation=identity,owner=b'original-full-requester',
        workload=identity,universe_head=identity,capability=identity,grant_use=identity,
        payload=identity,provenance=identity)
    item=replace(item,scope=scope,bound=bound)
    f=frame(scope,uhead=identity);before=scoped(BEYOND_WORD,scope=scope,head=identity,uhead=identity)
    now=current(before,f)
    facts=held(replace(state(BEYOND_WORD),scope=scope,universe_head=identity,ledger_head=identity),item,
        current=scope,current_epoch=BEYOND_WORD,current_universe_head=identity,current_ledger_head=identity,
        actual_unit=item.actual_unit,cgroup=item.cgroup,invocation=item.invocation)
    observed=S.L.RunObservation(scope=scope,resource_epoch=BEYOND_WORD,bound=bound,
        actual_unit=item.actual_unit,cgroup=item.cgroup,invocation=item.invocation,
        observation_head=facts.observation_head,observed='LIVE')
    original=replace(request(state(BEYOND_WORD),item,'UNKNOWN_OPERATION'),scope=scope,
        expected_ledger_head=identity)
    p=packet(before,(f,),(item,),(projection(item),),(bucket(held=item.amount),),
        before,(f,),(item,),(projection(item),),(bucket(held=item.amount),),now,intent(before,original),
        (facts,),(observed,))
    names={field.name:0 if field.type=='int' else b'complete-fixture-'+field.name.encode()
        for field in fields(K.ActorNativeObservation)}
    names.update(bound=bound,host_pid=2,namespace_pid=2,proc_host_pid=2,proc_namespace_pid=2,
        requester_uid=requester,configured_requester_uid=requester,requester_gid=0,
        workload_uid=7,workload_gid=7,sender_uid=7,sender_gid=7,
        capability_version=0x20080522,securebits=15,no_new_privs=1,proc_no_new_privs=1,
        original_requester=bound.owner,dispatch=facts.dispatch,namespace=facts.namespace,
        held_namespace=facts.namespace,helper_image=facts.helper_image,expected_helper_image=facts.helper_image,
        actor_wait=b'PIDFD_LIVE',helper_wait=b'PIDFD_LIVE',namespace_wait=b'PIDFD_LIVE')
    for name in ('real_uid','effective_uid','saved_uid','real_gid','effective_gid','saved_gid',
                 'proc_real_uid','proc_effective_uid','proc_saved_uid','proc_real_gid','proc_effective_gid',
                 'proc_saved_gid','proc_fs_uid','proc_fs_gid'):names[name]=7
    for actual,expected in (('executable_plan','expected_executable_plan'),
        ('requester_credentials','expected_requester_credentials'),('running_event','expected_running_event'),
        ('canonical_use_event','expected_canonical_use_event'),('store_genesis','expected_store_genesis'),
        ('source_lease','expected_source_lease')):names[expected]=names[actual]
    actor=K.ActorNativeObservation(**names);capabilities=(K.ActorCapability(0,0,0),)
    binding={'action':'ping','id':dict.fromkeys(FIELDS,identity.hex()),'peer':requester,
        'preparer':None,'owner':requester,'target_owner':None,'policy_epoch':quantity(0),
        'resource_epoch':quantity(BEYOND_WORD)}
    binding['id']['prime']=None;binding['id']['requirement']=None
    grant={'id':identity.hex(),'parent':None,'issuer':identity.hex(),'instance':identity.hex(),
        'root_set':identity.hex(),'policy':identity.hex(),'subject':requester,'owner':requester,
        'allowed':[True for _ in OPS],'state':'ACTIVE','epoch':quantity(0),'ceiling':quantity(16),
        'issued_at':quantity(0),'expires_at':quantity(16)}
    evidence=empty_evidence();evidence['owner_resolution']=copy.deepcopy(binding)
    authority={'binding':binding,'grants':[grant],'uses':[{'bound':copy.deepcopy(binding),'state':'RESERVED'}],
        'now':quantity(0),'evidence':evidence,'receipts':[],'events':[]}
    crosswalk=E.ActorExecutionCrosswalk(resource_current=now,operation_policy=identity,
        operation_root_set=identity,owner_genesis=b'full-owner-genesis-value',installation=b'full-installation-value',
        gate_config=b'full-Gate-config-value',managed_observation=b'full-managed-observation-value',
        original_grant=b'full-grant-value',complete_crosswalk=b'full-crosswalk-value',
        current_source=b'full-current-source-value',original_request=b'full-original-request-value',
        original_requester=bound.owner,original_transaction=None,preparer=None,
        selected_plan=actor.executable_plan)
    return p,actor,capabilities,(),(),crosswalk,authority


class ActorExecutionValueV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        core=SimpleNamespace(_lib=C.CDLL(os.environ['WORLDLINE_CORE_LIB']))
        cls.kernel=E.ActorExecutionKernel(core)

    def test_full_reserved_native_conjunction_keeps_original_uid_zero_and_nonzero(self):
        for uid in (0,7):
            with self.subTest(uid=uid):
                self.assertEqual(self.kernel.check(*specimen(uid)).status,'READY_VALUE_CONJUNCTION')

    def test_matching_event_identity_does_not_substitute_for_revoked_grant(self):
        values=list(specimen());authority=copy.deepcopy(values[-1]);authority['grants'][0]['state']='REVOKED'
        values[-1]=authority
        self.assertEqual(self.kernel.check(*values).status,'AUTHORITY_REFUSED')

    def test_current_epoch_and_full_original_binding_are_independent_required_conjuncts(self):
        for mutate in ('epoch','reservation'):
            values=list(specimen());authority=copy.deepcopy(values[-1])
            if mutate=='epoch':authority['evidence']['owner_resolution']['resource_epoch']=None
            else:
                authority['binding']['id']['reservation']=(b'\x02'*HASH_BYTES).hex()
                authority['uses'][0]['bound']=copy.deepcopy(authority['binding'])
            values[-1]=authority
            with self.subTest(field=mutate):self.assertNotEqual(self.kernel.check(*values).status,'READY_VALUE_CONJUNCTION')

    def test_raw_sender_proc_uid_and_complete_capability_roster_mismatches_refuse(self):
        base=specimen()
        for field,value in (('sender_uid',0),('proc_saved_uid',0),('expected_running_event',b'changed'),
                            ('actor_wait',b'PIDFD_TERMINAL')):
            altered=list(base);altered[1]=replace(altered[1],**{field:value})
            with self.subTest(field=field):self.assertEqual(self.kernel.check(*altered).status,'ACTOR_REFUSED')
        altered=list(base);altered[2]=(K.ActorCapability(0,1,0),)
        self.assertEqual(self.kernel.check(*altered).status,'ACTOR_REFUSED')

    def test_foreign_body_owns_both_complete_frames_before_output_alias(self):
        actor,data,length,rosters,authority,arena,extent,named,crosswalk=self.kernel.prepare(*specimen())
        args=[C.byref(actor),C.sizeof(actor),data,length]
        for _name,owned,count in rosters:args.extend((owned,count))
        args.extend((C.byref(authority),C.sizeof(authority),arena,extent))
        for _name,owned,count in named:args.extend((owned,count))
        args.extend((C.byref(crosswalk),C.sizeof(crosswalk),C.byref(authority),C.sizeof(S.L.RawResult)))
        self.assertEqual(self.kernel.call(*args),0)
        result=C.cast(C.byref(authority),C.POINTER(S.L.RawResult)).contents
        self.assertEqual(E.STATUSES[result.status],'READY_VALUE_CONJUNCTION')
