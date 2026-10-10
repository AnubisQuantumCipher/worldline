"""Complete original chain Append guard and durable same-operation ACK recovery."""
from pathlib import Path
from .core import hash_bytes_from_id,hash_id
from .canonical import canonical_bytes
from .chain_authority import ChainRow,ChainAnchors,replay_chain
from .operation_owner_kernel import replay_owner_chain
from .protected_operations import current_scope,OperationScope,canonical_metadata,clone
from .protected_startup import require,exact_json
from .operation_capture import archive,restore_archive
from .protected_operations import identity

class CanonicalOperationChains:
    def __init__(self,principal):
        self.p=principal;self.store=principal.store;self.pending={};principal.canonical=self
    def rows(self,kind,material=None):
        if material is None:material=self.p.capture.chain_material()
        domain=b'worldline-receipt-record-v1' if kind=='receipts' else b'worldline-event-v1'
        result=[];witness=self.p.journal.body['chains'][kind]
        for sql,raw in material[kind]:
            require(type(raw) is bytes,'OPERATION_FULL_CANONICAL_BYTES_REQUIRED')
            root=self.p.core.hash_bytes(domain+raw)
            if kind=='receipts':
                predecessor=sql['previous_receipt']
                indexed={item['receipt_id']:item for item,_raw in material[kind]}
                from .store import CHAIN_GENESIS
                previous=CHAIN_GENESIS if predecessor is None else (None if predecessor not in indexed else hash_bytes_from_id(indexed[predecessor]['chain_hash']))
            else:previous=hash_bytes_from_id(sql['predecessor'])
            result.append(ChainRow(previous,root,hash_bytes_from_id(sql['receipt_root'] if kind=='receipts' else sql['event_root']),hash_bytes_from_id(sql['chain_hash'])))
        return result
    def replay(self,kind,rows,head):
        w=self.p.journal.body['chains'][kind]
        from .store import CHAIN_GENESIS
        return replay_owner_chain(self.p,rows,ChainAnchors('RECEIPT' if kind=='receipts' else 'CAUSAL',CHAIN_GENESIS,bytes.fromhex(w['genesis']),head))
    def preflight(self,kind,payload,root,previous,proposed):
        from .canonical_owner_witness import OwnerCanonicalScope
        if type(current_scope()) is OwnerCanonicalScope:
            return self.p.owner_witness.preflight(kind,payload,root,previous,proposed)
        metadata=canonical_metadata(self.store);require(metadata is not None,'OPERATION_CHAIN_ORIGINAL_REQUESTER_ABSENT')
        scope=current_scope();row=self.p.journal.rows[scope.operation]
        old=self.p.capture.chain_material();rows=self.rows(kind,old);head=bytes.fromhex(self.p.journal.body['chains'][kind]['head'])
        require(self.replay(kind,rows,head).disposition=='READY','OPERATION_PROTECTED_OLD_CHAIN_NATIVE_REFUSED')
        from .ordinary_receipt_policy import native_preflight_head
        require(native_preflight_head(kind,old,previous,core=self.p.core)=='READY','OPERATION_CHAIN_CAPTURE_PREDECESSOR_CHANGED')
        added=ChainRow(previous,root,root,proposed)
        native=self.replay(kind,[*rows,added],proposed)
        require(native.disposition=='READY','OPERATION_ORIGINAL_APPEND_NATIVE_REFUSED')
        boundary={'name':'CANONICAL_INTENT','kind':kind,'old_material':archive(old).hex(),'payload':canonical_bytes(payload).hex(),
            'root':root.hex(),'previous':previous.hex(),'head':native.head.hex(),'operation':scope.operation,'requester':metadata}
        self.p.journal.append(scope.operation,'ACK',row['capture'],snapshot=row['snapshot'],native=row['native'],boundaries=row['boundaries']+[boundary])
        self.pending[kind]=boundary
    def acknowledge(self,kind):
        from .canonical_owner_witness import OwnerCanonicalScope
        if type(current_scope()) is OwnerCanonicalScope:
            return self.p.owner_witness.acknowledge(kind)
        scope=current_scope();row=self.p.journal.rows[scope.operation]
        boundary=self.pending[kind];actual=self.p.capture.chain_material();before=clone(self._material(boundary))
        from .ordinary_receipt_policy import native_acknowledge
        native=native_acknowledge(kind,before,actual,bytes.fromhex(boundary['payload']),
            bytes.fromhex(boundary['head']),boundary['requester'],core=self.p.core)
        refusal={'COMPLETE_PREFIX_CHANGED':'OPERATION_CANONICAL_COMPLETE_PREFIX_OR_EXTENT_CHANGED',
            'ACTUAL_WRITE_MISMATCH':'OPERATION_CANONICAL_ACTUAL_WRITE_MISMATCH',
            'REQUESTER_MISMATCH':'OPERATION_CANONICAL_REQUESTER_MISMATCH'}.get(native,'OPERATION_CANONICAL_ACTUAL_APPEND_NATIVE_REFUSED')
        require(native=='READY',refusal)
        require(self.replay(kind,self.rows(kind,actual),bytes.fromhex(boundary['head'])).disposition=='READY','OPERATION_CANONICAL_ACTUAL_APPEND_NATIVE_REFUSED')
        ack={'name':'CANONICAL_ACK','kind':kind,'head':boundary['head'],'full_material':archive(actual).hex(),'intent':identity(boundary).hex()}
        self.p.journal.append(scope.operation,'ACK',row['capture'],snapshot=row['snapshot'],native=row['native'],boundaries=row['boundaries']+[ack])
        self.pending.pop(kind)
    @staticmethod
    def _material(boundary):
        from .operation_capture import restore_archive
        return restore_archive(bytes.fromhex(boundary['old_material']))
    def reconcile(self,operation):
        """Lost ACK recognizes the exact original full append; never appends twice.
        Before/partial states remain durable unknown until original owner diagnosis.
        """
        row=self.p.journal.rows[operation]
        acknowledged={b['intent'] for b in row['boundaries'] if b['name']=='CANONICAL_ACK'}
        for boundary in row['boundaries']:
            if boundary['name']!='CANONICAL_INTENT' or identity(boundary).hex() in acknowledged:continue
            self.pending[boundary['kind']]=boundary
            # Historical capture and actual native mapping are independently
            # redecided before installing a settlement-only scope.
            with self.p.historical_scope(operation):self.acknowledge(boundary['kind'])
    def operation_rows(self,kind):
        """Every full operation record remains in the authenticated history."""
        rows=[];raws=[];seen=set()
        for event in self.p.journal.body['events']:
            for boundary in event['boundaries']:
                key=identity(boundary).hex()
                if key in seen:continue
                seen.add(key)
                if boundary['name']!='OPERATION_CHAIN_ACK' or boundary['kind']!=kind:continue
                raw=bytes.fromhex(boundary['payload']);root=self.p.core.hash_bytes(self.operation_domain(kind)+raw)
                rows.append(ChainRow(bytes.fromhex(boundary['previous']),root,bytes.fromhex(boundary['root']),bytes.fromhex(boundary['head'])))
                raws.append(raw)
        return rows,raws
    @staticmethod
    def operation_domain(kind):
        return b'worldline-operation-use-receipt-v1\0' if kind=='operation_receipts' else b'worldline-operation-causal-v1\0'
    def operation_replay(self,kind,rows,head):
        w=self.p.journal.body['chains'][kind]
        return replay_owner_chain(self.p,rows,ChainAnchors('RECEIPT' if kind=='operation_receipts' else 'CAUSAL',
            bytes.fromhex(w['genesis']),bytes.fromhex(self.p.policy['chains'][kind]['genesis']),head))
    def append_operation_record(self,operation,kind,payload):
        # Full protected grant-use records are separate from the original
        # collapse-only SQL receipt table; no dummy transaction or world is made.
        self._verify_operation_payload(operation,kind,payload)
        row=self.p.journal.rows[operation];raw=canonical_bytes(payload)
        rows,raws=self.operation_rows(kind)
        matches=[value for value in raws if exact_json(value)['operation']==operation]
        if matches:
            require(self.operation_replay(kind,rows,bytes.fromhex(self.p.journal.body['chains'][kind]['head'])).disposition=='READY','OPERATION_RECORD_REPLAY_NATIVE_REFUSED')
            return
        head=bytes.fromhex(self.p.journal.body['chains'][kind]['head'])
        require(self.operation_replay(kind,rows,head).disposition=='READY','OPERATION_PRIOR_FULL_RECORD_NATIVE_REFUSED')
        root=self.p.core.hash_bytes(self.operation_domain(kind)+raw)
        proposed=self.p.core.receipt_link(head,root) if kind=='operation_receipts' else self.p.core.causal_link(head,root)
        native=self.operation_replay(kind,[*rows,ChainRow(head,root,root,proposed)],proposed)
        require(native.disposition=='READY','OPERATION_APPEND_FULL_NATIVE_REFUSED')
        intent={'name':'OPERATION_CHAIN_INTENT','kind':kind,'operation':operation,'payload':raw.hex(),
                'previous':head.hex(),'root':root.hex(),'head':native.head.hex()}
        pending=[value for value in row['boundaries'] if value['name']=='OPERATION_CHAIN_INTENT' and value['kind']==kind]
        if not pending:
            self.p.journal.append(operation,'ACK',row['capture'],snapshot=row['snapshot'],native=row['native'],boundaries=row['boundaries']+[intent])
        row=self.p.journal.rows[operation]
        ack={**intent,'name':'OPERATION_CHAIN_ACK','intent':identity(intent).hex()}
        # The independent head CAS commits complete canonical bytes and native
        # result together. A lost filesystem/DB ACK is reconciled by the complete
        # old/new retained envelope, never by redispatch or regenerated payload.
        self.p.journal.append(operation,'ACK',row['capture'],snapshot=row['snapshot'],native=row['native'],boundaries=row['boundaries']+[ack])
    def _candidate_operation_record(self,operation,kind,payload):
        rows,raws=self.operation_rows(kind)
        selected=[i for i,raw in enumerate(raws) if exact_json(raw)['operation']==operation]
        raw=canonical_bytes(payload)
        if selected:
            # Candidate selection only. Native complete-roster interpretation
            # rejects duplicates, changed captures and one-sided payloads.
            return rows,raws,rows[selected[0]].stored_head
        head=bytes.fromhex(self.p.journal.body['chains'][kind]['head'])
        root=self.p.core.hash_bytes(self.operation_domain(kind)+raw)
        proposed=self.p.core.receipt_link(head,root) if kind=='operation_receipts' else self.p.core.causal_link(head,root)
        return [*rows,ChainRow(head,root,root,proposed)],[*raws,raw],proposed
    def _source_material(self,capture,result_capture,metadata,current_store,current_transaction):
        from .ordinary_receipt_policy import retained_material
        from .recovery_observation import acquire_syntax_facts
        from .transaction_relation import recovery_packets, recovery_syntax_fact
        original=[value for value in self.p.journal.body['events']
                  if value['operation']==capture['operation'] and value['cause']=='RESERVED']
        require(bool(original),'OPERATION_ORIGINAL_RESERVATION_CAPTURE_ABSENT')
        source=original[0]
        row=self.p.journal.rows[capture['operation']]
        retained=[value for value in row['boundaries'] if value['name']=='RESULT_CAPTURE']
        material={'capture':clone(capture),'stored_capture':clone(row['capture']),
            'result':clone(result_capture),'stored_result':None if not retained else restore_archive(bytes.fromhex(retained[0]['value'])),
            'current_store':current_store,'current_transaction':current_transaction,
            'original_worldline_chains':clone(result_capture['actual_store']),
            'requester':clone(metadata),
            'original_snapshot':restore_archive(bytes.fromhex(source['snapshot'])),
            'original_observation':clone(source['native']['observation']),
            'original_intents':[clone(value) for value in row['boundaries'] if value['name']=='OPERATION_CHAIN_INTENT'],
            'commit_authority':[clone(value) for value in row['boundaries'] if value['name'] in
                ('FULL_PRE_EFFECT_BOUNDARY','FULL_BROKER_PREPARED','FULL_BROKER_NATIVE',
                 'FULL_BROKER_CANONICAL_INTENT','FULL_BROKER_OWNER_DISPOSITION',
                 'FULL_BROKER_WORKER_RESULT','FULL_BROKER_COMMITTED')],
            'reservation_preimage':{'operation':capture['operation'],'request':clone(capture['request']),
                                   'binding':clone(capture['binding'])}}
        # Original packets remain byte-for-byte frozen. Missing historical
        # syntax observations are acquired by the actual protected read-only
        # parser owner and carried separately; native code binds every capsule
        # to its original packet/source/context before using its syntax facts.
        for packet in recovery_packets(material['commit_authority'],
                                       result_capture['actual_transaction']):
            capsules = acquire_syntax_facts(packet, principal=self.p)
            if capsules:
                material['commit_authority'].append(recovery_syntax_fact(packet, capsules))
        material['store_views']={name:{kind:retained_material(kind,value) for kind in ('receipts','events')}
            for name,value in (('provenance',capture['provenance']),('original',result_capture['actual_store']),('current',current_store))}
        return material
    def _effect_evidence(self,capture,result_capture,metadata,payload,event,receipts,receipt_raws,events,event_raws):
        from .protected_operations import empty_evidence
        material=self._source_material(capture,result_capture,metadata,self.p.capture.chain_material(),
            None if capture['transaction'] is None else
                self.p.controller.transactions._load_record(capture['transaction']['transactionId']))
        material['receipt_payloads']=receipt_raws;material['event_payloads']=event_raws
        historical=[]
        for raw in receipt_raws:
            frozen_payload=exact_json(raw);operation=frozen_payload['operation']
            if operation==capture['operation']:continue
            source_row=self.p.journal.rows.get(operation)
            if source_row is None:
                historical.append(None)
                continue
            original_capture=source_row['capture']
            frozen_result=restore_archive(bytes.fromhex(frozen_payload['actualResult']))
            original_metadata={'schema':'worldline.requester-operation-binding-v1',
                'binding':clone(original_capture['binding']),'originalRequest':clone(original_capture['request']),
                'reservationEvent':original_capture['reservation_event']}
            # Actual acknowledged bytes and the independent first retained
            # result/reservation/native frame are frozen historical sources.
            # They neither reopen today's transaction nor today's grant/policy.
            historical.append(self._source_material(original_capture,frozen_result,original_metadata,
                clone(frozen_result['actual_store']),clone(frozen_result['actual_transaction'])))
        material['historical_sources']=historical
        evidence=empty_evidence();evidence.update(effect_binding=clone(capture['binding']),
            actual_receipt_root=self.p.core.hash_bytes(self.operation_domain('operation_receipts')+canonical_bytes(payload)).hex(),
            actual_causal_root=self.p.core.hash_bytes(self.operation_domain('operation_events')+canonical_bytes(event)).hex(),
            witnessed_receipt_head=receipts[-1].stored_head.hex(),
            witnessed_causal_head=events[-1].stored_head.hex(),effect_material=archive(material).hex())
        return evidence
    @staticmethod
    def _dto(rows):
        return [{name:None if getattr(row,name) is None else getattr(row,name).hex()
                 for name in ('previous','actual_payload_root','stored_payload_root','stored_head')} for row in rows]
    def _check_effect(self,capture,evidence,receipts,events):
        from .operation_result_relation import OperationResultRelation
        snapshot=self.p._snapshot(capture,evidence=evidence)
        snapshot['receipts']=self._dto(receipts);snapshot['events']=self._dto(events)
        native=OperationResultRelation(self.p.core).observe(snapshot)
        require(native['decision']=='READY',native['decision'])
    def _verify_operation_payload(self,operation,kind,payload):
        # Read the complete authenticated current envelope before selecting
        # the capture, retained result, all rows and frozen historical sources.
        # Read disposition is not effect permission; the relation below decides.
        self.p.journal.load()
        capture=self.p.journal.rows[operation]['capture']
        result_capture=restore_archive(bytes.fromhex(payload['actualResult']))
        metadata={'schema':'worldline.requester-operation-binding-v1','binding':clone(capture['binding']),
            'originalRequest':clone(capture['request']),'reservationEvent':capture['reservation_event']}
        receipt=payload if kind=='operation_receipts' else {
            **{key:value for key,value in payload.items() if key!='receipt_head'},
            'schema':'worldline.protected-operation-use-receipt-v1'}
        receipts,receipt_raws,receipt_head=self._candidate_operation_record(operation,'operation_receipts',receipt)
        event=payload if kind=='operation_events' else {
            **payload,'schema':'worldline.protected-operation-causal-v1','receipt_head':receipt_head.hex()}
        events,event_raws,_=self._candidate_operation_record(operation,'operation_events',event)
        evidence=self._effect_evidence(capture,result_capture,metadata,receipt,event,receipts,receipt_raws,events,event_raws)
        self._check_effect(capture,evidence,receipts,events)
    def effect(self,capture,result_capture):
        self.p.journal.load()
        self.reconcile(capture['operation'])
        material=result_capture['actual_store']
        for kind in ('receipts','events'):
            require(self.replay(kind,self.rows(kind,material),bytes.fromhex(self.p.journal.body['chains'][kind]['head'])).disposition=='READY',
                'OPERATION_ORIGINAL_FULL_CHAIN_NATIVE_REFUSED')
        metadata={'schema':'worldline.requester-operation-binding-v1','binding':clone(capture['binding']),
            'originalRequest':clone(capture['request']),'reservationEvent':capture['reservation_event']}
        payload={'schema':'worldline.protected-operation-use-receipt-v1','operation':capture['operation'],
            'requester':metadata,'originalCapture':archive(capture).hex(),'actualResult':archive(result_capture).hex(),
            'originalWorldlineChains':archive(material).hex()}
        self.append_operation_record(capture['operation'],'operation_receipts',payload)
        _,_,receipt_head=self._candidate_operation_record(capture['operation'],'operation_receipts',payload)
        event={**payload,'schema':'worldline.protected-operation-causal-v1','receipt_head':receipt_head.hex()}
        self.append_operation_record(capture['operation'],'operation_events',event)
        receipts,receipt_raws=self.operation_rows('operation_receipts')
        events,event_raws=self.operation_rows('operation_events')
        evidence=self._effect_evidence(capture,result_capture,metadata,payload,event,receipts,receipt_raws,events,event_raws)
        self._check_effect(capture,evidence,receipts,events)
        return evidence,self._dto(receipts),self._dto(events)
