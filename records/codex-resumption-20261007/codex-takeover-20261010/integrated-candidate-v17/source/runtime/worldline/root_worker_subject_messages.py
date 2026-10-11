"""Actual sole sealed-message reader; source-rights intake precedes delivery."""
from __future__ import annotations
from collections import deque
import threading


class SubjectMessageReader:
    def __init__(self,service,channel,receipts):
        self.service,self.channel,self.receipts=service,channel,receipts
        self.condition=threading.Condition();self.messages=deque();self.retained=[];self.failure=None
        self.thread=threading.Thread(target=self.run,name='worldline-subject-sealed-reader',daemon=True)
        self.thread.start()
    def take(self):
        with self.condition:
            while not self.messages and self.failure is None:self.condition.wait()
            if self.messages:return self.messages.popleft()
            raise self.failure
    def run(self):
        from .root_worker_subject_service import _receive_message
        try:
            while True:
                value,raw,sender=_receive_message(self.channel,self.service.owner.source_lease.check(),self.receipts)
                transport={'value':value,'raw':raw,'sender':sender,'receive':self.receipts[-1]}
                self.retained.append(transport)
                if 'root_sync' in value:
                    from .root_worker_subject_sync import receive_current
                    receive_current(self.service,self.channel,value,raw,sender,self.receipts)
                if self.service.observe_service_control(value,transport):continue
                with self.condition:
                    self.messages.append((value,raw,sender));self.condition.notify_all()
        except BaseException as error:
            with self.condition:
                self.failure=error;self.condition.notify_all()
            self.service.message_reader_failed(error)


class WorkerSubjectMessageReader:
    """Receive complete original FD groups independently of handler progress."""
    def __init__(self,service):
        self.service=service;self.channel=service.channel
        self.condition=threading.Condition();self.messages=deque();self.retained=[];self.failure=None
        self.thread=threading.Thread(target=self.run,name='worldline-worker-subject-sealed-reader',daemon=True)
        self.thread.start()
    def take(self):
        with self.condition:
            while not self.messages and self.failure is None:self.condition.wait()
            if self.messages:return self.messages.popleft()
            raise self.failure
    def receive_role(self,delivery,role):
        from .root_worker_custody import _receive_fd
        from .protected_startup import require
        source=self.service.owner.source_lease.check()
        fd,sender=_receive_fd(self.channel,delivery['receipts'],source)
        delivery['fds'][role]=fd
        delivery['role_receipts'][role]=delivery['receipts'][-1]
        require(sender==delivery['sender'],'CUSTODY_LIVE_DESCRIPTOR_SENDER_CHANGED')
    def run(self):
        from .root_worker_subject_service import _receive_message
        from .protected_startup import require
        try:
            while True:
                receipts=[]
                value,raw,sender=_receive_message(self.channel,self.service.owner.source_lease.check(),receipts)
                delivery={'message':value,'raw':raw,'sender':sender,'header_receive':receipts[-1],
                    'fds':{},'receipts':[],'role_receipts':{},'transcript':None,
                    'transcript_raw':None,'transcript_sender':None,'transcript_receipts':[],'roster':None}
                self.retained.append(delivery)
                kind=value['kind']
                if kind=='INPUT_EOF_FRONT_BARRIER':
                    self.service.observe_front_stdin_barrier(value['request'],delivery)
                    continue
                if kind=='PREPARE':
                    self.receive_role(delivery,'request')
                elif kind in ('REQUEST','DRAINS'):
                    packet=value['packet']
                    roles=packet['transfer']['roster'] if kind=='REQUEST' else packet['roles']
                    for role in roles:self.receive_role(delivery,role['role'])
                    transcript,transcript_raw,transcript_sender=_receive_message(
                        self.channel,self.service.owner.source_lease.check(),delivery['transcript_receipts'])
                    require(transcript['kind']=='SEND_TRANSCRIPT' and transcript_sender==sender,
                        'CUSTODY_LIVE_FULL_AUTHENTIC_TRANSCRIPT_REQUIRED')
                    delivery.update(transcript=transcript,transcript_raw=transcript_raw,
                        transcript_sender=transcript_sender)
                    if kind=='REQUEST':
                        from .root_owned_descriptor_roster import adopt_subject_role_receipts
                        delivery['roster']=adopt_subject_role_receipts(self.service.owner,
                            packet['transfer']['original_frame'],delivery['fds'],
                            delivery['role_receipts'],sender,transcript,
                            sender_role_roster=packet['transfer']['roles'])
                    from .custody_subject_capture import role_roster
                    import os
                    delivery['received_roles']=role_roster(roles,delivery['fds'],
                        self.service.owner.source_lease.check(),worker_pid=os.getpid())
                with self.condition:
                    self.messages.append(delivery);self.condition.notify_all()
        except BaseException as error:
            with self.condition:
                self.failure=error;self.condition.notify_all()
            self.service.front_stdin_reader_failed(error)
