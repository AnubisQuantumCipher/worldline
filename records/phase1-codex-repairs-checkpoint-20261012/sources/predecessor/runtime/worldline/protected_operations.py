"""Protected canonical operation principal; source engineering, never admission.

One real StartupLease/issuer lock, complete HMAC journals and original sockets
own the decisions. No ordinary request supplies grants, facts or resource costs.
Missing original producers refuse. Historical settlement never redispatches.
"""
from __future__ import annotations
import asyncio
from contextlib import contextmanager
from contextvars import ContextVar
import copy
import ctypes
import hashlib
import hmac
import inspect
import json
import os
from pathlib import Path
import socket
import sqlite3
import stat
import uuid
from .client_peer import KernelPeer,RequestPeer,request_scope,current_peer
from .errors import WorldlineError
from .operation_authority_kernel import OperationAuthorityKernel,OPS,FIELDS,keys
from .operation_owner_kernel import initialize_owner_kernel, observe_operation
from .protected_startup import StartupLease,canonical,exact_json,private_bytes,require
from .protected_recovery_capture import ProtectedCapture
from .operation_capture import archive,restore_archive
def identity(value):return hashlib.sha256(archive(value)).digest()
from .recovery_authority_kernel_v3 import RecoveryAuthorityKernelV3,BoundUse,NativeObservation,HASH_FIELDS
from .chain_authority import ChainRow,ChainAnchors,replay_chain
from .core import hash_id,hash_bytes_from_id
from .validation import current_requirements

