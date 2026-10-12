"""One actual reply reader, independent of retained outbound output reservations."""
from __future__ import annotations
import threading
from .protected_startup import require


class RelayReplyDispatcher:
    def __init__(self,service):
        self.service=service;self.condition=threading.Condition();self.pending={};self.receipts=[]
        self.failure=None
        self.thread=threading.Thread(target=self.run,name='worldline-worker-relay-replies',daemon=True)
        self.thread.start()
    def register(self,kind,body,*,output=None):
        key=(kind,body['nonce'])
        ticket={'kind':kind,'request':body,'output':output,'reply':None,'result':None,
            'complete':False,'failure':None}
        with self.condition:
            if self.failure is not None:raise self.failure
            require(key not in self.pending,'CUSTODY_RELAY_REPLY_NONCE_ALREADY_PENDING')
            self.pending[key]=ticket
        return ticket
    def wait(self,ticket):
        with self.condition:
            while not ticket['complete'] and ticket['failure'] is None and self.failure is None:
                self.condition.wait()
            error=ticket['failure'] or self.failure
            if error is not None:raise error
            return ticket['reply']
    def run(self):
        from .root_worker_subject_service import _receive_message
        kinds={'GATE_RESPONSE':'GATE_REPORT','RESPONSE_WRITTEN':'OUTPUT_WRITTEN_REPORT',
            'PEER_STATUS':'PEER_STATUS_REPORT'}
        try:
            while True:
                body,frame=self.service.relay.receive(0xffffffff)
                received=self.service.relay.received[-1]
                require(body['type'] in kinds,'CUSTODY_RELAY_ACTUAL_REPLY_KIND_REQUIRED')
                packet,raw,sender=_receive_message(self.service.relay_channel,
                    self.service.owner.source_lease.check(),self.service.relay_receive_receipts)
                reply={'body':body,'frame':frame,'receive':received,'packet':packet,'raw':raw,
                    'sender':sender,'report_receive':self.service.relay_receive_receipts[-1]}
                self.receipts.append(reply)
                require(packet['kind']==kinds[body['type']],'CUSTODY_RELAY_ACTUAL_REPLY_REPORT_REQUIRED')
                with self.condition:
                    ticket=self.pending[(body['type'],body['nonce'])]
                    require(not ticket['complete'],'CUSTODY_RELAY_REPLY_ALREADY_CONSUMED')
                    ticket['reply']=reply
                if body['type']=='RESPONSE_WRITTEN':
                    from .root_worker_serving_peer import fact_capture
                    with fact_capture():
                        ticket['result']=self.service.consume_written_reply(ticket,reply)
                with self.condition:
                    ticket['complete']=True;self.condition.notify_all()
        except BaseException as error:
            with self.condition:
                self.failure=error;self.condition.notify_all()
