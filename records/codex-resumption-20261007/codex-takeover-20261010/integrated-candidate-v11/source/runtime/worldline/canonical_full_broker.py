"""Protected full-roster worker/canonical protocol, no legacy verdict adapter.

Every consequential call is under the existing principal lock/scope. Complete
native inputs and actual bytes enter its independently anchored journal before
dispatch. Restart only recognizes retained intent/effect; it never repeats an
exchange or supplies an absent Genesis. Split observations remain quarantined.
"""
from dataclasses import replace
from pathlib import Path
import os
from .protected_startup import require,protected
from .protected_operations import clone,identity,digest
from .operation_capture import archive,restore_archive
from .recovery_authority_kernel_v3 import BoundUse,NativeObservation
from .recovery_observation import redecide_packet
from .core import hash_bytes_from_id
from .manifest import Manifest
from .canonical_full_store import FullCanonicalStore
from .canonical_physical import FullPhysicalActuator,entry,raw
from .operation_owner_kernel import observe_exchange, initialize_exchange_kernel, prepare_exchange
from .errors import WorldlineError

def chain_dto(rows):
    return [{name:None if getattr(row,name) is None else getattr(row,name).hex()
        for name in ('previous','actual_payload_root','stored_payload_root','stored_head')} for row in rows]

class FullCanonicalBroker:
    def __init__(self,principal):
        self.p=principal;self.store=FullCanonicalStore(principal)
        self.kernel=initialize_exchange_kernel(principal);self.physical=FullPhysicalActuator(principal)
        policy=principal.policy['broker']
        require(set(policy)=={'schema','policy_path','state_path','physical_symbols','followup_plans'}
            and policy['schema']=='worldline.full-canonical-broker-v1'
            and policy['policy_path']==str(self.store.policy_path)
            and policy['state_path']==str(self.store.state_path), 'FULL_BROKER_SELECTED_OWNER_POLICY_REQUIRED')
        require(policy['physical_symbols']==['wl_full_physical_version_v1','wl_full_physical_layout_v1',
            'wl_full_physical_exchange_v1','wl_full_physical_recover_v1'],'FULL_BROKER_PHYSICAL_SYMBOL_ROSTER_CHANGED')
        principal.mapped_symbols([*policy['physical_symbols'],'wl_canonical_exchange_version_v1',
            'wl_canonical_exchange_layout_v1','wl_canonical_exchange_decide_v1'])
        for path in (self.store.policy_path,self.store.state_path):
            principal.lease.source_lease.file(str(path),('DATA',))
        # No dummy PRIME is required by construction; only a real commit needs
        # complete prepared mappings. Existing empty/nonempty root histories
        # and independently typed absent PRIME remain original accepted cases.
    def ack(self,operation,name,value):
        p=self.p;row=p.journal.rows[operation]
        boundary={'name':name,'value':archive(value).hex()}
        if boundary not in row['boundaries']:
            p.journal.append(operation,'ACK',row['capture'],snapshot=row['snapshot'],native=row['native'],
                boundaries=row['boundaries']+[boundary])
        return boundary
    def retained(self,operation,name):
        values=[value for value in self.p.journal.rows[operation]['boundaries'] if value['name']==name]
        require(len(values)==1,'FULL_BROKER_RETAINED_BOUNDARY_MISSING_OR_AMBIGUOUS')
        return restore_archive(bytes.fromhex(values[0]['value']))
    def retained_owner_disposition(self,operation,proof):
        # Multiple genuine owner attempts retain all old evidence. Select by
        # the exact complete proof and its original owner operation, never by
        # the last named boundary or a caller-supplied disposition enum.
        selected=[]
        for boundary in self.p.journal.rows[operation]['boundaries']:
            if boundary['name']=='FULL_BROKER_OWNER_DISPOSITION':
                value=restore_archive(bytes.fromhex(boundary['value']))
                if archive(value)==archive(proof):selected.append(value)
        require(len(selected)==1,'FULL_BROKER_EXACT_OWNER_PROOF_MISSING_OR_AMBIGUOUS')
        value=selected[0]
        require(value['owner']['binding']['action']=='quarantine.resolve'
            and value['owner']['binding']['id']['original_operation']==operation,
            'FULL_BROKER_OWNER_PROOF_ORIGINAL_OPERATION_CHANGED')
        return value
    def worker_observation(self):
        return self.p.capture.observe_effect()
    def canonical_observation(self):
        current=self.store.capture(self.store.data/'live')
        return NativeObservation(live_mapping=identity(current['mapping']),
            live_root=hash_bytes_from_id(current['root_set'])),current
    def prepare(self,operation,boundary):
        p=self.p;row=p.journal.rows[operation];capture=row['capture'];record=capture['transaction']
        require(record is not None and row['state']=='EFFECT_INTENT','FULL_BROKER_ORIGINAL_EFFECT_INTENT_REQUIRED')
        packet=bytes.fromhex(boundary['collapse_packet'])
        require(redecide_packet(packet,core=p.core)=='AUTHORIZED','FULL_BROKER_COMPLETE_ORIGINAL_PACKET_REFUSED')
        values=restore_archive(bytes.fromhex(boundary['collapse_values']))
        before_worker=p.capture.mapping_material(p.controller.paths.live)
        stage_worker=p.capture.mapping_material(record['preparedMapping'])
        before_root=self.store.capture(self.store.data/'live')
        require(before_root['root_set']==record['beforeRoot'],'FULL_BROKER_CANONICAL_BEFORE_PAYLOAD_SPLIT')
        self.ack(operation,'FULL_BROKER_STAGING_INTENT',{'transaction':record,'packet':packet,
            'before_worker':before_worker,'stage_worker':stage_worker,'before_root':before_root,
            'owner_policy':self.store.policy_raw,'owner_initial_state':self.store.raw})
        staged_root=self.store.stage(record)
        p.controller.transactions._fsync_payload_tree(Path(record['stagingPayload']))
        raw_packet=restore_archive(packet);selected=(raw_packet['primary'],raw_packet['staged'])
        ids=capture['binding']['id'];native=p.intact()
        mode='CHECKPOINT_RETURN' if values.mode=='CHECKPOINT_RETURN' else ('STAGED' if raw_packet['staged'] is not None else 'CANDIDATE')
        def identifier(name):return None if ids[name] is None else bytes.fromhex(ids[name])
        worker=BoundUse(mode=mode,operation=identifier('operation_id'),transaction=identifier('transaction'),
            capability=identifier('grant_id'),universe_head=identifier('universe_head'),instance=identifier('instance'),
            subject=values.expected_subject,staged_root=values.actual_staged_root,current_requirement=values.current_requirement,
            resulting_requirement=values.resulting_requirement,requester=identity(capture['request']['peer']),
            grant_use=identifier('use_id'),policy_identity=identifier('policy'),selected_evaluation=identity(selected),
            history_head=identity(tuple(value['authorityMaterial'] if value is not None else None for value in selected)),
            reservation=identifier('reservation'),host=identity({'boot':Path('/proc/sys/kernel/random/boot_id').read_bytes(),
                'machine':Path('/etc/machine-id').read_bytes()}),before_prime=identity(p.store.prime()),
            before_root=hash_bytes_from_id(record['beforeRoot']),before_mapping=identity(before_worker['target']),
            staged_mapping=identity(stage_worker['target']),input_snapshot=identifier('input_snapshot'),
            kernel_build=identifier('kernel_build'),kernel_library=identifier('kernel_library'),kernel_mapping=identifier('kernel_mapping'),
            issuer_head=identifier('issuer_head'),receipt_head=identity(p.capture.chain_material()['receipts']),
            causal_head=identity(p.capture.chain_material()['events']),policy_epoch=p.gate.universe.read()['record']['policy_epoch'],
            resource_epoch=capture['resource_intent'].bound.resource_epoch)
        canonical=replace(worker,before_mapping=identity(before_root['mapping']),staged_mapping=identity(staged_root['mapping']))
        captured={'packet':packet,'values':values,'worker':worker,'canonical':canonical,'before_worker':before_worker,
            'stage_worker':stage_worker,'before_root':before_root,'staged_root':staged_root,'kernel':native,
            'live_entry':raw(entry(self.store.data/'live')),'stage_entry':raw(entry(self.store.transactions/record['transactionId']/'mapping')),
            'marker_digest':p.core.hash_bytes(staged_root['marker'])}
        self.ack(operation,'FULL_BROKER_PREPARED',captured)
        return captured
    def arguments(self,operation,captured,phase,mode,*,owner_binding=None):
        p=self.p;row=p.journal.rows[operation];intent=row['capture']['resource_intent']
        require(p.intact()==captured['kernel'] and redecide_packet(captured['packet'],core=p.core)=='AUTHORIZED',
            'FULL_BROKER_HISTORICAL_SOURCE_PACKET_CHANGED')
        worker,wfacts=self.worker_observation();canonical,cfacts=self.canonical_observation()
        worldline=p.capture.chain_material();receipts=p.canonical.rows('receipts',worldline);events=p.canonical.rows('events',worldline)
        snapshot=p._snapshot(row['capture'],evidence=row['snapshot']['evidence'])
        snapshot['receipts']=clone(row['snapshot']['receipts']);snapshot['events']=clone(row['snapshot']['events'])
        if owner_binding is not None:snapshot['evidence']['owner_resolution']=clone(owner_binding)
        resource=p.resources.current_snapshot();observed=p.resources.collect(resource,intent)
        chains=p.journal.body['chains']
        material={'worker_issued':captured['worker'],'worker_recovered':captured['worker'],
            'canonical_issued':captured['canonical'],'canonical_recovered':captured['canonical'],
            'worker_native':worker,'canonical_native':canonical,
            'worker_receipt_genesis':bytes.fromhex(chains['receipts']['genesis']),
            'owner_receipt_genesis':bytes.fromhex(p.policy['chains']['receipts']['genesis']),
            'worker_receipt_head':bytes.fromhex(chains['receipts']['head']),
            'worker_causal_genesis':bytes.fromhex(chains['events']['genesis']),
            'owner_causal_genesis':bytes.fromhex(p.policy['chains']['events']['genesis']),
            'worker_causal_head':bytes.fromhex(chains['events']['head']),
            'quarantine_head':None if owner_binding is None else bytes.fromhex(owner_binding['id']['quarantine_head'])}
        args=(snapshot,resource.state,resource.rows,observed,intent,row['capture']['request']['peer']['uid'],
            captured['values'],material,phase,mode,chain_dto(receipts),chain_dto(events))
        return args,{'worker':wfacts,'canonical':cfacts,'worldline_chains':worldline}
    def decide(self,operation,captured,phase,mode,expected,*,owner_binding=None):
        args,facts=self.arguments(operation,captured,phase,mode,owner_binding=owner_binding)
        native=observe_exchange(self.p,*args,kernel=self.kernel)
        self.ack(operation,'FULL_BROKER_NATIVE',{'phase':phase,'mode':mode,'arguments':args,'facts':facts,'native':native})
        require(native['decision'] in expected,'FULL_BROKER_NATIVE_'+native['decision'])
        return args,native
    def commit(self,operation,transaction_id):
        p=self.p;row=p.journal.rows[operation]
        require(row['capture']['transaction']['transactionId']==transaction_id,'FULL_BROKER_TRANSACTION_JOIN_CHANGED')
        boundary=[value for value in row['boundaries'] if value['name']=='FULL_PRE_EFFECT_BOUNDARY']
        require(len(boundary)==1,'FULL_BROKER_ORIGINAL_AUTHORIZATION_BOUNDARY_MISSING')
        captured=self.prepare(operation,boundary[0])
        self.decide(operation,captured,'ISSUED','ADVANCE',('DISPATCH_WORKER',))
        self.ack(operation,'FULL_BROKER_WORKER_INTENT',captured)
        try:result=p.controller.transactions.commit(transaction_id)
        except WorldlineError as error:
            # A genuine worker COMMITTED outcome is retained independently; it
            # is insufficient for canonical success. Never rerun the worker.
            if (error.details or {}).get('state')!='COMMITTED':raise
            result=clone(error.details)
        self.ack(operation,'FULL_BROKER_WORKER_RESULT',{'result':result,'record':p.controller.transactions._load_record(transaction_id),
            'chains':p.capture.chain_material()})
        self.decide(operation,captured,'WORKER_INTENT','ADVANCE',('RECORD_WORKER',))
        args,native=self.decide(operation,captured,'WORKER_OBSERVED','ADVANCE',('DISPATCH_CANONICAL',))
        self.ack(operation,'FULL_BROKER_CANONICAL_INTENT',{'arguments':args,'native':native,'prepared':captured})
        from .canonical_physical import Entry
        actual=self.physical.exchange(p.active_peers[operation],self.store.data,self.store.transactions/transaction_id,
            prepare_exchange(self.p,*args,kernel=self.kernel),Entry.from_buffer_copy(captured['live_entry']),
            Entry.from_buffer_copy(captured['stage_entry']),captured['marker_digest'],
            payload=self.store.staging/transaction_id)
        self.ack(operation,'FULL_BROKER_PHYSICAL_RESULT',actual)
        require(actual['status']==0,'FULL_BROKER_PHYSICAL_UNKNOWN_OR_REFUSED')
        self.decide(operation,captured,'CANONICAL_INTENT','ADVANCE',('RECORD_EFFECT',))
        self.ack(operation,'FULL_BROKER_COMMITTED',{'result':result,'prepared':captured,'actual_physical':actual,
            'actual_worker':p.controller.transactions._load_record(transaction_id),'actual_chains':p.capture.chain_material(),
            'actual_canonical':self.store.capture(self.store.data/'live')})
        return result
    def recover(self,operation):
        # Missing result is not reconstructed from a DTO or a fresh current
        # grant. Reobserve both physical mappings, native recognize only both
        # After, and use the exact retained worker result/full original packet.
        captured=self.retained(operation,'FULL_BROKER_PREPARED')
        self.retained(operation,'FULL_BROKER_CANONICAL_INTENT')
        worker_result=self.retained(operation,'FULL_BROKER_WORKER_RESULT')
        args,native=self.decide(operation,captured,'CANONICAL_INTENT','ADVANCE',('RECORD_EFFECT',))
        row=self.p.journal.rows[operation]
        transaction_id=row['capture']['transaction']['transactionId']
        from .canonical_physical import Entry
        actual=self.physical.recover(self.store.data,self.store.transactions/transaction_id,
            prepare_exchange(self.p,*args,kernel=self.kernel),Entry.from_buffer_copy(captured['live_entry']),
            Entry.from_buffer_copy(captured['stage_entry']),captured['marker_digest'],
            payload=self.store.staging/transaction_id)
        self.ack(operation,'FULL_BROKER_RECOVERY_PHYSICAL_RESULT',actual)
        require(actual['status']==0,'FULL_BROKER_RECOVERY_PHYSICAL_UNKNOWN_OR_REFUSED')
        existing=[value for value in row['boundaries'] if value['name']=='FULL_BROKER_COMMITTED']
        if existing:return self.retained(operation,'FULL_BROKER_COMMITTED')['result']
        self.ack(operation,'FULL_BROKER_COMMITTED',{'result':worker_result['result'],'prepared':captured,
            'actual_physical':actual,'actual_worker':self.p.controller.transactions._load_record(transaction_id),
            'actual_chains':self.p.capture.chain_material(),'actual_canonical':self.store.capture(self.store.data/'live')})
        return worker_result['result']
    def resolve(self,original,owner_capture):
        captured=self.retained(original,'FULL_BROKER_PREPARED')
        args,native=self.decide(original,captured,'QUARANTINED','RESOLVE_OWNER',
            ('OWNER_RECORD_ABORT','OWNER_RECORD_EFFECT'),owner_binding=owner_capture['binding'])
        proof={'owner':owner_capture,'arguments':args,'native':native}
        self.ack(original,'FULL_BROKER_OWNER_DISPOSITION',proof)
        # This method has no dispatch path. The owner caller must consume the
        # selected original-use abort/settle transition and authentic resource
        # terminal/release. Unknown or split mappings remain held/quarantined.
        return {'decision':native['decision'],'proof':proof}
    def followup_plan(self,operation,right,event_id):
        row=self.p.journal.rows[operation]
        from .protected_startup import canonical
        events=[event for event in self.p.journal.body['events'] if digest(canonical(event))==event_id]
        materials=[value['material'] for value in row['boundaries'] if value['name']=='FOLLOWUP_NATIVE'
            and value['material']['right']==right]
        require(len(materials)==1 and len(events)==1 and events[0]['operation']==operation
            and any(value.get('material')==materials[0] for value in events[0]['boundaries']),
            'FULL_BROKER_FOLLOWUP_CURRENT_EVENT_CHANGED')
        from .canonical_followup import replay_followup
        require(replay_followup(self.p,materials[0])=='FOLLOWUP_READY','FULL_BROKER_FOLLOWUP_NATIVE_DENIED')
        plan=clone(self.p.policy['broker']['followup_plans'][right])
        require(set(plan)=={'cost_key','parent','launch'} and set(plan['launch'])==
            {'argv','cwd','environment','systemd_properties','policy','executables'},'FULL_BROKER_OWNER_FOLLOWUP_PLAN_REQUIRED')
        return {'operation':operation,'right':right,'event_id':event_id,'material':materials[0],
            'original_request':clone(row['capture']['request']),'owner_policy':self.p.policy_raw.hex(),'plan':plan}

def replay_boundary(principal,boundary):
    value=restore_archive(bytes.fromhex(boundary['value']))
    require(observe_exchange(principal, *value['arguments'])==value['native'],
        'FULL_BROKER_RETAINED_NATIVE_REPLAY_CHANGED')
