"""Original pre-handoff FrontQueued outputs without a Worker Ready grant."""
from __future__ import annotations
from .client_peer import RequestPeer,peer_read_source
from .custody_subject_capture import actor_identity,original_roles,socket_capture
from .protected_startup import require
from .root_worker_codec import raw_archive
from .root_worker_subject_custody import SubjectCustody
from .root_worker_subject_output import RequestOutputEmitter
from .errors import WorldlineError


class FrontQueuedEmitter(RequestOutputEmitter):
    def __init__(self,front,subject,original,queued,request):
        self.request=request;self.gates=[]
        super().__init__(front,subject,original,queued,native_capture=self._native)
    def _native(self,cause,require_ready=False):
        context=self.subject.journal.subject_context(self.subject.operation,'REQUEST',self.subject.subject,
            self.original,root_operation=self.subject.root_operation,kind='REQUEST_RESPONDED',
            actor_role=self.subject.actor_role,query_purpose='OUTPUT')
        return tuple(context['native_observations'])
    def observe_front(self):
        source=self.worker.source_lease.check();start=len(self.request.peer.read_receipts)
        gate={'mode':'FRONT','gate':'original-front-output','front_socket':None,
              'worker_socket':None,'transfer':None,'front_reread':None,'history':tuple(self.gates)}
        try:
            with peer_read_source(source):
                document=self.request.observation()
                gate['front_socket']=socket_capture(self.request.peer.descriptor(),source)
            gate['front_reread']=document
        except (OSError,WorldlineError) as error:
            detail={'class':'OSError' if isinstance(error,OSError) else 'WorldlineError',
                'code':error.errno if isinstance(error,OSError) else error.code,
                'message':str(error),'details':{} if isinstance(error,OSError) else error.details}
            gate.update(reread_error=raw_archive(detail),reread_failure={
                'source':source,'calls':tuple(self.request.peer.read_receipts[start:]),
                'error':detail,'close':self.request.peer.close_receipt})
            self.gates.append(gate)
            raise
        self.gates.append(gate)
        self.subject.serve_gate(self.original,gate,native=self._native('ROOT_FRONT_QUEUED_SERVING_GATE'))
        return document
    def emit(self,kind,value):
        from .root_worker_output_kernel import ReplayDisposition
        from .root_worker_subject_service import _write_line
        with self.lock:
            self.observe_front()
            produced=self.produce(kind,value)
            if kind=='RESPONSE_BYTES':
                self.response_event=self.subject.respond(self.original,value,produced['line'],
                    native=self._native('ROOT_FRONT_BEFORE_QUEUED_RESPONSE'),
                    gates=tuple(self.gates),out_seq=produced['out_seq'])
            decision=self.replay(produced)
            if decision.disposition is not ReplayDisposition.WRITE:return decision
            writes=[];source=self.worker.source_lease.check()
            self.actual_writes=getattr(self,'actual_writes',[])
            self.actual_writes.append({'record':produced,'write':writes})
            _write_line(self.request,produced['line'],source,writes)
            return self.acknowledge(produced,writes,source)


def queue_front_request(front,request,row,resource,context):
    from .protected_root_worker import RootWorkerFront
    from .root_worker_root_evidence import descriptor_inventory
    require(type(front) is RootWorkerFront and type(request) is RequestPeer
        and front.principal.journal.rows[row['capture']['operation']] is row
        and row['capture']['request']==request.observation(),
        'CUSTODY_FRONT_ORIGINAL_ACTUAL_RESERVATION_REQUIRED')
    source=front.source_lease.check();descriptors={'fd/'+str(item['fd']):item['fd']
        for item in descriptor_inventory()}
    locks={fd:str(path) for path,fd in front.principal.lease.fds.items()}
    locks.update({front.principal.gate.issuer.lock_fd:str(front.principal.gate.issuer.state/'issuer.lock'),
        front.principal.gate.universe.lock_fd:str(front.principal.gate.universe.state/'universe.lock'),
        front.custody_journal.lock_fd:str(front.custody_journal.lock_path)})
    roles=original_roles(descriptors,source,actor_identity(),None,locks)
    subject=SubjectCustody(front,row['capture']['operation'],'REQUEST',request.observation()['observationId'])
    queued=subject.request_queued(request,roles)
    emitter=FrontQueuedEmitter(front,subject,subject.last_original,queued,request)
    return subject,emitter
