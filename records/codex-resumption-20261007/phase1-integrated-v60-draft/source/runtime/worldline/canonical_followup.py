"""Fresh per-right post-commit decision using the original retained grant/use.

The authenticated original COMMITTED result is retained first. A denied or
unavailable follow-up cannot turn it into an uncommitted transaction. Physical
child launch requires the separately declared genuine scoped resource producer.
"""
from .protected_operations import current_scope,OperationScope,clone,quantity,identity,digest
from .protected_startup import require
from .operation_capture import archive,restore_archive
from .validation import current_requirements
from .core import hash_bytes_from_id
from .errors import WorldlineError

RIGHTS=('return.services','return.terminals','return.windows','automatic.ghosts')
def capture_followup(p,operation,right):
    require(right in RIGHTS,'OPERATION_UNKNOWN_FOLLOWUP_RIGHT')
    operation=p._operation_key(operation);p.historical_operation(operation)
    row=p.journal.rows[operation];captured=row['capture'];original=captured['binding']
    require(row['state'] in ('EFFECT_OBSERVED','SETTLED')
        and original['action'] in ('collapse.commit','transaction.commit'),
        'OPERATION_FOLLOWUP_WITHOUT_AUTHENTIC_COMMITTED_EFFECT')
    live=p.active_peers.get(operation)
    require(live is not None and live.observation()==captured['request'],
        'OPERATION_FOLLOWUP_ORIGINAL_PEER_UNAVAILABLE')
    scope,epoch,uhead,lhead,source=p.resources.current_context()
    native=p.intact();universe=p.gate.universe.read();issuer=p.gate.issuer.head()
    prime=p.store.prime();requirement=None if prime is None else current_requirements(p.store,p.controller.config,p.core)
    from .resource_run_ledger import dto_record
    resource_snapshot=p.resources.current_snapshot()
    full={'schema':'worldline.protected-followup-current-input-v1','right':right,
        'original_request':live.observation(),'original_capture':archive(captured).hex(),
        'original_effect_snapshot':archive(row['snapshot']).hex(),'original_effect_native':clone(row['native']),
        'current_scope':dto_record(scope),'current_resource_epoch':epoch,
        'current_universe_head':uhead,'current_resource_head':lhead,
        'current_source':source,'current_universe':universe,'current_issuer':issuer,
        'current_prime':prime,'current_requirement':requirement,'current_kernel':native,
        'full_current_rows':{'state':dto_record(resource_snapshot.state),'rows':[dto_record(value) for value in resource_snapshot.rows]}}
    # Snapshot is a data identity, not a selected source-verdict/authority flag.
    # Native eligibility binds the actual current policy/epoch and full original
    # peer/grant/use/transaction. All whole current sources remain retained.
    fresh=clone(original);fresh['action']=right
    fresh['id'].update(universe_head=uhead.hex(),resource_head=lhead.hex(),
        issuer_head=issuer['event_head'],policy=scope.policy.hex(),
        prime=None if prime is None else identity(prime).hex(),
        requirement=None if requirement is None else hash_bytes_from_id(requirement['requirementHash']).hex(),
        input_snapshot=digest(archive({key:value for key,value in full.items() if key!='full_current_rows'})))
    fresh['policy_epoch']=quantity(universe['record']['policy_epoch']);fresh['resource_epoch']=quantity(epoch)
    snapshot=p._snapshot(captured,evidence=row['snapshot']['evidence'])
    snapshot['evidence']['owner_resolution']=fresh
    snapshot['receipts']=clone(row['snapshot']['receipts']);snapshot['events']=clone(row['snapshot']['events'])
    answer=p.kernel.observe(snapshot,'AUTHORIZE_FOLLOWUP')
    material={'schema':'worldline.protected-followup-material-v1','operation':operation,'right':right,
        'full_current':archive(full).hex(),'snapshot':archive(snapshot).hex(),'native':answer}
    boundary={'name':'FOLLOWUP_NATIVE','material':material}
    p.journal.append(operation,'ACK',captured,snapshot=row['snapshot'],native=row['native'],
        boundaries=row['boundaries']+[boundary])
    return {**material,'event_id':p.journal.rows[operation]['event']}

def replay_followup(p,material):
    require(set(material)=={'schema','operation','right','full_current','snapshot','native'}
        and material['schema']=='worldline.protected-followup-material-v1',
        'OPERATION_FOLLOWUP_COMPLETE_MATERIAL_REQUIRED')
    snapshot=restore_archive(bytes.fromhex(material['snapshot']))
    full=restore_archive(bytes.fromhex(material['full_current']))
    require(full['right']==material['right'] and snapshot['evidence']['owner_resolution']['action']==material['right']
        and snapshot['binding']['id']['operation_id']==material['operation'],
        'OPERATION_FOLLOWUP_SAME_ORIGINAL_OPERATION_CHANGED')
    require(p.kernel.observe(snapshot,'AUTHORIZE_FOLLOWUP')==material['native'],
        'OPERATION_FOLLOWUP_NATIVE_REPLAY_CHANGED')
    return material['native']['decision']

def after_committed(p,transaction,context,result):
    scope=current_scope();require(type(scope) is OperationScope and scope.principal is p,
        'OPERATION_POST_COMMIT_ACTUAL_SCOPE_REQUIRED')
    operation=scope.operation;row=p.journal.rows[operation]
    require(result.get('state')=='COMMITTED' and transaction['transactionId']==row['capture']['transaction']['transactionId'],
        'OPERATION_POST_COMMIT_ORIGINAL_TRANSACTION_CHANGED')
    # This may only be called after the full canonical broker has supplied its
    # genuine result; a worker-only COMMITTED DTO cannot enter this seam.
    broker_ack=[value for value in row['boundaries'] if value['name']=='FULL_BROKER_COMMITTED']
    require(len(broker_ack)==1,'OPERATION_POST_COMMIT_FULL_BROKER_ACK_UNAVAILABLE')
    captured=clone({'result':result,'actual_store':p.capture.chain_material(),
        'actual_transaction':p.controller.transactions._load_record(transaction['transactionId'])})
    p.finish(operation,captured)
    skipped=[];warnings=[]
    selected=RIGHTS if transaction['kind']=='return' else ('automatic.ghosts',)
    for right in selected:
        try:
            material=capture_followup(p,operation,right)
            if material['native']['decision']!='FOLLOWUP_READY':
                skipped.append({'right':right,'reason':'OPERATION_FOLLOWUP_NATIVE_DENIED','event_id':material['event_id']})
                continue
            # Exact agreed scoped producer interface is a declared future source
            # dependency. A released original hold cannot finance this effect.
            raise WorldlineError('OPERATION_SCOPED_FOLLOWUP_DISPATCH_UNAVAILABLE',
                'fresh child hold, owned launch and native terminal producer required')
        except WorldlineError as error:
            skipped.append({'right':right,'reason':error.code})
            warnings.append({'phase':right,'code':error.code,'message':str(error)})
    previous=result.get('postCommit') or {}
    answer={**result,'postCommit':{**previous,'warnings':[*(previous.get('warnings') or []),*warnings],
        'effectsSkipped':[*(previous.get('effectsSkipped') or []),*skipped]}}
    row=p.journal.rows[operation]
    p.journal.append(operation,'ACK',row['capture'],snapshot=row['snapshot'],native=row['native'],
        boundaries=row['boundaries']+[{'name':'POST_COMMIT_REPORT','value':archive(answer).hex()}])
    return answer
