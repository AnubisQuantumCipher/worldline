"""Authentic original operation-journal inputs for future native PREPARED decoding.
No journal is created, no event appended, and this capture grants no transition.
"""
from dataclasses import dataclass
from .protected_startup import require,private_bytes,canonical
from .operation_capture import archive

@dataclass(frozen=True)
class PreparedInputs:
    operation: str
    journal_raw: bytes
    admission_head: tuple
    reserved_event_raw: bytes
    effect_intent_event_raw: bytes
    reserved_snapshot: bytes
    effect_intent_snapshot: bytes
    full_ordered_events: bytes


def capture_prepared_inputs(owner,operation):
    from .protected_root_worker import RootWorkerFront
    require(type(owner) is RootWorkerFront,'PREPARED_ACTUAL_FRONT_REQUIRED')
    owner.intact();p=owner.principal;j=p.journal
    raw=private_bytes(j.path)
    require(raw==j.raw,'PREPARED_OPERATION_JOURNAL_BYTES_CHANGED')
    # Original complete HMAC/head/policy/grant/use/native-redecision loader.
    # It must finish; two conveniently matching event names are insufficient.
    j.load()
    head=tuple(j.head_row())
    require(operation in j.rows and j.rows[operation]['state']=='EFFECT_INTENT',
            'PREPARED_CURRENT_EFFECT_INTENT_REQUIRED')
    events=j.body['events']
    reserved=[(i,e) for i,e in enumerate(events) if e['operation']==operation and e['cause']=='RESERVED']
    intents=[(i,e) for i,e in enumerate(events) if e['operation']==operation and e['cause']=='EFFECT_INTENT']
    require(len(reserved)==1 and len(intents)==1 and reserved[0][0]<intents[0][0],
            'PREPARED_ORIGINAL_ORDERED_HEADS_REQUIRED')
    r=reserved[0][1];e=intents[0][1]
    require(r['capture']==e['capture'],'PREPARED_CAPTURE_CHANGED')
    capture=j.rows[operation]['capture']
    require(capture['binding']['action'] in ('fork','race','revalidate','simulate','ghost.run','ghost.enable','root.add','init'),
            'PREPARED_ORIGINAL_WORKLOAD_REQUIRED')
    # Exact whole snapshots and entire ordered journal retained. Native decoder
    # must prove these map to its O.Grants/Uses/Binding inputs before authority.
    result=PreparedInputs(operation,raw,head,canonical(r),canonical(e),
        bytes.fromhex(r['snapshot']),bytes.fromhex(e['snapshot']),archive(events))
    owner.intact()
    require(private_bytes(j.path)==raw and tuple(j.head_row())==head,
            'PREPARED_OPERATION_CAPTURE_CHANGED')
    return result
