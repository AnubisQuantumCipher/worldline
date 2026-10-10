"""Source-only concrete protected owner issuer and before-attempt caller.

Root-installed owner policy/journal, exact StartupLease and real Gate/issuer,
terminal and full-resource stores are required. No ordinary COSMO right, supplied
DTO or serialized peer observation issues owner authority. Deployment, custody,
machine resource conjunction, anti-rollback and proof remain separate obligations.
"""
from __future__ import annotations
import base64
from dataclasses import asdict, replace
import hashlib
import hmac
import json
import os
from pathlib import Path
import socket
import stat
import tempfile
from threading import RLock
import uuid

from .errors import WorldlineError
from .evaluation_history import EvaluationCursor, EvaluationRecord
from .evaluation_authority import owner_projection, selected_owner_projection
from .evaluation_terminal import TerminalJournal
from .evaluation_pending import PendingHandle
from .owner_transitions import OwnerGrant, OwnerRequest, authorize_owner
from .owner_retry_audit import RetryAudit, UseReceipt, FullScope, decide_retry, authorize_retry_collapse, authorize_checkpoint, authorize_adopt_receipt
from .recovery_observation import archive, restore_archive
from .validation import current_requirements

DOMAIN=b'worldline-protected-owner-transitions-v1\0'
def require(value,code):
    if not value: raise WorldlineError(code,'protected owner transition refused')
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')
def digest(raw):return hashlib.sha256(raw).hexdigest()
def exact(raw):
    def pairs(rows):
        result={}
        for key,value in rows:
            require(key not in result,'OWNER_DUPLICATE_KEY');result[key]=value
        return result
    value=json.loads(raw,object_pairs_hook=pairs)
    require(raw in (canonical(value),canonical(value)+b'\n'),'OWNER_NONCANONICAL')
    return value
def private(path,*,confidential=True):
    path=Path(path)
    require(path.is_absolute() and os.geteuid()==0,'OWNER_PROTECTED_PRINCIPAL_REQUIRED')
    for ancestor in path.parents:
        info=ancestor.lstat()
        require(stat.S_ISDIR(info.st_mode) and info.st_uid==0 and not info.st_mode&0o022,'OWNER_UNTRUSTED_ANCESTOR')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        before=os.fstat(fd)
        forbidden=0o077 if confidential else 0o022
        require(stat.S_ISREG(before.st_mode) and before.st_uid==0 and before.st_nlink==1 and not before.st_mode&forbidden,'OWNER_FILE_CUSTODY')
        with os.fdopen(os.dup(fd),'rb') as src:raw=src.read()
        after=os.fstat(fd)
        require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==
                (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns) and len(raw)==before.st_size,'OWNER_FILE_CHANGED')
        return raw
    finally:os.close(fd)
def encoded(value):return base64.b64encode(archive(value)).decode('ascii')
def decoded(value):
    require(type(value) is str,'OWNER_ARCHIVE_ABSENT')
    raw=base64.b64decode(value,validate=True)
    require(base64.b64encode(raw).decode('ascii')==value,'OWNER_ARCHIVE_ENCODING')
    return restore_archive(raw)
def principal(uid):return canonical({'domain':'linux.uid.v1','uid':uid}).decode('ascii')

