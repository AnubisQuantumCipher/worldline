"""Lossless request/descriptor effects and authentic X5 subject transcripts.

The journal's native context supplies quantities, prior heads and full native
operation observations. This producer supplies only operations that happened.
Unknown send/receive/ACK outcomes keep original escrow and never imply closure.
"""
from __future__ import annotations
import asyncio,hashlib,hmac,os,socket,struct
from .canonical import canonical_bytes
from .client_peer import RequestPeer
from .root_worker_codec import original_archive,original_restore,raw_archive
from .custody_subject_capture import socket_capture,close_descriptor
from .protected_startup import require

class SubjectCustody:
    def __init__(self,owner,operation,subject_kind,subject,*,root_operation=None):
        require(subject_kind in ('REQUEST','DESCRIPTOR') and type(subject) is str and subject,
            'ROOT_CUSTODY_ACTUAL_SUBJECT_REQUIRED')
        self.owner=owner;self.journal=owner.custody_journal
        self.operation=operation;self.subject_kind=subject_kind;self.subject=subject
        self.last_profile=None;self.last_original=None;self.last_event=None
        from .protected_root_worker import RootWorkerFront,RootWorkerProcess,RootWorkerSlot
        require(type(owner) in (RootWorkerFront,RootWorkerProcess),'ROOT_CUSTODY_ACTUAL_SUBJECT_OWNER_REQUIRED')
        self.actor_role='FRONT' if type(owner) is RootWorkerFront else 'WORKER'
        if type(owner) is RootWorkerProcess:
            require(root_operation is None or root_operation==owner.operation,'ROOT_CUSTODY_ROOT_OWNER_CHANGED')
            self.root_operation=owner.operation
        else:
            if root_operation is None:
                self.root_operation=None
            else:
                slot=owner.slots.get(root_operation)
                require(type(slot) is RootWorkerSlot and slot.front is owner,'ROOT_CUSTODY_ACTUAL_ROOT_SLOT_REQUIRED')
                self.root_operation=slot.operation
    def append(self,kind,original,*,native=(),_control_sql_probe=None,**operands):
        context=self.journal.subject_context(self.operation,self.subject_kind,self.subject,original,
            root_operation=self.root_operation,kind=kind,actor_role=self.actor_role)
        context['binding']['original']=raw_archive(original)
        profile={'schema':'worldline.custody-subject-raw-v1','binding':context['binding'],
            'request':None,'front_socket':None,'worker_socket':None,'transfer':None,
            'relay':None,'descriptor':None,'spool':None,'ofd':None,'close':None,'response':None}
        profile.update(operands)
        evidence={key:value for key,value in context.items() if key!='binding'}
        evidence['subject_evidence']=profile
        evidence['actor_role']=self.actor_role
        evidence['native_observations']=tuple(context['native_observations'])+tuple(native)
        primitives={'reattach_epoch':None,'position':None,'next_subgeneration':None,
            'transfer_mode':None,'abort_class':None,'unknown_cause':None}
        primitives.update(context['primitive_inputs'])
        if profile['transfer'] is not None:primitives['transfer_mode']=profile['transfer']['mode']
        if kind=='DRAIN_FREEZE':primitives['position']=profile['spool']['position']
        evidence['primitive_inputs']=primitives
        event=self.journal.append(self.operation,kind,original,subject_kind=self.subject_kind,
            subject=self.subject,evidence=evidence,
            **({} if _control_sql_probe is None else {'_control_sql_probe':_control_sql_probe}))
        self.last_profile,self.last_original,self.last_event=profile,original,event
        return event
    def serve_gate(self,original,gate,*,native):
        from .root_worker_serving_peer import fact_capture
        with fact_capture():
            context=self.journal.subject_context(self.operation,self.subject_kind,self.subject,original,
                root_operation=self.root_operation,kind='REQUEST_RESPONDED',actor_role=self.actor_role,
                query_purpose='SERVING')
            context['binding']['original']=raw_archive(original)
            profile={'schema':'worldline.custody-subject-raw-v1','binding':context['binding'],
                'request':original['original_request'],'front_socket':None,'worker_socket':None,
                'transfer':None,'relay':None,'descriptor':None,'spool':None,'ofd':None,
                'close':None,'response':None,'serving_gate':gate}
            evidence={key:value for key,value in context.items() if key!='binding'}
            evidence.update(subject_evidence=profile,actor_role=self.actor_role,
                native_observations=tuple(context['native_observations'])+tuple(native))
        return self.journal.serve_subject(self.operation,original,subject_kind=self.subject_kind,
            subject=self.subject,evidence=evidence)
    def _output_observation(self,query,original,records,candidate,*,profile,native):
        from .root_worker_serving_peer import fact_capture
        with fact_capture():
            context=self.journal.subject_context(self.operation,self.subject_kind,self.subject,original,
                root_operation=self.root_operation,kind='REQUEST_RESPONDED',actor_role=self.actor_role,
                query_purpose='OUTPUT')
            context['binding']['original']=raw_archive(original)
            profile=dict(profile,binding=context['binding'])
            evidence={key:value for key,value in context.items() if key!='binding'}
            evidence.update(subject_evidence=profile,actor_role=self.actor_role,
                native_observations=tuple(context['native_observations'])+tuple(native),
                emitter={'records':original_archive(records).hex(),'candidate':original_archive(candidate).hex()})
            return query(self.operation,original,subject=self.subject,evidence=evidence)
    def output_prefix(self,original,records,candidate,*,profile,native):
        return self._output_observation(self.journal.output_prefix,original,records,candidate,
            profile=profile,native=native)
    def output_quantity(self,original,records,candidate,*,profile,native):
        return self._output_observation(self.journal.output_quantity,original,records,candidate,
            profile=profile,native=native)
    def output_replay(self,original,records,candidate,*,profile,native):
        return self._output_observation(self.journal.output_replay,original,records,candidate,
            profile=profile,native=native)
    def output_written(self,original,records,candidate,*,profile,native):
        return self._output_observation(self.journal.output_written,original,records,candidate,
            profile=profile,native=native)
    def request_queued(self,request,socket_roster):
        require(type(request) is RequestPeer,'ROOT_CUSTODY_ACTUAL_REQUEST_PEER_REQUIRED')
        document=request.observation();source=self.owner.source_lease.check()
        original={'original_request':document,'socket_roster':socket_roster}
        from .custody_stale_control import probe_request
        probe_request(self,request,socket_roster)
        return self.append('REQUEST_QUEUED',original,request=document,
            front_socket=socket_capture(request.peer.descriptor(),source))
    def request_transfer_intent(self,original,front_socket,transfer,relay=None):
        return self.append('REQUEST_TRANSFER_INTENT',original,request=original['original_request'],
            front_socket=front_socket,transfer=transfer,relay=relay)
    def request_intake(self,original,front_socket,worker_socket,transfer,relay=None,*,native=()):
        return self.append('REQUEST_INTAKE',original,native=native,request=original['original_request'],
            front_socket=front_socket,worker_socket=worker_socket,transfer=transfer,relay=relay)
    def abandon_request(self):
        require(self.last_profile is not None,'ROOT_CUSTODY_REQUEST_HISTORY_REQUIRED')
        profile=self.last_profile
        return self.append('REQUEST_ABANDON',self.last_original,request=profile['request'],
            front_socket=profile['front_socket'],worker_socket=profile['worker_socket'],
            transfer=profile['transfer'],relay=profile['relay'])
    def respond(self,original,response,line,relay=None,relay_body=None,*,send=None,native=(),gates=(),out_seq=None):
        require(type(line) is bytes and line==canonical_bytes(response)+b'\n',
            'ROOT_CUSTODY_EXACT_RESPONSE_BYTES_REQUIRED')
        original=dict(original);original['response']=response
        return self.append('REQUEST_RESPONDED',original,native=native,request=original['original_request'],
            response={'bytes':line,'sha256':hashlib.sha256(line).hexdigest(),'blob':line,
                'original':response,'relay':relay,'relay_body':relay_body,'send':send,
                'gates':gates,'out_seq':out_seq})
    def drain_stop(self,original,descriptor,spool):
        return self.append('DRAIN_STOP_INTENT',original,descriptor=descriptor,spool=spool)
    def drain_freeze(self,original,descriptor,spool):
        return self.append('DRAIN_FREEZE',original,descriptor=descriptor,spool=spool)
    def drain_ofd_evidence(self,original,descriptor,transfer,ofd):
        return self.append('DRAIN_OFD_EVIDENCE',original,descriptor=descriptor,transfer=transfer,ofd=ofd)
    def drain_intake(self,original,descriptor,ofd,*,native=()):
        return self.append('DRAIN_INTAKE',original,native=native,descriptor=descriptor,ofd=ofd)
    def drain_abandon(self,original,descriptor):
        return self.append('DRAIN_ABANDON',original,descriptor=descriptor)
    def drain_release(self,original,descriptor):
        receipt=close_descriptor(descriptor['fd'],self.owner.source_lease.check())
        self.last_close_receipt=receipt
        require(receipt['result']==0 and receipt['readback']['result']==-1
            and receipt['readback']['errno']==9,'ROOT_CUSTODY_DESCRIPTOR_CLOSE_AMBIGUOUS')
        return self.append('DRAIN_RELEASED',original,descriptor=descriptor,close=receipt)
    def worker_gone(self,kind,original,root_evidence,descriptor=None):
        # The SAME complete E-CR root worker-gone transcript is consumed by X5.
        require(kind in ('REQUEST_LOST','DRAIN_RECLAIMED'),'ROOT_CUSTODY_WORKER_GONE_EVENT_REQUIRED')
        from .protected_root_worker import RootWorkerFront
        require(type(self.owner) is RootWorkerFront
            and asyncio.current_task() in self.owner.collectors.values(),
            'ROOT_CUSTODY_ACTUAL_CLOSED_COLLECTOR_REQUIRED')
        context=self.journal.subject_context(self.operation,self.subject_kind,self.subject,original,
            root_operation=self.root_operation,kind=kind,actor_role='COLLECTOR',query_purpose='CLEANUP')
        context['binding']['original']=raw_archive(original)
        profile={'schema':'worldline.custody-subject-raw-v1','binding':context['binding'],
            'request':original['original_request'] if self.subject_kind=='REQUEST' else None,
            'front_socket':None,'worker_socket':None,'transfer':None,'relay':None,
            'descriptor':descriptor,'spool':None,'ofd':None,'close':None,'response':None}
        evidence={key:value for key,value in context.items() if key!='binding'}
        evidence['actor_role']='COLLECTOR'
        evidence.update(subject_evidence=profile,root_evidence=root_evidence)
        return self.journal.cleanup_subject(self.operation,kind,original,subject_kind=self.subject_kind,
            subject=self.subject,evidence=evidence)

