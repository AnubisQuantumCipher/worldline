"""Exact owned all-operation C ABI. No Python authorization/counter fallback."""
from __future__ import annotations
import ctypes as C
from .errors import CoreUnavailable
from .core import C_HASH,HASH_BYTES
from .chain_authority import _Digest,_Row,_digest,_api
from . import recovery_authority_kernel_v3 as RV
OPS=('ping', 'status', 'list', 'show', 'log.verify', 'init', 'root.add', 'root.remove', 'root.list', 'fork', 'race', 'graph', 'log', 'why', 'inspect', 'switch', 'collapse.prepare', 'collapse.commit', 'transaction.commit', 'transaction.abort', 'transaction.list', 'transaction.show', 'return.prepare', 'job.cancel', 'simulate', 'doctor', 'adapters', 'ghost.enable', 'ghost.disable', 'ghost.status', 'ghost.run', 'shell.info', 'prune', 'anchor.status', 'revalidate', 'validation.status', 'return.services', 'return.terminals', 'return.windows', 'automatic.ghosts', 'quarantine.resolve')
FIELDS=('operation_id', 'request_id', 'transaction', 'universe_head', 'instance', 'root_set', 'prime', 'policy', 'requirement', 'issuer', 'issuer_head', 'grant_id', 'use_id', 'reservation', 'resource_head', 'receipt_genesis', 'receipt_head', 'causal_genesis', 'causal_head', 'input_snapshot', 'kernel_build', 'kernel_library', 'kernel_mapping', 'provenance', 'target', 'quarantine_head', 'original_operation')
STATES=('RESERVED','EFFECT_OBSERVED','SETTLED','RELEASED','QUARANTINED')
COMMANDS=('RESERVE_USE','OBSERVE_EFFECT','SETTLE_USE','RELEASE_USE','RESOLVE_NO_EFFECT','RESOLVE_EFFECT','REPLAY_USE','QUARANTINE_USE','RESOLVE_RECOVERY','CHECK_GRANTS','AUTHORIZE_FOLLOWUP','AUTHORIZE_EXECUTION')
DECISIONS=('REFUSED','RESERVED_NEW','RESERVED_REPLAY','EFFECT_ACCEPTED','SETTLED_NEW','SETTLED_REPLAY','RELEASED_NEW','RELEASED_REPLAY','RESOLVED_NO_EFFECT','RESOLVED_EFFECT','QUARANTINED_NEW','OWNER_ABORT','OWNER_SETTLE','GRANTS_VALID','FOLLOWUP_READY','EXECUTION_READY')
class Quantity(C.Structure):
    _fields_=[('present',C.c_uint8),('negative',C.c_uint8),('first',C.c_int64),('length',C.c_int64)]
class UID(C.Structure):
    _fields_=[('present',C.c_uint8),('value',C.c_uint32)]
class Binding(C.Structure):
    _fields_=[('action',C.c_uint8),('id',_Digest*len(FIELDS))]+[(name,UID) for name in ('peer','preparer','owner','target_owner')]+[(name,Quantity) for name in ('policy_epoch','resource_epoch')]
class Grant(C.Structure):
    _fields_=[(name,_Digest) for name in ('id','parent','issuer','instance','root_set','policy')]+[(name,UID) for name in ('subject','owner')]+[('allowed',C.c_uint8*len(OPS)),('state',C.c_uint8)]+[(name,Quantity) for name in ('epoch','ceiling','issued_at','expires_at')]
class Use(C.Structure):
    _fields_=[('bound',Binding),('state',C.c_uint8)]
class Evidence(C.Structure):
    _fields_=[('effect_binding',Binding),('actual_receipt_root',_Digest),('actual_causal_root',_Digest),('no_effect_binding',Binding),('owner_resolution',Binding)]+[(name,_Digest) for name in ('quarantine_head','witnessed_receipt_head','witnessed_causal_head')]+[('recovery',RV.Request),('original_use',_Digest)]
    _fields_ += [('effect_material_first',C.c_int64),('effect_material_length',C.c_int64)]
