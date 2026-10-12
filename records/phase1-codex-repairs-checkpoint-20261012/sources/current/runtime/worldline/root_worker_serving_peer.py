"""Actual post-intake requester types, with native correspondence at each use."""
from __future__ import annotations
from contextlib import contextmanager
from contextvars import ContextVar
import inspect,json,secrets,threading
from .canonical import canonical_bytes
from .client_peer import RequestPeer,validate_observation,peer_read_source
from .errors import WorldlineError
from .root_worker_codec import raw_archive
from .custody_subject_capture import socket_capture
from .protected_startup import require

_FACT_CAPTURE=ContextVar('worldline_custody_request_fact_capture',default=False)

@contextmanager
def fact_capture():
    """Fact-only recursive capture; this scope must never invoke an effect."""
    token=_FACT_CAPTURE.set(True)
    try:yield
    finally:_FACT_CAPTURE.reset(token)


def _caller():
    frame=inspect.currentframe()
    try:
        caller=frame.f_back.f_back
        return caller.f_code.co_filename+':'+caller.f_code.co_qualname
    finally:del frame


class CrosswalkRequestPeer:
    custody_mode='FRESH'
    def __init__(self,actual,subject,original,transfer,front_socket,service,*,subject_roster,admission_native,admission=None,history=None,native_history=None,lock=None):
        require(type(actual) is RequestPeer,'CUSTODY_SERVING_ACTUAL_RECEIVED_PEER_REQUIRED')
        self.admission=subject.last_event if admission is None else admission
        service.owner.custody_journal.require_event(self.admission)
        require(self.admission['kind']=='REQUEST_INTAKE','CUSTODY_SERVING_NATIVE_INTAKE_REQUIRED')
        self.actual=actual;self.peer=actual.peer;self.subject=subject;self.original=original
        self.transfer=transfer;self.front_socket=front_socket;self.service=service
        self.subject_roster=subject_roster
        self.admission_native=admission_native
        self.gates=[] if history is None else history
        self.native_history=[] if native_history is None else native_history
        self.lock=threading.RLock() if lock is None else lock
    def raw_observation(self):return self.actual.observation()
    def observation(self):
        with self.lock:
            if _FACT_CAPTURE.get():return self.raw_observation()
            source=self.service.owner.source_lease.check();start=len(self.peer.read_receipts)
            try:
                with peer_read_source(source):
                    document=self.raw_observation()
                    worker_socket=socket_capture(self.peer.descriptor(),source)
            except (OSError,WorldlineError) as error:
                detail={'class':'OSError' if isinstance(error,OSError) else 'WorldlineError',
                    'code':error.errno if isinstance(error,OSError) else error.code,
                    'message':str(error),'details':{} if isinstance(error,OSError) else error.details}
                self.gates.append({'mode':'FRESH','gate':_caller(),'front_socket':self.front_socket,
                    'worker_socket':None,'transfer':self.transfer,'history':tuple(self.gates),
                    'reread_error':raw_archive(detail),'reread_failure':{
                        'source':source,'calls':tuple(self.peer.read_receipts[start:]),'error':detail,
                        'close':self.peer.close_receipt}})
                raise
            native=self.service.native('ROOT_WORKER_FRESH_SERVING_GATE',subject_roster=self.subject_roster)
            transfer=dict(self.transfer,current_inventory=raw_archive(native[0]['provenance']['subject_capture']['inventory']))
            gate={'mode':'FRESH','gate':_caller(),'front_socket':self.front_socket,
                'worker_socket':worker_socket,
                'transfer':transfer,'history':tuple(self.gates)}
            historical=self.admission_native+tuple(item for captured in self.native_history for item in captured)
            self.subject.serve_gate(self.original,gate,native=historical+native)
            self.gates.append(gate)
            self.native_history.append(native)
            return document
    def worker_observation(self):return self.actual.worker_observation()
    def retained_gates(self):
        with self.lock:
            return tuple(self.gates),self.admission_native+tuple(item for captured in self.native_history for item in captured)
    def duplicate(self):
        actual=self.actual.duplicate()
        retained=CrosswalkRequestPeer(actual,self.subject,self.original,self.transfer,self.front_socket,
            self.service,subject_roster=self.subject_roster,admission_native=self.admission_native,
            admission=self.admission,history=self.gates,native_history=self.native_history,lock=self.lock)
        self.service.request_holders.append(retained)
        return retained
    def close(self):
        with peer_read_source(self.service.owner.source_lease.check()):self.actual.close()


