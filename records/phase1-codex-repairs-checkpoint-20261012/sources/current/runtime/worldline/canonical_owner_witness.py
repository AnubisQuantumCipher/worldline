"""Actual owner reservation -> original complete canonical-chain witness.

No ordinary operation right, broker UID, owner flag or copied verdict substitutes
for the retained owner issuer/history/native reservation. Recovery writes consume
that original record and never create a new evaluation use.
"""
from .client_peer import RequestPeer,current_peer
from .protected_startup import require,exact_json
from .operation_capture import archive,restore_archive
from .protected_owner import encoded

class OwnerCanonicalScope:
    def __init__(self,bridge,peer):self.bridge=bridge;self.principal=bridge.p;self.peer=peer
    def metadata(self):return self.bridge.capture(self.peer)

class OwnerCanonicalWitness:
    def __init__(self,principal):self.p=principal;self.owner=principal.owner;self.pending={}
    def capture(self,request):
        require(type(request) is RequestPeer and current_peer() is not None,
            'OWNER_CANONICAL_ACTUAL_PEER_REQUIRED')
        observed,who=self.owner._peer(request)
        raw=bytes.fromhex(observed['rawRequest']);document=exact_json(raw,canonical_required=False)
        require(document['op'] in self.p.owner_names,'OWNER_CANONICAL_ORDINARY_RIGHT_SUBSTITUTION')
        intent=document['args'].get('intent') if document['op']=='owner.recover' else observed['requestId']
        self.owner.intact();row=self.owner.journal.rows.get(intent)
        require(row is not None and row['cause'] not in ('ISSUED',),
            'OWNER_CANONICAL_NATIVE_RESERVATION_REQUIRED')
        record=row['record'];q=record['request']
        require(q.peer==who and record['base']['principal']==who,
            'OWNER_CANONICAL_ORIGINAL_PRINCIPAL_CHANGED')
        captured={'operation':intent,'schema':'worldline.owner-canonical-binding-v1',
            'owner_binding':self.owner.binding,'original_request':observed,
            'owner_journal':self.owner.journal.persisted.hex(),
            'owner_head':self.owner.journal.persisted_head.hex(),
            'owner_event':row['event'],'owner_record':encoded(record)}
        self.verify(captured)
        return captured
    def verify(self,captured):
        """Native replay of full authentic current and retained owner histories."""
        from .journal_witness_kernel import verify_owner
        return verify_owner(self.p,captured)
    def preflight(self,kind,payload,root,previous,proposed):
        from .protected_operations import current_scope,identity
        scope=current_scope();require(type(scope) is OwnerCanonicalScope and scope.bridge is self,
            'OWNER_CANONICAL_ACTUAL_SCOPE_REQUIRED')
        captured=scope.metadata();require(payload.get('requesterBinding')==captured,'OWNER_CANONICAL_REQUESTER_CHANGED')
        chain=self.p.canonical;old=self.p.capture.chain_material();rows=chain.rows(kind,old)
        head=bytes.fromhex(self.p.journal.body['chains'][kind]['head'])
        require(chain.replay(kind,rows,head).disposition=='READY' and previous==head,
            'OWNER_CANONICAL_FULL_OLD_CHAIN_REFUSED')
        from .chain_authority import ChainRow
        native=chain.replay(kind,[*rows,ChainRow(previous,root,root,proposed)],proposed)
        require(native.disposition=='READY','OWNER_CANONICAL_APPEND_NATIVE_REFUSED')
        from .canonical import canonical_bytes
        boundary={'name':'OWNER_CANONICAL_INTENT','kind':kind,'old_material':archive(old).hex(),
            'payload':canonical_bytes(payload).hex(),'root':root.hex(),'previous':previous.hex(),'head':native.head.hex()}
        self.p.journal.append(captured['operation'],'OWNER_CANONICAL',captured,boundaries=[boundary])
        self.pending[kind]=(captured,boundary)
    def acknowledge(self,kind):
        from .protected_operations import identity
        require(kind in self.pending,'OWNER_CANONICAL_INTENT_ABSENT')
        captured,intent=self.pending[kind];self.verify(captured)
        actual=self.p.capture.chain_material();before=restore_archive(bytes.fromhex(intent['old_material']))
        require(archive(actual[kind][:-1])==archive(before[kind])
            and len(actual[kind])>len(before[kind]),'OWNER_CANONICAL_COMPLETE_PREFIX_CHANGED')
        sql,raw=actual[kind][-1]
        from .core import hash_bytes_from_id
        require(raw.hex()==intent['payload'] and hash_bytes_from_id(sql['chain_hash']).hex()==intent['head'],
            'OWNER_CANONICAL_ACTUAL_BYTES_CHANGED')
        require(self.p.canonical.replay(kind,self.p.canonical.rows(kind,actual),bytes.fromhex(intent['head'])).disposition=='READY',
            'OWNER_CANONICAL_ACTUAL_APPEND_REFUSED')
        ack={'name':'CANONICAL_ACK','kind':kind,'head':intent['head'],'full_material':archive(actual).hex(),
            'intent':identity(intent).hex(),'owner_capture':archive(captured).hex()}
        self.p.journal.append(captured['operation'],'OWNER_CANONICAL',captured,boundaries=[intent,ack])
        self.pending.pop(kind)
    def reconcile(self):
        from .protected_operations import identity
        done={boundary['intent'] for event in self.p.journal.body['events'] for boundary in event['boundaries']
            if event['cause']=='OWNER_CANONICAL' and boundary['name']=='CANONICAL_ACK'}
        for event in tuple(self.p.journal.body['events']):
            if event['cause']!='OWNER_CANONICAL':continue
            for boundary in event['boundaries']:
                if boundary['name']=='OWNER_CANONICAL_INTENT' and identity(boundary).hex() not in done:
                    captured=restore_archive(bytes.fromhex(event['capture']));self.verify(captured)
                    self.pending[boundary['kind']]=(captured,boundary)
                    self.acknowledge(boundary['kind']) # exact surviving write only; no redispatch
                    done.add(identity(boundary).hex())
