"""Full owned native root/task/child transport. DTOs supply no custody."""
from __future__ import annotations
import ctypes as C
from dataclasses import dataclass
from . import resource_run_ledger as L
from . import resource_scoped_run_ledger as S
from . import resource_os_observation as O
from . import resource_actor_admission as K
from . import resource_actor_execution as E
from . import operation_authority_kernel as A
from .resource_child_schema import ProcessObservation,RootController,TaskOrigin,NamespaceObservation
from .errors import CoreUnavailable
MODES=('ROOT_CONTROLLER_ADMISSION','CHILD_ADMISSION','TASK_RESERVATION_ADMISSION')
STATUSES=('ROOT_READY_CONJUNCTION','CHILD_READY_CONJUNCTION','LEDGER_REFUSED','AUTHORITY_REFUSED',
 'CURRENT_REFUSED','CONTROLLER_REFUSED','ACTOR_REFUSED','TASK_REFUSED','PARENT_REFUSED',
 'PROCESS_ANCESTRY_REFUSED','NAMESPACE_ANCESTRY_REFUSED','TASK_READY_CONJUNCTION','TASK_TRANSITION_REFUSED')
class RawProcess(C.Structure):
    _fields_=[('raw_status',L.RawId),('raw_stat',L.RawId),('raw_cgroup',L.RawId),('raw_maps',L.RawId),('raw_cmdline',L.RawId),('raw_pidfd_info',L.RawId),('namespace',L.RawId),('cgroup',L.RawId),('actual_unit',L.RawId),('invocation',L.RawId),('source_lease',L.RawId),('pidfd_wait',L.RawId),('host_pid',L.RawQuantity),('start_tick',L.RawQuantity),('parent_pid',L.RawQuantity),('parent_start_tick',L.RawQuantity),('real_uid',L.RawQuantity),('effective_uid',L.RawQuantity),('saved_uid',L.RawQuantity),('real_gid',L.RawQuantity),('effective_gid',L.RawQuantity),('saved_gid',L.RawQuantity)]
class RawController(C.Structure):
    _fields_=[('bound',L.RawBinding),('process',RawProcess),('requester_uid',L.RawQuantity),('requester_gid',L.RawQuantity),('raw_manager',L.RawId),('raw_channel',L.RawId),('owner_endpoint',L.RawId),('expected_owner_endpoint',L.RawId),('source_lease',L.RawId),('expected_source_lease',L.RawId),('worker_image',L.RawId),('expected_worker_image',L.RawId),('handler_plan',L.RawId),('expected_handler_plan',L.RawId),('raw_request',L.RawId),('requester',L.RawId),('dispatch',L.RawId),('running_event',L.RawId),('expected_running_event',L.RawId),('store_genesis',L.RawId),('expected_store_genesis',L.RawId),('current_source',L.RawId)]
class RawTask(C.Structure):
    _fields_=[('action',C.c_uint8),('root',L.RawBinding),('child',L.RawBinding),('task_id',L.RawId),('root_world',L.RawId),('child_world',L.RawId),('root_instance',L.RawId),('child_instance',L.RawId),('world_store',L.RawId),('full_world_ancestry',L.RawId),('original_workload',L.RawId),('sandbox',L.RawId),('adapter',L.RawId),('context',L.RawId),('mission',L.RawId),('stdin',L.RawId),('credential_source',L.RawId),('executable_source',L.RawId),('configuration',L.RawId),('owner_plan',L.RawId),('native_cost_input',L.RawId),('raw_request',L.RawId),('requester',L.RawId),('cause',L.RawId),('root_dispatch',L.RawId),('root_running_event',L.RawId),('task_journal',L.RawId),('task_intent',L.RawId),('task_reservation_event',L.RawId),('task_launch_event',L.RawId),('parent_namespace_source',L.RawId),('fd_lineage',L.RawId),('source_lease',L.RawId)]
class RawNamespace(C.Structure):
    _fields_=[('identity',L.RawId),('parent',L.RawId),('raw_nsfs',L.RawId),('raw_get_parent',L.RawId),('source_lease',L.RawId)]
class RawChildInput(C.Structure):
    _fields_=[('mode',C.c_uint8),('controller',RawController),('task',RawTask)]
