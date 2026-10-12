"""Actual closed root witness into unchanged scoped historical settlement.

The complete original packet/native/closure/launch/source history is transported
from the real owned collector. No packet reconstruction, fresh grant, use or
exchange occurs, and no observation of another reservation is changed.
"""
from .protected_startup import require

def install_root_closed_witness(principal,guard):
    from .root_worker_closed import ClosedFrontEscrow
    from .root_worker_failed_closure import FailedFrontEscrow
    from .protected_operations import CanonicalOperationPrincipal
    from .protected_scoped_resource_runtime import ProtectedScopedResourcePrincipal
    from . import resource_scoped_run_ledger as S
    require(type(guard) in (ClosedFrontEscrow,FailedFrontEscrow) and type(principal) is CanonicalOperationPrincipal
        and principal.lease is guard.fresh_lease and guard.phase=='RECONSTRUCTED',
            'ROOT_CLOSED_RESOURCE_ACTUAL_FRESH_PRINCIPAL_REQUIRED')
    resources=principal.resources
    require(type(resources) is ProtectedScopedResourcePrincipal and resources.lease is principal.lease
        and resources.operation_principal is principal and resources.gate is principal.gate,
            'ROOT_CLOSED_RESOURCE_SAME_EXACT_PROTECTED_COMPONENTS_REQUIRED')
    proof=guard.intact();packet=proof['packet'];row=proof['original_row'];owned=guard.owned
    resources.intact();resources.journal.load()
    selected=[item for item in resources.current_snapshot().rows if item.bound==row.bound]
    require(selected==[row],'ROOT_CLOSED_RESOURCE_CURRENT_FULL_ORIGINAL_ROW_CHANGED')
    actual=resources.committed_resource_history(row.bound.operation,row.bound.reservation)
    running=[event for event in actual if S.restore(event['packet']).request.original.kind=='RECORD_RUNNING']
    seed=proof['historical_root_native']['record']['provenance']
    require(len(running)==1 and running[0]==seed['running_event'],
            'ROOT_CLOSED_RESOURCE_ACTUAL_RETAINED_RUNNING_CHANGED')
    native=resources.scoped_kernel.classify(proof['classification_input'])
    require(native==proof['native'] and native.status=='REAPED'
        and resources.scoped_kernel.validate(packet)==proof['consistent'],
            'ROOT_CLOSED_RESOURCE_WHOLE_NATIVE_REPLAY_REFUSED')
    # The legacy consumer expects this complete source shape. We supply the
    # actual original root observation; no DTO or HMAC-only result is invented.
    source={'kernel':dict(proof['physical']['raw']),'launch_prefix':resources.journal.events,
            'root_custody_proof':proof,'retained_original_resource_history':actual}
    require(source['kernel']['closed']==owned.closed and source['kernel']['outer']==owned.outer,
            'ROOT_CLOSED_RESOURCE_ACTUAL_NAMESPACE_AND_OUTER_WITNESS_CHANGED')
    body={'packet':packet,'native':resources.scoped_kernel.classify(packet),'original_row':row,
        'owned_closed':owned.closed,'owned_closed_event':owned.outer,
        'launch_prefix':resources.journal.events,'source':source,
        'current_source':resources._context(resources.current_snapshot())[1],
        'issuer_head':principal.gate.issuer.head(),'installation':principal.lease.spec,
        'committed_history':resources.scoped_service.committed_history()}
    require(body['native'].status=='REAPED','ROOT_CLOSED_RESOURCE_RETAINED_NATIVE_REFUSED')
    resources.observations.load()
    for event in resources.observations.events:
        if event['cause']=='CLOSED_NATIVE_WITNESS' and event['reservation']==row.bound.reservation.hex():
            old=S.restore(event['payload'])
            if old.get('source',{}).get('root_custody_proof',{}).get('owned_closed')==owned.closed:
                require(old['original_row']==row and resources.scoped_kernel.classify(old['packet'])==old['native']
                    and old['native'].status=='REAPED','ROOT_CLOSED_RESOURCE_DUPLICATE_REPLAY_CHANGED')
                return event
    event=resources.observations.append('CLOSED_NATIVE_WITNESS',row.bound.reservation.hex(),body)
    resources.observations.load()
    require(event in resources.observations.events,'ROOT_CLOSED_RESOURCE_ACTUAL_COMMITTED_WITNESS_ABSENT')
    return event