class Input(C.Structure):
    _fields_=[('schema',C.c_uint32),('mode',C.c_uint8),('bound',Binding),('now',Quantity),('facts',Evidence)]
class Result(C.Structure):
    _fields_=[('disposition',C.c_uint8)]
def keys(value,expected):
    if type(value) is not dict or set(value)!=set(expected):raise ValueError('exact complete operation DTO keys required')
    return value
def digest(value):
    if value is None:return _Digest()
    if type(value) is not str or bytes.fromhex(value).hex()!=value:raise ValueError('canonical complete digest required')
    return _digest(bytes.fromhex(value))
def uid(value):
    if value is None:return UID()
    if type(value) is not int or value<0 or C.c_uint32(value).value!=value:raise ValueError('complete native uid_t required')
    return UID(1,value)
class Arena:
    def __init__(self):self.raw=bytearray()
    def quantity(self,value):
        if value is None:return Quantity(0,0,1,0)
        value=keys(value,('negative','raw'))
        if type(value['negative']) is not bool or type(value['raw']) is not str:raise ValueError('lossless optional quantity required')
        raw=bytes.fromhex(value['raw'])
        if raw.hex()!=value['raw']:raise ValueError('canonical LE quantity bytes required')
        first=len(self.raw)+1;self.raw.extend(raw)
        if C.c_int64(first).value!=first or C.c_int64(len(raw)).value!=len(raw):raise ValueError('quantity storage extent unavailable')
        return Quantity(1,int(value['negative']),first,len(raw))
    def material(self,value):
        if value is None:return (1,0)
        if type(value) is not str:raise ValueError('lossless effect material bytes required')
        raw=bytes.fromhex(value)
        if raw.hex()!=value:raise ValueError('canonical effect material byte encoding required')
        first=len(self.raw)+1
        if C.c_int64(first).value!=first or C.c_int64(len(raw)).value!=len(raw):raise ValueError('effect material storage extent unavailable')
        self.raw.extend(raw)
        return (first,len(raw))
    def binding(self,value):
        keys(value,('action','id','peer','preparer','owner','target_owner','policy_epoch','resource_epoch'))
        keys(value['id'],FIELDS)
        if type(value['action']) is not str or value['action'] not in OPS:raise ValueError('unknown operation')
        return Binding(OPS.index(value['action']),(_Digest*len(FIELDS))(*(digest(value['id'][f]) for f in FIELDS)),*(uid(value[f]) for f in ('peer','preparer','owner','target_owner')),*(self.quantity(value[f]) for f in ('policy_epoch','resource_epoch')))
    def grant(self,value):
        keys(value,('id','parent','issuer','instance','root_set','policy','subject','owner','allowed','state','epoch','ceiling','issued_at','expires_at'))
        if type(value['allowed']) is not list or len(value['allowed'])!=len(OPS) or any(type(x) is not bool for x in value['allowed']):raise ValueError('complete ordered native rights roster required')
        if value['state'] not in ('ACTIVE','REVOKED'):raise ValueError('grant lifecycle unknown')
        return Grant(*(digest(value[f]) for f in ('id','parent','issuer','instance','root_set','policy')),uid(value['subject']),uid(value['owner']),(C.c_uint8*len(OPS))(*value['allowed']),('ACTIVE','REVOKED').index(value['state']),*(self.quantity(value[f]) for f in ('epoch','ceiling','issued_at','expires_at')))
