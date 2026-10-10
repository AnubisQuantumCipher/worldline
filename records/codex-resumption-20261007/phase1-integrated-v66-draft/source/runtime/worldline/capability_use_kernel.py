"""Complete owned native use roster marshalling; DTOs supply no custody."""
from __future__ import annotations
import ctypes as C
from adapter import capabilities,genesis,revocation,universes
from .errors import CoreUnavailable

STATES=('RESERVED','CONSUMED','RELEASED')
KINDS=('LEGACY_CHARGED_USE','BOUND_RESERVATION')
MODES=('RESERVE_USE','CONSUME_USE','RELEASE_USE')
STATUSES=('REFUSED','RESERVED_NEW','RESERVED_REPLAY','CONSUMED_NEW','CONSUMED_REPLAY','RELEASED_NEW','RELEASED_REPLAY')
DIGEST_FIELDS=('capability_id','operation_id','transaction_id','requester_id','universe_head',
               'request_identity','grant_use_identity','recovery_binding_identity')

class Binding(C.Structure):
    _fields_=[(name,genesis.Digest) for name in DIGEST_FIELDS]+[('policy_epoch',C.c_uint64),('action',C.c_int32)]
class Row(C.Structure):
    _fields_=[('kind',C.c_int32),('state',C.c_int32),('bound',Binding),('chain',revocation.Lineage)]
class Input(C.Structure):
    _fields_=[('u',universes.Record),('g',genesis.Universe),('ask',capabilities.CheckInput),
              ('chain',revocation.Lineage),('bound',Binding),('mode',C.c_int32)]
class Result(C.Structure):
    _fields_=[('status',C.c_int32)]

def binding(value):
    value=genesis._keys(value,set(DIGEST_FIELDS)|{'policy_epoch','action'})
    result=Binding()
    for name in DIGEST_FIELDS:setattr(result,name,genesis._digest(value[name]))
    result.policy_epoch=genesis._integer(value['policy_epoch'],C.c_uint64(-1).value)
    if type(value['action']) is not str or value['action'] not in genesis._ACTIONS:
        raise ValueError('use binding action is noncanonical')
    result.action=genesis._ACTIONS[value['action']]
    return result

class UseReservationKernel:
    def __init__(self,native):
        self.native=native
        try:
            version=native.cosmogony_use_reservation_version_v1
            layout=native.cosmogony_use_reservation_layout_v1
            self.call=native.cosmogony_use_reservation_decide_v1
        except AttributeError as exc:raise CoreUnavailable('native capability-use reservation unavailable') from exc
        version.argtypes,version.restype=[],C.c_int32
        layout.argtypes,layout.restype=[C.c_uint32,C.c_uint32],C.c_long
        if version()!=1:raise CoreUnavailable('capability-use reservation version differs')
        for kind,typ in enumerate((Binding,Row,Input,Result,capabilities.Capability,capabilities.CheckInput,
                                     revocation.Lineage,revocation.Link,universes.Record,genesis.Universe,
                                     genesis.Request,universes.Policy,genesis.Agent,capabilities.Scope,
                                     capabilities.Ceiling,capabilities.Usage,genesis.Digest,capabilities.Actions),1):
            if layout(kind,0)!=C.sizeof(typ) or layout(kind,1)!=C.alignment(typ):
                raise CoreUnavailable('capability-use reservation size/alignment differs')
            for field,(name,_type) in enumerate(typ._fields_,2):
                if layout(kind,field)!=getattr(typ,name).offset:
                    raise CoreUnavailable('capability-use reservation field offset differs')
        for symbol,typ in (('cosmogony_revocation_lineage_bytes',revocation.Lineage),
                           ('cosmogony_revocation_link_bytes',revocation.Link),
                           ('cosmogony_universe_record_bytes',universes.Record)):
            size=getattr(native,symbol);size.argtypes,size.restype=[],C.c_int32
            if size()!=C.sizeof(typ):raise CoreUnavailable('original COSMOGONY dependency layout differs')
        self.call.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t,C.c_size_t,
                           C.c_void_p,C.c_size_t,C.c_size_t,C.c_void_p,C.c_size_t]
        self.call.restype=C.c_int32

    def prepare(self,snapshot,mode):
        value=genesis._keys(snapshot,{'record','genesis','lineage','request','target','base_usage','now_tick','binding','rows','grants'})
        if type(mode) is not str or mode not in MODES:raise ValueError('use reservation command is noncanonical')
        if type(value['rows']) is not list or type(value['grants']) is not list:raise ValueError('complete use/grant rosters required')
        chain=revocation.parse_lineage(value['lineage'])
        ask=capabilities.make_input(value['lineage'][-1]['grant'],value['request'],
            authority_id=value['record']['policy']['authority_id'],target_world_id=value['target'],
            usage=value['base_usage'],now_tick=value['now_tick'])
        request=Input(universes.parse_record(value['record']),genesis.parse_universe(value['genesis']),ask,chain,
                      binding(value['binding']),MODES.index(mode))
        rows=(Row*len(value['rows']))()
        for index,item in enumerate(value['rows']):
            item=genesis._keys(item,{'kind','state','bound','lineage'})
            if type(item['kind']) is not str or item['kind'] not in KINDS or type(item['state']) is not str or item['state'] not in STATES:
                raise ValueError('use roster category is noncanonical')
            rows[index]=Row(KINDS.index(item['kind']),STATES.index(item['state']),binding(item['bound']),
                            revocation.parse_lineage(item['lineage']))
        grants=(capabilities.Capability*len(value['grants']))()
        for index,item in enumerate(value['grants']):grants[index]=capabilities.parse_capability(item)
        return request,rows,grants

    def observe(self,snapshot,mode):
        request,rows,grants=self.prepare(snapshot,mode);answer=Result()
        # Owned complete request/row/grant arenas stay live through synchronous call.
        if self.call(C.byref(request),C.sizeof(request),rows,len(rows),C.sizeof(rows),
                     grants,len(grants),C.sizeof(grants),C.byref(answer),C.sizeof(answer))!=0:
            raise CoreUnavailable('native capability-use reservation transport refused')
        if answer.status<0 or answer.status>=len(STATUSES):raise CoreUnavailable('native use reservation output differs')
        return {'status':STATUSES[answer.status],
                'request_bytes':C.string_at(C.byref(request),C.sizeof(request)),
                'rows_bytes':C.string_at(rows,C.sizeof(rows)),
                'grants_bytes':C.string_at(grants,C.sizeof(grants)),
                'result_bytes':C.string_at(C.byref(answer),C.sizeof(answer))}

    def decide(self,snapshot,mode):return self.observe(snapshot,mode)['status']
