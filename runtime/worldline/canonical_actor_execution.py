"""Complete protected before-exec capture of the original reserved use.

The scoped actor composite must independently decode and redecide this complete
frame alongside its full scoped packet and actual kernel actor observations.
This capture never returns a permission Boolean or treats an event ID as a grant.
The scoped producer is a separately declared pending source dependency.
"""
from .protected_startup import require
from .operation_capture import archive,restore_archive
from .protected_operations import clone,quantity,identity,digest
from .client_peer import RequestPeer
from .validation import current_requirements
from .core import hash_bytes_from_id


def scoped_components(p):
    # Explicit exact composition seam; an arbitrary subclass or service DTO
    # cannot substitute for the actual root lease/native journal producer.
    from .protected_scoped_resource_runtime import ProtectedScopedResourcePrincipal
    from .protected_scoped_resource_service import ScopedRunLedgerService
    require(type(p.resources) is ProtectedScopedResourcePrincipal
        and type(p.resources.scoped_service) is ScopedRunLedgerService
        and p.resources.service is p.resources.scoped_service
        and p.resources.lease is p.lease and p.resources.gate is p.gate
        and p.resources.operation_principal is p,
        'OPERATION_ACTUAL_SCOPED_RESOURCE_CUSTODY_REQUIRED')
    return p.resources


def complete_history(p,operation,reservation):
    from . import resource_scoped_run_ledger as S
    producer=scoped_components(p)
    history=tuple(producer.scoped_service.committed_history())
    selected=[]
    capture=p.journal.rows[operation]['capture'];bound=capture['resource_intent'].bound
    # The service has authenticated and natively replayed the whole retained
    # chronology. Recheck every complete transported packet/native record;
    # filtering transports only the original tuple, never establishes custody.
    for event in history:
        require(type(event) is dict and set(event)=={'schema','prior','packet','native','source','principal','reply'}
            and event['schema']=='worldline.protected-scoped-resource-event-v1',
            'OPERATION_SCOPED_FULL_HISTORY_SCHEMA_CHANGED')
        packet=S.restore(event['packet']);native=S.restore(event['native'])
        require(type(packet) is S.ScopedPacket and type(native) is S.ScopedNativeDecision
            and producer.scoped_kernel.decide(packet)==native and native.status=='READY',
            'OPERATION_SCOPED_COMPLETE_NATIVE_HISTORY_CHANGED')
        original=packet.request.original
        if original.operation_id==bytes.fromhex(operation) and original.reservation==reservation:
            require(original.bound==bound,'OPERATION_SCOPED_ORIGINAL_FULL_BOUND_CHANGED')
            selected.append(clone(event))
    require(tuple(selected)==producer.committed_resource_history(operation,reservation),
        'OPERATION_SCOPED_PRODUCER_SELECTION_CHANGED')
    return history,tuple(selected)