class RelayRequestPeer:
    custody_mode='RELAY'
    def __init__(self,subject,original,service,admission):
        service.owner.custody_journal.require_event(admission)
        require(admission['kind']=='REQUEST_INTAKE','CUSTODY_SERVING_NATIVE_INTAKE_REQUIRED')
        self.subject=subject;self.original=original;self.service=service;self.admission=admission
        self.gates=[];self.lock=threading.RLock();self._closed=False;self.holders=[self];self.close_records=[]
        validate_observation(original['original_request'])
    def raw_observation(self):return json.loads(canonical_bytes(self.original['original_request']))
    def observation(self):
        if _FACT_CAPTURE.get():return self.raw_observation()
        with self.lock:
            require(not self._closed,'CUSTODY_RELAY_REQUEST_CLOSED')
            with fact_capture():
                context=self.subject.journal.subject_context(self.subject.operation,'REQUEST',self.subject.subject,
                    self.original,root_operation=self.subject.root_operation,
                    kind='REQUEST_RESPONDED',actor_role=self.subject.actor_role,query_purpose='OUTPUT')
            binding=context['binding'];view=context['native_context']
            # This is the ordinal of actual recorded gate uses, not a lifecycle
            # generation, reservation, charge or reattach quantity calculation.
            body={'type':'GATE_REQUEST','generation':str(int.from_bytes(binding['generation'],'little')),
                'reattach_epoch':str(int.from_bytes(view['reattach_epoch'],'little')),
                'request':self.subject.subject,'subgeneration':str(int.from_bytes(binding['subgeneration'],'little')),
                'operation':self.subject.operation,'gate':_caller(),'sequence':str(len(self.gates)+1),
                'nonce':secrets.token_hex(32),'admission_head':self.admission['event_id'],'payload':{}}
            ticket=self.service.transmit_relay(body,'GATE_SOURCE',
                {'channel_duplicate':self.service.duplicate_receipts['relay_service']},
                reply_kind='GATE_RESPONSE')
            reply=self.service.relay_replies.wait(ticket)
            frame=ticket['frame'];response,response_frame=reply['body'],reply['frame']
            for name in ('generation','reattach_epoch','request','subgeneration','operation','gate',
                         'sequence','nonce','admission_head'):
                require(response[name]==body[name],'CUSTODY_RELAY_GATE_BINDING_CHANGED')
            require(response['type']=='GATE_RESPONSE','CUSTODY_RELAY_GATE_RESPONSE_REQUIRED')
            report=dict(reply['packet']['report'],report_raw=reply['raw'],report_sender=reply['sender'],
                report_receive=reply['report_receive'])
            gate=self.service.relay.profile(frame,body,response_frame,response)
            gate.update(mode='RELAY',history=tuple(self.gates),front_socket=report['front_socket'],
                front_channel=report['channel'],front_channel_document=report['channel_document'],
                request_send=ticket['send'],response_receive=reply['receive'],
                request_receive=report['request_receive'],response_send=report['response_send'],
                front_reread=report['front_reread'],reread_error=report['reread_error'],
                reread_failure=report['reread_failure'])
            self.gates.append(gate)
            payload=response['payload']
            if 'error' in payload:
                error=payload['error']
                from .errors import WorldlineError
                if error['class']=='OSError':raise OSError(error['code'],error['message'])
                if error['class']=='WorldlineError':raise WorldlineError(error['code'],error['message'],error['details'])
                require(False,'CUSTODY_RELAY_UNKNOWN_REREAD_ERROR_CLASS')
            document=json.loads(payload['observation'])
            validate_observation(document)
            self.subject.serve_gate(self.original,gate,native=self.service.native('ROOT_WORKER_RELAY_SERVING_GATE'))
            return document
    def duplicate(self):
        with self.lock:
            require(not self._closed,'CUSTODY_RELAY_REQUEST_CLOSED')
            retained=RelayRequestPeer(self.subject,self.original,self.service,self.admission)
            retained.gates=self.gates;retained.lock=self.lock;retained.holders=self.holders
            retained.close_records=self.close_records
            self.holders.append(retained);self.service.request_holders.append(retained)
            return retained
    def close(self):
        with self.lock:
            if self._closed:return
            self._closed=True
            self.close_records.append({'holder':self.holders.index(self),
                'source':self.service.owner.source_lease.check()})


def require_selected_peer(request,record):
    """Check actual construction/retention identity, never confer serving permission."""
    actual=record['peer'];service=actual.service;admission=record['intake']
    service.owner.custody_journal.require_event(admission)
    mode=admission['retained_record']['x5']['subject_evidence']['transfer']['mode']
    selected={'FRESH':CrosswalkRequestPeer,'RELAY':RelayRequestPeer}[mode]
    require(type(request) is selected and request.subject is record['subject']
        and request.service is service and request.admission is admission
        and (request is actual or any(holder is request for holder in service.request_holders)),
        'CUSTODY_SERVING_ACTUAL_SELECTED_RETAINED_PEER_REQUIRED')
    return request