@dataclass(frozen=True,slots=True)
class ResourceChildNativeObservation:
    entry_point:str
    mode:str
    status:str
    actor_input:bytes
    resource_arena:bytes
    resource_rosters:tuple[tuple[str,bytes,int],...]
    authority_input:bytes
    authority_arena:bytes
    authority_rosters:tuple[tuple[str,bytes,int],...]
    crosswalk:bytes
    child_input:bytes
    raw_output:bytes
    transport_status:int
_TYPED={ProcessObservation:RawProcess,RootController:RawController,TaskOrigin:RawTask,NamespaceObservation:RawNamespace}
S._KNOWN.update({typ.__name__:typ for typ in (*_TYPED,ResourceChildNativeObservation)})
def _owned(value,arena):
    raw_type=_TYPED.get(type(value))
    if raw_type is None:raise ValueError('complete genuine typed child/controller record required')
    raw=raw_type()
    for name,kind in raw._fields_:
        datum=getattr(value,name)
        if kind is L.RawId:encoded=L._id(datum,arena)
        elif kind is L.RawQuantity:encoded=L._quantity(datum,arena)
        elif kind is L.RawBinding:encoded=L._marshal('Binding',datum,arena)
        elif kind is RawProcess:encoded=_owned(datum,arena)
        else:
            if datum not in A.OPS:raise ValueError('original operation action unavailable')
            encoded=A.OPS.index(datum)
        setattr(raw,name,encoded)
    return raw