def capture_execution(p,operation,reservation,original_request):
    from . import resource_scoped_run_ledger as S
    from .resource_run_ledger import dto_record
    from .protected_scoped_resource_service import snapshot_record
    operation=p._operation_key(operation);producer=scoped_components(p)
    with p.gate.mutex,producer.order:
        p.intact();row=p.journal.rows[operation];captured=row['capture'];intent=captured['resource_intent']
        require(row['state'] in ('EFFECT_INTENT','EFFECT_OBSERVED','SETTLED') and intent.reservation==reservation
            and type(original_request) is RequestPeer and p.active_peers.get(operation) is original_request
            and original_request.observation()==captured['request'],
            'OPERATION_BEFORE_EXEC_ACTUAL_ORIGINAL_RESERVED_REQUEST_REQUIRED')
        history,selected=complete_history(p,operation,reservation)
        running=[event for event in selected if S.restore(event['packet']).request.original.kind=='RECORD_RUNNING']
        require(len(running)==1,'OPERATION_BEFORE_EXEC_SINGLE_RUNNING_COMMIT_REQUIRED')
        before=producer.current_snapshot();current,source,_catalogue=producer._context(before)
        rows=[item for item in before.rows if item.bound==intent.bound]
        require(len(rows)==1 and rows[0].state=='RUNNING' and rows[0].scope==intent.scope,
            'OPERATION_BEFORE_EXEC_CURRENT_RUNNING_FULL_ORIGIN_CHANGED')
        native=p.intact();universe=p.gate.universe.read();issuer=p.gate.issuer.head()
        prime=p.store.prime();requirement=None if prime is None else current_requirements(p.store,p.controller.config,p.core)
        plan=p.resource_launch_material(original_request,reservation)
        grants=[grant for grant in p.journal.body['grants']
            if grant['id']==captured['binding']['id']['grant_id']]
        require(len(grants)==1,'OPERATION_BEFORE_EXEC_RETAINED_GRANT_CANDIDATE_UNAVAILABLE')
        grant=clone(grants[0])
        fresh=clone(captured['binding'])
        fresh['id'].update(universe_head=current.universe_head.hex(),resource_head=current.ledger_head.hex(),
            issuer_head=issuer['event_head'],policy=grant['policy'],
            instance=current.scope.instance.hex(),root_set=p.gate.config['managed_observation']['root_set_id'],
            prime=None if prime is None else identity(prime).hex(),
            requirement=None if requirement is None else hash_bytes_from_id(requirement['requirementHash']).hex(),
            receipt_head=p.journal.body['chains']['operation_receipts']['head'],
            causal_head=p.journal.body['chains']['operation_events']['head'])
        fresh['policy_epoch']=quantity(universe['record']['policy_epoch'])
        fresh['resource_epoch']=quantity(current.resource_epoch)
        snapshot=p._snapshot(captured,evidence=row['snapshot']['evidence'])
        snapshot['receipts']=clone(row['snapshot']['receipts']);snapshot['events']=clone(row['snapshot']['events'])
        snapshot['evidence']['owner_resolution']=fresh
        answer=p.kernel.observe(snapshot,'AUTHORIZE_EXECUTION')
        # A denial is retained with the entire attempted capture. Returning the
        # frame permits the actor composite to redecide it; it cannot ACK a deny.
        full={'schema':'worldline.protected-actor-execution-current-v1',
            'operation':operation,'reservation':reservation,'original_request':original_request.observation(),
            'original_capture':archive(captured).hex(),'current_binding':fresh,
            'current_observation':S.record(current),'current_source':S.record(source),
            'complete_snapshot':snapshot_record(before),'complete_scoped_history':clone(history),
            'selected_scoped_history':clone(selected),'running_event':clone(running[0]),
            'universe':universe,'issuer':issuer,'prime':prime,'requirement':requirement,
            'native_mapping':native,'plan':clone(plan),
            # These are independently sourced values with different grammars.
            # The actor composite must consume a genuine native crosswalk;
            # operation Policy is not resource Scope.Policy, and Root_Set is
            # not the hash of the scoped producer's complete store root record.
            'execution_crosswalk':{
                'schema':'worldline.protected-operation-resource-crosswalk-v1',
                'owner_genesis':clone(p.journal.owner_genesis),
                'installation':clone(p.lease.spec),'gate_config_raw':p.gate.config_raw,
                'gate_managed_observation':clone(p.gate.config['managed_observation']),
                'operation_grant':grant,'operation_binding':clone(fresh),
                'operation_policy':grant['policy'],
                'resource_policy':current.scope.policy.hex(),
                'root_set':fresh['id']['root_set'],'root_head':current.root_head.hex(),
                'resource_current':S.record(current),'resource_source':S.record(source),
                'transaction':clone(captured['transaction']),
                'original_request':clone(captured['request']),
                'preparer_peer':None if captured['transaction'] is None else clone(captured['transaction'].get('preparerPeer'))}}
        material={'schema':'worldline.protected-actor-execution-material-v1','operation':operation,
            'reservation':reservation.hex(),'full_current':archive(full).hex(),
            'snapshot':archive(snapshot).hex(),'native':answer}
        boundary={'name':'ACTOR_EXECUTION_NATIVE','material':material}
        p.journal.append(operation,'ACK',captured,snapshot=row['snapshot'],native=row['native'],
            boundaries=row['boundaries']+[boundary])
        terminal=p.journal.rows[operation]
        return {'original_request':clone(captured['request']),'scope':dto_record(intent.scope),
            'bound':dto_record(intent.bound),'native_use':p._original_native_use(terminal),
            'event_id':terminal['event'],'native':answer,'current':clone(full),'plan':clone(plan),
            'scoped_history':clone(selected),'authority_snapshot':clone(snapshot),'material':material}


