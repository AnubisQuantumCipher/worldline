"""Real-library native value controls; authored only, UNBUILT and UNRUN.

These full input fixtures do not attest a Linux process, protected task journal,
issuer or parent. Genuine original child-world/runtime controls remain required.
"""
import copy
import ctypes as C
from dataclasses import fields,replace
import os
from types import SimpleNamespace
import unittest
from worldline import resource_child_execution as J
from worldline.resource_child_schema import ProcessObservation,RootController,TaskOrigin,NamespaceObservation
from worldline import resource_scoped_run_ledger as S
from test_resource_actor_execution_v1 import specimen
from test_resource_scoped_history_v1 import projection

def full_child(requester=0,*,epoch=None,action="fork"):
    p,actor,caps,groups,proc_groups,w,a=specimen(requester)
    a=copy.deepcopy(a)
    for binding in (a['binding'],a['uses'][0]['bound'],a['evidence']['owner_resolution']):
        binding['action']=action
        if action=='fork':
            binding['id']['prime']=binding['id']['instance']
            binding['id']['requirement']=binding['id']['instance']
        elif action=='init':binding['target_owner']=requester
    root=p.rows[0]
    if epoch is not None:
        from worldline.protected_operations import quantity
        root=replace(root,bound=replace(root.bound,resource_epoch=epoch))
        before=replace(p.before,resource_epoch=epoch)
        old=replace(p.history[0],first_epoch=epoch)
        now=replace(p.current,resource_epoch=epoch)
        facts=replace(p.facts[0],current_epoch=epoch,retained=root.bound)
        observed=replace(p.observed[0],resource_epoch=epoch,bound=root.bound)
        p=replace(p,before=before,proposed=before,history=(old,),proposed_history=(old,),current=now,
          rows=(root,),proposed_rows=(root,),facts=(facts,),observed=(observed,),projection=(projection(root),),proposed_projection=(projection(root),))
        w=replace(w,resource_current=now)
        for binding in (a['binding'],a['uses'][0]['bound'],a['evidence']['owner_resolution']):binding['resource_epoch']=quantity(epoch)
    cb=replace(root.bound,reservation=b'child-reservation',operation=b'child-task',workload=b'complete-original-workload',payload=b'complete-original-payload')
    child=replace(root,bound=cb,parent=root.bound.reservation,cgroup=root.cgroup+b'/child',
        planned_unit=b'owned-child-unit',actual_unit=b'owned-child-unit',invocation=b'actual-child-invocation')
    actor=replace(actor,bound=cb)
    cf=replace(p.facts[0],retained=cb,actual_unit=child.actual_unit,cgroup=child.cgroup,invocation=child.invocation,
        namespace=actor.namespace,held_namespace=actor.namespace)
    co=replace(p.observed[0],bound=cb,actual_unit=child.actual_unit,cgroup=child.cgroup,invocation=child.invocation)
    p=replace(p,rows=(root,child),proposed_rows=(root,child),projection=(projection(root),projection(child)),
        proposed_projection=(projection(root),projection(child)),facts=(p.facts[0],cf),observed=(p.observed[0],co))
    pv={field.name:0 if field.type=='int' else b'full-root-'+field.name.encode() for field in fields(ProcessObservation)}
    pv.update(host_pid=7,namespace=b'actual-root-namespace',cgroup=root.cgroup,actual_unit=root.actual_unit,
        invocation=root.invocation,source_lease=actor.source_lease,pidfd_wait=b'PIDFD_LIVE')
    process=ProcessObservation(**pv)
    root_facts=replace(p.facts[0],namespace=process.namespace,held_namespace=process.namespace)
    p=replace(p,facts=(root_facts,p.facts[1]))
    rv={field.name:b'full-root-'+field.name.encode() for field in fields(RootController)}
    rv.update(bound=root.bound,process=process,requester_uid=requester,requester_gid=actor.requester_gid,
        source_lease=actor.source_lease,worker_image=p.facts[0].helper_image,handler_plan=w.selected_plan,
        raw_request=w.original_request,requester=w.original_requester,dispatch=p.facts[0].dispatch,
        store_genesis=p.current.store_genesis,current_source=w.current_source)
    for actual,expected in (('owner_endpoint','expected_owner_endpoint'),('source_lease','expected_source_lease'),
       ('worker_image','expected_worker_image'),('handler_plan','expected_handler_plan'),('running_event','expected_running_event'),('store_genesis','expected_store_genesis')):rv[expected]=rv[actual]
    controller=RootController(**rv)
    # Complete task/world/workload records remain independent factual inputs.
    tv={field.name:b'full-task-'+field.name.encode() for field in fields(TaskOrigin)}
    tv.update(action=action,root=root.bound,child=cb,task_id=cb.operation,root_world=None,child_world=b'actual-created-child-world',
        original_workload=cb.workload,raw_request=w.original_request,requester=w.original_requester,
        owner_plan=actor.executable_plan,root_dispatch=controller.dispatch,root_running_event=controller.running_event,
        source_lease=controller.source_lease,cause=p.request.cause,stdin=b'',mission=b'')
    task=TaskOrigin(**tv)
    av={field.name:0 if field.type=='int' else b'full-child-'+field.name.encode() for field in fields(ProcessObservation)}
    av.update(host_pid=actor.host_pid,parent_pid=process.host_pid,parent_start_tick=process.start_tick,
        raw_status=actor.raw_proc_status,raw_cgroup=actor.raw_proc_cgroup,raw_maps=actor.raw_proc_maps,
        raw_cmdline=actor.raw_proc_cmdline,raw_pidfd_info=actor.raw_pidfd_info,namespace=actor.namespace,
        source_lease=controller.source_lease,pidfd_wait=b'PIDFD_LIVE',actual_unit=child.actual_unit,
        cgroup=child.cgroup,invocation=child.invocation,real_uid=actor.real_uid,effective_uid=actor.effective_uid,
        saved_uid=actor.saved_uid,real_gid=actor.real_gid,effective_gid=actor.effective_gid,saved_gid=actor.saved_gid)
    processes=(process,ProcessObservation(**av))
    namespaces=(NamespaceObservation(identity=process.namespace,parent=None,raw_nsfs=b'root-nsfs',raw_get_parent=b'actual-root-parent-query',source_lease=controller.source_lease),
      NamespaceObservation(identity=actor.namespace,parent=process.namespace,raw_nsfs=b'child-nsfs',raw_get_parent=b'actual-parent-fd-query',source_lease=controller.source_lease))
    return p,actor,caps,groups,proc_groups,controller,task,(task,),processes,namespaces,w,a