_LAYOUT=(
    ('D_Raw_Observation',K.RawActorObservation),
    ('D_Raw_Capability',K.RawActorCapability),
    ('D_Raw_Packet',K.RawActorPacket),
    ('X_Raw_Crosswalk',E.RawExecutionCrosswalk),
    ('W_Raw_Id',L.RawId),
    ('W_Raw_Quantity',L.RawQuantity),
    ('W_Raw_Epoch',L.RawEpoch),
    ('W_Raw_Context',L.RawContext),
    ('W_Raw_Binding',L.RawBinding),
    ('W_Raw_Row',L.RawRow),
    ('W_Raw_State',L.RawState),
    ('W_Raw_Native',L.RawNative),
    ('W_Raw_Request',L.RawRequest),
    ('W_Raw_Packet',None),
    ('W_Raw_Result',L.RawResult),
    ('N_Raw_State',S.RawScopedState),
    ('N_Raw_Scope_Frame',S.RawScopeFrame),
    ('N_Raw_Physical_Key',S.RawPhysicalKey),
    ('N_Raw_Bucket',S.RawPhysicalBucket),
    ('N_Raw_Projection',S.RawPhysicalProjection),
    ('N_Raw_Current_Observation',S.RawCurrentObservation),
    ('N_Raw_Intent',S.RawScopedIntent),
    ('N_Raw_Packet',S.RawScopedPacket),
    ('O_Raw_Facts',O.RawFacts),
    ('O_Raw_Input',O.RawObservationInput),
    ('T_Raw_Quantity',A.Quantity),
    ('T_Raw_UID',A.UID),
    ('T_Raw_Binding',A.Binding),
    ('T_Raw_Grant',A.Grant),
    ('T_Raw_Use',A.Use),
    ('T_Raw_Evidence',A.Evidence),
    ('T_Raw_Input',A.Input),
    ('T_Raw_Result',A.Result),
    ('TC_Raw_Digest',A._Digest),
    ('TC_Raw_Row',A._Row),
    ('TC_Raw_Anchors',None),
    ('TC_Raw_Result',None),
    ('Y_Raw_Process',RawProcess),
    ('Y_Raw_Controller',RawController),
    ('Y_Raw_Task',RawTask),
    ('Y_Raw_Namespace',RawNamespace),
    ('Y_Raw_Input',RawChildInput),
)
class ResourceChildExecutionKernel:
    def __init__(self,core):
        self.authority=A.OperationAuthorityKernel(core)
        try:
            version=core._lib.wl_resource_child_execution_version_v1
            layout=core._lib.wl_resource_child_execution_layout_v1
            self.call=core._lib.wl_resource_child_execution_decide_v1
        except AttributeError as error:raise CoreUnavailable('full native root/task/child conjunction unavailable') from error
        version.argtypes,version.restype=[],C.c_uint32
        layout.argtypes,layout.restype=[C.c_uint32,C.c_uint32],C.c_long
        if version()!=1:raise CoreUnavailable('child native ABI generation differs')
        for kind,(_name,typ) in enumerate(_LAYOUT):
            if typ is None:continue
            if layout(kind,0)!=C.sizeof(typ) or layout(kind,1)!=C.alignment(typ):
                raise CoreUnavailable('full child native layout differs',record=_name)
            for selector,(name,_type) in enumerate(typ._fields_,2):
                if layout(kind,selector)!=getattr(typ,name).offset:
                    raise CoreUnavailable('full child native field differs',record=_name,field=name)
        self.call.argtypes=[C.c_void_p,C.c_size_t]*len(PARAMETERS)
        self.call.restype=C.c_int
    def prepare(self,mode,packet,actor,capabilities,groups,proc_groups,controller,task,tasks,processes,namespaces,crosswalk,authority_snapshot):
        if mode not in MODES:raise ValueError('exact native child mode required')
        if type(packet) is not S.ScopedPacket:raise ValueError('complete scoped packet required')
        arena=bytearray()
        ledger=S.RawScopedPacket(1,S._marshal(packet.before,arena),S._marshal(packet.proposed,arena),
            S._marshal(packet.current,arena),S._marshal(packet.request,arena))
        rosters=[]
        for name,raw_type,data_type in S._ROSTERS:
            values=getattr(packet,name)
            if type(values) is not tuple or any(type(row) is not data_type for row in values):raise ValueError('complete original scoped roster required: '+name)
            array=(raw_type*len(values))()
            for index,row in enumerate(values):
                if data_type is O.PhysicalFacts:encoded=S._facts(row,arena)
                elif data_type in (L.RunRow,L.RunObservation):encoded=L._marshal('Row' if data_type is L.RunRow else 'Native',row,arena)
                else:encoded=S._marshal(row,arena)
                array[index]=encoded
            rosters.append((name,array,len(array)))
        captured=K.RawActorObservation()
        if mode=='CHILD_ADMISSION':
            if type(actor) is not K.ActorNativeObservation:raise ValueError('complete actual actor observation required')
            for name,kind in captured._fields_:
                value=getattr(actor,name)
                encoded=L._marshal('Binding',value,arena) if kind is L.RawBinding else L._id(value,arena) if kind is L.RawId else L._quantity(value,arena)
                setattr(captured,name,encoded)
        elif actor is not None:raise ValueError('root/task admission has typed absent confined actor')
        if type(capabilities) is not tuple or any(type(row) is not K.ActorCapability for row in capabilities):raise ValueError('complete capability roster required')
        caps=(K.RawActorCapability*len(capabilities))()
        for index,row in enumerate(capabilities):caps[index]=K.RawActorCapability(*(L._quantity(getattr(row,name),arena) for name,_kind in K.RawActorCapability._fields_))
        rosters.append(('capabilities',caps,len(caps)))
        for name,values in (('groups',groups),('proc_groups',proc_groups)):
            if type(values) is not tuple or any(type(row) is not int for row in values):raise ValueError('complete group roster required')
            array=(L.RawQuantity*len(values))()
            for index,value in enumerate(values):array[index]=L._quantity(value,arena)
            rosters.append((name,array,len(array)))
        if type(crosswalk) is not E.ActorExecutionCrosswalk:raise ValueError('full original typed crosswalk required')
        cross=E.RawExecutionCrosswalk()
        for name,kind in cross._fields_:
            value=getattr(crosswalk,name)
            if kind is S.RawCurrentObservation:encoded=S._marshal(value,arena)
            elif kind is A._Digest:
                if type(value) is not bytes:raise ValueError('complete operation digest required')
                encoded=A.digest(value.hex())
            else:encoded=L._id(value,arena)
            setattr(cross,name,encoded)
        raw_controller=_owned(controller,arena)
        if mode=='ROOT_CONTROLLER_ADMISSION':
            if task is not None:raise ValueError('root admission has typed absent task')
            raw_task=RawTask()
        else:raw_task=_owned(task,arena)
        child=RawChildInput(MODES.index(mode),raw_controller,raw_task);extra=[]
        for name,values,typ in (('tasks',tasks,TaskOrigin),('processes',processes,ProcessObservation),('namespaces',namespaces,NamespaceObservation)):
            if type(values) is not tuple or any(type(row) is not typ for row in values):raise ValueError('complete retained child roster required: '+name)
            array=(_TYPED[typ]*len(values))()
            for index,value in enumerate(values):array[index]=_owned(value,arena)
            extra.append((name,array,len(array)))
        data=(C.c_uint8*max(1,len(arena)))()
        if arena:C.memmove(data,bytes(arena),len(arena))
        authority,raw_arena,arrays=self.authority.prepare(authority_snapshot,'AUTHORIZE_EXECUTION')
        authority_data=(C.c_uint8*max(1,len(raw_arena.raw)))()
        if raw_arena.raw:C.memmove(authority_data,bytes(raw_arena.raw),len(raw_arena.raw))
        named=tuple((name,array,len(array)) for name,array in zip(('grants','uses','receipts','events'),arrays))
        return K.RawActorPacket(ledger,captured),data,len(arena),tuple(rosters),authority,authority_data,len(raw_arena.raw),named,cross,child,tuple(extra)
    def _decide(self,mode,*values):
        actor,data,length,rosters,authority,authority_data,authority_length,named,cross,child,extra=self.prepare(mode,*values)
        output=L.RawResult();arguments=[C.byref(actor),C.sizeof(actor),data,L._extent(length)]
        for _name,array,count in rosters:arguments.extend((array,L._extent(count)))
        arguments.extend((C.byref(authority),C.sizeof(authority),authority_data,L._extent(authority_length)))
        for _name,array,count in named:arguments.extend((array,L._extent(count)))
        arguments.extend((C.byref(cross),C.sizeof(cross),C.byref(child),C.sizeof(child)))
        for _name,array,count in extra:arguments.extend((array,L._extent(count)))
        arguments.extend((C.byref(output),C.sizeof(output)))
        transport=self.call(*arguments)
        if transport!=0:raise CoreUnavailable('complete child native transport refused')
        if output.status>=len(STATUSES):raise CoreUnavailable('child native result malformed')
        return ResourceChildNativeObservation('wl_resource_child_execution_decide_v1',mode,STATUSES[output.status],
            bytes(actor),bytes(data)[:length],tuple((name,bytes(array),count) for name,array,count in (*rosters,*extra)),
            bytes(authority),bytes(authority_data)[:authority_length],tuple((name,bytes(array),count) for name,array,count in named),
            bytes(cross),bytes(child),bytes(output),transport)
    def root_controller(self,packet,controller,crosswalk,authority_snapshot):
        return self._decide('ROOT_CONTROLLER_ADMISSION',packet,None,(),(),(),controller,None,(),(),(),crosswalk,authority_snapshot)
    def task_reservation(self,packet,controller,task,tasks,crosswalk,authority_snapshot):
        return self._decide('TASK_RESERVATION_ADMISSION',packet,None,(),(),(),controller,task,tasks,(),(),crosswalk,authority_snapshot)
    def child(self,packet,actor,capabilities,groups,proc_groups,controller,task,tasks,processes,namespaces,crosswalk,authority_snapshot):
        return self._decide('CHILD_ADMISSION',packet,actor,capabilities,groups,proc_groups,controller,task,tasks,processes,namespaces,crosswalk,authority_snapshot)
PARAMETERS=('Input', 'Arena', 'History', 'Proposed_History', 'Rows', 'Proposed_Rows', 'Projection', 'Proposed_Projection', 'Buckets', 'Proposed_Buckets', 'Actual_Buckets', 'Observed', 'Facts', 'Capabilities', 'Groups', 'Proc_Groups', 'Authority_Input', 'Authority_Arena', 'Authority_Grants', 'Authority_Uses', 'Authority_Receipts', 'Authority_Events', 'Crosswalk', 'Child_Input', 'Tasks', 'Processes', 'Namespaces', 'Output')