def replay_execution(p,material,*,owner_genesis):
    from . import resource_scoped_run_ledger as S
    from .protected_scoped_resource_service import snapshot_restore
    require(type(material) is dict and set(material)=={'schema','operation','reservation','full_current','snapshot','native'}
        and material['schema']=='worldline.protected-actor-execution-material-v1',
        'OPERATION_BEFORE_EXEC_FULL_MATERIAL_REQUIRED')
    snapshot=restore_archive(bytes.fromhex(material['snapshot']))
    full=restore_archive(bytes.fromhex(material['full_current']))
    require(full['schema']=='worldline.protected-actor-execution-current-v1'
        and full['operation']==material['operation'] and full['reservation'].hex()==material['reservation']
        and snapshot['binding']['id']['operation_id']==material['operation']
        and snapshot['evidence']['owner_resolution']==full['current_binding'],
        'OPERATION_BEFORE_EXEC_NATIVE_ORIGINAL_BINDING_CHANGED')
    captured=restore_archive(bytes.fromhex(full['original_capture']))
    require(captured['binding']==snapshot['binding'] and captured['request']==full['original_request']
        and captured['resource_intent'].reservation==full['reservation'],
        'OPERATION_BEFORE_EXEC_FULL_CAPTURE_CHANGED')
    crosswalk=full['execution_crosswalk']
    require(crosswalk['owner_genesis']==owner_genesis
        and crosswalk['operation_binding']==full['current_binding']
        and crosswalk['operation_policy']==full['current_binding']['id']['policy']
        and crosswalk['root_set']==full['current_binding']['id']['root_set']
        and crosswalk['original_request']==captured['request'],
        'OPERATION_BEFORE_EXEC_RETAINED_OWNER_CROSSWALK_CHANGED')
    producer=scoped_components(p)
    actual=tuple(producer.scoped_service.committed_history())
    history=tuple(full['complete_scoped_history'])
    require(actual[:len(history)]==history,'OPERATION_BEFORE_EXEC_PROTECTED_HISTORY_PREFIX_CHANGED')
    selected=[]
    for event in history:
        packet=S.restore(event['packet']);decision=S.restore(event['native'])
        require(type(packet) is S.ScopedPacket and type(decision) is S.ScopedNativeDecision
            and producer.scoped_kernel.decide(packet)==decision and decision.status=='READY',
            'OPERATION_BEFORE_EXEC_SCOPED_NATIVE_REPLAY_CHANGED')
        if packet.request.original.operation_id==bytes.fromhex(material['operation']) and packet.request.original.reservation==full['reservation']:
            require(packet.request.original.bound==captured['resource_intent'].bound,
                'OPERATION_BEFORE_EXEC_RETAINED_FULL_ORIGIN_CHANGED')
            selected.append(event)
    require(tuple(selected)==tuple(full['selected_scoped_history'])
        and [event for event in selected if S.restore(event['packet']).request.original.kind=='RECORD_RUNNING']==[full['running_event']],
        'OPERATION_BEFORE_EXEC_FULL_RUNNING_HISTORY_CHANGED')
    before=snapshot_restore(full['complete_snapshot']);current=S.restore(full['current_observation'])
    require(type(current) is S.CurrentObservation and before.state.current==current.scope
        and before.state.resource_epoch==current.resource_epoch and before.state.ledger_head==current.ledger_head,
        'OPERATION_BEFORE_EXEC_CURRENT_NATIVE_DOMAIN_CHANGED')
    require(p.kernel.observe(snapshot,'AUTHORIZE_EXECUTION')==material['native'],
        'OPERATION_BEFORE_EXEC_FULL_AUTHORITY_REDECISION_CHANGED')
    return material['native']
