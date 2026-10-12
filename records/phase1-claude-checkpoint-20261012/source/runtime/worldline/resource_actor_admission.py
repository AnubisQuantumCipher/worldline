"""Owned full actual-library credential conjunct, data does not grant permission."""
from __future__ import annotations
import ctypes as C
from dataclasses import dataclass,fields
from . import resource_scoped_run_ledger as S
from . import resource_run_ledger as L
from .errors import CoreUnavailable

STATUSES=('READY_CONJUNCT','INVALID_LEDGER','INVALID_NATIVE_ROSTER','RUNNING_ROW_ABSENT',
          'BINDING_MISMATCH','REQUESTER_MISMATCH','SOURCE_MISMATCH','CREDENTIAL_INVALID',
          'ISOLATION_NOT_ESTABLISHED')
@dataclass(frozen=True,slots=True,kw_only=True)
class ActorNativeObservation:
    bound: L.RunBinding
    raw_frame: bytes
    raw_sender: bytes
    ticket: bytes
    raw_proc_status: bytes
    raw_proc_cgroup: bytes
    raw_proc_maps: bytes
    raw_proc_cmdline: bytes
    raw_pidfd_info: bytes
    namespace: bytes
    held_namespace: bytes
    helper_image: bytes
    expected_helper_image: bytes
    executable_plan: bytes
    expected_executable_plan: bytes
    original_requester: bytes
    requester_credentials: bytes
    expected_requester_credentials: bytes
    dispatch: bytes
    running_event: bytes
    expected_running_event: bytes
    canonical_use_event: bytes
    expected_canonical_use_event: bytes
    store_genesis: bytes
    expected_store_genesis: bytes
    source_lease: bytes
    expected_source_lease: bytes
    actor_wait: bytes
    helper_wait: bytes
    namespace_wait: bytes
    host_pid: int
    namespace_pid: int
    sender_uid: int
    sender_gid: int
    real_uid: int
    effective_uid: int
    saved_uid: int
    real_gid: int
    effective_gid: int
    saved_gid: int
    capability_version: int
    effective_low: int
    permitted_low: int
    inheritable_low: int
    effective_high: int
    permitted_high: int
    inheritable_high: int
    securebits: int
    no_new_privs: int
    requester_uid: int
    requester_gid: int
    configured_requester_uid: int
    workload_uid: int
    workload_gid: int
    proc_host_pid: int
    proc_namespace_pid: int
    proc_real_uid: int
    proc_effective_uid: int
    proc_saved_uid: int
    proc_real_gid: int
    proc_effective_gid: int
    proc_saved_gid: int
    proc_effective: int
    proc_permitted: int
    proc_inheritable: int
    proc_bounding: int
    proc_ambient: int
    proc_no_new_privs: int
    proc_fs_uid: int
    proc_fs_gid: int

@dataclass(frozen=True,slots=True)
class ActorCapability:
    index:int
    bounding:int
    ambient:int

class RawActorObservation(C.Structure):
    _fields_=[
        ('bound',L.RawBinding),
        ('raw_frame',L.RawId),
        ('raw_sender',L.RawId),
        ('ticket',L.RawId),
        ('raw_proc_status',L.RawId),
        ('raw_proc_cgroup',L.RawId),
        ('raw_proc_maps',L.RawId),
        ('raw_proc_cmdline',L.RawId),
        ('raw_pidfd_info',L.RawId),
        ('namespace',L.RawId),
        ('held_namespace',L.RawId),
        ('helper_image',L.RawId),
        ('expected_helper_image',L.RawId),
        ('executable_plan',L.RawId),
        ('expected_executable_plan',L.RawId),
        ('original_requester',L.RawId),
        ('requester_credentials',L.RawId),
        ('expected_requester_credentials',L.RawId),
        ('dispatch',L.RawId),
        ('running_event',L.RawId),
        ('expected_running_event',L.RawId),
        ('canonical_use_event',L.RawId),
        ('expected_canonical_use_event',L.RawId),
        ('store_genesis',L.RawId),
        ('expected_store_genesis',L.RawId),
        ('source_lease',L.RawId),
        ('expected_source_lease',L.RawId),
        ('actor_wait',L.RawId),
        ('helper_wait',L.RawId),
        ('namespace_wait',L.RawId),
        ('host_pid',L.RawQuantity),
        ('namespace_pid',L.RawQuantity),
        ('sender_uid',L.RawQuantity),
        ('sender_gid',L.RawQuantity),
        ('real_uid',L.RawQuantity),
        ('effective_uid',L.RawQuantity),
        ('saved_uid',L.RawQuantity),
        ('real_gid',L.RawQuantity),
        ('effective_gid',L.RawQuantity),
        ('saved_gid',L.RawQuantity),
        ('capability_version',L.RawQuantity),
        ('effective_low',L.RawQuantity),
        ('permitted_low',L.RawQuantity),
        ('inheritable_low',L.RawQuantity),
        ('effective_high',L.RawQuantity),
        ('permitted_high',L.RawQuantity),
        ('inheritable_high',L.RawQuantity),
        ('securebits',L.RawQuantity),
        ('no_new_privs',L.RawQuantity),
        ('requester_uid',L.RawQuantity),
        ('requester_gid',L.RawQuantity),
        ('configured_requester_uid',L.RawQuantity),
        ('workload_uid',L.RawQuantity),
        ('workload_gid',L.RawQuantity),
        ('proc_host_pid',L.RawQuantity),
        ('proc_namespace_pid',L.RawQuantity),
        ('proc_real_uid',L.RawQuantity),
        ('proc_effective_uid',L.RawQuantity),
        ('proc_saved_uid',L.RawQuantity),
        ('proc_real_gid',L.RawQuantity),
        ('proc_effective_gid',L.RawQuantity),
        ('proc_saved_gid',L.RawQuantity),
        ('proc_effective',L.RawQuantity),
        ('proc_permitted',L.RawQuantity),
        ('proc_inheritable',L.RawQuantity),
        ('proc_bounding',L.RawQuantity),
        ('proc_ambient',L.RawQuantity),
        ('proc_no_new_privs',L.RawQuantity),
        ('proc_fs_uid',L.RawQuantity),
        ('proc_fs_gid',L.RawQuantity),
    ]
