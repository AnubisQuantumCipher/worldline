"""Native use reservation under the real protected issuer/store lock and head.

Full historical source packets, grant events, use events and outstanding intents
remain authenticated and retained. Installed source/native binding and exclusive
principal bootstrap remain prerequisites; no service is installed by this file.
"""
from __future__ import annotations
import ctypes as C
import fcntl
import hashlib
import hmac
import os
from pathlib import Path
import stat
from intent_gate import Gate, require, protected, save, canonical
from issuer.protected import ProtectedIssuer
from .capability_use_kernel import UseReservationKernel
from .errors import CoreUnavailable
from .protected_recovery_capture import ProtectedCapture,private_bytes,exact_json,refuse,identity
from .recovery_observation import archive,restore_archive

_DOMAIN=b'worldline-protected-full-capability-reservations-v1\0'
_ZERO='0'*64

class ProtectedUseReservations:
    def __init__(self,gate,capture,*,startup_lease):
        if type(gate) is not Gate or type(capture) is not ProtectedCapture or type(gate.issuer) is not ProtectedIssuer or os.geteuid()!=0:
            refuse('CAPABILITY_USE_PROTECTED_PRINCIPAL_REQUIRED')
        self.gate,self.capture,self.issuer=gate,capture,gate.issuer
        self._lock_intact()
        self.conf=exact_json(private_bytes(gate.root/'authority/gate/use-reservation-bind.json'))
        require(type(self.conf) is dict and set(self.conf)=={'schema','library','library_sha256','source_root','source_inventory','build'} and
                self.conf['schema']=='cosmogony.protected-use-reservation-bind-v1','CAPABILITY_USE_BIND_SCHEMA')
        self._source_intact()
        path=Path(self.conf['library']);protected(path)
        require(hashlib.sha256(path.read_bytes()).hexdigest()==self.conf['library_sha256'],'CAPABILITY_USE_NATIVE_BYTES_CHANGED')
        # This is the same actual protected installed library selected by the
        # original issuer/Universe adapters, now with additive native exports.
        require(path.resolve()==(gate.root/'install/universe_source/lib/libcosmogony_core.so').resolve(),
                'CAPABILITY_USE_ORIGINAL_ISSUER_LIBRARY_SPLIT')
        self.native=C.CDLL(str(path))
        # Bind every export that the adapter can execute before its constructor
        # invokes version/layout functions. CDLL loading itself is not covered
        # by this post-load check; loader/pre-main custody remains required.
        self.native_material=self._native_material()
        self.kernel=UseReservationKernel(self.native)
        self.path=self.issuer.state/'full-use-reservations.json'
        self.poisoned=False;self.rows={};self.events=[]
        from .protected_startup import StartupLease
        require(type(startup_lease) is StartupLease and capture.startup_lease is startup_lease,
                'CAPABILITY_USE_PROTECTED_STARTUP_LEASE_REQUIRED')
        startup_lease.capture_journal_admission(gate,'full-use-reservations',self.path,self._envelope())
        require(os.path.lexists(self.path),'CAPABILITY_USE_PRIOR_JOURNAL_MISSING')
        self._load()

    def _lock_intact(self):
        descriptor=self.issuer.lock_fd
        actual=os.fstat(descriptor);path=(self.issuer.state/'issuer.lock').lstat()
        require(stat.S_ISREG(actual.st_mode) and actual.st_uid==0 and actual.st_nlink==1 and
                stat.S_IMODE(actual.st_mode)&0o077==0 and
                (actual.st_dev,actual.st_ino)==(path.st_dev,path.st_ino),'CAPABILITY_USE_ISSUER_LOCK_CHANGED')
        fcntl.flock(descriptor,fcntl.LOCK_EX|fcntl.LOCK_NB)
        self.issuer.head() # original anchored canonical store/head verification

    def _source_intact(self):
        root=Path(self.conf['source_root']);protected(root,directory=True)
        expected=exact_json(private_bytes(self.conf['source_inventory']));actual={}
        for path in sorted(root.rglob('*')):
            if path.is_symlink():refuse('CAPABILITY_USE_SOURCE_SYMLINK')
            if path.is_file():
                protected(path);actual[path.relative_to(root).as_posix()]={
                    'mode':oct(stat.S_IMODE(path.stat().st_mode)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        require(actual==expected,'CAPABILITY_USE_COMPLETE_SOURCE_CHANGED')

    def _native_material(self):
        path=Path(self.conf['library']);protected(path)
        raw=path.read_bytes();before=path.stat();segments=[];ranges=[]
        for line in Path('/proc/self/maps').read_text().splitlines():
            fields=line.split(maxsplit=5)
            if len(fields)!=6 or fields[5]!=str(path.resolve()):continue
            bounds,permissions,offset,device,inode,_name=fields
            start,end=(int(value,16) for value in bounds.split('-'))
            try:fd=os.open(Path('/proc/self/map_files')/bounds,os.O_RDONLY|os.O_CLOEXEC)
            except OSError:refuse('CAPABILITY_USE_MAPPED_DESCRIPTOR_UNAVAILABLE')
            try:
                mapped=os.fstat(fd)
                with os.fdopen(os.dup(fd),'rb') as file:content=file.read()
                require((mapped.st_dev,mapped.st_ino)==(before.st_dev,before.st_ino) and content==raw,
                        'CAPABILITY_USE_MAPPED_DESCRIPTOR_DIFFERS')
            finally:os.close(fd)
            segments.append({'permissions':permissions,'offset':offset,'device':device,'inode':inode,'length':end-start})
            ranges.append((start,end,permissions))
        require(bool(segments),'CAPABILITY_USE_NATIVE_MAPPING_ABSENT')
        # Include the constructor's ABI queries as well as the decision and
        # original revocation entry. All must resolve inside this exact mapped
        # library before any adapter query is invoked; no layout result from a
        # different object is accepted as evidence of this object's ABI.
        for name in ('cosmogony_use_reservation_version_v1',
                     'cosmogony_use_reservation_layout_v1',
                     'cosmogony_use_reservation_decide_v1',
                     'cosmogony_revocation_lineage_bytes',
                     'cosmogony_revocation_link_bytes',
                     'cosmogony_universe_record_bytes',
                     'cosmogony_revocation_check'):
            if name in ('cosmogony_use_reservation_version_v1',
                        'cosmogony_use_reservation_layout_v1',
                        'cosmogony_use_reservation_decide_v1'):
                # Preserve the adapter constructor's original typed missing-API
                # error, without invoking any query before mapping is checked.
                try:
                    symbol=getattr(self.native,name)
                except AttributeError as exc:
                    raise CoreUnavailable('native capability-use reservation unavailable') from exc
            else:
                # Original dependency-size/revocation lookups did not have the
                # adapter's missing-API translation. Preserve their failures.
                symbol=getattr(self.native,name)
            address=C.cast(symbol,C.c_void_p).value
            require(address is not None and any(start<=address<end and 'x' in permission for start,end,permission in ranges),
                    'CAPABILITY_USE_NATIVE_SYMBOL_MAPPING_DIFFERS')
        after=path.stat()
        require((before.st_dev,before.st_ino,before.st_size,before.st_ctime_ns,before.st_mtime_ns)==
                (after.st_dev,after.st_ino,after.st_size,after.st_ctime_ns,after.st_mtime_ns),
                'CAPABILITY_USE_NATIVE_FILE_CHANGED')
        require(hashlib.sha256(raw).hexdigest()==self.conf['library_sha256'],'CAPABILITY_USE_NATIVE_PIN_CHANGED')
        return {'library':os.fsencode(path),'bytes':raw,'device':before.st_dev,'inode':before.st_ino,
                'segments':segments,'build':private_bytes(self.conf['build'])}

    def _intact(self):
        if self.poisoned:refuse('CAPABILITY_USE_DURABILITY_UNKNOWN')
        self._lock_intact();self._source_intact();self.capture.intact()
        require(self._native_material()==self.native_material,'CAPABILITY_USE_HISTORICAL_MAPPING_UNAVAILABLE')

    def _envelope(self):
        body={'schema':'cosmogony.full-protected-use-reservations-v1','events':self.events}
        return {'body':body,'mac':hmac.new(self.issuer.key,_DOMAIN+canonical(body),hashlib.sha256).hexdigest()}

    def _save(self):
        if self.poisoned:refuse('CAPABILITY_USE_DURABILITY_UNKNOWN')
        try:
            require(os.path.lexists(self.path),'CAPABILITY_USE_PRIOR_JOURNAL_MISSING')
            require(exact_json(private_bytes(self.path))==self.persisted,'CAPABILITY_USE_PRIOR_JOURNAL_CUSTODY_CHANGED')
            envelope=self._envelope();save(self.path,envelope)
            require(exact_json(private_bytes(self.path))==envelope,'CAPABILITY_USE_DURABLE_READBACK_DIFFERS')
            self.persisted=restore_archive(archive(envelope))
        except BaseException:
            self.poisoned=True
            raise

    @staticmethod
    def _next_row(payload,status):
        snapshot=payload['decision_snapshot']
        if status.startswith('RESERVED_'):state='RESERVED'
        elif status.startswith('CONSUMED_'):state='CONSUMED'
        elif status.startswith('RELEASED_'):state='RELEASED'
        else:refuse('CAPABILITY_USE_REFUSAL_HAS_NO_TRANSITION')
        return {'kind':'BOUND_RESERVATION','state':state,'bound':snapshot['binding'],'lineage':payload['issued_lineage']}

    def _load(self):
        envelope=exact_json(private_bytes(self.path))
        require(type(envelope) is dict and set(envelope)=={'body','mac'} and
                type(envelope['body']) is dict and set(envelope['body'])=={'schema','events'} and
                envelope['body']['schema']=='cosmogony.full-protected-use-reservations-v1' and
                type(envelope['body']['events']) is list,'CAPABILITY_USE_JOURNAL_SCHEMA')
        expected=hmac.new(self.issuer.key,_DOMAIN+canonical(envelope['body']),hashlib.sha256).hexdigest()
        require(type(envelope['mac']) is str and hmac.compare_digest(expected,envelope['mac']),
                'CAPABILITY_USE_JOURNAL_AUTHENTICATION')
        prior='GENESIS';rows={}
        for event in envelope['body']['events']:
            require(type(event) is dict and set(event)=={'prior','command','status','payload'} and event['prior']==prior,
                    'CAPABILITY_USE_JOURNAL_EVENT_SCHEMA')
            raw=bytes.fromhex(event['payload']);require(raw.hex()==event['payload'],'CAPABILITY_USE_JOURNAL_ENCODING')
            payload=restore_archive(raw)
            require(type(payload) is dict and set(payload)=={'decision_snapshot','issuer_material','capture','native_material','issued_lineage','native_decision_material'},
                    'CAPABILITY_USE_FULL_SNAPSHOT_SCHEMA')
            require(payload['native_material']==self.native_material,'CAPABILITY_USE_REPLAY_KERNEL_UNAVAILABLE')
            retained_rows=[item for item in payload['decision_snapshot']['rows'] if item['kind']=='BOUND_RESERVATION']
            require(retained_rows==list(rows.values()),'CAPABILITY_USE_REPLAY_ROSTER_PREFIX_CHANGED')
            observation=self.kernel.observe(payload['decision_snapshot'],event['command'])
            require(observation==payload['native_decision_material'],
                    'CAPABILITY_USE_FULL_RAW_NATIVE_REDECISION_DIFFERS')
            actual=observation['status']
            require(actual==event['status'],'CAPABILITY_USE_HISTORICAL_NATIVE_REDECISION_DIFFERS')
            row=self._next_row(payload,actual);operation=row['bound']['operation_id']
            require(operation==payload['capture']['pending']['operation_id'],'CAPABILITY_USE_REPLAY_OPERATION_CHANGED')
            if operation in rows:
                require(rows[operation]['bound']==row['bound'] and rows[operation]['lineage']==row['lineage'],
                        'CAPABILITY_USE_REPLAY_BOUND_FACTS_CHANGED')
            rows[operation]=row;prior=hashlib.sha256(canonical(event)).hexdigest()
        self.events,self.rows=envelope['body']['events'],rows
        self.persisted=restore_archive(archive(envelope))

    def _issuer_material(self):
        self._lock_intact();anchor=self.issuer.head()
        grants,revoked,uses,sequence,head=self.issuer.store._replay_uses()
        require(anchor['event_head']==head and anchor['sequence']==sequence,'CAPABILITY_USE_ISSUER_REPLAY_HEAD_CHANGED')
        events=[dict(zip(('seq','previous_hash','body_json','event_hash'),row)) for row in
            self.issuer.store.db.execute('SELECT seq,previous_hash,body_json,event_hash FROM events ORDER BY seq').fetchall()]
        require(self.issuer.head()==anchor,'CAPABILITY_USE_ISSUER_CHANGED_DURING_CAPTURE')
        return {'anchor':anchor,'policy':restore_archive(archive(self.issuer.policy)),
                'grants':grants,'revoked':tuple(sorted(revoked)),'uses':uses,'events':events}

    def _bound(self,capture,*,fresh):
        capability=capture['pending']['capability'];use=capture['capability_use']
        request=capability['request']
        # Today's policy is consulted only before an effect. Settlement uses
        # the complete authenticated retained request and peer identity.
        require(request['actor_id']==self.gate.lab_policy.actor_id(capture['peer']['uid']),
                'CAPABILITY_USE_RETAINED_PEER_CHANGED')
        if fresh:
            expected=self.gate.lab_policy.capability_request(self.issuer.policy,
                request['actor_id'],request['action'],capture['pending']['operation_id'])
            require(request==expected,'CAPABILITY_USE_CURRENT_REQUEST_CHANGED')
        require(use['operation_id']==request['request_id'] and
                use['capability_id']==capability['capability_id'] and use['transaction_id']==capture['record']['transactionId'],
                'CAPABILITY_USE_ACTUAL_PEER_REQUEST_CHANGED')
        return {'capability_id':use['capability_id'],'operation_id':use['operation_id'],
                'transaction_id':identity(use['transaction_id']).hex(),'requester_id':request['actor_id'],
                'universe_head':use['universe_head'],'request_identity':identity(request).hex(),
                'grant_use_identity':identity(use).hex(),'recovery_binding_identity':identity(capture['binding']).hex(),
                'policy_epoch':use['policy_epoch'],'action':use['action']}

    def _snapshot(self,capture,mode):
        self._intact();self.capture.historical(capture)
        material=self._issuer_material();grants=material['grants'];uses=material['uses'];revoked=set(material['revoked'])
        capability=capture['pending']['capability'];operation=capture['pending']['operation_id'];bound=self._bound(capture,fresh=mode=='RESERVE_USE')
        historical=self.rows.get(operation)
        if historical is not None:require(historical['bound']==bound,'CAPABILITY_USE_SAME_OPERATION_CHANGED')
        lineage=self.issuer.store._lineage(grants,revoked,capability['capability_id'])
        rows=[]
        # Preserve the full protected issuer event material separately. A row
        # already charged by issuer.use and still RESERVED in our journal is
        # represented by that identical reservation exactly once, never omitted.
        for use_operation,use in uses.items():
            if use_operation in self.rows:
                reserved=self.rows[use_operation]
                require(reserved['state']!='RELEASED','CAPABILITY_USE_RELEASED_ROW_HAS_COMMITTED_USE')
                clean={name:value for name,value in use.items() if name not in ('kind','grant_state')}
                require(identity(clean).hex()==reserved['bound']['grant_use_identity'],
                        'CAPABILITY_USE_ISSUER_USE_AND_RESERVATION_DIFFER')
                continue
            original_lineage=self.issuer.store._lineage(grants,revoked,use['capability_id'])
            legacy={'capability_id':use['capability_id'],'operation_id':use['operation_id'],
                'transaction_id':identity(use['transaction_id']).hex(),'requester_id':original_lineage[-1]['grant']['subject_id'],
                'universe_head':use['universe_head'],'request_identity':_ZERO,'grant_use_identity':identity(use).hex(),
                'recovery_binding_identity':_ZERO,'policy_epoch':use['policy_epoch'],'action':use['action']}
            rows.append({'kind':'LEGACY_CHARGED_USE','state':'CONSUMED','bound':legacy,'lineage':original_lineage})
        rows.extend(restore_archive(archive(list(self.rows.values()))))
        policy=material['policy']
        if mode=='RESERVE_USE':
            record=self.gate.universe.read()['record']
        else:
            # Historical settlement cannot substitute today's Universe/policy
            # into the original request. The canonical original policy/context
            # and full reservation decision remain authenticated in the journal.
            prior=next(event for event in self.events if restore_archive(bytes.fromhex(event['payload']))['decision_snapshot']['binding']['operation_id']==operation)
            retained=restore_archive(bytes.fromhex(prior['payload']))['decision_snapshot']
            record=retained['record'];policy={**policy,'genesis_universe':retained['genesis'],
                                            'usage':retained['base_usage'],'now_tick':retained['now_tick']}
        snapshot={'record':record,'genesis':policy['genesis_universe'],'lineage':lineage,
                  'request':capability['request'],'target':capability['target_world_id'],'base_usage':policy['usage'],
                  'now_tick':policy['now_tick'],'binding':bound,'rows':rows,'grants':list(grants.values())}
        issued_lineage=historical['lineage'] if historical is not None else lineage
        return {'decision_snapshot':snapshot,'issuer_material':material,'capture':capture,
                'native_material':self.native_material,'issued_lineage':issued_lineage}

    def _transition(self,capture,mode):
        payload=self._snapshot(capture,mode)
        payload['native_decision_material']=self.kernel.observe(payload['decision_snapshot'],mode)
        status=payload['native_decision_material']['status']
        require(status!='REFUSED','CAPABILITY_USE_NATIVE_TRANSITION_REFUSED')
        # Append complete fresh/retained material before exposing the admitted
        # reservation or settlement acknowledgement to the principal.
        prior='GENESIS' if not self.events else hashlib.sha256(canonical(self.events[-1])).hexdigest()
        self.events.append({'prior':prior,'command':mode,'status':status,'payload':archive(payload).hex()})
        self._save();row=self._next_row(payload,status);self.rows[row['bound']['operation_id']]=row
        return {'status':status,'bound':row['bound'],'journal_head':hashlib.sha256(canonical(self.events[-1])).hexdigest()}

    def reserve(self,capture):return self._transition(capture,'RESERVE_USE')

    def consume(self,capture):
        # Command source is the principal after established historical effect;
        # this function records exactly the existing protected use, then changes
        # RESERVED -> CONSUMED without another increment or fresh eligibility.
        self._intact();operation=capture['pending']['operation_id']
        require(operation in self.rows,'CAPABILITY_USE_RESERVATION_ABSENT')
        require(self.rows[operation]['bound']==self._bound(capture,fresh=False),'CAPABILITY_USE_CONSUME_BINDING_CHANGED')
        require(self.rows[operation]['state'] in ('RESERVED','CONSUMED'),'CAPABILITY_USE_CONSUME_ALREADY_RELEASED')
        payload=self._snapshot(capture,'CONSUME_USE')
        require(self.kernel.decide(payload['decision_snapshot'],'CONSUME_USE') in ('CONSUMED_NEW','CONSUMED_REPLAY'),
                'CAPABILITY_USE_CONSUME_NATIVE_PREFLIGHT_REFUSED')
        result=self.issuer.use(capture['capability_use'],self.issuer.head()['event_head'])
        answer=self._transition(capture,'CONSUME_USE')
        return {'reservation':answer,'issuer_use':result}

    def release(self,capture):
        # Called only after protected no-effect and resource release proof, with
        # an authenticated retained reservation. Never erase a recorded use.
        self._intact()
        require(self.issuer.store.recorded_use(capture['pending']['operation_id']) is None,
                'CAPABILITY_USE_EFFECT_ALREADY_CHARGED')
        return self._transition(capture,'RELEASE_USE')
