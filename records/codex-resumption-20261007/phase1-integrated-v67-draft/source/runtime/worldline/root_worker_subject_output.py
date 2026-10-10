"""Actual ordered request output, durably retained in the original HMAC journal."""
from __future__ import annotations
import hashlib,threading
from .canonical import canonical_bytes
from .root_worker_codec import original_archive,original_restore
from .protected_startup import require


class RequestOutputEmitter:
    def __init__(self,worker,subject,original,intake,*,native_capture):
        self.worker,self.subject,self.original,self.intake=worker,subject,original,intake
        self.native_capture=native_capture
        principal=worker.principal
        if not hasattr(principal,'custody_output_lock'):principal.custody_output_lock=threading.RLock()
        self.lock=principal.custody_output_lock
        worker.custody_journal.require_event(intake)
        require(intake['kind'] in ('REQUEST_QUEUED','REQUEST_INTAKE') and intake['operation']==subject.operation
            and intake['subject']==subject.subject,'CUSTODY_OUTPUT_ACTUAL_NATIVE_ADMISSION_REQUIRED')
        self.records=[];self.written=[];self.peer_status=[]
        for boundary in worker.principal.journal.rows[subject.operation]['boundaries']:
            if boundary['name']=='REQUEST_OUTPUT':self.records.append(original_restore(bytes.fromhex(boundary['value'])))
            elif boundary['name']=='REQUEST_OUTPUT_WRITTEN':self.written.append(original_restore(bytes.fromhex(boundary['value'])))
            elif boundary['name']=='REQUEST_OUTPUT_PEER_STATUS':self.peer_status.append(original_restore(bytes.fromhex(boundary['value'])))
    def _retain(self,name,record):
        journal=self.worker.principal.journal;row=journal.rows[self.subject.operation]
        boundary={'name':name,'value':original_archive(record).hex()}
        journal.append(self.subject.operation,'ACK',row['capture'],snapshot=row['snapshot'],native=row['native'],
            boundaries=row['boundaries']+[boundary])
        return record
    def scope(self):
        from .root_worker_serving_peer import fact_capture
        with fact_capture():
            context=self.subject.journal.subject_context(self.subject.operation,'REQUEST',self.subject.subject,
                self.original,root_operation=self.subject.root_operation,kind='REQUEST_RESPONDED',
                actor_role=self.subject.actor_role,query_purpose='OUTPUT')
        binding=context['binding'];view=context['native_context']
        return {'generation':binding['generation'],
            'root_operation':None if view['root'] is None else view['root']['operation'],
            'operation':self.subject.operation,'request':self.subject.subject,
            'subgeneration':binding['subgeneration'],'reattach_epoch':view['reattach_epoch']}
    def produce(self,kind,value):
        with self.lock:
            require(kind in ('PROGRESS_BYTES','RESPONSE_BYTES'),'CUSTODY_OUTPUT_ORIGINAL_FRAME_KIND_REQUIRED')
            line=canonical_bytes(value)+b'\n'
            candidate={'request':self.subject.subject,'admission_head':self.intake['event_id'],
                'type':kind,'line':line,'sha256':hashlib.sha256(line).hexdigest(),
                'source':self.worker.source_lease.check(),'scope':self.scope()}
            quantity=self.subject.output_quantity(self.original,tuple(self.records),candidate,
                profile=self.intake['retained_record']['x5']['subject_evidence'],
                native=self.native_capture('ROOT_WORKER_BEFORE_OUTPUT_ALLOCATION',require_ready=False))
            record=dict(candidate,out_seq=str(int.from_bytes(quantity,'little')))
            self._retain('REQUEST_OUTPUT',record);self.records.append(record)
            return record
    def acknowledge(self,record,write,source,*,relay=None):
        with self.lock:
            actual={'request':self.subject.subject,'admission_head':self.intake['event_id'],
                'type':'RESPONSE_WRITTEN','out_seq':record['out_seq'],'sha256':record['sha256'],
                'write':tuple(write),'source':source,'scope':self.scope(),'production_scope':record['scope']}
            if relay is not None:actual['relay']=relay
            quantity=self.subject.output_written(self.original,tuple(self.records),actual,
                profile=self.intake['retained_record']['x5']['subject_evidence'],
                native=self.native_capture('ROOT_WORKER_AFTER_ACTUAL_OUTPUT_WRITE',require_ready=False))
            self._retain('REQUEST_OUTPUT_WRITTEN',actual);self.written.append(actual)
            self.written_quantity=quantity
            return actual
    def retained(self):
        return {'produced':tuple(self.records),'written':tuple(self.written),
            'peer_status':tuple(self.peer_status)}
    def replay_candidate(self,record):
        return dict(record,source=self.worker.source_lease.check(),scope=self.scope(),
            production_scope=record['scope'])
    def replay(self,record):
        with self.lock:
            candidate=self.replay_candidate(record)
            decision=self.subject.output_replay(self.original,tuple(self.records),candidate,
                profile=self.intake['retained_record']['x5']['subject_evidence'],
                native=self.native_capture('ROOT_WORKER_BEFORE_OUTPUT_REPLAY',require_ready=False))
            require(str(int.from_bytes(decision.ordinal,'little'))==record['out_seq'],
                'CUSTODY_OUTPUT_NATIVE_REPLAY_ORDINAL_CHANGED')
            return decision
    def retain_peer_status(self,candidate):
        with self.lock:
            quantity=self.subject.output_written(self.original,tuple(self.records),candidate,
                profile=self.intake['retained_record']['x5']['subject_evidence'],
                native=self.native_capture('ROOT_WORKER_AFTER_AUTHENTIC_PEER_STATUS',require_ready=False))
            self._retain('REQUEST_OUTPUT_PEER_STATUS',candidate);self.peer_status.append(candidate)
            self.written_quantity=quantity
            return quantity
