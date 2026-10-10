"""Actual front-side WLRY gates and ordered client forwarding.

The dedicated socket is a member of the original complete root role roster.
Frames, raw kernel channel credentials and sealed syscall reports are retained;
a transport EOF never authorizes release of the original requester escrow.
"""
from __future__ import annotations
import hashlib,threading
from .canonical import canonical_bytes
from .custody_subject_capture import actor_identity,socket_capture
from .root_worker_subject_transfer import role_socket_document
from .errors import WorldlineError
from .protected_startup import require
from .root_worker_subject_custody import AuthenticatedSubjectRelay


class FrontRelayEndpoint:
    def __init__(self,service):
        self.service=service;self.channel=service.relay_channel
        self.relay=AuthenticatedSubjectRelay(self.channel,service.owner.custody_journal.key,
            service.owner.source_lease.check())
        self.records=[];self.failure=None;self.stopping=False
        self.thread=threading.Thread(target=self.run,name='worldline-front-request-relay',daemon=True)
        self.thread.start()
    def _scope(self,escrow,body):
        from .root_worker_serving_peer import fact_capture
        with fact_capture():
            context=escrow.subject.journal.subject_context(escrow.subject.operation,'REQUEST',escrow.subject.subject,
                escrow.original,root_operation=escrow.subject.root_operation,kind='REQUEST_RESPONDED',
                actor_role=escrow.subject.actor_role,query_purpose='OUTPUT')
        binding=context['binding'];view=context['native_context']
        for name,value in (('generation',str(int.from_bytes(binding['generation'],'little'))),
            ('subgeneration',str(int.from_bytes(binding['subgeneration'],'little'))),
            ('reattach_epoch',str(int.from_bytes(view['reattach_epoch'],'little'))),
            ('request',escrow.subject.subject),('operation',escrow.subject.operation),
            ('admission_head',escrow.intake['event_id'])):
            require(body[name]==value,'CUSTODY_RELAY_ACTUAL_CURRENT_BINDING_CHANGED')
    def run(self):
        try:
            while not self.stopping:
                body,frame=self.relay.receive(0xffffffff)
                if body['type']=='INPUT_EOF_BARRIER':
                    self.stdin_eof_barrier(body,frame,self.relay.received[-1])
                    continue
                escrow=self.service.escrows[body['request']]
                escrow.relay_admitted.wait()
                self.service.owner.custody_journal.require_event(escrow.intake)
                self._scope(escrow,body)
                record={'body':body,'frame':frame,'receive':self.relay.received[-1]}
                self.records.append(record)
                if body['type']=='GATE_REQUEST':self.gate(escrow,body,record)
                elif body['type'] in ('PROGRESS_BYTES','RESPONSE_BYTES'):self.output(escrow,body,record)
                elif body['type']=='PEER_HELD':self.peer_status(escrow,body,record)
                else:require(False,'CUSTODY_RELAY_ACTUAL_MESSAGE_KIND_REQUIRED')
        except BaseException as error:
            self.failure=error
            self.records.append({'failure':{'class':type(error).__name__,'message':str(error),
                'errno':getattr(error,'errno',None)},'stopping':self.stopping})
            self.service.message_reader_failed(error)
    def stdin_eof_barrier(self,body,frame,received):
        from .root_worker_subject_service import _receive_message
        packet,raw,sender=_receive_message(self.channel,self.service.owner.source_lease.check(),
            self.service.relay_receive_receipts)
        require(packet['kind']=='INPUT_EOF_BARRIER_SOURCE' and packet['request']==body['payload']
            and packet['frame']==frame and packet['body']==body,'CUSTODY_LIVE_AUTHENTIC_STDIN_BARRIER_REQUIRED')
        self.service.observe_stdin_barrier('RELAY',body['payload'],{'body':body,'frame':frame,
            'receive':received,'packet':packet,'raw':raw,'sender':sender,
            'report_receive':self.service.relay_receive_receipts[-1]})
    def gate(self,escrow,body,record):
        from .root_worker_subject_service import _send_message,_message
        from .root_worker_subject_service import _receive_message
        from .root_worker_subject_sync import receive_current
        packet,raw,sender=_receive_message(self.channel,self.service.owner.source_lease.check(),
            self.service.relay_receive_receipts)
        require(packet['kind']=='GATE_SOURCE','CUSTODY_RELAY_ACTUAL_GATE_SOURCE_REQUIRED')
        receive_current(self.service,self.channel,packet,raw,sender,self.service.relay_receive_receipts)
        record.update(source_packet=packet,source_raw=raw,source_sender=sender)
        from .client_peer import peer_read_source
        from .root_worker_codec import raw_archive
        source=self.service.owner.source_lease.check();front=None;error=None;failure=None
        start=len(escrow.peer.peer.read_receipts)
        try:
            with peer_read_source(source):
                observation=escrow.peer.observation()
                front=socket_capture(escrow.peer.peer.descriptor(),source)
            payload={'observation':canonical_bytes(observation)}
        except (OSError,WorldlineError) as caught:
            error={'class':'OSError' if isinstance(caught,OSError) else 'WorldlineError',
                'code':caught.errno if isinstance(caught,OSError) else caught.code,
                'message':str(caught),'details':{} if isinstance(caught,OSError) else caught.details}
            failure={'source':source,'calls':tuple(escrow.peer.peer.read_receipts[start:]),'error':error,
                'close':escrow.peer.peer.close_receipt}
            observation=None;payload={'error':error}
        response=dict(body,type='GATE_RESPONSE',payload=payload)
        response_frame=self.relay.send(response)
        channel=socket_capture(self.channel.fileno(),source)
        report={'front_socket':front,'channel':channel,'channel_document':role_socket_document(channel),
            'request_receive':record['receive'],'response_send':self.relay.sent[-1],
            'front_reread':observation,'reread_error':None if error is None else raw_archive(error),
            'reread_failure':failure}
        record.update(response=response,response_frame=response_frame,report=report)
        _send_message(self.channel,_message('GATE_REPORT',report=report),source,self.service.relay_send_receipts)
    def output(self,escrow,body,record):
        from .root_worker_subject_service import _send_message,_receive_message,_message,_write_line
        sequence=body['payload']['out_seq'];line=body['payload']['line']
        require(type(sequence) is str and sequence==str(int(sequence)) and int(sequence)>=0
            and type(line) is bytes and hashlib.sha256(line).hexdigest()==body['payload']['sha256'],
            'CUSTODY_RELAY_EXACT_OUTPUT_BYTES_REQUIRED')
        packet,raw,sender=_receive_message(self.channel,self.service.owner.source_lease.check(),
            self.service.relay_receive_receipts)
        require(packet['kind']=='OUTPUT_SOURCE','CUSTODY_RELAY_ACTUAL_OUTPUT_SOURCE_REQUIRED')
        record.update(source_packet=packet,source_raw=raw,source_sender=sender)
        from .root_worker_subject_sync import receive_current
        receive_current(self.service,self.channel,packet,raw,sender,self.service.relay_receive_receipts)
        escrow.output_pending.setdefault(sequence,[]).append(record)
        self.drain_outputs(escrow)
    def drain_outputs(self,escrow):
        from .root_worker_subject_service import _send_message,_message,_write_line
        from .root_worker_output_kernel import ReplayDisposition
        for sequence,pending in tuple(escrow.output_pending.items()):
            current=pending[0]
            decision=self.require_replay(escrow,current)
            if decision.disposition is ReplayDisposition.HOLD:continue
            if decision.disposition is ReplayDisposition.DROP:
                for duplicate in tuple(pending):
                    duplicate_decision=self.require_replay(escrow,duplicate)
                    if duplicate_decision.disposition is ReplayDisposition.DROP:
                        duplicate['native_drop']=duplicate['native_replay']
                        pending.remove(duplicate)
                if not pending:del escrow.output_pending[sequence]
                continue
            require(decision.disposition is ReplayDisposition.WRITE,'CUSTODY_RELAY_NATIVE_WRITE_REQUIRED')
            escrow.next_output=int.from_bytes(decision.ordinal,'little')
            current_body=current['body'];payload=current_body['payload'];writes=[]
            source=self.service.owner.source_lease.check()
            current['writes']=writes
            _write_line(escrow.peer,payload['line'],source,writes)
            acknowledgement=dict(current_body,type='RESPONSE_WRITTEN',payload={
                'out_seq':payload['out_seq'],'sha256':payload['sha256']})
            sent=self.relay.send(acknowledgement)
            channel=socket_capture(self.channel.fileno(),source)
            report={'body':acknowledgement,'frame':sent,'write':tuple(writes),'source':source,
                'native':self.service.native('ROOT_FRONT_AFTER_ACTUAL_RELAY_WRITE'),
                'actor':actor_identity(self.channel),
                'channel':channel,'channel_document':role_socket_document(channel),
                'front_socket':socket_capture(escrow.peer.peer.descriptor(),source),
                'output_receive':current['receive'],'written_send':self.relay.sent[-1]}
            from .scoped_capture_namespace_source import capture_actor_namespace
            report['sender_actor_namespace']=capture_actor_namespace(report['actor'],source)
            current['written']=report
            from .root_worker_codec import original_archive,raw_archive
            peerproof=dict(current['replay_candidate']['relay'],channel=current['source_packet']['worker_channel'],
                channel_document=current['source_packet']['worker_channel_document'],
                front_channel=channel,front_channel_document=role_socket_document(channel),
                request_frame=current['frame'],request_body=dict(current_body,payload=original_archive(current_body['payload'])),
                response_frame=sent,response_body=dict(acknowledgement,payload=original_archive(acknowledgement['payload'])),
                written_send=report['written_send'],writer_actor=report['actor'],
                writer_native=raw_archive(report['native']),worker_native=raw_archive(current['source_packet']['native']),
                worker_origin=current['source_packet']['worker_origin'])
            current['written_record']={'request':escrow.subject.subject,'admission_head':escrow.intake['event_id'],
                'type':'RESPONSE_WRITTEN','out_seq':payload['out_seq'],'sha256':payload['sha256'],
                'write':tuple(writes),'source':source,'scope':current['writer_scope'],
                'production_scope':current['source_packet']['candidate']['production_scope'],'relay':peerproof}
            _send_message(self.channel,_message('OUTPUT_WRITTEN_REPORT',report=report),source,
                self.service.relay_send_receipts)
            escrow.output_written.append(current)
            pending.remove(current)
            if not pending:del escrow.output_pending[sequence]
    def require_replay(self,escrow,record):
        from .root_worker_codec import original_archive,raw_archive
        packet=record['source_packet'];context=escrow.subject.journal.subject_context(
            escrow.subject.operation,'REQUEST',escrow.subject.subject,escrow.original,
            root_operation=escrow.subject.root_operation,kind='REQUEST_RESPONDED',
            actor_role=escrow.subject.actor_role,query_purpose='OUTPUT')
        binding=context['binding'];view=context['native_context'];source=self.service.owner.source_lease.check()
        scope={'generation':binding['generation'],'root_operation':view['root']['operation'],
            'operation':escrow.subject.operation,'request':escrow.subject.subject,
            'subgeneration':binding['subgeneration'],'reattach_epoch':view['reattach_epoch']}
        channel=socket_capture(self.channel.fileno(),source)
        candidate=dict(packet['candidate'],source=source,scope=scope,relay={
            'frame':record['frame'],'body':dict(record['body'],payload=original_archive(record['body']['payload'])),
            'channel':channel,'channel_document':role_socket_document(channel),
            'front_socket':socket_capture(escrow.peer.peer.descriptor(),source),
            'output_send':packet['send'],'output_receive':record['receive'],
            'report_raw':record['source_raw'],'report_sender':record['source_sender'],
            'worker_channel':packet['worker_channel'],'worker_channel_document':packet['worker_channel_document'],
            'worker_actor':packet['actor'],'worker_origin':packet['worker_origin'],
            'worker_native':raw_archive(packet['native']),
            'channel_duplicate':packet['channel_duplicate']})
        from .scoped_capture_namespace_source import namespace_source
        candidate['relay']['relay_namespace_source']=namespace_source(self.service.owner,
            self.service.owner._retained_owned_roster,actor_identity(self.channel),
            sender_actor_namespace=packet['root_sync']['frame']['sender_actor_namespace'])
        record['writer_scope']=scope;record['replay_candidate']=candidate
        decision=escrow.subject.output_replay(escrow.original,packet['records'],candidate,
            profile=escrow.intake['retained_record']['x5']['subject_evidence'],
            native=self.service.native('ROOT_FRONT_BEFORE_RELAY_FORWARD'))
        require(str(int.from_bytes(decision.ordinal,'little'))==record['body']['payload']['out_seq'],
            'CUSTODY_RELAY_NATIVE_RESERVED_OUTPUT_ORDINAL_CHANGED')
        record['native_replay']={'ordinal':decision.ordinal,'disposition':decision.disposition.name}
        return decision
    def peer_status(self,escrow,body,record):
        from .root_worker_subject_service import _send_message,_message
        from .root_worker_subject_service import _receive_message
        from .root_worker_subject_sync import receive_current
        packet,raw,sender=_receive_message(self.channel,self.service.owner.source_lease.check(),
            self.service.relay_receive_receipts)
        require(packet['kind']=='PEER_HELD_SOURCE','CUSTODY_RELAY_ACTUAL_PEER_HELD_SOURCE_REQUIRED')
        receive_current(self.service,self.channel,packet,raw,sender,self.service.relay_receive_receipts)
        record.update(source_packet=packet,source_raw=raw,source_sender=sender)
        self.drain_outputs(escrow)
        from .root_worker_serving_peer import fact_capture
        with fact_capture():
            context=escrow.subject.journal.subject_context(escrow.subject.operation,'REQUEST',
                escrow.subject.subject,escrow.original,root_operation=escrow.subject.root_operation,
                kind='REQUEST_RESPONDED',actor_role=escrow.subject.actor_role,query_purpose='OUTPUT')
        binding=context['binding'];view=context['native_context'];source=self.service.owner.source_lease.check()
        scope={'generation':binding['generation'],'root_operation':view['root']['operation'],
            'operation':escrow.subject.operation,'request':escrow.subject.subject,
            'subgeneration':binding['subgeneration'],'reattach_epoch':view['reattach_epoch']}
        written=tuple(item['written_record'] for item in escrow.output_written)
        candidate={'request':escrow.subject.subject,'admission_head':escrow.intake['event_id'],
            'type':'OUTPUT_PREFIX','source':source,'scope':scope,'written':written}
        native=self.service.native('ROOT_FRONT_BEFORE_AUTHENTIC_PEER_STATUS')
        quantity=escrow.subject.output_prefix(escrow.original,packet['records'],candidate,
            profile=escrow.intake['retained_record']['x5']['subject_evidence'],native=native)
        escrow.next_output=int.from_bytes(quantity,'little')
        record['prefix_query']={'candidate':candidate,'quantity':quantity,'native':native}
        response=dict(body,type='PEER_STATUS',sequence=str(escrow.next_output),
            payload={'next_out_seq':str(escrow.next_output)})
        frame=self.relay.send(response);channel=socket_capture(self.channel.fileno(),source)
        report={'body':response,'frame':frame,'native':self.service.native('ROOT_FRONT_PEER_STATUS'),
            'actor':actor_identity(self.channel),'source':source,'channel':channel,
            'channel_document':role_socket_document(channel),'written':written,
            'request_receive':record['receive'],'peer_status_send':self.relay.sent[-1]}
        from .scoped_capture_namespace_source import capture_actor_namespace
        report['sender_actor_namespace']=capture_actor_namespace(report['actor'],source)
        record['report']=report
        _send_message(self.channel,_message('PEER_STATUS_REPORT',report=report),source,
            self.service.relay_send_receipts)
