"""Exact same-original K4 terminal ACK capture and lost-ACK completion.

Both resource protocols preserve their own complete packets. A scoped packet is
never projected into the old single-context state. Recovery requires the actual
authenticated prior K4 intent and real committed resource response; no fresh
socket, grant, exchange, use, dispatch or absent-history initialization occurs.
"""
from .protected_startup import require
from .protected_operations import clone


def capture_ack(p,capture,resource):
    from .protected_resource_runtime import ProtectedResourcePrincipal
    if type(p.resources) is ProtectedResourcePrincipal:
        envelope={'schema':'worldline.canonical-k4-resource-ack-v1',
            'family':'ORIGINAL','complete':clone(resource)}
    else:
        from .canonical_actor_execution import scoped_components
        from . import resource_scoped_run_ledger as S
        scoped_components(p)
        # Preserve every actual result field and typed packet/native roster;
        # explicit allowlist transport has no custody or authority of its own.
        envelope={'schema':'worldline.canonical-k4-resource-ack-v1',
            'family':'SCOPED','complete':S.record(resource)}
    replay_ack(p,capture,envelope)
    return envelope


def replay_ack(p,capture,envelope):
    from .journal_witness_kernel import verify_resource_ack
    verify_resource_ack(p,capture,envelope)
    # Decoding is transport only: the native full-history join owns protocol,
    # exact committed membership, original request and terminal reply decisions.
    if envelope['family']=='ORIGINAL':
        return clone(envelope['complete'])
    from . import resource_scoped_run_ledger as S
    return S.restore(envelope['complete'])


def recover_pending(p,operation):
    from .operation_capture import archive,restore_archive
    from .operation_owner_kernel import observe_exchange, initialize_exchange_kernel, prepare_exchange
    operation=p._operation_key(operation);p.intact();row=p.journal.rows[operation]
    require(row['state']=='QUARANTINED','FULL_BROKER_K4_PENDING_ORIGINAL_QUARANTINE_REQUIRED')
    proofs=[]
    for boundary in row['boundaries']:
        if boundary['name']=='FULL_BROKER_OWNER_DISPOSITION':
            proof=restore_archive(bytes.fromhex(boundary['value']))
            if proof not in proofs:proofs.append(proof)
    # Do not choose a convenient verdict from multiple owner attempts. Exact
    # unambiguous prior intent is required; all unresolved attempts survive.
    require(len(proofs)==1,'FULL_BROKER_K4_RETAINED_OWNER_ATTEMPT_AMBIGUOUS')
    proof=proofs[0]
    retained=p.resource_owner_resolution_material(operation,proof)
    require(archive(retained['proof'])==archive(proof)
        and observe_exchange(p, *proof['arguments'])==proof['native'],
        'FULL_BROKER_K4_PENDING_FULL_NATIVE_OWNER_INTENT_CHANGED')
    # The actual protected resource principal recognizes a complete existing
    # committed duplicate before fresh context/eligibility, or captures genuine
    # original closure/never-dispatched evidence. Unknown still remains held.
    method=getattr(type(p.resources),'resolve_historical',None)
    require(callable(method),'FULL_RESOURCE_DISTINCT_K4_TERMINAL_PRODUCER_UNAVAILABLE')
    resource=method(p.resources,p,operation,row['capture']['resource_intent'].reservation,proof)
    ack=capture_ack(p,row['capture'],resource)
    return p.complete_canonical_resolution(operation,proof,ack)