class NativeChildAuthorityV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.kernel=J.ResourceChildExecutionKernel(SimpleNamespace(_lib=C.CDLL(os.environ['WORLDLINE_CORE_LIB'])))
    def test_full_distinct_child_under_effectful_running_root_uid_zero_and_nonzero(self):
        for uid in (0,7):
            with self.subTest(uid=uid):self.assertEqual(self.kernel.child(*full_child(uid)).status,'CHILD_READY_CONJUNCTION')
    def test_root_is_privileged_controller_not_confined_actor_and_retains_genesis(self):
        for epoch in (None,0):
            v=full_child(epoch=epoch,action="init")
            self.assertEqual(self.kernel.root_controller(v[0],v[5],v[-2],v[-1]).status,'ROOT_READY_CONJUNCTION')
    def test_original_none_world_and_nonempty_created_child_are_independent(self):
        v=full_child(action='init');self.assertIsNone(v[6].root_world);self.assertIsNotNone(v[6].child_world)
        self.assertEqual(self.kernel.child(*v).status,'CHILD_READY_CONJUNCTION')
    def test_reserved_or_unknown_parent_is_not_running_authority(self):
        for phase in ('RESERVED','SETTLEMENT_UNKNOWN'):
            v=list(full_child());root=v[0].rows[0]
            root=replace(root,state=phase,planned_unit=None if phase=='RESERVED' else root.planned_unit,
                actual_unit=None,cgroup=None,invocation=None)
            v[0]=replace(v[0],rows=(root,v[0].rows[1]),proposed_rows=(root,v[0].rows[1]))
            self.assertNotEqual(self.kernel.child(*v).status,'CHILD_READY_CONJUNCTION')
    def test_sibling_cgroup_full_parent_contract_not_relabelled(self):
        v=list(full_child());child=replace(v[0].rows[1],cgroup=b'/sibling-service')
        v[0]=replace(v[0],rows=(v[0].rows[0],child),proposed_rows=(v[0].rows[0],child))
        self.assertNotEqual(self.kernel.child(*v).status,'CHILD_READY_CONJUNCTION')
    def test_child_execution_requires_actual_reserved_and_launch_history_facts(self):
        for field in ('task_reservation_event','task_launch_event'):
            v=list(full_child());task=replace(v[6],**{field:None});v[6]=task;v[7]=(task,)
            self.assertEqual(self.kernel.child(*v).status,'TASK_REFUSED')
    def test_current_grant_revocation_refuses_even_full_matching_task_records(self):
        v=list(full_child());a=copy.deepcopy(v[-1]);a['grants'][0]['state']='REVOKED';v[-1]=a
        self.assertEqual(self.kernel.child(*v).status,'AUTHORITY_REFUSED')
    def test_complete_task_membership_and_all_physical_ancestry_are_required(self):
        for index,value in ((7,()),(8,()),(9,())):
            v=list(full_child());v[index]=value
            self.assertNotEqual(self.kernel.child(*v).status,'CHILD_READY_CONJUNCTION')
        v=list(full_child());v[6]=replace(v[6],stdin=b'changed full retained stdin')
        self.assertEqual(self.kernel.child(*v).status,'TASK_REFUSED')
        v=list(full_child());v[8]=(v[8][0],replace(v[8][1],parent_pid=0))
        self.assertEqual(self.kernel.child(*v).status,'PROCESS_ANCESTRY_REFUSED')
        v=list(full_child());v[9]=(v[9][0],replace(v[9][1],parent=b'foreign-namespace'))
        self.assertEqual(self.kernel.child(*v).status,'NAMESPACE_ANCESTRY_REFUSED')
    def test_prelaunch_reservation_is_full_native_transition_without_a_new_use(self):
        from test_resource_run_ledger_v1 import BEYOND_WORD_NEXT
        v=full_child();p,root,child=v[0],v[0].rows[0],v[0].rows[1]
        reserved=replace(child,state='RESERVED',planned_unit=None,actual_unit=None,cgroup=None,invocation=None)
        before=replace(p,rows=(root,),projection=(projection(root),),facts=(p.facts[0],),observed=(p.observed[0],))
        after=replace(p.before,resource_epoch=BEYOND_WORD_NEXT,ledger_head=b'actual-task-proposed-head')
        request=replace(p.request.original,kind='RESERVE',scope=root.scope,expected_epoch=p.before.resource_epoch,
          expected_ledger_head=p.before.ledger_head,reservation=child.bound.reservation,operation_id=child.bound.operation,
          requester=child.bound.owner,bound=child.bound,new_row=reserved)
        packet=replace(before,proposed=after,proposed_rows=(root,reserved),proposed_projection=(projection(root),projection(reserved)),
          request=replace(p.request,original=request,cause=child.bound.operation))
        task=replace(v[6],cause=child.bound.operation,task_reservation_event=None,task_launch_event=None)
        result=self.kernel.task_reservation(packet,v[5],task,(task,),v[-2],v[-1])
        self.assertEqual(result.status,'TASK_READY_CONJUNCTION')
        self.assertEqual(len(v[-1]['uses']),len(full_child()[-1]['uses']))
        changed=replace(reserved,parent=None)
        packet=replace(packet,proposed_rows=(root,changed),request=replace(packet.request,original=replace(request,new_row=changed)))
        self.assertNotEqual(self.kernel.task_reservation(packet,v[5],task,(task,),v[-2],v[-1]).status,'TASK_READY_CONJUNCTION')
    def test_root_body_copies_full_frames_before_output_alias_and_signed_zero(self):
        v=full_child();owned=self.kernel.prepare('ROOT_CONTROLLER_ADMISSION',v[0],None,(),(),(),v[5],None,(),(),(),v[-2],v[-1])
        actor,data,length,rosters,authority,ad,alen,named,cross,child,extra=owned
        child.controller.requester_uid.negative=1 # Original accepted signed zero.
        args=[C.byref(actor),C.sizeof(actor),data,length]
        for _name,array,count in rosters:args.extend((array,count))
        args.extend((C.byref(authority),C.sizeof(authority),ad,alen))
        for _name,array,count in named:args.extend((array,count))
        args.extend((C.byref(cross),C.sizeof(cross),C.byref(child),C.sizeof(child)))
        for _name,array,count in extra:args.extend((array,count))
        args.extend((C.byref(authority),C.sizeof(S.L.RawResult)))
        self.assertEqual(self.kernel.call(*args),0)
        result=C.cast(C.byref(authority),C.POINTER(S.L.RawResult)).contents
        self.assertEqual(J.STATUSES[result.status],'ROOT_READY_CONJUNCTION')
