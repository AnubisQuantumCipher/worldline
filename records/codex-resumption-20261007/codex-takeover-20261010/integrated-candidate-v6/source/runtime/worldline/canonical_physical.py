"""Owned full native exchange caller, selected mapped library only.

There is no executable selector, subprocess service, fixed evaluation array,
caller authority flag or fallback library. Foreign pointer/readability, syscall
correspondence and native/body/cost proofs remain full original obligations.
"""
import ctypes as C
import os
from .core import CCollapseRequest,HASH_BYTES
from .protected_startup import require,protected
from .errors import CoreUnavailable
class Entry(C.Structure):
    _fields_=[('present',C.c_uint8),('device',C.c_uint64),('inode',C.c_uint64)]
class Request(C.Structure):
    _fields_=[('collapse_facts',CCollapseRequest),('expected_live',Entry),('observed_live',Entry),
        ('expected_stage',Entry),('observed_stage',Entry),('expected_marker_digest',C.c_uint8*HASH_BYTES),
        ('observed_marker_digest',C.c_uint8*HASH_BYTES),('payload_durable',C.c_uint8),('recovery_clean',C.c_uint8)]
class Witness(C.Structure):
    _fields_=[('live_before',Entry),('stage_before',Entry),('live_after',Entry),('stage_after',Entry),
        ('marker_digest',C.c_uint8*HASH_BYTES),('decision',C.c_uint8),('exchange_attempted',C.c_uint8),('syscall_errno',C.c_int)]
def raw(value):return C.string_at(C.byref(value),C.sizeof(value))
def entry(path):
    protected(path,directory=True);info=path.stat()
    return Entry(1,info.st_dev,info.st_ino)
class FullPhysicalActuator:
    def __init__(self,principal):
        self.p=principal
        try:
            version=principal.core._lib.wl_full_physical_version_v1
            layout=principal.core._lib.wl_full_physical_layout_v1
            self.call=principal.core._lib.wl_full_physical_exchange_v1
        except AttributeError as exc:raise CoreUnavailable('selected full physical native boundary unavailable') from exc
        version.argtypes,version.restype=[],C.c_uint32
        layout.argtypes,layout.restype=[C.c_uint32,C.c_uint32],C.c_long
        require(version()==1,'FULL_PHYSICAL_VERSION_CHANGED')
        for kind,typ in enumerate((Entry,Request,Witness),1):
            require(layout(kind,0)==C.sizeof(typ) and layout(kind,1)==C.alignment(typ),'FULL_PHYSICAL_LAYOUT_CHANGED')
            for field,(name,_type) in enumerate(typ._fields_,2):
                require(layout(kind,field)==getattr(typ,name).offset,'FULL_PHYSICAL_FIELD_CHANGED')
        self.call.argtypes=[C.c_int]*3+[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t]+[C.c_void_p,C.c_size_t,C.c_size_t]*8+[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t]
        self.call.restype=C.c_int
    def exchange(self,peer,data,transaction,prepared,expected_live,expected_stage,marker):
        self.p.intact();peer.observation()
        request=Request(prepared[0].operation_input.collapse,expected_live,entry(data/'live'),expected_stage,
            entry(transaction/'mapping'),(C.c_uint8*HASH_BYTES).from_buffer_copy(marker),
            (C.c_uint8*HASH_BYTES).from_buffer_copy(self.p.core.hash_bytes((transaction/'mapping'/'.worldline-generation.json').read_bytes())),1,1)
        # payload_durable/recovery_clean are established by the selected producer
        # before this caller, retained in the complete native intent. They are not
        # endpoint fields or authorization decisions. The C boundary recaptures.
        raw_input,arena,storage,rosters=prepared;witness=Witness()
        fds=[]
        try:
            for path in (data,transaction):
                protected(path,directory=True)
                fds.append(os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC))
            args=[peer.peer.descriptor(),*fds,C.byref(raw_input),C.sizeof(raw_input),storage,len(arena.raw)]
            for roster in rosters:args.extend((roster,len(roster),C.sizeof(roster)))
            args.extend((C.byref(request),C.sizeof(request),C.byref(witness),C.sizeof(witness)))
            status=self.call(*args)
            return {'status':status,'request':raw(request).hex(),'witness':raw(witness).hex()}
        finally:
            for fd in fds:os.close(fd)