DOMAIN=b'worldline-protected-canonical-operations-v1\0'
_CURRENT=ContextVar('worldline_actual_operation_scope',default=None)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def quantity(value):
    # Representation only. Eligibility and arithmetic are exclusively native.
    if type(value) is not int or value<0:raise WorldlineError('OPERATION_QUANTITY_INVALID','nonnegative native quantity required')
    return {'negative':False,'raw':value.to_bytes((value.bit_length()+7)//8,'little').hex()}
def empty_binding():
    return {'action':'ping','id':dict.fromkeys(FIELDS), 'peer':None,'preparer':None,'owner':None,'target_owner':None,'policy_epoch':None,'resource_epoch':None}
def empty_evidence():
    return {'effect_binding':empty_binding(),'actual_receipt_root':None,'actual_causal_root':None,
            'no_effect_binding':empty_binding(),'owner_resolution':empty_binding(),'quarantine_head':None,
            'witnessed_receipt_head':None,'witnessed_causal_head':None,
            'recovery':{'issued':BoundUse(mode='CANDIDATE',**dict.fromkeys(HASH_FIELDS),policy_epoch=None,resource_epoch=None),
                        'recovered':BoundUse(mode='CANDIDATE',**dict.fromkeys(HASH_FIELDS),policy_epoch=None,resource_epoch=None),
                        'historical':'UNESTABLISHED','native':NativeObservation(live_mapping=None,live_root=None)},'original_use':None,'effect_material':None}
def clone(value):return restore_archive(archive(value))

class OperationJournal:
    """Existing authenticated full journal plus independent bootstrap-head CAS.

    Runtime does not create a table, Genesis, journal, grant or absent file.
    A mutation intent retains exact old/new envelopes before the journal write.
    Lost ACK finalizes only authenticated identical bytes; partial/missing data
    quarantines. Host/root rollback resistance remains a deployment obligation.
    """
    def __init__(self,principal):
        self.p=principal;self.path=Path(principal.policy['journal']);self.poisoned=False
        require(str(self.path) in principal.lease.spec['provisioned_state'],'OPERATION_JOURNAL_NOT_PROVISIONED')
        require(self.path==principal.gate.issuer.state/'worldline-operations.json','OPERATION_JOURNAL_PATH_SPLIT')
        self._source_append_control=None;self._native_startup_completed=False
        self._open_head_database()
        if self.p.lease.plan is None:
            # Preserve the explicit historical offline full-resource route.
            self._reconcile_envelope();self.raw=private_bytes(self.path);self.load()
        else:
            # Full custody cannot be captured until construct has joined the
            # real canonical principal and RootCustodyJournalV2. No INTENT is
            # finalized and no cached history supplies startup authority here.
            self.raw=private_bytes(self.path)
    def _native_custody(self):
        from .root_worker_journal_v2 import RootCustodyJournalV2
        lease=self.p.lease;custody=lease.custody_journal_v2
        require(lease.plan is not None and self.p is lease.canonical_operation_principal
            and type(custody) is RootCustodyJournalV2,
            'OPERATION_JOURNAL_COMPLETE_ACTUAL_CUSTODY_REQUIRED')
        lease.intact();custody.intact()
        return custody
    def complete_native_startup(self):
        from .custody_operation_startup_kernel import decide_journal
        require(not self._native_startup_completed,
            'OPERATION_JOURNAL_NATIVE_STARTUP_ALREADY_COMPLETED')
        custody=self._native_custody()
        with custody.lock:
            before_raw=private_bytes(self.path);before_head=self.head_row()
            decision=decide_journal(custody)
            self.startup_redecision=decision
            require(private_bytes(self.path)==before_raw and self.head_row()==before_head,
                'OPERATION_JOURNAL_CHANGED_DURING_STARTUP_REDECISION')
            if decision.state=='Finalize_Surviving_Next':
                self._reconcile_envelope(native_decision=decision)
            else:
                require(decision.state=='Stable' and before_head[3]=='STABLE'
                    and before_head[2]==digest(before_raw),
                    'OPERATION_JOURNAL_NATIVE_STABLE_HEAD_CHANGED')
            self.raw=private_bytes(self.path);self._load_history()
            readback=decide_journal(custody)
            self.startup_readback=readback
            require(readback.state=='Stable' and private_bytes(self.path)==self.raw,
                'OPERATION_JOURNAL_NATIVE_STARTUP_READBACK_REFUSED')
            self._native_startup_completed=True
    def set_source_append_control(self,control):
        # A pinned owner control may observe/pause the real append boundary.
        # It supplies no verdict, candidate bytes or replacement native facts.
        require(self.p.lease.plan is not None and self._native_startup_completed
            and self._source_append_control is None,
            'OPERATION_JOURNAL_SINGLE_SOURCE_CONTROL_REQUIRED')
        function=control.__func__ if inspect.ismethod(control) else control
        require(inspect.isfunction(function),'OPERATION_JOURNAL_SOURCE_CONTROL_FUNCTION_REQUIRED')
        self.p.lease.source_lease.file(function.__code__.co_filename,('SOURCE','ENTRY'))
        self.p.lease.source_lease.check()
        self._source_append_control=control
    def _observe_source_append(self,operation,cause,capture,snapshot,native,boundaries):
        control=self._source_append_control
        if control is None:return
        function=control.__func__ if inspect.ismethod(control) else control
        self.p.lease.source_lease.file(function.__code__.co_filename,('SOURCE','ENTRY'))
        self.p.lease.source_lease.check()
        before=(self.raw,self.head_row(),archive(self.body),archive(self.rows),archive(self.preparations))
        captured=clone((capture,snapshot,native,list(boundaries)))
        result=control(self,operation,cause,*captured)
        require(result is None,'OPERATION_JOURNAL_SOURCE_CONTROL_CANNOT_AUTHORIZE')
        self.p.intact();self.p.lease.source_lease.check()
        require((self.raw,self.head_row(),archive(self.body),archive(self.rows),archive(self.preparations))==before
            and private_bytes(self.path)==before[0],
            'OPERATION_JOURNAL_SOURCE_CONTROL_CHANGED_AUTHORITY')
    def _finalize_native(self,row):
        from .custody_operation_startup_kernel import decide_journal
        custody=self._native_custody()
        decision=decide_journal(custody)
        self.finalize_redecision=decision
        require(decision.state=='Finalize_Surviving_Next' and self.head_row()==row
            and private_bytes(self.path)==row[5],
            'OPERATION_JOURNAL_NATIVE_FINALIZATION_CHANGED')
        self._finalize(row[2],row[5],expected_row=row)
    def _open_head_database(self):
        path=Path(self.p.policy['head_database'])
        require(path==self.p.gate.issuer.state/'worldline-operation-head.sqlite' and str(path) in self.p.lease.spec['provisioned_state'],'OPERATION_HEAD_DATABASE_NOT_PROVISIONED')
        private_bytes(path);info=path.stat();self.head_identity=(info.st_dev,info.st_ino)
        self.db=sqlite3.connect(path.as_uri()+'?mode=rw',uri=True,isolation_level=None,check_same_thread=False)
        self.db.execute('PRAGMA trusted_schema=OFF');self.db.execute('PRAGMA synchronous=FULL')
        require(self.db.execute('PRAGMA journal_mode').fetchone()[0].lower()=='wal'
            and self.db.execute('PRAGMA quick_check').fetchall()==[('ok',)],'OPERATION_HEAD_DATABASE_DURABILITY_UNESTABLISHED')
        expected={'canonical_operation_head':('name','installation','genesis','head','state','prior_envelope','next_envelope'),
                  'canonical_operation_admission':('name','installation','genesis','owner_envelope','initial_envelope','state')}
        names={row[0] for row in self.db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
        require(names==set(expected),'OPERATION_HEAD_DATABASE_SCHEMA_CHANGED')
        for name,columns in expected.items():require(tuple(row[1] for row in self.db.execute('PRAGMA table_info('+name+')'))==columns,'OPERATION_HEAD_DATABASE_COLUMNS_CHANGED')
        row=self.db.execute('SELECT installation,genesis,owner_envelope,initial_envelope,state FROM canonical_operation_admission WHERE name=?',('worldline-operations',)).fetchone()
        require(row is not None and row[0]==self.p.lease.spec['installation_id'] and row[1]==self.p.policy['genesis']
            and row[4]=='CONSUMED','OPERATION_EXPLICIT_OWNER_ADMISSION_UNESTABLISHED')
        owner_raw=private_bytes(self.p.policy['genesis_file']);require(row[2]==owner_raw,'OPERATION_OWNER_GENESIS_CHANGED')
        owner=exact_json(owner_raw);keys(owner,('body','mac'))
        require(hmac.compare_digest(owner['mac'],hmac.new(self.p.gate.issuer.key,DOMAIN+b'owner-genesis\0'+canonical(owner['body']),'sha256').hexdigest()),'OPERATION_OWNER_GENESIS_AUTHENTICATION')
        body=owner['body'];keys(body,('schema','installation','installation_genesis','binding','gate_head','issuer_head','universe','store','resource','owner','initial_envelope'))
        require(body['schema']=='worldline.operation-owner-genesis-v1' and body['installation']==self.p.lease.spec['installation_id']
            and body['installation_genesis']==digest(self.p.lease.genesis_raw) and body['binding']==self.p.binding
            and body['gate_head']==self.p.lease.genesis['gate_head'] and body['issuer_head']==self.p.lease.genesis['issuer_head']
            and body['owner']==self.p.owner.binding and archive(body['initial_envelope']).hex()==row[3],
            'OPERATION_COMPLETE_OWNER_GENESIS_BINDING_CHANGED')
        from .resource_run_ledger import dto_record
        self.owner_genesis=body
        origin=self.p.resource_origin_service
        require(body['store']==self.p.lease.genesis['store'] and body['resource']['genesis']==dto_record(origin.genesis)
            and body['universe']['genesis_sha256']==self.p.gate.universe.genesis_sha256,
            'OPERATION_INITIAL_STORE_RESOURCE_UNIVERSE_GENESIS_CHANGED')
        with origin.ordered_operation(),origin.connect() as db:
            origin._snapshot(db) # genuine complete original native replay
            actual=[bytes(row['record']).hex() for row in db.execute('SELECT record FROM run_events ORDER BY ordinal')]
            require(actual[:len(body['resource']['events'])]==body['resource']['events'],'OPERATION_INITIAL_FULL_RESOURCE_HISTORY_PREFIX_CHANGED')
    def mac(self,body):return hmac.new(self.p.gate.issuer.key,DOMAIN+canonical(body),'sha256').hexdigest()
    def head_row(self):
        path=Path(self.p.policy['head_database']);info=path.stat()
        require((info.st_dev,info.st_ino)==self.head_identity and not path.is_symlink(),'OPERATION_HEAD_DATABASE_IDENTITY_CHANGED')
        try:row=self.db.execute('SELECT installation,genesis,head,state,prior_envelope,next_envelope FROM canonical_operation_head WHERE name=?',('worldline-operations',)).fetchone()
        except sqlite3.Error as exc:raise WorldlineError('OPERATION_OWNER_BOOTSTRAP_SCHEMA_UNAVAILABLE','owner-provisioned retained head table required') from exc
        require(row is not None and row[0]==self.p.lease.spec['installation_id'] and row[1]==self.p.policy['genesis'],'OPERATION_OWNER_BOOTSTRAP_BINDING')
        return row
    def _reconcile_envelope(self,native_decision=None):
        row=self.head_row();require(os.path.lexists(self.path),'OPERATION_PRIOR_JOURNAL_MISSING')
        if self.p.lease.plan is not None:
            require(native_decision is self.startup_redecision
                and native_decision.state=='Finalize_Surviving_Next',
                'OPERATION_JOURNAL_NATIVE_FINALIZATION_REQUIRED')
        if row[3]=='STABLE':return
        require(row[3]=='INTENT' and type(row[4]) is bytes and type(row[5]) is bytes,'OPERATION_MUTATION_INTENT_INVALID')
        for raw in row[4:6]:
            env=exact_json(raw);keys(env,('body','mac'))
            require(hmac.compare_digest(env['mac'],self.mac(env['body'])),'OPERATION_MUTATION_INTENT_AUTHENTICATION')
        actual=private_bytes(self.path)
        # Only a complete surviving already-written envelope completes ACK.
        # The old envelope is retained for diagnosis; no restart regenerates it.
        require(actual==row[5],'OPERATION_MUTATION_PARTIAL_REQUIRES_OWNER_DIAGNOSIS')
        self._sync(actual)
        if self.p.lease.plan is None:self._finalize(row[2],row[5])
        else:self._finalize_native(row)
    def _sync(self,expected):
        fd=os.open(self.path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
        directory=os.open(self.path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:
            require(private_bytes(self.path)==expected,'OPERATION_SYNC_CHANGED')
            os.fsync(fd);os.fsync(directory)
            require(private_bytes(self.path)==expected,'OPERATION_SYNC_READBACK_CHANGED')
        finally:os.close(fd);os.close(directory)
    def _finalize(self,old_head,raw,expected_row=None):
        db=self.db;db.execute('BEGIN IMMEDIATE')
        try:
            if self.p.lease.plan is None:
                require(expected_row is None,'OPERATION_OFFLINE_HEAD_ROUTE_CHANGED')
                changed=db.execute('UPDATE canonical_operation_head SET head=?,state=?,prior_envelope=NULL,next_envelope=NULL WHERE name=? AND head=? AND state=?',(digest(raw),'STABLE','worldline-operations',old_head,'INTENT')).rowcount
            else:
                require(expected_row is not None and self.head_row()==expected_row
                    and expected_row[2]==old_head and expected_row[3]=='INTENT'
                    and expected_row[5]==raw and private_bytes(self.path)==raw,
                    'OPERATION_NATIVE_FINAL_HEAD_CAPTURE_CHANGED')
                changed=db.execute('UPDATE canonical_operation_head SET head=?,state=?,prior_envelope=NULL,next_envelope=NULL WHERE name=? AND installation=? AND genesis=? AND head=? AND state=? AND prior_envelope=? AND next_envelope=?',
                    (digest(raw),'STABLE','worldline-operations',*expected_row)).rowcount
            require(changed==1,'OPERATION_FINAL_HEAD_CAS_CHANGED');db.execute('COMMIT')
        except BaseException:
            if db.in_transaction:db.execute('ROLLBACK')
            self.poisoned=True;raise
    def load(self):
        if self.p.lease.plan is None:return self._load_history()
        from .custody_operation_startup_kernel import decide_journal
        require(self._native_startup_completed,'OPERATION_JOURNAL_NATIVE_STARTUP_NOT_COMPLETED')
        custody=self._native_custody()
        with custody.lock:
            before_raw=private_bytes(self.path);before_head=self.head_row()
            require(before_raw==self.raw,'OPERATION_JOURNAL_PRIOR_CHANGED')
            decision=decide_journal(custody)
            self.load_redecision=decision
            require(decision.state=='Stable','OPERATION_JOURNAL_NATIVE_LOAD_NOT_STABLE')
            self._load_history()
            require(private_bytes(self.path)==before_raw and self.head_row()==before_head,
                'OPERATION_JOURNAL_NATIVE_LOAD_HAS_NO_WRITE')
            return decision
    def _load_history(self):
        env=exact_json(self.raw);keys(env,('body','mac'));body=env['body']
        require(type(env['mac']) is str and hmac.compare_digest(env['mac'],self.mac(body)),'OPERATION_JOURNAL_AUTHENTICATION')
        keys(body,('schema','binding','grants','events','chains'))
        require(body['schema']=='worldline.canonical-operation-journal-v1' and body['binding']==self.p.binding and type(body['events']) is list and type(body['grants']) is list,'OPERATION_JOURNAL_SCHEMA_BINDING')
        row=self.head_row();require(row[3]=='STABLE' and row[2]==digest(self.raw),'OPERATION_INDEPENDENT_HEAD_CHANGED')
        require(body['grants']==self.owner_genesis['initial_envelope']['body']['grants'],'OPERATION_GRANT_ROSTER_NOT_OWNER_GENESIS_HISTORY')
        self.body=body;self.rows={};self.preparations={};prior=self.p.policy['genesis']
        states={'RESERVED':'RESERVED','EFFECT_INTENT':'RESERVED','EFFECT_OBSERVED':'EFFECT_OBSERVED','SETTLED':'SETTLED','RELEASED':'RELEASED','QUARANTINED':'QUARANTINED','RESOLVED_EFFECT':'EFFECT_OBSERVED','RESOLVED_NO_EFFECT':'RELEASED'}
        for event in body['events']:
            keys(event,('prior','operation','cause','capture','snapshot','native','boundaries'))
            require(event['prior']==prior,'OPERATION_EVENT_PREFIX_CHANGED')
            captured=restore_archive(bytes.fromhex(event['capture']))
            require(captured['operation']==event['operation'],'OPERATION_EVENT_ID_CHANGED')
            old=self.rows.get(event['operation']);cause=event['cause']
            if cause=='OWNER_CANONICAL':
                require(event['native'] is None and event['snapshot'] is None,
                    'OWNER_CANONICAL_NOT_ORDINARY_AUTHORITY')
                self.p.owner_witness.verify(captured)
            elif cause=='PREPARATION':
                require(old is None and event['native'] is None and event['snapshot'] is None,'OPERATION_PREPARATION_NOT_AUTHORITY')
                self.preparations[event['operation']]=captured
            else:
                snap=restore_archive(bytes.fromhex(event['snapshot']))
                keys(event['native'],('command','observation'));mode=event['native']['command']
                require(snap['binding']==captured['binding'],'OPERATION_REPLAY_CAPTURE_NATIVE_BINDING_CHANGED')
                observed=self.p.operation_decision(snap,mode)
                require(observed==event['native']['observation'],'OPERATION_FULL_NATIVE_REPLAY_CHANGED')
                require(observed['decision']!='REFUSED','OPERATION_DENIED_JOURNAL_EVENT')
                if old is not None:
                    require(archive(old['capture'])==archive(captured) and event['boundaries'][:len(old['boundaries'])]==old['boundaries'],'OPERATION_IMMUTABLE_CAPTURE_OR_BOUNDARIES_CHANGED')
                require(cause in ('RESERVED','EFFECT_INTENT','EFFECT_OBSERVED','SETTLED','RELEASED','QUARANTINED','ACK','RESOLVED_EFFECT','RESOLVED_NO_EFFECT'),'OPERATION_EVENT_CAUSE_INVALID')
                expected=[{'bound':clone(row['capture']['binding']),'state':states[row['state']]} for row in self.rows.values()]
                if cause=='ACK':
                    require(old is not None,'OPERATION_ACK_PRIOR_ABSENT')
                    if mode=='RESOLVE_RECOVERY':
                        require(old['state']=='EFFECT_INTENT' and snap['uses']==expected and observed['decision'] in ('OWNER_ABORT','OWNER_SETTLE'),'OPERATION_OWNER_RESOLUTION_ORDER')
                    else:require(event['snapshot']==archive(old['snapshot']).hex() and event['native']==old['native'],'OPERATION_ACK_CANNOT_REAUTHORIZE')
                else:
                    require(snap['uses']==expected and snap['grants']==body['grants'],'OPERATION_COMPLETE_PRIOR_USE_OR_GRANT_ROSTER_CHANGED')
                    rule={'RESERVED':(None,'RESERVE_USE','RESERVED_NEW'),
                          'EFFECT_INTENT':('RESERVED','RESERVE_USE','RESERVED_REPLAY'),
                          'EFFECT_OBSERVED':('EFFECT_INTENT','OBSERVE_EFFECT','EFFECT_ACCEPTED'),
                          'SETTLED':(('EFFECT_OBSERVED','RESOLVED_EFFECT'),'SETTLE_USE','SETTLED_NEW'),
                          'RELEASED':(('RESERVED','EFFECT_INTENT'),'RELEASE_USE','RELEASED_NEW'),
                          'QUARANTINED':(('RESERVED','EFFECT_INTENT','EFFECT_OBSERVED','QUARANTINED'),'QUARANTINE_USE','QUARANTINED_NEW'),
                          'RESOLVED_EFFECT':('QUARANTINED',('RESOLVE_EFFECT','RESOLVE_EFFECT_HISTORICAL'),'RESOLVED_EFFECT'),
                          'RESOLVED_NO_EFFECT':('QUARANTINED',('RESOLVE_NO_EFFECT','RESOLVE_NO_EFFECT_HISTORICAL'),'RESOLVED_NO_EFFECT')}.get(cause)
                    require(rule is not None,'OPERATION_NATIVE_TRANSITION_CAUSE_INVALID')
                    prior_state=None if old is None else old['state']
                    require((prior_state in rule[0] if type(rule[0]) is tuple else prior_state==rule[0])
                        and (mode in rule[1] if type(rule[1]) is tuple else mode==rule[1])
                        and observed['decision']==rule[2],'OPERATION_NATIVE_TRANSITION_ORDER')
                    require(digest(captured['input_snapshot_raw'])==captured['binding']['id']['input_snapshot'],'OPERATION_FULL_INPUT_SNAPSHOT_CHANGED')
                    if mode in ('RESOLVE_EFFECT_HISTORICAL','RESOLVE_NO_EFFECT_HISTORICAL'):
                        # Matching serialized frames are never historical owner
                        # custody. Require the exact prior protected intent and
                        # native dual disposition retained before resource work.
                        proof=snap['owner_completion']
                        require(any(boundary['name']=='FULL_BROKER_OWNER_DISPOSITION'
                            and boundary['value']==archive(proof).hex()
                            for boundary in old['boundaries']),
                            'OPERATION_K4_HISTORICAL_OWNER_INTENT_NOT_RETAINED')
                        acknowledgments=[boundary for boundary in event['boundaries']
                            if boundary['name']=='FULL_BROKER_K4_RESOURCE_ACK']
                        require(len(acknowledgments)==1,
                            'OPERATION_K4_COMPLETE_TERMINAL_ACK_REQUIRED')
                        envelope=restore_archive(bytes.fromhex(acknowledgments[0]['value']))
                        from .canonical_k4_recovery import replay_ack
                        replay_ack(self.p,captured,envelope)

                self.rows[event['operation']]={'capture':captured,'state':cause if cause!='ACK' else old['state'],'boundaries':event['boundaries'],'event':digest(canonical(event)),'snapshot':snap,'native':event['native']}
            prior=digest(canonical(event))
        from .canonical_followup import replay_followup
        from .canonical_actor_execution import replay_execution
        from .canonical_full_broker import replay_boundary
        native_boundaries=set()
        for event in body['events']:
            for boundary in event['boundaries']:
                if boundary['name']=='FOLLOWUP_NATIVE':replay_followup(self.p,boundary['material'])
                if boundary['name']=='ACTOR_EXECUTION_NATIVE':replay_execution(self.p,boundary['material'],owner_genesis=self.owner_genesis)
                if boundary['name']=='FULL_BROKER_NATIVE' and identity(boundary) not in native_boundaries:
                    replay_boundary(self.p,boundary);native_boundaries.add(identity(boundary))
        require(body['chains']==self._chain_heads(),'OPERATION_CHAIN_WITNESS_HISTORY_CHANGED')
    def _chain_heads(self):
        result=clone(self.p.policy['chains']);seen=set()
        for event in self.body['events']:
            for boundary in event['boundaries']:
                key=identity(boundary).hex()
                if key in seen:continue
                seen.add(key)
                if boundary['name'] in ('CANONICAL_ACK','OPERATION_CHAIN_ACK'):result[boundary['kind']]['head']=boundary['head']
        return result
    def append(self,operation,cause,capture,*,snapshot=None,native=None,boundaries=()):
        if self.p.lease.plan is None:
            return self._append_held(operation,cause,capture,snapshot=snapshot,native=native,boundaries=boundaries)
        with self._native_custody().lock:
            return self._append_held(operation,cause,capture,snapshot=snapshot,native=native,boundaries=boundaries)
    def _append_held(self,operation,cause,capture,*,snapshot=None,native=None,boundaries=()):
        require(not self.poisoned,'OPERATION_JOURNAL_DURABILITY_UNKNOWN');self.p.intact()
        require(private_bytes(self.path)==self.raw,'OPERATION_JOURNAL_PRIOR_CHANGED')
        self._observe_source_append(operation,cause,capture,snapshot,native,boundaries)
        prior=self.p.policy['genesis'] if not self.body['events'] else digest(canonical(self.body['events'][-1]))
        event={'prior':prior,'operation':operation,'cause':cause,'capture':archive(capture).hex(),
               'snapshot':None if snapshot is None else archive(snapshot).hex(),'native':native,'boundaries':list(boundaries)}
        body=clone(self.body);body['events'].append(event)
        old=self.rows.get(operation);extent=0 if old is None else len(old['boundaries'])
        for boundary in list(boundaries)[extent:]:
            if boundary['name'] in ('CANONICAL_ACK','OPERATION_CHAIN_ACK'):body['chains'][boundary['kind']]['head']=boundary['head']
        raw=canonical({'body':body,'mac':self.mac(body)})+b'\n';row=self.head_row();db=self.db
        try:
            if self.p.lease.plan is not None:
                from .custody_operation_startup_kernel import decide_append
                require(self._native_startup_completed,'OPERATION_JOURNAL_NATIVE_STARTUP_NOT_COMPLETED')
                candidate={'raw':raw,'body':body,
                    'operation_authority_observations':[{'event':item,
                        'material':bytes.fromhex(item['snapshot']),
                        'observation':item['native']['observation']}
                        for item in body['events'] if item['cause'] not in ('PREPARATION','OWNER_CANONICAL')],
                    'boundary_archives':[[archive(boundary) for boundary in item['boundaries']]
                        for item in body['events']]}
                self.append_redecision=decide_append(self._native_custody(),candidate)
                require(self.append_redecision.state=='AppendAllowed' and self.head_row()==row
                    and private_bytes(self.path)==self.raw,
                    'OPERATION_JOURNAL_NATIVE_APPEND_CAPTURE_CHANGED')
            db.execute('BEGIN IMMEDIATE')
            if self.p.lease.plan is None:
                changed=db.execute('UPDATE canonical_operation_head SET state=?,prior_envelope=?,next_envelope=? WHERE name=? AND head=? AND state=?',('INTENT',self.raw,raw,'worldline-operations',digest(self.raw),'STABLE')).rowcount
            else:
                require(self.head_row()==row and row[3]=='STABLE' and row[2]==digest(self.raw)
                    and private_bytes(self.path)==self.raw,
                    'OPERATION_NATIVE_MUTATION_HEAD_CAPTURE_CHANGED')
                changed=db.execute('UPDATE canonical_operation_head SET state=?,prior_envelope=?,next_envelope=? WHERE name=? AND installation=? AND genesis=? AND head=? AND state=? AND prior_envelope IS ? AND next_envelope IS ?',
                    ('INTENT',self.raw,raw,'worldline-operations',*row)).rowcount
            require(changed==1,'OPERATION_MUTATION_HEAD_CAS_CHANGED');db.execute('COMMIT')
            temporary=self.path.parent/('.operation-write-'+uuid.uuid4().hex)
            fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
            with os.fdopen(fd,'wb') as output:output.write(raw);output.flush();os.fsync(output.fileno())
            require(private_bytes(self.path)==self.raw,'OPERATION_PRIOR_CHANGED_BEFORE_REPLACE')
            os.replace(temporary,self.path);self._sync(raw)
            if self.p.lease.plan is None:self._finalize(row[2],raw)
            else:
                intent=(row[0],row[1],row[2],'INTENT',self.raw,raw)
                self._finalize_native(intent)
            self.raw=raw;self.load()
        except BaseException:
            if db.in_transaction:db.execute('ROLLBACK')
            self.poisoned=True;self.p.lease.poisoned=True;raise
        return self.rows.get(operation)

class OperationScope:
    def __init__(self,principal,operation,peer):self.principal=principal;self.operation=operation;self.peer=peer
    def metadata(self):
        self.principal.intact();row=self.principal.journal.rows[self.operation]
        if self.peer is None:
            self.principal.historical_operation(self.operation)
        else:
            require(self.peer is self.principal.active_peers.get(self.operation),'OPERATION_ACTUAL_PEER_HANDLE_CHANGED')
            require(self.peer.observation()==row['capture']['request'],'OPERATION_ORIGINAL_PEER_REQUEST_CHANGED')
        require(row['state'] in ('EFFECT_INTENT','EFFECT_OBSERVED','SETTLED'),'OPERATION_CANONICAL_WRITE_WITHOUT_INTENT')
        return {'schema':'worldline.requester-operation-binding-v1','binding':clone(row['capture']['binding']),
                'originalRequest':clone(row['capture']['request']),'reservationEvent':row['capture']['reservation_event']}
@contextmanager
def operation_scope(scope):
    token=_CURRENT.set(scope)
    try:yield
    finally:_CURRENT.reset(token)
def current_scope():return _CURRENT.get()
def canonical_metadata(store):
    principal=getattr(store,'canonical_operation_principal',None)
    if principal is None:return None
    scope=current_scope()
    from .canonical_owner_witness import OwnerCanonicalScope
    require(type(scope) in (OperationScope,OwnerCanonicalScope) and scope.principal is principal,'OPERATION_CANONICAL_WRITE_OUTSIDE_ACTUAL_SCOPE')
    return scope.metadata()

class CanonicalOperationPrincipal:
    operation_names=OPS
    owner_names=("owner.retry","owner.adopt","owner.recover")
    def __init__(self,lease,recovery,resources,owner):
        import recovery_principal
        from .protected_owner import ProtectedOwnerPrincipal
        from .protected_resource_runtime import ProtectedResourcePrincipal
        scoped=False
        if type(resources) is not ProtectedResourcePrincipal:
            # Explicit pending additive source dependency. No subclass or
            # object with matching attributes supplies the protected producer.
            from .protected_scoped_resource_runtime import ProtectedScopedResourcePrincipal
            scoped=type(resources) is ProtectedScopedResourcePrincipal
        require(type(lease) is StartupLease and type(recovery) is recovery_principal.ProtectedRecoveryPrincipal and
                (type(resources) is ProtectedResourcePrincipal or scoped) and type(owner) is ProtectedOwnerPrincipal,'OPERATION_ACTUAL_PROTECTED_COMPONENTS_REQUIRED')
        require(recovery is lease.principal and owner.controller is lease.controller and resources.lease is lease and resources.gate is lease.gate,'OPERATION_EXCLUSIVE_STARTUP_JOIN')
        lease.require_runtime()
        self.lease,self.recovery,self.resources,self.owner=lease,recovery,resources,owner
        self.resource_origin_service=resources.historical_service if scoped else resources.service
        self.gate,self.controller,self.store,self.core=lease.gate,lease.controller,lease.store,lease.controller.core
        self.capture=recovery.capture;require(type(self.capture) is ProtectedCapture,'OPERATION_ACTUAL_CAPTURE_REQUIRED')
        self.policy_path=self.gate.issuer.state/'worldline-operation-policy.json';self.policy_raw=private_bytes(self.policy_path);self.policy=exact_json(self.policy_raw)
        keys(self.policy,('schema','installation','owner_uid','issuer','genesis','journal','selection','chains','issuer_policy','store_genesis','source_inventory','resource_descriptor','plans','broker','head_database','genesis_file'))
        require(self.policy['schema']=='worldline.operation-policy-v1' and self.policy['installation']==lease.spec['installation_id'] and self.policy['owner_uid']==owner.policy['owner_uid'] and self.policy['issuer_policy']==self.gate.issuer.policy_sha256 and self.policy['store_genesis']==self.store.get_meta('protectedStoreGenesis'),'OPERATION_OWNER_POLICY_BINDING_CHANGED')
        require(self.policy_path in lease.allowed,'OPERATION_POLICY_NOT_IN_INSTALLATION')
        self.binding={'installation':lease.spec['installation_id'],'genesis':self.policy['genesis'],'policy_bytes':self.policy_raw.hex(),'issuer_key':digest(self.gate.issuer.key),'store_genesis':self.policy['store_genesis']}
        self.operation_lock=asyncio.Lock()
        self.kernel=initialize_owner_kernel(self);self.active_peers={};self.preparing={};self.pending={};self.alarm=None
        from .canonical_owner_witness import OwnerCanonicalWitness
        self.owner_witness=OwnerCanonicalWitness(self)
        self.resources.operation_principal=self
        self.intact();self.journal=OperationJournal(self)
        from .canonical_operation_chains import CanonicalOperationChains
        self.canonical=CanonicalOperationChains(self)
        self.store.canonical_operation_principal=self;self.recovery.operation_principal=self;self.controller.canonical_operation_principal=self
        self.resources.operation_principal=self
        self.full_broker=None
    def close_resource_control(self,control):
        # The selected owner factory has stopped intake and joined every real
        # admitted service handler before closing the existing head database.
        from .owner_resource_control import OwnerResourceControl
        require(type(control) is OwnerResourceControl and control.principal is self
            and control.server is None,'OPERATION_RESOURCE_CONTROL_QUIESCENT_OWNER_REQUIRED')
        with self.resources.order:
            self.lease.intact()
            self.journal.db.close()
            self.active_peers.clear()
    def broker(self):
        if self.full_broker is None:
            from .canonical_full_broker import FullCanonicalBroker
            self.full_broker=FullCanonicalBroker(self)
        return self.full_broker
    def followup_plan(self,operation,right,event_id):
        return self.broker().followup_plan(self._operation_key(operation),right,event_id)
    def intact(self):
        self.lease.intact();self.capture.intact();self.owner.intact();self.resources.intact()
        require(private_bytes(self.policy_path)==self.policy_raw,'OPERATION_OWNER_POLICY_CHANGED')
        self.gate.issuer.head();self.lease.loaded()
        material=self.capture.kernel_material()
        # Every operation export's actual address belongs to the same measured
        # selected library. Merely loading a symbol by its name is insufficient.
        raw=material['library_bytes'];library=Path(os.fsdecode(material['library_path']))
        ranges=[]
        for line in Path('/proc/self/maps').read_text().splitlines():
            fields=line.split(maxsplit=5)
            if len(fields)==6 and fields[5]==str(library):ranges.append((fields[0],fields[1]))
        for name in ('wl_operation_authority_decide_v1','wl_operation_authority_version_v1','wl_operation_authority_layout_v1',
                     'wl_canonical_operation_decide_v1','wl_canonical_operation_version_v1','wl_canonical_operation_layout_v1'):
            address=ctypes.cast(getattr(self.core._lib,name),ctypes.c_void_p).value
            require(address is not None and any(int(bounds.split('-')[0],16)<=address<int(bounds.split('-')[1],16) and 'x' in permissions for bounds,permissions in ranges),'OPERATION_EXACT_SYMBOL_MAPPING_CHANGED')
        require(raw==library.read_bytes(),'OPERATION_MAPPED_LIBRARY_BYTES_CHANGED')
        return material
    def mapped_symbols(self,names):
        material=self.intact();library=Path(os.fsdecode(material['library_path']))
        selected=[]
        for line in Path('/proc/self/maps').read_text().splitlines():
            fields=line.split(maxsplit=5)
            if len(fields)==6 and fields[5]==str(library):selected.append((fields[0],fields[1]))
        for name in names:
            address=ctypes.cast(getattr(self.core._lib,name),ctypes.c_void_p).value
            require(address is not None and any(int(bounds.split('-')[0],16)<=address<int(bounds.split('-')[1],16)
                and 'x' in permissions for bounds,permissions in selected),'FULL_BROKER_SYMBOL_OUTSIDE_SELECTED_NATIVE')
        return material
    def reconcile_before_endpoint(self):
        if self.lease.plan is not None:
            return self._reconcile_native_before_endpoint()
        self.intact()
        # A retained PREPARATION cannot become RESERVED by restart inference.
        require(not set(self.journal.preparations)-set(self.journal.rows),'OPERATION_INCOMPLETE_PREPARATION_REQUIRES_OWNER_DIAGNOSIS')
        self.owner_witness.reconcile()
        self.unresolved=set()
        for operation in tuple(self.journal.rows):
            row=self.journal.rows[operation]
            if row['state'] in ('RESOLVED_EFFECT','RESOLVED_NO_EFFECT'):
                try:self.recover_owner_resolution(operation)
                except WorldlineError:self.unresolved.add(operation)
            elif row['state'] in ('EFFECT_OBSERVED','SETTLED'):self.recover_committed(operation)
            elif row['state']=='EFFECT_INTENT':
                if any(b['name']=='RESULT_CAPTURE' for b in row['boundaries']):self.recover_committed(operation)
                elif any(b['name']=='FULL_BROKER_PREPARED' for b in row['boundaries']):
                    try:
                        with self.historical_scope(operation):
                            result=self.broker().recover(operation)
                            self.finish(operation,clone({'result':result,'actual_store':self.capture.chain_material(),
                                'actual_transaction':self.controller.transactions._load_record(row['capture']['transaction']['transactionId'])}))
                    except WorldlineError:self.unresolved.add(operation)
                else:self.unresolved.add(operation)
            elif row['state']=='QUARANTINED' and any(
                    boundary['name']=='FULL_BROKER_OWNER_DISPOSITION' for boundary in row['boundaries']):
                try:
                    from .canonical_k4_recovery import recover_pending
                    recover_pending(self,operation)
                except WorldlineError:self.unresolved.add(operation)
            elif row['state'] in ('RESERVED','QUARANTINED'):
                self.unresolved.add(operation)
    def _reconcile_native_before_endpoint(self):
        self.intact()
        # The original incomplete-preparation refusal remains mandatory.
        require(not set(self.journal.preparations)-set(self.journal.rows),
            'OPERATION_INCOMPLETE_PREPARATION_REQUIRES_OWNER_DIAGNOSIS')
        self.owner_witness.reconcile()
        self.unresolved=set()
        for operation in tuple(self.journal.rows):
            decision=self.lease.redecide_recovery_operation(self,operation)
            self.recovery_redecision=decision
            if decision.state=='NoRecovery':continue
            if decision.state=='RetainUnresolved':
                self.unresolved.add(operation)
            elif decision.state=='RecoverCommitted':
                self.recover_committed(operation)
            elif decision.state=='RecoverOwnerResolution':
                try:self.recover_owner_resolution(operation)
                except WorldlineError:self.unresolved.add(operation)
            elif decision.state=='RecoverFullBroker':
                try:
                    row=self.journal.rows[operation]
                    with self.historical_scope(operation):
                        result=self.broker().recover(operation)
                        self.finish(operation,clone({'result':result,'actual_store':self.capture.chain_material(),
                            'actual_transaction':self.controller.transactions._load_record(row['capture']['transaction']['transactionId'])}))
                except WorldlineError:self.unresolved.add(operation)
            elif decision.state=='RecoverK4':
                try:
                    from .canonical_k4_recovery import recover_pending
                    recover_pending(self,operation)
                except WorldlineError:self.unresolved.add(operation)
            else:
                require(False,'OPERATION_RECOVERY_COMPLETE_NATIVE_ROUTE_REFUSED')
    def _transaction(self,document):
        op=document['op'];args=document['args']
        if op in ('collapse.commit','transaction.commit','transaction.abort'):
            require(set(args)=={'transactionId'} and type(args['transactionId']) is str,'OPERATION_TRANSACTION_INTENT_FIELDS')
            return self.controller.transactions._load_record(args['transactionId'])
        if op=='quarantine.resolve':
            require(set(args)=={'operation','reason'} and type(args['operation']) is str and type(args['reason']) is str and args['reason'],'OPERATION_RESOLUTION_INTENT_FIELDS')
            row=self.journal.rows.get(args['operation'])
            if row is not None:
                require(row['state']=='QUARANTINED','OPERATION_RESOLUTION_NOT_QUARANTINED')
                return clone(row['capture']['transaction'])
            row=self.recovery.journal.latest[args['operation']]
            require(row['state']=='QUARANTINED','OPERATION_RESOLUTION_NOT_QUARANTINED')
            return clone(row['capture']['record'])
        return None
    def resource_request_material(self,original_request,operation_id,transaction_record):
        require(type(original_request) is RequestPeer and self.active_peers.get(operation_id) is original_request,'OPERATION_RESOURCE_ACTUAL_REQUEST_REQUIRED')
        captured=self.preparing.get(operation_id) or self.journal.preparations.get(operation_id)
        require(captured is not None and captured['request']==original_request.observation() and archive(captured['transaction'])==archive(transaction_record),'OPERATION_RESOURCE_PREPARATION_JOIN_CHANGED')
        plan=self.policy['plans'].get(captured['document']['op'])
        keys(plan,('cost_key','parent','launch'))
        # These are identities/encodings of captured facts. Native Resource_Run_Ledger
        # decides every quantity and lifecycle transition. A candidate grant is
        # explicitly not a reservation or an authority verdict.
        return {'requester':archive(captured['request']['peer']), 'capability':bytes.fromhex(captured['grant']['id']),
            'grant_use':identity(captured['use']), 'workload':identity({'operation':operation_id,'transaction':transaction_record,'subject':captured['subject']}),
            'payload':identity(captured['payload']),'provenance':identity(captured['provenance']),
            'parent':None if plan['parent'] is None else bytes.fromhex(plan['parent']),'cost_key':plan['cost_key']}
    def _row_for_request(self,original_request):
        require(type(original_request) is RequestPeer,'OPERATION_RESOURCE_ORIGINAL_SOCKET_REQUIRED')
        matches=[row for row in self.journal.rows.values() if row['capture']['request']==original_request.observation()]
        require(len(matches)==1,'OPERATION_RESOURCE_REQUEST_ROW_AMBIGUOUS')
        return matches[0]
    def pending_for_operation(self,operation_id):
        # Stable object identity owned by this actual protected journal. No
        # ordinary DTO or legacy promote flag can manufacture the pending use.
        if type(operation_id) is bytes:operation_id=operation_id.hex()
        row=self.journal.rows.get(operation_id)
        require(row is not None,'OPERATION_RETAINED_PENDING_ABSENT')
        pending=self.pending.get(operation_id)
        if pending is None:
            pending={'operation':operation_id,'resource_intent':clone(row['capture']['resource_intent']),
                'reservation_event':row['capture']['reservation_event']}
            self.pending[operation_id]=pending
        return pending
    def _original_native_use(self,row):
        capture=row['capture'];original=None
        for event in self.journal.body['events']:
            if event['operation']==capture['operation'] and event['cause']=='RESERVED':original=event;break
        require(original is not None,'OPERATION_ORIGINAL_RESERVATION_HISTORY_MISSING')
        snapshot=restore_archive(bytes.fromhex(original['snapshot']))
        observed=observe_operation(self,snapshot,'RESERVE_USE')
        require(observed==original['native']['observation'] and observed['decision']=='RESERVED_NEW','OPERATION_ORIGINAL_NATIVE_USE_UNESTABLISHED')
        return {'snapshot':snapshot,'observation':observed,'event':digest(canonical(original))}
    def resource_binding(self,pending,original_request):
        from .resource_run_ledger import dto_record
        operation=pending['operation'];row=self.journal.rows[operation];captured=row['capture']
        require(pending is self.pending_for_operation(operation) and self.active_peers.get(operation) is original_request
            and captured['request']==original_request.observation(),'OPERATION_RESOURCE_PENDING_CUSTODY_CHANGED')
        request=captured['resource_intent'];native=self._original_native_use(row)
        return {'scope':dto_record(request.scope),'bound':dto_record(request.bound),'request':dto_record(request),
            'native_use':native,'event_id':row['event'],'full_capture':archive(captured).hex()}
    def resource_lifecycle_binding(self,pending,original_request,request,launch_events):
        from .resource_run_ledger import dto_record,RunRequest
        require(type(request) is RunRequest,'OPERATION_COMPLETE_RESOURCE_LIFECYCLE_REQUIRED')
        row=self.journal.rows[pending['operation']];captured=row['capture'];original=captured['resource_intent']
        require(pending is self.pending_for_operation(captured['operation']) and request.bound==original.bound
            and original_request.observation()==captured['request'],'OPERATION_RESOURCE_LIFECYCLE_ORIGINAL_BINDING_CHANGED')
        # Full retained launch history comes from the exact resource principal,
        # not an operation argument. The physical native producer rechecks it.
        key=request.reservation.hex();self.resources.journal.load()
        actual=self.resources.journal.rows.get(key)
        require(actual is not None and actual['events']==launch_events,'OPERATION_RESOURCE_LAUNCH_HISTORY_CHANGED')
        boundary={'name':'RESOURCE_LIFECYCLE_INTENT','request':dto_record(request),'launch_events':clone(launch_events)}
        require(row['state'] in ('RESERVED','EFFECT_INTENT','EFFECT_OBSERVED','QUARANTINED'),'OPERATION_RESOURCE_LIFECYCLE_STATE_INVALID')
        self.journal.append(captured['operation'],'ACK',captured,snapshot=row['snapshot'],native=row['native'],boundaries=row['boundaries']+[boundary])
        return {'scope':dto_record(request.scope),'bound':dto_record(request.bound),'request':dto_record(request),
            'native_use':self._original_native_use(row),'event_id':self.journal.rows[captured['operation']]['event'],
            'retained_launch_events':clone(launch_events),'full_capture':archive(captured).hex()}
    def resource_launch_material(self,original_request,reservation):
        from .resource_run_ledger import dto_record
        row=self._row_for_request(original_request);capture=row['capture'];intent=capture['resource_intent']
        require(intent.reservation==reservation and row['state'] in ('EFFECT_INTENT','EFFECT_OBSERVED','SETTLED'),
            'OPERATION_LAUNCH_WITHOUT_ACTUAL_INTENT')
        root_owner=getattr(self,'root_worker_process',None) or getattr(self,'root_worker',None)
        if root_owner is not None:
            from .protected_root_worker import RootWorkerFront,RootWorkerProcess
            from .root_worker_plan import handler_plan
            require(type(root_owner) in (RootWorkerFront,RootWorkerProcess)
                and root_owner.principal is self,'OPERATION_GENUINE_ROOT_HANDLER_PLAN_OWNER_REQUIRED')
            return handler_plan(root_owner,intent.bound)
        plan=self.policy['plans'][capture['document']['op']]['launch']
        keys(plan,('argv','cwd','environment','systemd_properties','policy','executables'))
        for path,selection in plan['executables'].items():
            keys(selection,('sha256','role'));require(Path(path) in self.lease.allowed,'OPERATION_LAUNCH_EXECUTABLE_UNSELECTED')
            require(selection['role'] in ('SOURCE','EXTENSION','INTERPRETER','DATA') and self.lease.source_lease.file(path,(selection['role'],)) and digest(Path(path).read_bytes())==selection['sha256'],'OPERATION_LAUNCH_EXECUTABLE_CHANGED')
        # Keep role custody in the retained plan. The declared producer consumes
        # a digest selection map; it cannot consume nested policy metadata.
        selected=clone(plan)
        selected['executables']={path:value['sha256'] for path,value in plan['executables'].items()}
        return {'bound':dto_record(intent.bound),**selected}
    def resource_actor_execution_material(self,operation,reservation,original_request):
        from .canonical_actor_execution import capture_execution
        return capture_execution(self,operation,reservation,original_request)
    def original_workload_material(self,runner,world,adapter,mission,context,project,spec,
                                  sandbox_argv,*,low_priority,timeout):
        from .canonical_workload_capture import capture_workload
        return capture_workload(self,runner,world,adapter,mission,context,project,spec,
            sandbox_argv,low_priority=low_priority,timeout=timeout)
    async def pump_original_workload(self,slot,capture_id):
        from .canonical_actor_stdin import pump_original
        return await pump_original(self,slot,capture_id)
    def resource_committed_settlement(self,pending,original_request,reservation):
        row=self.journal.rows[pending['operation']];capture=row['capture']
        require(pending is self.pending_for_operation(capture['operation']) and capture['request']==original_request.observation()
            and capture['resource_intent'].reservation==reservation and row['state'] in ('EFFECT_OBSERVED','SETTLED'),'OPERATION_RESOURCE_COMMITTED_CUSTODY_CHANGED')
        observed=observe_operation(self,row['snapshot'],row['native']['command'])
        require(observed==row['native']['observation'] and observed['decision'] in ('EFFECT_ACCEPTED','SETTLED_NEW','SETTLED_REPLAY'),'OPERATION_RESOURCE_COMMITTED_NATIVE_UNESTABLISHED')
        return {'native_use':self._original_native_use(row),'effect_snapshot':archive(row['snapshot']).hex(),
            'effect_native':observed,'event_id':row['event'],'full_capture':archive(capture).hex()}
    def resource_historical_settlement(self,operation,reservation):
        operation=self._operation_key(operation)
        from .resource_run_ledger import dto_record
        self.historical_operation(operation);row=self.journal.rows[operation];capture=row['capture']
        require(capture['resource_intent'].reservation==reservation and row['state'] in ('EFFECT_OBSERVED','SETTLED'),
            'OPERATION_HISTORICAL_EFFECT_REQUIRED')
        replay=observe_operation(self,row['snapshot'],row['native']['command'])
        require(replay==row['native']['observation'] and replay['decision'] in ('EFFECT_ACCEPTED','SETTLED_NEW','SETTLED_REPLAY'),
            'OPERATION_HISTORICAL_FULL_EFFECT_REPLAY_CHANGED')
        effects=[clone(b) for b in row['boundaries'] if b['name'] in ('RESULT_CAPTURE','CANONICAL_ACK','OPERATION_CHAIN_ACK')]
        resource_packets=self._retain_resource_packets(operation,reservation)
        row=self.journal.rows[operation]
        return {'original_request':clone(capture['request']),'scope':dto_record(capture['resource_intent'].scope),
            'bound':dto_record(capture['resource_intent'].bound),'native_use':self._original_native_use(row),'event_id':row['event'],
            'effects':effects,'receipts':clone(row['snapshot']['receipts']),'causal':clone(row['snapshot']['events']),
            'resource_packets':resource_packets}
    def _retain_resource_packets(self,operation,reservation):
        """Read actual complete service commits, replay full history, retain bytes.

        No request/launch DTO is reconstructed into a purported commit. The
        service owns the complete recorded packet/result and native row history.
        Legacy records without a full stored packet retain a named dependency.
        """
        from .resource_run_ledger import dto_record
        operation=self._operation_key(operation);row=self.journal.rows[operation]
        intent=row['capture']['resource_intent'];service=self.resources.service
        require(intent.reservation==reservation,'OPERATION_PACKET_RESERVATION_CHANGED')
        packets=[];retained=[]
        with service.ordered_operation(),service.order,service.connect() as db:
            db.execute('BEGIN')
            snapshot=service._snapshot(db) # whole native chronological replay
            history=[bytes(value['record']) for value in db.execute('SELECT record FROM run_events ORDER BY ordinal')]
            for raw in history:
                record=exact_json(raw)
                # Selection transports data only; full raw history is retained
                # below and already replayed by the actual native service.
                from .resource_run_ledger import restore_dto
                request=restore_dto(record['request'])
                if request.operation_id!=bytes.fromhex(operation) or request.reservation!=reservation:continue
                require(request.bound==intent.bound and request.scope==intent.scope,
                    'OPERATION_COMPLETE_PACKET_BINDING_CHANGED')
                require(record.get('schema')=='worldline.protected-resource-event-v2' and 'packet' in record,
                    'OPERATION_LEGACY_FULL_PACKET_CAPTURE_UNAVAILABLE')
                packet=clone(record['packet']);_state,_rows,decoded=service._decode_packet(packet)
                require(decoded==request and record['owner_uid']==os.geteuid(),
                    'OPERATION_PACKET_WRITER_OR_REQUEST_CHANGED')
                # Already inside the service's non-reentrant ticket ordering.
                # Read its authentic same-request reply in this same DB snapshot;
                # do not recursively enqueue recover behind ourselves.
                answer=service._previous(db,packet,request,os.geteuid())
                require(type(answer) is dict and answer.get('status')=='READY','OPERATION_FULL_PACKET_COMMIT_UNESTABLISHED')
                retained.append({'record':raw.hex(),'packet':packet,'reply':clone(answer)})
                if request.kind in ('RELEASE_HOLD','CHARGE_BUDGET'):packets.append(packet)
            boundary={'name':'RESOURCE_FULL_COMMITTED_HISTORY','history':[raw.hex() for raw in history],
                'state':dto_record(snapshot.state),'rows':[dto_record(item) for item in snapshot.rows],
                'selected':retained,'operation':operation,'reservation':reservation.hex()}
        # ACK records the exact complete actual service event/native inputs,
        # writer and original response. It grants no fresh operation or use.
        if boundary not in row['boundaries']:
            self.journal.append(operation,'ACK',row['capture'],snapshot=row['snapshot'],native=row['native'],
                boundaries=row['boundaries']+[boundary])
        return packets
    @staticmethod
    def _operation_key(operation):
        if type(operation) is bytes:operation=operation.hex()
        require(type(operation) is str and bytes.fromhex(operation).hex()==operation,'OPERATION_ID_REPRESENTATION')
        return operation
    def resource_historical_lifecycle_binding(self,operation,reservation,request,launch_events):
        operation=self._operation_key(operation)
        from .resource_run_ledger import dto_record,RunRequest
        self.historical_operation(operation);row=self.journal.rows[operation];capture=row['capture']
        require(type(request) is RunRequest and request.reservation==reservation and request.bound==capture['resource_intent'].bound,
            'OPERATION_HISTORICAL_RESOURCE_BINDING_CHANGED')
        self.resources.journal.load();actual=self.resources.journal.rows.get(reservation.hex())
        require(actual is not None and actual['events']==launch_events,'OPERATION_HISTORICAL_FULL_LAUNCH_HISTORY_CHANGED')
        boundary={'name':'RESOURCE_LIFECYCLE_INTENT','request':dto_record(request),'launch_events':clone(launch_events)}
        if boundary not in row['boundaries']:
            row=self.journal.append(operation,'ACK',capture,snapshot=row['snapshot'],native=row['native'],boundaries=row['boundaries']+[boundary])
        return {'scope':dto_record(request.scope),'bound':dto_record(request.bound),'request':dto_record(request),
            'native_use':self._original_native_use(row),'event_id':row['event'],'retained_launch_events':clone(launch_events),
            'full_capture':archive(capture).hex()}
    def historical_operation(self,operation):
        operation=self._operation_key(operation)
        self.intact();row=self.journal.rows[operation];capture=row['capture']
        native=self._original_native_use(row)
        current=self.intact()
        require(all(current[name]==capture['native'][name] for name in ('library_bytes','build_bytes','library_path')),'OPERATION_HISTORICAL_EXACT_NATIVE_SELECTION_CHANGED')
        require(row['state'] in ('EFFECT_INTENT','EFFECT_OBSERVED','SETTLED','QUARANTINED'),'OPERATION_HISTORICAL_STATE_INVALID')
        return native
    @contextmanager
    def historical_scope(self,operation):
        operation=self._operation_key(operation)
        self.historical_operation(operation)
        with operation_scope(OperationScope(self,operation,None)):yield
    def _rows(self):
        states={'RESERVED':'RESERVED','EFFECT_INTENT':'RESERVED','EFFECT_OBSERVED':'EFFECT_OBSERVED','SETTLED':'SETTLED','RELEASED':'RELEASED','QUARANTINED':'QUARANTINED','RESOLVED_EFFECT':'EFFECT_OBSERVED','RESOLVED_NO_EFFECT':'RELEASED'}
        return [{'bound':clone(row['capture']['binding']),'state':states[row['state']]} for row in self.journal.rows.values()]
    def _snapshot(self,capture,*,evidence=None):
        return {'binding':clone(capture['binding']),'grants':clone(self.journal.body['grants']),'uses':self._rows(),'now':quantity(self.gate.issuer.policy['now_tick']),
                'evidence':empty_evidence() if evidence is None else clone(evidence),'receipts':[],'events':[]}
    def operation_decision(self,snapshot,command):
        if command not in ('RESOLVE_EFFECT_HISTORICAL','RESOLVE_NO_EFFECT_HISTORICAL'):
            return observe_operation(self,snapshot,command)
        # Actual protected chronological journal replay establishes custody of
        # the complete original owner frame. The native helper redecides that
        # entire dual frame and the current complete use/grant/chain rosters;
        # no copied decision, fresh-policy substitution or second use enters.
        keys(snapshot,('binding','grants','uses','now','evidence','receipts','events','owner_completion'))
        proof=snapshot['owner_completion'];keys(proof,('owner','arguments','native'))
        from .operation_owner_kernel import observe_owner_completion
        from .operation_owner_kernel import observe_exchange, initialize_exchange_kernel, prepare_exchange
        require(observe_exchange(self, *proof['arguments'])==proof['native'],
            'OPERATION_K4_COMPLETE_ORIGINAL_DUAL_FRAME_CHANGED')
        current={name:clone(value) for name,value in snapshot.items() if name!='owner_completion'}
        native=observe_owner_completion(self, proof['arguments'],current)
        expected='RESOLVED_EFFECT' if command=='RESOLVE_EFFECT_HISTORICAL' else 'RESOLVED_NO_EFFECT'
        require(native['decision']==expected,'OPERATION_K4_HISTORICAL_NATIVE_COMPLETION_REFUSED')
        return native
    def _prepare_resource_use(self,request):
        self.intact();document=exact_json(bytes.fromhex(request.observation()['rawRequest']),canonical_required=False)
        keys(document,('id','op','args'));require(document['op'] in OPS and type(document['args']) is dict,'OPERATION_ORIGINAL_INTENT_SCHEMA')
        operation=identity(uuid.uuid4().hex).hex();self.active_peers[operation]=request
        tx=self._transaction(document);observed=request.observation();uid=observed['peer']['uid']
        selected=self.policy['selection'].get(str(uid),{}).get(document['op'])
        grants=[g for g in self.journal.body['grants'] if g['id']==selected]
        require(len(grants)==1,'OPERATION_NATIVE_GRANT_CANDIDATE_ABSENT')
        # Selection is only a candidate from owner state. Native eligibility is
        # evaluated after the complete actual resource/request capture joins.
        grant=clone(grants[0]);facts=self.gate.facts();universe=self.gate.universe.read();issuer=self.gate.issuer.head()
        subject=self.store.prime()
        payload=[] if subject is None else [(key,{'value':item.value,'canonical':item.canonical,'root_hash':item.root_hash}) for key,item in self.controller.transactions._capture_current_roots().items()];provenance=self.capture.chain_material();native=self.intact()
        captured={'operation':operation,'request':observed,'document':document,'transaction':tx,'grant':grant,'use':uuid.uuid4().hex,
            'subject':subject,'payload':payload,'provenance':provenance,'native':native,'facts':facts,'universe':universe,'issuer':issuer}
        self.preparing[operation]=captured
        self.journal.append(operation,'PREPARATION',captured)
        intent=self.resources.intent_for_operation(request,operation,tx)
        captured['resource_intent']=clone(intent)
        from .resource_run_ledger import dto_record
        scope,epoch,_uhead,_lhead,source=self.resources.current_context()
        material={'scope':dto_record(scope),'bound':dto_record(intent.bound),'request':dto_record(intent),
            'target_owner':self.policy['owner_uid'],'descriptor':private_bytes(self.policy['resource_descriptor']),'source_material':source}
        # Projection must come from the actual protected full-native producer.
        # It contains complete context/binding/source material, not a verdict.
        keys(material,('scope','bound','request','target_owner','descriptor','source_material'))
        requirement=None if subject is None else current_requirements(self.store,self.controller.config,self.core)
        captured['input_snapshot_raw']=archive(captured)
        ids={f:None for f in FIELDS}
        ids.update(operation_id=operation,request_id=identity(observed).hex(),transaction=None if tx is None else identity(tx['transactionId']).hex(),
            universe_head=bytes.fromhex(universe['event_head']).hex(),instance=self.gate.config['managed_observation']['worldline_instance_id'],root_set=self.gate.config['managed_observation']['root_set_id'],prime=None if subject is None else identity(subject).hex(),
            policy=bytes.fromhex(grant['policy']).hex(),requirement=None if requirement is None else hash_bytes_from_id(requirement['requirementHash']).hex(),issuer=self.policy['issuer'],issuer_head=bytes.fromhex(issuer['event_head']).hex(),
            grant_id=grant['id'],use_id=identity(captured['use']).hex(),reservation=intent.reservation.hex(),resource_head=_lhead.hex(),
            receipt_genesis=self.journal.body['chains']['operation_receipts']['genesis'],receipt_head=self.journal.body['chains']['operation_receipts']['head'],
            causal_genesis=self.journal.body['chains']['operation_events']['genesis'],causal_head=self.journal.body['chains']['operation_events']['head'],input_snapshot=digest(captured['input_snapshot_raw']),
            kernel_build=digest(native['build_bytes']),kernel_library=digest(native['library_bytes']),kernel_mapping=identity(native).hex(),provenance=intent.bound.provenance.hex(),target=intent.bound.workload.hex())
        if document['op']=='quarantine.resolve':
            row=self.journal.rows.get(document['args']['operation'])
            if row is not None:
                ids['quarantine_head']=identity(row).hex();ids['original_operation']=row['capture']['operation']
            else:
                row=self.recovery.journal.latest[document['args']['operation']]
                ids['quarantine_head']=identity(row).hex();ids['original_operation']=bytes.fromhex(row['capture']['pending']['operation_id']).hex()
        prepared=None if tx is None else tx.get('preparerPeer')
        captured['binding']={'action':document['op'],'id':ids,'peer':uid,'preparer':None if prepared is None else prepared['peer']['uid'],
            'owner':self.policy['owner_uid'],'target_owner':material['target_owner'],'policy_epoch':quantity(universe['record']['policy_epoch']),'resource_epoch':quantity(epoch)}
        captured['resource_material']=clone(material);captured['reservation_event']=identity({'operation':operation,'request':observed,'binding':captured['binding']}).hex()
        snapshot=self._snapshot(captured);native=observe_operation(self,snapshot,'RESERVE_USE')
        require(native['decision']=='RESERVED_NEW','OPERATION_FRESH_NATIVE_REFUSED')
        row=self.journal.append(operation,'RESERVED',captured,snapshot=snapshot,native={'command':'RESERVE_USE','observation':native})
        self.preparing.pop(operation,None)
        self.resources.operation_principal=self
        return row
    def prepare_resource_control(self,request,control):
        """Actual native grant use, before the separately owned resource RPC.

        This explicit source-owned control route does not fabricate a peer,
        authorize through a Boolean, perform a handler effect or precommit a
        lifecycle. The complete original RESERVE_USE capture remains mandatory.
        """
        from .owner_resource_control import OwnerResourceControl
        require(type(control) is OwnerResourceControl and control.principal is self
            and type(request) is RequestPeer and current_peer() is request,
            'OPERATION_ACTUAL_OWNER_CONTROL_REQUEST_REQUIRED')
        control.intact()
        row=self._prepare_resource_use(request)
        control.intact()
        return row
    def start_resource_control_effect(self,request,control):
        """Original full native before-effect check, retaining its whole boundary."""
        from .owner_resource_control import OwnerResourceControl
        require(type(control) is OwnerResourceControl and control.principal is self
            and current_peer() is request, 'OPERATION_ACTUAL_RESOURCE_CONTROL_REQUIRED')
        control.intact();row=self._row_for_request(request);capture=row['capture']
        operation=capture['operation'];boundary=self.pre_effect(operation)
        snapshot=self._snapshot(capture);native=observe_operation(self,snapshot,'RESERVE_USE')
        require(native['decision']=='RESERVED_REPLAY',
            'OPERATION_FRESH_RESERVATION_CHANGED_BEFORE_EFFECT')
        row=self.journal.append(operation,'EFFECT_INTENT',capture,snapshot=snapshot,
            native={'command':'RESERVE_USE','observation':native},boundaries=[boundary,
            {'name':'DISPATCH_INTENT','resource':clone(control.reserve_result)}])
        control.intact();return row
    def _reserve(self,request):
        row=self._prepare_resource_use(request)
        intent=row['capture']['resource_intent'];operation=row['capture']['operation']
        packet=self.resources.reserve_packet(intent)
        resources=self.resources.submit_bound(self.pending_for_operation(operation),packet,request)
        return row,resources
    def pre_effect(self,operation):
        from .admission import ResourcePolicy
        from .operation_owner_kernel import observe_canonical
        from .resource_run_ledger import dto_record
        from .canonical_operation_machine import replay_machine
        row=self.journal.rows[operation];capture=row['capture'];intent=capture['resource_intent']
        require(row['state']=='RESERVED','OPERATION_FRESH_BOUNDARY_WITHOUT_RESERVED_USE')
        self.intact();peer=self.active_peers.get(operation)
        require(type(peer) is RequestPeer and peer.observation()==capture['request'],'OPERATION_ACTUAL_ORIGINAL_PEER_CHANGED')
        policy=ResourcePolicy.from_mapping(self.policy['plans'][capture['document']['op']]['launch']['policy'])
        machine=self.resources.machine_admission(intent.reservation,policy,'DISPATCH')
        replay_machine(self,machine,policy,intent.reservation)
        before=self.resources.current_snapshot();native_rows=self.resources.collect(before,intent)
        values=None;packet=None
        if capture['document']['op'] in ('collapse.commit','transaction.commit'):
            tx=self.controller.transactions;record=tx._load_record(capture['transaction']['transactionId'])
            tx._pre_exchange_guards(record['transactionId']);candidate=self.store.world(record['candidateWorld'])
            tx.stop_writers(candidate);generation=tx._generation();current=tx._capture_current_roots();staged=tx._capture_staged(record)
            from .manifest import Manifest
            from .validation import content_root_set
            requirement=current_requirements(self.store,self.controller.config,self.core)
            result,observed=tx._observe_authorization(record,candidate,current_manifests=current,
                staged_root=Manifest.root_set_hash(staged.values(),self.core),staged_content_root=content_root_set(staged,self.core),
                current_requirement=requirement,generation_before=generation)
            require(result=='AUTHORIZED' and observed.decide(self.core)=='AUTHORIZED' and type(observed.packet) is bytes,
                'OPERATION_ORIGINAL_FULL_EVALUATION_NATIVE_REFUSED')
            from .recovery_observation import redecide_packet
            require(redecide_packet(observed.packet,core=self.core)=='AUTHORIZED','OPERATION_FULL_PACKET_NATIVE_REDECISION_REFUSED')
            values,packet=observed.values,observed.packet
        snapshot=self._snapshot(capture)
        composite=observe_canonical(self,snapshot,before.state,before.rows,native_rows,intent,
            peer.observation()['peer']['uid'],values)
        require(composite['decision']=='READY','OPERATION_FULL_PRE_EFFECT_NATIVE_REFUSED')
        require(before==self.resources.current_snapshot(),'OPERATION_RESOURCE_CHANGED_AT_BOUNDARY')
        return {'name':'FULL_PRE_EFFECT_BOUNDARY','authority_snapshot':archive(snapshot).hex(),
            'state':dto_record(before.state),'rows':[dto_record(value) for value in before.rows],
            'observed':[dto_record(value) for value in native_rows],'machine':clone(machine),
            'collapse_packet':None if packet is None else packet.hex(),'collapse_values':archive(values).hex(),'native':composite}
    async def invoke(self,request,context,handler):
        async with self.operation_lock:
            root_worker=getattr(self,'root_worker',None)
            if root_worker is not None:
                from .protected_root_worker import RootWorkerFront
                require(type(root_worker) is RootWorkerFront and root_worker.principal is self,
                        'OPERATION_ACTUAL_ROOT_WORKER_FRONT_REQUIRED')
                document=exact_json(bytes.fromhex(request.observation()['rawRequest']),canonical_required=False)
                require(not getattr(self,'unresolved',set()) or document['op']=='quarantine.resolve',
                    'OPERATION_UNRESOLVED_NATIVE_USE_BEFORE_ORDINARY_ROUTE')
                if document['op'] not in self.owner_names:
                    return await root_worker.invoke(request,context,handler)
            return await self._invoke_serial(request,context,handler)
    async def _invoke_serial(self,request,context,handler):
        require(type(request) is RequestPeer and context.peer is request and current_peer() is request,'OPERATION_GENUINE_REQUEST_CONTEXT_REQUIRED')
        document=exact_json(bytes.fromhex(request.observation()['rawRequest']),canonical_required=False)
        require(not getattr(self,'unresolved',set()) or document['op']=='quarantine.resolve','OPERATION_UNRESOLVED_NATIVE_USE_BEFORE_ORDINARY_ROUTE')
        if document['op'] in self.owner_names:
            from .canonical_owner_witness import OwnerCanonicalScope
            # Retry evaluation must enter a genuine full-resource owner adapter;
            # an ordinary grant or owner-only endpoint cannot supply that right.
            if document['op']=='owner.retry':
                raise WorldlineError('OWNER_ORIGINAL_FULL_RESOURCE_ATTEMPT_ROUTE_UNINTEGRATED',
                    'native owner reservation and actual protected launch must join before evaluation')
            with operation_scope(OwnerCanonicalScope(self.owner_witness,request)):
                result=handler(document['args'],context)
                if inspect.isawaitable(result):result=await result
                return result
        row,resource=self._reserve(request);operation=row['capture']['operation'];capture=row['capture']
        try:
            if capture['document']['op'] in ('fork','race','revalidate','simulate','ghost.run','ghost.enable','root.add','init'):
                raise WorldlineError('OPERATION_ORIGINAL_WORKLOAD_RESOURCE_ROUTE_UNINTEGRATED','actual full-resource launch and all nested effects required')
            boundary=self.pre_effect(operation)
            snapshot=self._snapshot(capture);native=observe_operation(self,snapshot,'RESERVE_USE')
            require(native['decision']=='RESERVED_REPLAY','OPERATION_FRESH_RESERVATION_CHANGED_BEFORE_EFFECT')
            row=self.journal.append(operation,'EFFECT_INTENT',capture,snapshot=snapshot,native={'command':'RESERVE_USE','observation':native},boundaries=[boundary,{'name':'DISPATCH_INTENT','resource':clone(resource)}])
            with operation_scope(OperationScope(self,operation,request)):
                if capture['document']['op']=='quarantine.resolve':result=self.resolve_quarantine(request,capture,row)
                else:
                    result=handler(capture['document']['args'],context)
                    if inspect.isawaitable(result):result=await result
                # Authenticated direct caller result is retained before canonical
                # settlement. No retry invokes the handler again.
                result_capture=clone({'result':result,'actual_store':self.capture.chain_material(),'actual_transaction':None if capture['transaction'] is None else self.controller.transactions._load_record(capture['transaction']['transactionId'])})
                terminal=self.journal.rows[operation]
                if terminal['state']=='SETTLED':
                    # The broker already retained/settled the authentic commit
                    # before any fresh per-right post-effect. Preserve its exact
                    # result capture; reports may add only warnings/skipped data.
                    self.journal.append(operation,'ACK',capture,snapshot=terminal['snapshot'],native=terminal['native'],
                        boundaries=terminal['boundaries']+[{'name':'RETURN_REPORT','value':archive(result_capture).hex()}])
                else:self.finish(operation,result_capture)
            return result
        except BaseException as exc:
            self.quarantine(operation,exc);raise
        finally:self.active_peers.pop(operation,None)
    def quarantine(self,operation,error):
        row=self.journal.rows[operation]
        if row['state'] in ('SETTLED','RELEASED'):return
        snapshot=self._snapshot(row['capture']);observed=observe_operation(self,snapshot,'QUARANTINE_USE')
        require(observed['decision']=='QUARANTINED_NEW','OPERATION_UNKNOWN_NATIVE_QUARANTINE_REFUSED')
        self.journal.append(operation,'QUARANTINED',row['capture'],snapshot=snapshot,native={'command':'QUARANTINE_USE','observation':observed},
            boundaries=row['boundaries']+[{'name':'UNKNOWN','error':type(error).__name__,'message':str(error)}])
        self.alarm=operation
    def finish(self,operation,result_capture):
        row=self.journal.rows[operation];capture=row['capture']
        retained=[b for b in row['boundaries'] if b['name']=='RESULT_CAPTURE']
        if retained:require(retained[-1]['value']==archive(result_capture).hex(),'OPERATION_RETAINED_RESULT_CHANGED')
        else:
            require(row['state']=='EFFECT_INTENT','OPERATION_RESULT_WITHOUT_INTENT')
            row=self.journal.append(operation,'ACK',capture,snapshot=row['snapshot'],native=row['native'],
                boundaries=row['boundaries']+[{'name':'RESULT_CAPTURE','value':archive(result_capture).hex()}])
        if row['state']=='SETTLED':
            replay=observe_operation(self,row['snapshot'],row['native']['command'])
            require(replay==row['native']['observation'] and replay['decision']=='SETTLED_NEW','OPERATION_TERMINAL_REPLAY_CHANGED')
            self.resources.settle_historical(self,operation,capture['resource_intent'].reservation)
            return row
        if row['state']=='EFFECT_INTENT':
            evidence,receipts,events=self.canonical_effect(capture,result_capture)
            snapshot=self._snapshot(capture,evidence=evidence);snapshot['receipts']=receipts;snapshot['events']=events
            observed=observe_operation(self,snapshot,'OBSERVE_EFFECT')
            require(observed['decision']=='EFFECT_ACCEPTED','OPERATION_AUTHENTIC_CANONICAL_EFFECT_UNESTABLISHED')
            row=self.journal.rows[operation]
            row=self.journal.append(operation,'EFFECT_OBSERVED',capture,snapshot=snapshot,
                native={'command':'OBSERVE_EFFECT','observation':observed},boundaries=row['boundaries'])
        require(row['state']=='EFFECT_OBSERVED','OPERATION_UNKNOWN_EFFECT_REQUIRES_DISTINCT_OWNER_RESOLUTION')
        # Exact historical native input/whole chains establish the committed
        # effect. Current deny/revocation and an absent client socket cannot
        # select another exchange or borrow another capability use.
        replay=observe_operation(self,row['snapshot'],row['native']['command'])
        require(replay==row['native']['observation'] and replay['decision']=='EFFECT_ACCEPTED','OPERATION_EFFECT_REPLAY_CHANGED')
        self.resources.settle_historical(self,operation,capture['resource_intent'].reservation)
        snapshot=self._snapshot(capture,evidence=row['snapshot']['evidence'])
        snapshot['receipts']=row['snapshot']['receipts'];snapshot['events']=row['snapshot']['events']
        observed=observe_operation(self,snapshot,'SETTLE_USE');require(observed['decision']=='SETTLED_NEW','OPERATION_HISTORICAL_SETTLEMENT_NATIVE_REFUSED')
        row=self.journal.rows[operation]
        return self.journal.append(operation,'SETTLED',capture,snapshot=snapshot,native={'command':'SETTLE_USE','observation':observed},
            boundaries=row['boundaries']+[{'name':'SETTLEMENT_ACK','value':archive(result_capture).hex()}])
    def recover_committed(self,operation):
        self.historical_operation(operation);row=self.journal.rows[operation]
        retained=[b for b in row['boundaries'] if b['name']=='RESULT_CAPTURE']
        require(len(retained)==1,'OPERATION_COMPLETE_RESULT_UNAVAILABLE_UNKNOWN_RETAINED')
        with self.historical_scope(operation):return self.finish(operation,restore_archive(bytes.fromhex(retained[0]['value'])))
    def canonical_effect(self,capture,result_capture):
        # The actual canonical writer/crosswalk below owns the complete payloads.
        return self.canonical.effect(capture,result_capture)
    def resolve_quarantine(self,request,owner_capture,owner_row):
        operation=owner_capture['document']['args']['operation']
        if operation in self.journal.rows:return self.resolve_canonical_quarantine(request,owner_capture,owner_row)
        row=self.recovery.journal.latest[operation]
        require(row['state']=='QUARANTINED' and owner_capture['binding']['id']['quarantine_head']==identity(row).hex(),'OPERATION_QUARANTINE_HEAD_CHANGED')
        original=row['capture'];binding=self.capture.historical(original);native,facts=self.capture.observe_effect()
        original_use=None
        if operation in self.recovery.uses.rows:
            require(self.recovery.uses.rows[operation]['bound']==self.recovery.uses._bound(original,fresh=False),'OPERATION_ORIGINAL_RECOVERY_USE_CUSTODY_UNESTABLISHED')
            original_use=binding.grant_use.hex() if binding.grant_use is not None else None
        else:require(self.gate.issuer.store.recorded_use(operation) is None,'OPERATION_NO_EFFECT_UNRESERVED_USE_CHANGED')
        evidence=empty_evidence();evidence.update(quarantine_head=identity(row).hex(),original_use=original_use,
            recovery={'issued':binding,'recovered':binding,'historical':'HISTORICALLY_AUTHORIZED','native':native})
        snapshot=self._snapshot(owner_capture,evidence=evidence)
        disposition=observe_operation(self,snapshot,'RESOLVE_RECOVERY')
        require(disposition['decision'] in ('OWNER_ABORT','OWNER_SETTLE'),'OPERATION_OWNER_RESOLUTION_NATIVE_REFUSED')
        # Native closure joins the distinct fresh owner grant/reserved use, full
        # historical binding and actual Before/After mapping. Python transports
        # the native-selected disposition and never selects an exchange.
        self.journal.append(owner_capture['operation'],'ACK',owner_capture,snapshot=snapshot,
            native={'command':'RESOLVE_RECOVERY','observation':disposition},boundaries=owner_row['boundaries']+[{'name':'OWNER_RESOLUTION_NATIVE','original_row':archive(row).hex()}])
        resolution={'owner_binding':clone(owner_capture['binding']),'owner_request':request.observation(),'quarantined_row':clone(row),
            'original_capture':clone(original),'original_native_observation':clone(native),'actual_effect':facts,'resource_context':self.resources.current_context()}
        # Native protocol chooses legal Quarantined -> Effect_Observed/Aborted;
        # this operation never calls capture.dispatch or issues another exchange.
        if disposition['decision']=='OWNER_SETTLE':
            row=self.recovery._append(row,'OWNER_EFFECT_RESOLUTION','OWNER_EFFECT_RESOLUTION',resolution=resolution)
            return self.recovery._settle(row)
        row=self.recovery._append(row,'OWNER_NO_EFFECT_RESOLUTION','OWNER_NO_EFFECT_RESOLUTION',resolution=resolution)
        # _abort handles an already ABORTED native transaction and authentic
        # closed release history; partial/unknown release remains quarantined.
        return self.recovery._abort(row)
    def resource_owner_resolution_material(self,operation,complete_owner_native_proof):
        # The resource producer reads this exact principal-owned durable event,
        # not a proof DTO or a caller's disposition flag. Replaying its complete
        # native frame preserves original owner authorization without a new use.
        row=self.journal.rows.get(operation)
        require(row is not None and row['state']=='QUARANTINED',
            'FULL_BROKER_K4_RETAINED_QUARANTINE_REQUIRED')
        self._original_native_use(row)
        proof=self.broker().retained_owner_disposition(operation,complete_owner_native_proof)
        require(archive(proof)==archive(complete_owner_native_proof),
            'FULL_BROKER_K4_PROOF_NOT_RETAINED_EVENT')
        from .operation_owner_kernel import observe_exchange, initialize_exchange_kernel, prepare_exchange
        native=observe_exchange(self, *proof['arguments'])
        require(native==proof['native'] and native['decision'] in
            ('OWNER_RECORD_ABORT','OWNER_RECORD_EFFECT'),
            'FULL_BROKER_K4_COMPLETE_NATIVE_REPLAY_REFUSED')
        owner=proof['owner'];owner_row=self.journal.rows.get(owner['operation'])
        require(owner_row is not None and archive(owner_row['capture'])==archive(owner)
            and owner_row['state'] in ('EFFECT_INTENT','QUARANTINED')
            and owner['binding']['action']=='quarantine.resolve'
            and owner['binding']['id']['original_operation']==operation,
            'FULL_BROKER_K4_DISTINCT_OWNER_OPERATION_CUSTODY_CHANGED')
        intents=[event for event in self.journal.body['events']
            if event['operation']==owner['operation'] and event['cause']=='EFFECT_INTENT'
            and event['capture']==archive(owner).hex()]
        require(len(intents)==1,'FULL_BROKER_K4_ORIGINAL_OWNER_EFFECT_INTENT_REQUIRED')
        original_intent=intents[0]
        original_snapshot=restore_archive(bytes.fromhex(original_intent['snapshot']))
        require(original_intent['native']['command']=='RESERVE_USE'
            and observe_operation(self,original_snapshot,'RESERVE_USE')==original_intent['native']['observation']
            and original_intent['native']['observation']['decision']=='RESERVED_REPLAY',
            'FULL_BROKER_K4_ORIGINAL_OWNER_NATIVE_USE_REFUSED')
        return {'operation':operation,'event_id':row['event'],'proof':clone(proof),
            'original_request':clone(row['capture']['request']),
            'original_capture':clone(row['capture']),
            'original_native_use':self._original_native_use(row),
            'scope':clone(row['capture']['resource_material']['scope']),
            'bound':clone(row['capture']['resource_intent'].bound),
            'packets':[clone(value['packet']) for boundary in row['boundaries']
                if boundary['name']=='RESOURCE_FULL_COMMITTED_HISTORY'
                for value in boundary['selected']],
            'retained_resource_history':[clone(boundary) for boundary in row['boundaries']
                if boundary['name']=='RESOURCE_FULL_COMMITTED_HISTORY'],
            'owner_event_id':digest(canonical(original_intent)),
            'owner_native_intent':clone(original_intent),'owner_current_state':owner_row['state'],
            'owner_capture':clone(owner)}
    def recover_owner_resolution(self,operation):
        self.intact();row=self.journal.rows[operation]
        require(row['state'] in ('RESOLVED_EFFECT','RESOLVED_NO_EFFECT'),
            'FULL_BROKER_OWNER_RESOLVED_STATE_REQUIRED')
        acknowledgments=[b for b in row['boundaries'] if b['name']=='FULL_BROKER_K4_RESOURCE_ACK']
        require(len(acknowledgments)==1,'FULL_BROKER_OWNER_RESOURCE_ACK_REQUIRED')
        envelope=restore_archive(bytes.fromhex(acknowledgments[0]['value']))
        if row['native']['command'] in ('RESOLVE_EFFECT_HISTORICAL','RESOLVE_NO_EFFECT_HISTORICAL'):
            from .canonical_k4_recovery import replay_ack
            resource=replay_ack(self,row['capture'],envelope)
        else:
            # Preserve the exact older original-protocol histories. They do not
            # become scoped history by projection or a family label.
            resource=envelope
            _state,_rows,intent=self.resources.service._decode_packet(resource['packet'])
            require(intent.bound==row['capture']['resource_intent'].bound
                and intent.kind in ('RELEASE_HOLD','CHARGE_BUDGET')
                and self.resources.service.recover(resource['packet'],peer_uid=os.geteuid())==resource['reply'],
                'FULL_BROKER_OWNER_RESOURCE_ACK_REPLAY_CHANGED')
        if row['state']=='RESOLVED_EFFECT':
            original=row['snapshot'];snapshot=self._snapshot(row['capture'],evidence=original['evidence'])
            snapshot['receipts']=clone(original['receipts']);snapshot['events']=clone(original['events'])
            answer=observe_operation(self,snapshot,'SETTLE_USE')
            require(answer['decision']=='SETTLED_NEW','FULL_BROKER_OWNER_RESTART_SETTLEMENT_REFUSED')
            self.journal.append(operation,'SETTLED',row['capture'],snapshot=snapshot,
                native={'command':'SETTLE_USE','observation':answer},boundaries=row['boundaries'])
        self.unresolved.discard(operation)
        return {'operation':operation,'state':self.journal.rows[operation]['state'],
            'resource':resource,'new_exchange':False}
    def resolve_canonical_quarantine(self,request,owner_capture,owner_row):
        operation=owner_capture['document']['args']['operation'];row=self.journal.rows[operation]
        require(row['state']=='QUARANTINED' and identity(row).hex()==owner_capture['binding']['id']['quarantine_head'],
            'FULL_BROKER_OWNER_QUARANTINE_HEAD_CHANGED')
        self._original_native_use(row)
        broker=self.broker();resolution=broker.resolve(operation,owner_capture);selected=resolution['decision']
        # The native decision recognizes genuine Before/After, never grants an
        # exchange. Complete native owner/use/current-context and both actual
        # mapping observations are retained before any terminal disposition.
        proof=resolution['proof']
        require(proof['owner']['request']==request.observation(),'FULL_BROKER_OWNER_ORIGINAL_PEER_CHANGED')
        method=getattr(type(self.resources),'resolve_historical',None)
        release=None if method is None else method.__get__(self.resources,type(self.resources))
        require(callable(release),'FULL_RESOURCE_DISTINCT_K4_TERMINAL_PRODUCER_UNAVAILABLE')
        resource=release(self,operation,row['capture']['resource_intent'].reservation,proof)
        from .canonical_k4_recovery import capture_ack
        ack=capture_ack(self,row['capture'],resource)
        return self.complete_canonical_resolution(operation,proof,ack)
    def complete_canonical_resolution(self,operation,proof,ack):
        # Called by the fresh actual owner endpoint and the historical restart
        # route. Both consume the same authenticated prior K4 intent and actual
        # resource commit, with no new exchange/use or fresh client descriptor.
        operation=self._operation_key(operation)
        from .canonical_k4_recovery import replay_ack
        row=self.journal.rows[operation]
        require(row['state']=='QUARANTINED','FULL_BROKER_K4_ORIGINAL_STATE_CHANGED')
        self.resource_owner_resolution_material(operation,proof)
        resource=replay_ack(self,row['capture'],ack)
        owner_capture=proof['owner'];selected=proof['native']['decision'];broker=self.broker()
        row=self.journal.rows[operation];evidence=empty_evidence()
        evidence.update(owner_resolution=clone(owner_capture['binding']),quarantine_head=owner_capture['binding']['id']['quarantine_head'])
        if selected=='OWNER_RECORD_EFFECT':
            result=broker.recover(operation)
            captured=clone({'result':result,'actual_store':self.capture.chain_material(),
                'actual_transaction':self.controller.transactions._load_record(row['capture']['transaction']['transactionId'])})
            factual,receipts,events=self.canonical_effect(row['capture'],captured)
            evidence.update(factual);evidence.update(owner_resolution=clone(owner_capture['binding']),
                quarantine_head=owner_capture['binding']['id']['quarantine_head'])
            command,expected='RESOLVE_EFFECT_HISTORICAL','RESOLVED_EFFECT'
        else:
            captured=None;receipts=[];events=[];evidence['no_effect_binding']=clone(row['capture']['binding'])
            command,expected='RESOLVE_NO_EFFECT_HISTORICAL','RESOLVED_NO_EFFECT'
        snapshot=self._snapshot(row['capture'],evidence=evidence);snapshot['receipts']=receipts;snapshot['events']=events
        snapshot['owner_completion']=clone(proof)
        self.mapped_symbols(['wl_canonical_owner_completion_version_v1',
            'wl_canonical_owner_completion_layout_v1','wl_canonical_owner_completion_decide_v1'])
        native=self.operation_decision(snapshot,command);require(native['decision']==expected,'FULL_BROKER_OWNER_USE_DISPOSITION_REFUSED')
        old=self.journal.rows[operation]
        boundaries=old['boundaries']+[{'name':'FULL_BROKER_K4_RESOURCE_ACK','value':archive(ack).hex()}]
        if captured is not None:boundaries.append({'name':'RESULT_CAPTURE','value':archive(captured).hex()})
        self.journal.append(operation,expected,row['capture'],snapshot=snapshot,
            native={'command':command,'observation':native},boundaries=boundaries)
        if selected=='OWNER_RECORD_EFFECT':
            # RESOLVED_EFFECT carries the native historical effect; finish uses
            # the same original use/resource evidence without fresh eligibility.
            terminal=self.journal.rows[operation]
            settle=self._snapshot(terminal['capture'],evidence=evidence);settle['receipts']=receipts;settle['events']=events
            answer=observe_operation(self,settle,'SETTLE_USE');require(answer['decision']=='SETTLED_NEW','FULL_BROKER_OWNER_HISTORICAL_SETTLEMENT_REFUSED')
            self.journal.append(operation,'SETTLED',terminal['capture'],snapshot=settle,
                native={'command':'SETTLE_USE','observation':answer},boundaries=terminal['boundaries'])
        self.unresolved.discard(operation)
        return {'operation':operation,'state':self.journal.rows[operation]['state'],'native_disposition':selected,
            'resource':resource,'new_exchange':False}