class OwnerJournal:
    """Existing complete authenticated owner journal; absence never initializes.
    A surviving mutation intent quarantines. Live save compares complete prior
    bytes before replacing, and durably readbacks journal and independent head.
    External rollback/custody guarantees still require deployment evidence.
    """
    def __init__(self,owner,path):
        self.owner=owner;self.path=Path(path);self.head=self.path.with_name('owner-head.json')
        self.intent=self.path.with_name('owner-mutation-intent.json');self.poisoned=False
        require(not os.path.lexists(self.intent),'OWNER_MUTATION_RECOVERY_REQUIRED')
        self.persisted=private(self.path);self.persisted_head=private(self.head);self._load()
    def _mac(self,body):return hmac.new(self.owner.gate.issuer.key,DOMAIN+canonical(body),'sha256').hexdigest()
    def _load(self):
        envelope=exact(self.persisted);require(type(envelope) is dict and set(envelope)=={'body','mac'},'OWNER_JOURNAL_SCHEMA')
        body=envelope['body'];require(type(envelope['mac']) is str and hmac.compare_digest(envelope['mac'],self._mac(body)),'OWNER_JOURNAL_AUTHENTICATION')
        require(type(body) is dict and set(body)=={'schema','binding','events'} and body['schema']=='worldline.protected-owner-journal-v1'
                and body['binding']==self.owner.binding and type(body['events']) is list,'OWNER_JOURNAL_BINDING')
        self.body=body;self.rows={};prior='GENESIS'
        for event in body['events']:
            require(type(event) is dict and set(event)=={'prior','cause','intent','record'} and event['prior']==prior,'OWNER_EVENT_CHAIN')
            record=decoded(event['record']);require(type(record) is dict and set(record)=={'base','request','boundaries'},'OWNER_EVENT_RECORD')
            base=record['base'];require(type(base) is dict and base['intent']==event['intent'],'OWNER_INTENT_IDENTITY')
            old=self.rows.get(event['intent']);cause=event['cause']
            require(cause in ('ISSUED','RESERVED','DISPATCH_INTENT','OBSERVED','CONSUMED','QUARANTINE','COLLAPSE_INTENT','COLLAPSE_OBSERVED','SETTLED'),'OWNER_EVENT_CAUSE')
            if old is None:
                require(cause=='ISSUED' and record['request'].grant.state=='ISSUED' and record['boundaries']==[],'OWNER_ISSUE_ORDER')
            else:
                require(archive(old['record']['base'])==archive(base),'OWNER_INTENT_BASE_CHANGED')
                require(record['boundaries'][:len(old['record']['boundaries'])]==old['record']['boundaries'],'OWNER_BOUNDARY_PREFIX_CHANGED')
                allowed={'ISSUED':('RESERVED','QUARANTINE'),'RESERVED':('DISPATCH_INTENT','COLLAPSE_INTENT','QUARANTINE'),
                    'DISPATCH_INTENT':('OBSERVED','QUARANTINE'),'OBSERVED':('CONSUMED','QUARANTINE'),
                    'QUARANTINE':('OBSERVED','QUARANTINE'),'CONSUMED':('COLLAPSE_INTENT',),
                    'COLLAPSE_INTENT':('COLLAPSE_OBSERVED',),'COLLAPSE_OBSERVED':('SETTLED',),'SETTLED':()}
                require(cause in allowed[old['cause']],'OWNER_USE_STATE_REPLAY')
                state='RESERVED' if cause in ('RESERVED','DISPATCH_INTENT','OBSERVED','QUARANTINE') else 'CONSUMED'
                if cause=='QUARANTINE':state=old['record']['request'].grant.state
                if cause in ('COLLAPSE_INTENT','COLLAPSE_OBSERVED'):state=old['record']['request'].grant.state
                if cause=='SETTLED':state='CONSUMED'
                require(record['request']==replace(old['record']['request'],grant=replace(old['record']['request'].grant,state=state)),'OWNER_GRANT_AMPLIFICATION')
            require(type(record['request']) is OwnerRequest and record['request'].peer==base['principal']
                    and record['request'].owner==principal(self.owner.policy['owner_uid'])
                    and record['request'].trusted_issuer==self.owner.policy['owner_issuer_id'],'OWNER_RETAINED_PRINCIPAL')
            if cause=='RESERVED':
                before=self.owner._projection(base,after=False)
                require(authorize_owner(before.records,before.finalization,record['request'],core=self.owner.core)=='READY','OWNER_NATIVE_RESERVATION_REPLAY_REFUSED')
            if cause=='SETTLED' and record['request'].action=='ADOPT_REQUIREMENT':
                boundary=record['boundaries'][-1]
                require(boundary['name']=='OWNER_ADOPT_USE_CONSUMED','OWNER_ADOPT_CONSUMED_RECORD_ABSENT')
                effect=[item['capture'] for item in record['boundaries'] if item['name']=='OWNER_COLLAPSE_EFFECT_INTENT']
                require(len(effect)==1,'OWNER_ADOPT_EFFECT_INTENT_AMBIGUOUS')
                bound=effect[0]['owner_binding'];owner=bound['owner']
                issued=next(row for row in bound['events'] if row['cause']=='ISSUED')
                reserved=next(row for row in bound['events'] if row['cause']=='RESERVED')
                receipt=UseReceipt(record['request'].grant,digest(canonical(issued)),digest(canonical(reserved)),digest(canonical(event)),
                    boundary['issued_event'],boundary['reserved_event'])
                audit=RetryAudit(owner.request,receipt,None,None,owner.current_epoch)
                before=self.owner._projection(base,after=False)
                values=restore_archive(effect[0]['packet'])['values']
                require(authorize_adopt_receipt(before.records,before.finalization,audit,values,owner.scope,owner.resulting,core=self.owner.core)=='READY',
                    'OWNER_ADOPT_CONSUMED_NATIVE_REPLAY_REFUSED')
            prior=digest(canonical(event))
            self.rows[event['intent']]={'cause':cause,'event':prior,'record':record}
        anchor=exact(self.persisted_head)
        head_body={'schema':'worldline.protected-owner-head-v1','binding':self.owner.binding,'event_head':prior,'journal_sha256':digest(self.persisted)}
        require(anchor=={'body':head_body,'mac':self._mac(head_body)},'OWNER_ANCHORED_HEAD_CHANGED')
    def _write_existing(self,path,raw):
        private(path)
        fd,name=tempfile.mkstemp(prefix='.owner-write-',dir=path.parent)
        temporary=Path(name)
        try:
            os.fchmod(fd,0o600)
            with os.fdopen(fd,'wb') as output:output.write(raw);output.flush();os.fsync(output.fileno())
            os.replace(temporary,path)
            d=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            try:os.fsync(d)
            finally:os.close(d)
            require(private(path)==raw,'OWNER_DURABLE_READBACK_CHANGED')
        finally:
            if temporary.exists():temporary.unlink()
    def append(self,intent,cause,record):
        require(not self.poisoned and not os.path.lexists(self.intent),'OWNER_DURABILITY_UNKNOWN')
        require(private(self.path)==self.persisted and private(self.head)==self.persisted_head,'OWNER_PRIOR_JOURNAL_CHANGED')
        self.owner.intact()
        prior='GENESIS' if not self.body['events'] else digest(canonical(self.body['events'][-1]))
        event={'prior':prior,'cause':cause,'intent':intent,'record':encoded(record)}
        body={**self.body,'events':self.body['events']+[event]}
        raw=canonical({'body':body,'mac':self._mac(body)})+b'\n'
        head_body={'schema':'worldline.protected-owner-head-v1','binding':self.owner.binding,'event_head':digest(canonical(event)),'journal_sha256':digest(raw)}
        head_raw=canonical({'body':head_body,'mac':self._mac(head_body)})+b'\n'
        marker={'schema':'worldline.owner-journal-mutation-v1','before_journal':digest(self.persisted),'before_head':digest(self.persisted_head),
                'after_journal':digest(raw),'after_head':digest(head_raw),'event':event}
        try:
            fd=os.open(self.intent,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
            with os.fdopen(fd,'wb') as output:output.write(canonical({'body':marker,'mac':self._mac(marker)})+b'\n');output.flush();os.fsync(output.fileno())
            d=os.open(self.path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            try:os.fsync(d)
            finally:os.close(d)
            self._write_existing(self.path,raw);self._write_existing(self.head,head_raw)
            self.intent.unlink()
            d=os.open(self.path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            try:os.fsync(d)
            finally:os.close(d)
            self.persisted,self.persisted_head=raw,head_raw;self._load()
        except BaseException:self.poisoned=True;raise
        return self.rows[intent]

class OwnerAdmission:
    """Live protected reservation handed to the actual EngineEvaluationWriter."""
    def __init__(self,owner,intent):self.owner=owner;self.intent=intent
    def begin(self,terminal,subject,current,measured,core):
        owner=self.owner
        with owner.lock:
            owner.intact();row=owner.journal.rows[self.intent];record=row['record'];base=record['base'];q=record['request']
            require(row['cause']=='RESERVED' and terminal is owner.terminal and core is owner.core,'OWNER_BEGIN_SOURCE_CHANGED')
            require(subject['instanceId']==q.subject and owner.store.world(q.subject).content_id==q.content
                    and current['requirementHash']==q.current_requirement,'OWNER_BEGIN_MEASURED_BINDING_CHANGED')
            now=current_requirements(owner.store,owner.controller.config,owner.core)
            resource=owner.resource_snapshot()
            before=owner._projection(base,after=False)
            fresh=replace(q,current_requirement=now['requirementHash'],resulting_requirement=now['requirementHash'],current_epoch=resource.state.resource_epoch)
            require(authorize_owner(before.records,before.finalization,fresh,core=core)=='READY','OWNER_BEFORE_ATTEMPT_NATIVE_REFUSED')
            require(type(base['pending_handle']) is dict and set(base['pending_handle'])==set(PendingHandle.__dataclass_fields__),'OWNER_ALLOCATED_RUN_UNAVAILABLE')
            handle=PendingHandle(**base['pending_handle'])
            # The original pending kernel replays the complete real intent/head.
            # Durable owner reservation is already present before this link or checks.
            record={**record,'boundaries':record['boundaries']+[{'name':'EVALUATION_DISPATCH_INTENT','measurement':measured,'requirement':current,
                'resource_snapshot':owner.resource_dto(resource),'issuer_head':owner.gate.issuer.head()}]}
            owner.journal.append(self.intent,'DISPATCH_INTENT',record)
            linked=terminal.pending.replay(handle.run)
            require(linked==handle,'OWNER_PENDING_REPLAY_CHANGED')
            return linked

class OwnerAdoption:
    """Live issue intent; independently measured resulting tree reserves it."""
    def __init__(self,owner,intent):self.owner=owner;self.intent=intent
    def transaction_id(self):return self.owner.journal.rows[self.intent]['record']['request'].transaction
    def reserve(self,subject,transaction,current,resulting):
        owner=self.owner
        with owner.lock:
            owner.intact();row=owner.journal.rows[self.intent];record=row['record'];q=record['request']
            require(row['cause'] in ('ISSUED','RESERVED'),'OWNER_ADOPT_ISSUE_STATE_CHANGED')
            resource=owner.resource_snapshot()
            # Both hashes come from the original independent live/staged producers.
            # Owner Expected_Requirement stays as originally requested and signed.
            proposed=replace(q,subject=subject.instance_id,content=subject.content_id,transaction=transaction,
                current_requirement=current['requirementHash'],resulting_requirement=resulting['requirementHash'],
                current_epoch=resource.state.resource_epoch,grant=replace(q.grant,state='RESERVED'))
            before=owner._projection(record['base'],after=False)
            require(authorize_owner(before.records,before.finalization,proposed,core=owner.core)=='READY','OWNER_ADOPT_RESULT_NATIVE_REFUSED')
            require(proposed==replace(q,grant=replace(q.grant,state='RESERVED')),'OWNER_ADOPT_ISSUED_BINDING_CHANGED')
            if row['cause']=='ISSUED':
                owner.journal.append(self.intent,'RESERVED',{**record,'request':proposed,
                    'boundaries':record['boundaries']+[{'name':'INDEPENDENT_RESULT_REQUIREMENT','current':current,
                        'resulting':resulting,'resource_snapshot':owner.resource_dto(resource),'issuer_head':owner.gate.issuer.head()}]})
            return proposed

class ProtectedOwnerPrincipal:
    def __init__(self,gate,controller,resource_service,*,startup_lease):
        import intent_gate
        import run_service
        from .protected_startup import StartupLease
        require(type(startup_lease) is StartupLease and type(gate) is intent_gate.Gate and
                type(resource_service) is run_service.RunLedgerService,'OWNER_ACTUAL_SOURCE_INTERFACE_UNAVAILABLE')
        require(os.geteuid()==0 and startup_lease.gate is gate and startup_lease.controller is controller
                and startup_lease.state_path==controller.paths.state,'OWNER_STARTUP_LEASE_BINDING')
        self.lease=startup_lease;self.gate=gate;self.controller=controller;self.store=controller.store;self.core=controller.core
        self.resources=resource_service;self.lock=RLock()
        self.terminal=getattr(self.store,'evaluation_terminal',None)
        require(type(self.terminal) is TerminalJournal,'OWNER_EXISTING_TERMINAL_REQUIRED')
        self.policy_path=gate.state_path.parent/'owner-policy.json';raw=private(self.policy_path);self.policy=exact(raw)
        require(type(self.policy) is dict and set(self.policy)=={'schema','installation_id','owner_uid','owner_gid','owner_issuer_id','gate_config_sha256',
            'issuer_policy_sha256','issuer_key_sha256','store_genesis','native_sha256','sources'} and self.policy['schema']=='worldline.protected-owner-policy-v1','OWNER_POLICY_SCHEMA')
        require(type(self.policy['owner_uid']) is int and self.policy['owner_uid']>=0 and type(self.policy['owner_gid']) is int and self.policy['owner_gid']>=0
                and type(self.policy['owner_issuer_id']) is str and self.policy['owner_issuer_id'],'OWNER_POLICY_PRINCIPAL_ABSENT')
        require(self.policy_path in self.lease.allowed and self.policy['installation_id']==self.lease.spec['installation_id']
                and self.policy['gate_config_sha256']==digest(gate.config_raw) and self.policy['issuer_policy_sha256']==gate.issuer.policy_sha256
                and self.policy['issuer_key_sha256']==digest(gate.issuer.key) and self.policy['store_genesis']==self.store.get_meta('protectedStoreGenesis')
                and self.policy['native_sha256']==digest(private(Path(self.core.library_path),confidential=False)),'OWNER_POLICY_INSTALLATION_CHANGED')
        require(self.policy['sources'] and type(self.policy['sources']) is dict,'OWNER_COMPLETE_SOURCE_IDENTITY_ABSENT')
        required_sources={Path(__file__),Path(__file__).with_name('owner_retry_audit.py'),Path(__file__).with_name('owner_transitions.py'),
            Path(__file__).with_name('owner_collapse_data.py'),Path(__file__).with_name('owner_intent_endpoint.py'),
            Path(__file__).with_name('transaction.py'),Path(__file__).with_name('evaluation_authority.py'),
            Path(__file__).with_name('evaluation_writer.py'),Path(__file__).with_name('revalidate.py'),
            Path(__file__).with_name('recovery_observation.py'),Path(__file__).with_name('protected_recovery_capture.py'),
            Path(intent_gate.__file__),Path(run_service.__file__),Path(__file__).with_name('protected_owner_bootstrap.py')}
        require(required_sources <= {Path(path) for path in self.policy['sources']},'OWNER_REQUIRED_SOURCE_OMITTED')
        for path,expected in self.policy['sources'].items():
            require(Path(path) in self.lease.allowed and digest(private(Path(path),confidential=False))==expected,'OWNER_SOURCE_IDENTITY_CHANGED')
        self.binding={key:self.policy[key] for key in ('installation_id','owner_issuer_id','owner_uid','gate_config_sha256',
            'issuer_policy_sha256','issuer_key_sha256','store_genesis','native_sha256')};self.binding['policy_sha256']=digest(raw)
        self.intact();self._owner_genesis()
        self.journal=OwnerJournal(self,gate.state_path.parent/'owner-transitions.json')
        controller.protected_owner=self
        controller.transactions.protected_owner=self
    def _owner_genesis(self):
        """Consume an existing complete owner-provisioned Genesis admission.
        No daemon initialization, issue-on-absence or existence-derived first
        boot. The protected operator provisioning action remains unperformed.
        """
        from .resource_run_ledger import dto_record
        root=self.gate.state_path.parent
        genesis_path=root/'owner-genesis.json';ledger_path=root/'owner-bootstrap.json'
        require(genesis_path in self.lease.allowed and ledger_path in self.lease.allowed,'OWNER_GENESIS_NOT_INSTALLATION_BOUND')
        required={str(root/name) for name in ('owner-policy.json','owner-transitions.json','owner-head.json','owner-genesis.json','owner-bootstrap.json')}
        require(required <= set(self.lease.spec['provisioned_state']),'OWNER_EXISTING_LAYOUT_NOT_PROVISIONED')
        raw=private(genesis_path);envelope=exact(raw)
        require(type(envelope) is dict and set(envelope)=={'body','mac'},'OWNER_GENESIS_SCHEMA')
        body=envelope['body']
        expected={'schema','binding','installation_genesis_sha256','gate_head','issuer_head','store_head','resource_genesis','journal_sha256','head_sha256'}
        require(type(body) is dict and set(body)==expected and body['schema']=='worldline.protected-owner-genesis-v1'
            and body['binding']==self.binding,'OWNER_GENESIS_BINDING_CHANGED')
        mac=hmac.new(self.gate.issuer.key,DOMAIN+b'genesis\0'+canonical(body),'sha256').hexdigest()
        require(type(envelope['mac']) is str and hmac.compare_digest(envelope['mac'],mac),'OWNER_GENESIS_AUTHENTICATION')
        require(body['installation_genesis_sha256']==digest(self.lease.genesis_raw)
            and body['gate_head']==self.lease.genesis['gate_head'] and body['issuer_head']==self.lease.genesis['issuer_head']
            and body['store_head']==self.lease.genesis['store']['initial_head']
            and body['resource_genesis']==dto_record(self.resources.genesis),'OWNER_GENESIS_INITIAL_HEADS_CHANGED')
        initial={'schema':'worldline.protected-owner-journal-v1','binding':self.binding,'events':[]}
        journal=canonical({'body':initial,'mac':hmac.new(self.gate.issuer.key,DOMAIN+canonical(initial),'sha256').hexdigest()})+b'\n'
        head={'schema':'worldline.protected-owner-head-v1','binding':self.binding,'event_head':'GENESIS','journal_sha256':digest(journal)}
        head_raw=canonical({'body':head,'mac':hmac.new(self.gate.issuer.key,DOMAIN+canonical(head),'sha256').hexdigest()})+b'\n'
        require(body['journal_sha256']==digest(journal) and body['head_sha256']==digest(head_raw),'OWNER_GENESIS_INITIAL_JOURNAL_CHANGED')
        ledger=exact(private(ledger_path))
        admission={'schema':'worldline.owner-bootstrap-admission-v1','genesis_sha256':digest(raw),'binding':self.binding,
            'state':'CONSUMED','events':[{'cause':'OWNER_GENESIS_PROVISIONED','genesis_sha256':digest(raw),
                'journal_sha256':digest(journal),'head_sha256':digest(head_raw)}]}
        require(ledger=={'body':admission,'mac':hmac.new(self.gate.issuer.key,DOMAIN+b'bootstrap\0'+canonical(admission),'sha256').hexdigest()},
            'OWNER_ONE_SHOT_GENESIS_ADMISSION_UNESTABLISHED')
        self.genesis_raw,self.bootstrap_raw=raw,private(ledger_path)

    def intact(self):
        self.lease.intact()
        require(self.gate.issuer.lock_fd>=0,'OWNER_STARTUP_LEASE_LOST')
        info=os.fstat(self.gate.issuer.lock_fd)
        require(stat.S_ISREG(info.st_mode) and info.st_uid==0 and info.st_nlink==1,'OWNER_ISSUER_LOCK_CUSTODY')
        self.gate.issuer.head()
        if hasattr(self,'genesis_raw'):
            require(private(self.gate.state_path.parent/'owner-genesis.json')==self.genesis_raw
                and private(self.gate.state_path.parent/'owner-bootstrap.json')==self.bootstrap_raw,'OWNER_GENESIS_ADMISSION_CHANGED')
    def resource_snapshot(self):
        # Actual retained complete full ledger plus original native replay.
        with self.resources.ordered_operation(),self.resources.connect() as db:
            return self.resources._snapshot(db)
    @staticmethod
    def resource_dto(snapshot):
        from .resource_run_ledger import dto_record
        return {'state':dto_record(snapshot.state),'rows':[dto_record(row) for row in snapshot.rows]}
    def _projection(self,base,*,after):
        world=base['world'];material=base['before_material']
        return owner_projection(self.store,world,base['current_requirement']['requirementHash'],core=self.core,material=material)
    def _peer(self,request):
        from .client_peer import RequestPeer
        require(type(request) is RequestPeer,'OWNER_ORIGINAL_PEER_DESCRIPTOR_REQUIRED')
        observed=request.observation();peer=observed['peer']
        require(peer['uid']==self.policy['owner_uid'],'OWNER_KERNEL_PEER_REFUSED')
        return observed,principal(peer['uid'])
    def _prior(self,projection):return projection.current
    def _failed(self,projection,requirement):
        # Proposal only: actual K.Latest_Failed_Head checks complete source history.
        failed=None
        for row in (() if projection.finalization is None else (projection.finalization,))+projection.records:
            if row.requirement==requirement and row.state=='COMPLETED' and row.outcome=='FAIL':failed=EvaluationCursor(row.epoch,row.run)
        return failed
    def _intent(self,request):
        observation,who=self._peer(request);identifier=observation['requestId']
        require(type(identifier) is str and identifier,'OWNER_REQUEST_ID_REQUIRED')
        return identifier,observation,who
    def _duplicate(self,intent,observed):
        old=self.journal.rows.get(intent)
        if old is None:return None
        base=old['record']['base']
        require(base['request_observation']['rawRequest']==observed['rawRequest'] and base['principal']==principal(observed['peer']['uid']),'OWNER_DUPLICATE_CONFLICT')
        return old
    def retry(self,request,world_value,reason):
        with self.lock:
            self.intact();intent,observed,who=self._intent(request)
            old=self._duplicate(intent,observed)
            if old is not None:return self.recover(request,intent)
            require(type(reason) is str and reason,'OWNER_REASON_REQUIRED')
            world=self.store.world(world_value);current=current_requirements(self.store,self.controller.config,self.core)
            before=owner_projection(self.store,world,current['requirementHash'],core=self.core)
            resource=self.resource_snapshot()
            # Original durable allocator reserves intent only; no checks or target
            # pending link occur before complete native owner reservation below.
            handle=self.terminal.pending.reserve_pending(world.instance_id,world.content_id,current['requirementHash'])
            attempted=EvaluationCursor(handle.epoch,handle.run);grant_id=uuid.uuid4().hex;use_id=uuid.uuid4().hex
            txid=uuid.uuid4().hex;failed=self._failed(before,current['requirementHash'])
            g=OwnerGrant('RETRY_EVALUATION','ISSUED',grant_id,use_id,self.policy['owner_issuer_id'],who,world.instance_id,world.content_id,
                txid,current['requirementHash'],current['requirementHash'],reason,grant_id,grant_id,use_id,failed,before.current,attempted,resource.state.resource_epoch)
            q=OwnerRequest('RETRY_EVALUATION',who,principal(self.policy['owner_uid']),self.policy['owner_issuer_id'],world.instance_id,world.content_id,
                txid,current['requirementHash'],current['requirementHash'],before.current,attempted,resource.state.resource_epoch,g)
            base={'intent':intent,'request_observation':observed,'principal':who,'world':world,'current_requirement':current,
                'before_material':before.authority_material,'resource_snapshot':self.resource_dto(resource),'issuer_head':self.gate.issuer.head(),
                'pending_handle':asdict(handle),'expected_requirement':current['requirementHash']}
            # Handles are serialized as exact data and reconstructed locally.
            record={'base':base,'request':q,'boundaries':[]};self.journal.append(intent,'ISSUED',record)
            reserved=replace(q,grant=replace(g,state='RESERVED'))
            require(authorize_owner(before.records,before.finalization,reserved,core=self.core)=='READY','OWNER_RETRY_NATIVE_RESERVATION_REFUSED')
            record={**record,'request':reserved};self.journal.append(intent,'RESERVED',record)
            try:result=self.controller.revalidator.revalidate(world.instance_id,owner_admission=OwnerAdmission(self,intent))
            except BaseException as error:
                row=self.journal.rows[intent];record={**row['record'],'boundaries':row['record']['boundaries']+[{'name':'EVALUATOR_EXCEPTION','type':type(error).__qualname__,'text':str(error)}]}
                self.journal.append(intent,'QUARANTINE',record);raise
            return self._observe_consume(intent,result)
    def _observe_consume(self,intent,result):
        row=self.journal.rows[intent];record=row['record'];base=record['base'];q=record['request']
        after=owner_projection(self.store,self.store.world(q.subject),q.current_requirement,core=self.core)
        # Full classifier/producer replay provides the acknowledged terminal row.
        require(any(r.run==q.attempt.run and r.epoch==q.attempt.epoch and r.state in ('COMPLETED','ERROR') for r in after.records),'OWNER_TERMINAL_ACK_NOT_OBSERVED')
        observed={**record,'boundaries':record['boundaries']+[{'name':'ACTUAL_TERMINAL_ACK','after_material':after.authority_material,'result':result}]}
        if row['cause']!='OBSERVED':self.journal.append(intent,'OBSERVED',observed)
        else:observed=record
        events=[e for e in self.journal.body['events'] if e['intent']==intent]
        require(any(e['cause']=='DISPATCH_INTENT' for e in events),'OWNER_USE_DISPATCH_NOT_RETAINED')
        issue=next(e for e in events if e['cause']=='ISSUED');reserve=next(e for e in events if e['cause']=='RESERVED')
        consumed={**observed,'request':replace(q,grant=replace(q.grant,state='CONSUMED')),
            'boundaries':observed['boundaries']+[{'name':'OWNER_USE_CONSUMED',
                'issued_event':digest(canonical(issue)),'reserved_event':digest(canonical(reserve)),
                'grant':q.grant.grant,'use':q.grant.use_id,'issuer_head':self.gate.issuer.head()}]}
        self.journal.append(intent,'CONSUMED',consumed)
        return self._answer(intent)
    def _answer(self,intent):
        row=self.journal.rows[intent]
        return {'schema':'worldline.owner-transition-answer-v1','intent':intent,'state':row['cause'],'event_head':row['event'],
            'transaction':row['record']['request'].transaction,'boundaries':encoded(row['record']['boundaries'])}
    def recover(self,request,intent):
        with self.lock:
            self.intact();_id,observed,_who=self._intent(request);old=self.journal.rows.get(intent)
            require(old is not None,'OWNER_INTENT_NOT_COMMITTED')
            require(old['record']['base']['principal']==principal(observed['peer']['uid']),'OWNER_RECOVERY_PEER_CONFLICT')
            if observed['operation']!='owner.recover':self._duplicate(intent,observed)
            if old['cause'] in ('DISPATCH_INTENT','QUARANTINE','OBSERVED') and old['record']['request'].action=='RETRY_EVALUATION':
                try:return self._observe_consume(intent,{'source':'retained-terminal-recovery'})
                except WorldlineError as error:
                    if error.code=='OWNER_TERMINAL_ACK_NOT_OBSERVED':return self._answer(intent)
                    raise
            # No second evaluation/launch, no release, no issue-on-absence.
            return self._answer(intent)
    def audit(self,world,requirement,*,prepared=None):
        self.intact();matches=[]
        for intent,row in self.journal.rows.items():
            q=row['record']['request']
            if row['cause'] in ('CONSUMED','COLLAPSE_INTENT','COLLAPSE_OBSERVED','SETTLED') and q.action=='RETRY_EVALUATION' and q.subject==world.instance_id and q.content==world.content_id and q.current_requirement==requirement:
                matches.append((intent,row))
        require(matches,'OWNER_RETRY_RECEIPT_ABSENT')
        intent,row=matches[-1];record=row['record'];base=record['base'];consumed=record['request'].grant
        events=[e for e in self.journal.body['events'] if e['intent']==intent]
        issue=next(e for e in events if e['cause']=='ISSUED');reserve=next(e for e in events if e['cause']=='RESERVED')
        consumed_event=next(e for e in events if e['cause']=='CONSUMED')
        issued_id,reserved_id,consumed_id=(digest(canonical(e)) for e in (issue,reserve,consumed_event))
        before=self._projection(base,after=False)
        after=owner_projection(self.store,world,requirement,core=self.core)
        q=decoded(reserve['record'])['request']
        # Consumed references are read from the actual immutable event chain,
        # not a caller's receipt. Whole event bytes remain in the signed journal.
        use_records=[item for item in record['boundaries'] if item['name']=='OWNER_USE_CONSUMED']
        require(len(use_records)==1,'OWNER_CONSUMED_RECEIPT_AMBIGUOUS')
        use_record=use_records[0]
        require(use_record['name']=='OWNER_USE_CONSUMED','OWNER_CONSUMED_RECEIPT_ABSENT')
        receipt=UseReceipt(consumed,issued_id,reserved_id,consumed_id,
            use_record['issued_event'],use_record['reserved_event'])
        cursor=after.current if prepared is None else EvaluationCursor(prepared['epoch'],prepared['run'])
        audit=RetryAudit(q,receipt,after.current,cursor,self.resource_snapshot().state.resource_epoch)
        require(decide_retry(before.records,after.records,before.finalization,after.finalization,audit,core=self.core)=='READY','OWNER_RETRY_FULL_AUDIT_REFUSED')
        return before,after,audit
    def selected(self,world,requirement,*,prepared=None):
        _before,after,_audit=self.audit(world,requirement,prepared=prepared)
        return selected_owner_projection(world,after)
    def retry_transaction(self,world,requirement):
        _before,_after,audit=self.audit(world,requirement)
        return audit.before_request.transaction
    def conjunction_retry(self,values,subject,transaction,requirement):
        before,after,audit=self.audit(subject,requirement)
        return authorize_retry_collapse(before.records,after.records,before.finalization,after.finalization,audit,values,
            FullScope(subject.instance_id,subject.content_id,transaction),core=self.core)
    def has_retry(self,world,requirement):
        self.intact()
        return any(row['cause'] in ('CONSUMED','COLLAPSE_INTENT','COLLAPSE_OBSERVED','SETTLED') and row['record']['request'].action=='RETRY_EVALUATION'
            and row['record']['request'].subject==world.instance_id and row['record']['request'].content==world.content_id
            and row['record']['request'].current_requirement==requirement for row in self.journal.rows.values())
    def prepare_adopt(self,request,world_value,reason,expected_requirement):
        with self.lock:
            self.intact();intent,observed,who=self._intent(request)
            old=self._duplicate(intent,observed)
            if old is not None:return self.recover(request,intent)
            require(type(reason) is str and reason and type(expected_requirement) is str and expected_requirement,'OWNER_ADOPT_REASON_EXPECTATION_REQUIRED')
            world=self.controller.returns.select(world_value)
            require(world.actor=='worldline','OWNER_ADOPT_CHECKPOINT_REQUIRED')
            current=current_requirements(self.store,self.controller.config,self.core)
            before=owner_projection(self.store,world,current['requirementHash'],core=self.core)
            resource=self.resource_snapshot();txid=uuid.uuid4().hex;grant_id=uuid.uuid4().hex;use_id=uuid.uuid4().hex
            g=OwnerGrant('ADOPT_REQUIREMENT','ISSUED',grant_id,use_id,self.policy['owner_issuer_id'],who,world.instance_id,world.content_id,
                txid,current['requirementHash'],expected_requirement,reason,grant_id,grant_id,use_id,None,before.current,None,resource.state.resource_epoch)
            q=OwnerRequest('ADOPT_REQUIREMENT',who,principal(self.policy['owner_uid']),self.policy['owner_issuer_id'],world.instance_id,world.content_id,
                txid,current['requirementHash'],expected_requirement,before.current,None,resource.state.resource_epoch,g)
            base={'intent':intent,'request_observation':observed,'principal':who,'world':world,'current_requirement':current,
                'before_material':before.authority_material,'resource_snapshot':self.resource_dto(resource),'issuer_head':self.gate.issuer.head(),
                'pending_handle':None,'expected_requirement':expected_requirement}
            self.journal.append(intent,'ISSUED',{'base':base,'request':q,'boundaries':[]})
            # Preparation materializes/measures only; owner reservation occurs in
            # the original resulting-requirement seam before native prepare READY.
            candidate=self.controller.returns.prepare_candidate(world)
            prepared=self.controller.transactions.prepare(candidate.instance_id,kind='return',return_of=world.instance_id,
                owner_adoption=OwnerAdoption(self,intent))
            return {**self._answer(intent),'prepared':asdict(prepared)}
    def adopt_request(self,subject,transaction,current,resulting):
        self.intact()
        found=[row for row in self.journal.rows.values() if row['record']['request'].action=='ADOPT_REQUIREMENT'
            and row['record']['request'].transaction==transaction]
        if not found:return None
        require(len(found)==1 and found[0]['cause']=='RESERVED','OWNER_ADOPT_RESERVED_RECEIPT_UNAVAILABLE')
        q=found[0]['record']['request'];before=self._projection(found[0]['record']['base'],after=False)
        # Do not substitute owner's saved expected hash for fresh staged capture.
        fresh=replace(q,subject=subject.instance_id,content=subject.content_id,current_requirement=current,
            resulting_requirement=resulting,current_epoch=self.resource_snapshot().state.resource_epoch)
        require(authorize_owner(before.records,before.finalization,fresh,core=self.core)=='READY','OWNER_ADOPT_FRESH_NATIVE_REFUSED')
        return fresh
    def conjunction_checkpoint(self,values,subject,transaction,resulting):
        q=self.adopt_request(subject,transaction,current=None if values.current_requirement is None else 'sha256:'+values.current_requirement.hex(),
            resulting=None if resulting is None else 'sha256:'+resulting.hex())
        projection=owner_projection(self.store,subject,None if values.current_requirement is None else 'sha256:'+values.current_requirement.hex(),core=self.core)
        return authorize_checkpoint(projection.records,projection.finalization,values,resulting,
            FullScope(subject.instance_id,subject.content_id,transaction),q,core=self.core)
    def capture_collapse(self,values,subject,transaction,resulting,*,prepared=None):
        from .owner_collapse_data import OwnerCollapseData
        scope=FullScope(subject.instance_id,subject.content_id,transaction)
        requirement=None if values.current_requirement is None else 'sha256:'+values.current_requirement.hex()
        if values.mode=='CHECKPOINT_RETURN':
            request=self.adopt_request(subject,transaction,requirement,None if resulting is None else 'sha256:'+resulting.hex())
            if request is None:return OwnerCollapseData('CHECKPOINT_EQUAL',scope,subject,requirement,None,None,None,None,None,None,resulting,None)
            row=next(row for row in self.journal.rows.values() if row['record']['request'].transaction==transaction)
            return OwnerCollapseData('ADOPT_REQUIREMENT',scope,subject,requirement,row['record']['base']['before_material'],None,request,None,
                self.resource_snapshot().state.resource_epoch,None,resulting,row['event'])
        before,after,audit=self.audit(subject,requirement,prepared=prepared)
        return OwnerCollapseData('RETRY_EVALUATION',scope,subject,requirement,before.authority_material,after.authority_material,
            audit.before_request,audit.receipt,audit.current_epoch,prepared,resulting,audit.receipt.consumed_event)
    def validate_packet_owner(self,packet):
        """Authenticate separately from packet replay through the actual journal.
        The protected canonical service must call this before fresh owner effects.
        After-effect settlement must use its retained signed owner intent instead.
        """
        from .owner_collapse_data import OwnerCollapseData
        from .recovery_observation import restore_archive
        data=restore_archive(packet);owner=data.get('owner')
        require(type(owner) is OwnerCollapseData,'OWNER_PACKET_CAPTURE_ABSENT')
        actual=self.capture_collapse(data['values'],self.store.world(owner.scope.subject),owner.scope.transaction,
            owner.resulting,prepared=owner.prepared)
        require(archive(actual)==archive(owner),'OWNER_PACKET_JOURNAL_CUSTODY_CHANGED')
        return actual


    def recovery_binding(self,capture):
        """Authentic producer-side binding under the actual owner/store lease.
        This is captured before dispatch and then covered by the existing full
        recovery journal HMAC. No claimant supplies this object through IPC.
        """
        with self.lock:
            owner=self.validate_packet_owner(capture['packet'])
            if owner.mode=='CHECKPOINT_EQUAL':return None
            matches=[(intent,row) for intent,row in self.journal.rows.items()
                if row['record']['request'].transaction==owner.scope.transaction]
            require(len(matches)==1,'OWNER_RECOVERY_INTENT_AMBIGUOUS')
            intent,row=matches[0]
            require(owner.event in (row['event'],owner.receipt.consumed_event if owner.receipt is not None else None),
                'OWNER_RECOVERY_EVENT_CHANGED')
            original_subject=capture['record'].get('returnOf') or capture['record']['candidateWorld']
            require(capture['record']['transactionId']==owner.scope.transaction and original_subject==owner.scope.subject,
                'OWNER_RECOVERY_ORIGINAL_TRANSACTION_CHANGED')
            return {'schema':'worldline.owner-recovery-binding-v1','intent':intent,'owner':owner,
                'record':row['record'],'events':[event for event in self.journal.body['events'] if event['intent']==intent],
                'pending':capture['pending'],'binding':capture['binding'],'packet':capture['packet'],
                'policy_binding':self.binding}
    def begin_collapse(self,capture):
        with self.lock:
            self.intact();bound=capture.get('owner_binding')
            if bound is None:return None
            require(archive(self.recovery_binding(capture))==archive(bound),'OWNER_BEFORE_EXCHANGE_CUSTODY_CHANGED')
            intent=bound['intent'];row=self.journal.rows[intent]
            expected='RESERVED' if bound['owner'].mode=='ADOPT_REQUIREMENT' else 'CONSUMED'
            require(row['cause']==expected,'OWNER_EXCHANGE_ONESHOT_REFUSED')
            record={**row['record'],'boundaries':row['record']['boundaries']+[{'name':'OWNER_COLLAPSE_EFFECT_INTENT','capture':capture}]}
            return self.journal.append(intent,'COLLAPSE_INTENT',record)
    def historical_owner_binding(self,capture):
        """After-effect check: same signed intent, no current policy substitution."""
        with self.lock:
            self.intact();bound=capture.get('owner_binding')
            if bound is None:return None
            require(bound['policy_binding']==self.binding,'OWNER_HISTORICAL_INSTALLATION_CHANGED')
            row=self.journal.rows.get(bound['intent'])
            require(row is not None and row['cause'] in ('COLLAPSE_INTENT','COLLAPSE_OBSERVED','SETTLED'),
                'OWNER_HISTORICAL_EFFECT_INTENT_ABSENT')
            effects=[item['capture'] for item in row['record']['boundaries'] if item['name']=='OWNER_COLLAPSE_EFFECT_INTENT']
            require(len(effects)==1 and archive(effects[0])==archive(capture),'OWNER_HISTORICAL_FULL_CAPTURE_CHANGED')
            events=[event for event in self.journal.body['events'] if event['intent']==bound['intent']]
            require(archive(events[:len(bound['events'])])==archive(bound['events'])
                and archive(bound['record']['base'])==archive(row['record']['base']),'OWNER_HISTORICAL_FULL_PREFIX_CHANGED')
            return row
    def finish_collapse(self,principal,row):
        """Consume Adopt once after actual native effect and original receipts.
        The actual protected recovery principal supplies its own retained row;
        caller packet DTOs never establish these effects or journal custody.
        """
        import recovery_principal
        require(type(principal) is recovery_principal.ProtectedRecoveryPrincipal and principal.gate is self.gate
            and principal.capture.controller is self.controller and principal.capture.startup_lease is self.lease,
            'OWNER_ACTUAL_RECOVERY_SERVICE_REQUIRED')
        capture=row['capture'];operation=capture['pending']['operation_id']
        require(not principal.journal.poisoned and operation in principal.journal.latest and
            archive(principal.journal.latest[operation])==archive(row),'OWNER_ACTUAL_RECOVERY_JOURNAL_CHANGED')
        owner_row=self.historical_owner_binding(capture)
        if owner_row is None:return None
        bound=capture['owner_binding'];intent=bound['intent'];owner=bound['owner']
        required=('RECEIPT_ACK','UNIVERSE_ACK','RESOURCE_ACK','GRANT_ACK')
        evidence={name:principal._boundary(row,name) for name in required}
        if owner_row['cause']=='SETTLED':
            acknowledgements=[item for item in owner_row['record']['boundaries'] if item['name']=='OWNER_COLLAPSE_EFFECT_ACK']
            require(len(acknowledgements)==1 and archive(acknowledgements[0]['recovery_evidence'])==archive(evidence),
                'OWNER_COMMITTED_DUPLICATE_ACK_CHANGED')
            self.store.verify_chains();retained=self.store.receipt_for_transaction(owner.scope.transaction)
            require(retained is not None and self.store.read_canonical('receipts',retained['canonical_path'],chain_hash=retained['chain_hash'])
                ==acknowledgements[0]['canonical_receipt'],'OWNER_COMMITTED_DUPLICATE_RECEIPT_CHANGED')
            # Exact durable replay: later policy/head/live movement cannot issue
            # another effect or revoke an already consumed owner settlement.
            return self._answer(intent)
        binding=principal.capture.historical(capture);native,facts=principal.capture.observe_effect()
        action,_state=principal.relation.decide(state='CLAIMED',issued=binding,recovered=binding,
            fresh='REFUSED',historical='HISTORICALLY_AUTHORIZED',grant_eligible=False,native=native)
        require(action=='SETTLE','OWNER_AFTER_EFFECT_NATIVE_UNESTABLISHED')
        actual=self.controller.transactions._load_record(owner.scope.transaction)
        require(actual['state']=='COMMITTED','OWNER_ORIGINAL_RECEIPT_STATE_UNESTABLISHED')
        self.store.verify_chains();receipt=self.store.receipt_for_transaction(owner.scope.transaction)
        require(receipt is not None,'OWNER_ORIGINAL_CANONICAL_RECEIPT_ABSENT')
        canonical_receipt=self.store.read_canonical('receipts',receipt['canonical_path'],chain_hash=receipt['chain_hash'])
        result=evidence['RECEIPT_ACK']['receipt']
        require(result['transactionId']==owner.scope.transaction and result['state']=='COMMITTED'
            and result['beforeRoot']==capture['record']['beforeRoot'] and result['afterRoot']==capture['record']['stagedRoot']
            and result['receipt']['receiptId']==receipt['receipt_id'],'OWNER_ACTUAL_CANONICAL_RECEIPT_CHANGED')
        if owner_row['cause']=='COLLAPSE_INTENT':
            observed={**owner_row['record'],'boundaries':owner_row['record']['boundaries']+[{'name':'OWNER_COLLAPSE_EFFECT_ACK',
                'native_observation':facts,'recovery_evidence':evidence,'receipt_row':dict(receipt),'canonical_receipt':canonical_receipt}]}
            owner_row=self.journal.append(intent,'COLLAPSE_OBSERVED',observed)
        record=owner_row['record'];events=[event for event in self.journal.body['events'] if event['intent']==intent]
        issue=next(event for event in events if event['cause']=='ISSUED');reserved=next(event for event in events if event['cause']=='RESERVED')
        if owner.mode=='ADOPT_REQUIREMENT':
            consumed=replace(owner.request.grant,state='CONSUMED')
            # The proposed consumed event identity is exact canonical bytes that
            # will be durably written. Native receipt replay runs again on load.
            boundary={'name':'OWNER_ADOPT_USE_CONSUMED','issued_event':digest(canonical(issue)),
                'reserved_event':digest(canonical(reserved)),'grant':consumed.grant,'use':consumed.use_id,
                'receipt_row':dict(receipt),'canonical_receipt':canonical_receipt}
            settled={**record,'request':replace(record['request'],grant=consumed),'boundaries':record['boundaries']+[boundary]}
            prior=digest(canonical(self.journal.body['events'][-1]))
            event={'prior':prior,'cause':'SETTLED','intent':intent,'record':encoded(settled)}
            consumed_id=digest(canonical(event))
            use=UseReceipt(consumed,boundary['issued_event'],boundary['reserved_event'],consumed_id,
                boundary['issued_event'],boundary['reserved_event'])
            audit=RetryAudit(owner.request,use,None,None,owner.current_epoch)
            before=self._projection(record['base'],after=False)
            values=restore_archive(capture['packet'])['values']
            require(authorize_adopt_receipt(before.records,before.finalization,audit,values,owner.scope,owner.resulting,core=self.core)=='READY',
                'OWNER_ADOPT_CONSUMED_NATIVE_REFUSED')
        else:settled=record
        self.journal.append(intent,'SETTLED',settled)
        return self._answer(intent)

def installed_owner(controller):
    owner=getattr(controller,'protected_owner',None)
    require(type(owner) is ProtectedOwnerPrincipal and owner.controller is controller,'OWNER_PROTECTED_SOURCE_UNAVAILABLE')
    owner.intact();return owner