class OperationAuthorityKernel:
    def __init__(self,core):
        self.core=core
        try:
            version=core._lib.wl_operation_authority_version_v1;layout=core._lib.wl_operation_authority_layout_v1
            self.call=core._lib.wl_operation_authority_decide_v1
        except AttributeError as exc:raise CoreUnavailable('complete native operation authority unavailable') from exc
        version.argtypes,version.restype=[],C.c_uint32
        layout.argtypes,layout.restype=[C.c_uint32,C.c_uint32],C.c_long
        if version()!=2:raise CoreUnavailable('operation authority version differs')
        for kind,typ in enumerate((Quantity,UID,Binding,Grant,Use,Evidence,Input,Result),1):
            if layout(kind,0)!=C.sizeof(typ) or layout(kind,1)!=C.alignment(typ):raise CoreUnavailable('operation authority size/alignment differs')
            for field,(name,_type) in enumerate(typ._fields_,2):
                if layout(kind,field)!=getattr(typ,name).offset:raise CoreUnavailable('operation authority field offset differs')
        RV.RecoveryAuthorityKernelV3(core) # every nested full-domain recovery ABI field
        _api(core) # independently verify every shared digest/chain ABI field
        self.call.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t]+[C.c_void_p,C.c_size_t,C.c_size_t]*4+[C.c_void_p,C.c_size_t]
        self.call.restype=C.c_int
    def prepare(self,snapshot,command,*,arena=None):
        keys(snapshot,('binding','grants','uses','now','evidence','receipts','events'))
        if command not in COMMANDS:raise ValueError('unknown operation transition')
        arena=Arena() if arena is None else arena;bound=arena.binding(snapshot['binding']);facts=snapshot['evidence']
        keys(facts,('effect_binding','actual_receipt_root','actual_causal_root','no_effect_binding','owner_resolution','quarantine_head','witnessed_receipt_head','witnessed_causal_head','recovery','original_use','effect_material'))
        recovery=keys(facts['recovery'],('issued','recovered','historical','native'))
        if recovery['historical'] not in RV.HISTORICAL:raise ValueError('historical native redecision class required')
        historical=RV.Request(3,1,1,RV.HISTORICAL.index(recovery['historical']),0,
            RV.RecoveryAuthorityKernelV3._binding(recovery['issued'],arena.raw),RV.RecoveryAuthorityKernelV3._binding(recovery['recovered'],arena.raw),
            RV.RecoveryAuthorityKernelV3._native(recovery['native']))
        evidence=Evidence(arena.binding(facts['effect_binding']),digest(facts['actual_receipt_root']),digest(facts['actual_causal_root']),arena.binding(facts['no_effect_binding']),arena.binding(facts['owner_resolution']),*(digest(facts[f]) for f in ('quarantine_head','witnessed_receipt_head','witnessed_causal_head')),historical,digest(facts['original_use']))
        evidence.effect_material_first,evidence.effect_material_length=arena.material(facts['effect_material'])
        request=Input(1,COMMANDS.index(command),bound,arena.quantity(snapshot['now']),evidence)
        arrays=[]
        for name,typ in (('grants',Grant),('uses',Use),('receipts',_Row),('events',_Row)):
            values=snapshot[name]
            if type(values) is not list:raise ValueError('complete ordered roster required')
            items=[]
            for value in values:
                if name=='grants':items.append(arena.grant(value))
                elif name=='uses':
                    keys(value,('bound','state'))
                    if value['state'] not in STATES:raise ValueError('use state unknown')
                    items.append(Use(arena.binding(value['bound']),STATES.index(value['state'])))
                else:
                    fields=('previous','actual_payload_root','stored_payload_root','stored_head');keys(value,fields)
                    items.append(_Row(*(digest(value[f]) for f in fields)))
            arrays.append((typ*len(items))(*items))
        return request,arena,arrays
    def observe(self,snapshot,command):
        request,arena,arrays=self.prepare(snapshot,command)
        raw=(C.c_uint8*len(arena.raw)).from_buffer_copy(arena.raw);result=Result()
        args=[C.byref(request),C.sizeof(request),raw,len(arena.raw)]
        for array in arrays:args.extend((array,len(array),C.sizeof(array)))
        args.extend((C.byref(result),C.sizeof(result)))
        if self.call(*args)!=0 or result.disposition>=len(DECISIONS):raise CoreUnavailable('complete operation native transport refused')
        return {'decision':DECISIONS[result.disposition],'input':C.string_at(C.byref(request),C.sizeof(request)).hex(),'arena':bytes(arena.raw).hex(),'rosters':[C.string_at(a,C.sizeof(a)).hex() for a in arrays],'output':C.string_at(C.byref(result),C.sizeof(result)).hex()}