class RawActorCapability(C.Structure):
    _fields_=[('index',L.RawQuantity),('bounding',L.RawQuantity),('ambient',L.RawQuantity)]
class RawActorPacket(C.Structure):
    _fields_=[('ledger',S.RawScopedPacket),('captured',RawActorObservation)]

# Extends only the declared owned-schema framing, never public eager callbacks.
S._KNOWN.update({ActorNativeObservation.__name__:ActorNativeObservation,
                 ActorCapability.__name__:ActorCapability})

class ActorAdmissionKernel:
    def __init__(self,core):
        self.scoped=S.ScopedRunLedgerKernel(core)
        try:
            version=core._lib.wl_resource_actor_admission_version_v1
            layout=core._lib.wl_resource_actor_admission_layout_v1
            self.call=core._lib.wl_resource_actor_admission_check_v1
        except AttributeError as error:raise CoreUnavailable('actor native credential conjunct unavailable') from error
        version.argtypes,version.restype=[],C.c_uint32
        layout.argtypes,layout.restype=[C.c_uint32,C.c_uint32],C.c_long
        if version()!=1:raise CoreUnavailable('actor native ABI version differs')
        for kind,typ in enumerate((RawActorObservation,RawActorCapability,RawActorPacket)):
            if layout(kind,0)!=C.sizeof(typ) or layout(kind,1)!=C.alignment(typ):
                raise CoreUnavailable('actor native ABI layout differs')
            for selector,(field,_kind) in enumerate(typ._fields_,2):
                if layout(kind,selector)!=getattr(typ,field).offset:
                    raise CoreUnavailable('actor native ABI field differs',field=field)
        self.call.argtypes=[C.c_void_p,C.c_size_t]*(len(S._ROSTERS)+6)
        self.call.restype=C.c_int
    def prepare(self,packet,observation,capabilities,groups,proc_groups):
        if (type(observation) is not ActorNativeObservation or type(capabilities) is not tuple
            or any(type(row) is not ActorCapability for row in capabilities)):
            raise ValueError('complete typed actor/native source required')
        raw,old_arena,length,rosters=self.scoped.prepare(packet)
        arena=bytearray(bytes(old_arena)[:length]);captured=RawActorObservation()
        for field,kind in captured._fields_:
            value=getattr(observation,field)
            if kind is L.RawBinding:datum=L._marshal('Binding',value,arena)
            elif kind is L.RawId:datum=L._id(value,arena)
            else:datum=L._quantity(value,arena)
            setattr(captured,field,datum)
        caps=(RawActorCapability*len(capabilities))()
        for index,row in enumerate(capabilities):
            caps[index]=RawActorCapability(*(L._quantity(getattr(row,field),arena)
                                           for field,_kind in RawActorCapability._fields_))
        extra=[('capabilities',caps,len(capabilities))]
        for name,values in (('groups',groups),('proc_groups',proc_groups)):
            if type(values) is not tuple or any(type(value) is not int for value in values):
                raise ValueError('complete actor group roster required')
            owned=(L.RawQuantity*len(values))()
            for index,value in enumerate(values):owned[index]=L._quantity(value,arena)
            extra.append((name,owned,len(values)))
        data=(C.c_uint8*max(1,len(arena)))()
        if arena:C.memmove(data,bytes(arena),len(arena))
        raw_packet=RawActorPacket(raw,captured);result=L.RawResult()
        all_rosters=(*rosters,*extra)
        return raw_packet,data,len(arena),all_rosters
    def check(self,packet,observation,capabilities,groups,proc_groups):
        raw_packet,data,length,all_rosters=self.prepare(packet,observation,capabilities,groups,proc_groups)
        result=L.RawResult()
        arguments=[C.byref(raw_packet),C.sizeof(raw_packet),data,L._extent(length)]

        for _name,owned,count in all_rosters:arguments.extend((owned,L._extent(count)))
        arguments.extend((C.byref(result),C.sizeof(result)))
        transport=self.call(*arguments)
        if transport!=0:raise CoreUnavailable('actor native complete transport refused')
        if result.status>=len(STATUSES):raise CoreUnavailable('actor native result malformed')
        return S.ScopedNativeDecision('wl_resource_actor_admission_check_v1',STATUSES[result.status],
            bytes(raw_packet),bytes(data)[:length],tuple((name,bytes(owned),count) for name,owned,count in all_rosters),
            bytes(result),transport)