class AuthenticatedSubjectRelay:
    """Actual WLRY request/reply exchange; no Python gate verdict or FD alias."""
    DOMAIN=b'worldline.root-worker-relay-v1\0'
    def __init__(self,channel,key,source):
        require(type(channel) is socket.socket and type(key) is bytes and key,
            'ROOT_CUSTODY_AUTHENTIC_RELAY_CHANNEL_REQUIRED')
        self.channel,self.key,self.source=channel,key,source
        self.sent=[];self.received=[];self.used=set()
    def frame(self,body):
        payload=original_archive(body)
        prefix=b'WLRY'+struct.pack('!I',len(payload))+payload
        return prefix+hmac.new(self.key,self.DOMAIN+prefix,hashlib.sha256).digest()
    def send(self,body):
        nonce=(body['type'],body['nonce']);require(nonce not in self.used,'ROOT_CUSTODY_RELAY_NONCE_REPLAY')
        raw=self.frame(body);position=0;parts=[]
        receipt={'fd':self.channel.fileno(),'frame':raw,'body':body,'parts':parts,
            'source':self.source,'result':0,'errno':0}
        self.sent.append(receipt)
        while position<len(raw):
            offered=raw[position:]
            try:sent=self.channel.send(offered,socket.MSG_NOSIGNAL)
            except OSError as error:
                parts.append({'call':'send','args':{'fd':self.channel.fileno(),'flags':socket.MSG_NOSIGNAL,'body':offered},
                    'fd':self.channel.fileno(),'raw':None,'result':-1,'errno':error.errno,'source':self.source})
                receipt.update(result=-1,errno=error.errno);raise
            parts.append({'call':'send','args':{'fd':self.channel.fileno(),'flags':socket.MSG_NOSIGNAL,'body':offered},
                'fd':self.channel.fileno(),'raw':offered[:sent],'result':sent,'errno':0,'source':self.source})
            require(sent>0,'ROOT_CUSTODY_RELAY_SEND_UNKNOWN');position+=sent
        self.used.add(nonce);receipt['result']=position
        return raw
    def receive(self,frame_limit):
        parts=[]
        retained={'fd':self.channel.fileno(),'parts':parts,'source':self.source}
        self.received.append(retained)
        def exact(length):
            chunks=[];remaining=length
            while remaining:
                try:piece=self.channel.recv(remaining)
                except OSError as error:
                    parts.append({'call':'recv','args':{'fd':self.channel.fileno(),'flags':0,'maximum':remaining},
                        'fd':self.channel.fileno(),'raw':None,'result':-1,'errno':error.errno,'source':self.source})
                    retained.update(result=-1,errno=error.errno,
                        frame=b''.join(part['raw'] for part in parts if type(part['raw']) is bytes))
                    raise
                parts.append({'call':'recv','args':{'fd':self.channel.fileno(),'flags':0,'maximum':remaining},
                    'fd':self.channel.fileno(),'raw':piece,'result':len(piece),'errno':0,'source':self.source})
                require(piece,'ROOT_CUSTODY_RELAY_EOF_AMBIGUOUS');chunks.append(piece);remaining-=len(piece)
            return b''.join(chunks)
        try:
            header=exact(8);require(header[:4]==b'WLRY','ROOT_CUSTODY_RELAY_HEADER_REQUIRED')
            length=struct.unpack('!I',header[4:])[0]
            require(length<=frame_limit,'ROOT_CUSTODY_RELAY_FRAME_LIMIT')
            payload=exact(length);mac=exact(32);raw=header+payload+mac
            require(hmac.compare_digest(mac,hmac.new(self.key,self.DOMAIN+header+payload,hashlib.sha256).digest()),
                'ROOT_CUSTODY_RELAY_HMAC_CHANGED')
            body=original_restore(payload)
            nonce=(body['type'],body['nonce'])
            require(nonce not in self.used,'ROOT_CUSTODY_RELAY_NONCE_REPLAY')
            self.used.add(nonce);retained.update(frame=raw,body=body,result=len(raw),errno=0)
            return body,raw
        except BaseException as error:
            retained['frame']=b''.join(part['raw'] for part in parts if type(part['raw']) is bytes)
            retained['failure']={'class':type(error).__name__,'message':str(error),
                'code':getattr(error,'code',None),'errno':getattr(error,'errno',None),
                'details':getattr(error,'details',None)}
            raise
    def profile(self,request_frame,request_body,response_frame,response_body):
        channel=socket_capture(self.channel.fileno(),self.source)
        from .root_worker_subject_transfer import role_socket_document
        request_projection=dict(request_body,payload=original_archive(request_body['payload']))
        response_projection=dict(response_body,payload=original_archive(response_body['payload']))
        return {'channel':channel,'channel_document':role_socket_document(channel),
            'request_frame':request_frame,'request_body':request_projection,'response_frame':response_frame,
            'response_body':response_projection,'sequence':request_body['sequence'],'nonce':request_body['nonce'],
            'send_receipts':tuple(self.sent),'receive_receipts':tuple(self.received)}
