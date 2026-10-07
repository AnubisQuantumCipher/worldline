"""Candidate protected durable principal; no installed service or acceptance claim.

Uses actual intent_gate.Gate, ProtectedIssuer, the WORLDLINE Controller and full
native packet producer. The service receives operation identifiers only. Neither
caller verdicts nor caller-authenticated packet DTOs are accepted. Source-only
bootstrap/provisioning and K4 integration remain dependencies. Native capability
use reservation is authored additively; genuine custody, proof and accepted lab
controls remain OPEN until independently qualified and actually verified.
"""
from __future__ import annotations
import hashlib
import hmac
import os
from pathlib import Path
import socket
import stat
import struct

from intent_gate import Gate, Refusal, broker_rpc, canonical, protected, require, save
from worldline.errors import WorldlineError
from worldline.protected_recovery_capture import (ProtectedCapture, private_bytes,
    exact_json, refuse, identity)
from worldline.recovery_observation import archive, restore_archive
from worldline.recovery_protocol_kernel import RecoveryProtocolKernel, STATES

_DOMAIN=b'worldline-protected-recovery-full-journal-v1\0'
# Linux ucred: native signed pid_t, unsigned uid_t/gid_t. Preserve their full
# kernel domains without imposing a signed UID/GID ceiling.
_UCRED=struct.Struct('iII')


class ProtectedJournal:
    """Full historical packets, facts and boundary results in root-private custody.

    Existing issuer key/private-file/atomic-save conventions are used. HMAC
    authenticates complete canonical bytes; every earlier snapshot is retained.
    This is not an independently protected monotonic counter or hardware rollback
    anchor. Those custody/durability obligations remain OPEN.
    """
    def __init__(self,gate,kernel,*,startup_lease):
        require(os.geteuid()==0 and type(gate) is Gate,'RECOVERY_ROOT_PRINCIPAL_REQUIRED')
        require(gate.issuer is not None,'RECOVERY_PROTECTED_ISSUER_UNAVAILABLE')
        self.gate,self.kernel=gate,kernel
        self.path=gate.state_path.parent/'recovery-full-journal.json'
        protected(self.path.parent,directory=True,private=True)
        self.poisoned=False
        self.body={'schema':'worldline.protected-recovery-journal-v1',
                   'gate_config':hashlib.sha256(gate.config_raw).hexdigest(),'issuer_policy':gate.issuer.policy_sha256,'events':[]}
        self.latest={}
        from worldline.protected_startup import StartupLease
        require(type(startup_lease) is StartupLease,'RECOVERY_PROTECTED_STARTUP_LEASE_REQUIRED')
        startup_lease.open_journal(gate,'recovery-full-journal',self.path,
            {'body':self.body,'mac':self._mac(self.body)})
        require(os.path.lexists(self.path),'RECOVERY_PRIOR_JOURNAL_MISSING')
        self._load()

    def _mac(self,body):
        return hmac.new(self.gate.issuer.key,_DOMAIN+canonical(body),hashlib.sha256).hexdigest()

    def _load(self):
        envelope=exact_json(private_bytes(self.path))
        require(type(envelope) is dict and set(envelope)=={'body','mac'},'RECOVERY_JOURNAL_SCHEMA')
        body=envelope['body']
        require(type(body) is dict and set(body)==set(self.body) and
                body['schema']==self.body['schema'] and body['gate_config']==self.body['gate_config'] and
                type(body['issuer_policy']) is str and type(body['events']) is list,
                'RECOVERY_JOURNAL_CONTEXT_CHANGED')
        require(type(envelope['mac']) is str and hmac.compare_digest(envelope['mac'],self._mac(body)),
                'RECOVERY_JOURNAL_AUTHENTICATION_FAILED')
        prior='GENESIS'; latest={}
        for event in body['events']:
            require(type(event) is dict and set(event)=={'prior','operation','state','cause','boundary','snapshot'},
                    'RECOVERY_JOURNAL_EVENT_SCHEMA')
            require(event['prior']==prior and type(event['operation']) is str and
                    type(event['snapshot']) is str and event['state'] in STATES and
                    type(event['boundary']) is str,'RECOVERY_JOURNAL_EVENT_INVALID')
            try: snapshot_raw=bytes.fromhex(event['snapshot']); snapshot=restore_archive(snapshot_raw)
            except (ValueError,WorldlineError) as exc: raise Refusal('RECOVERY_JOURNAL_FULL_SNAPSHOT_INVALID') from exc
            require(event['snapshot']==snapshot_raw.hex() and type(snapshot) is dict and
                    snapshot['capture']['pending']['operation_id']==event['operation'] and
                    snapshot['state']==event['state'],'RECOVERY_JOURNAL_OPERATION_CHANGED')
            earlier=latest.get(event['operation'])
            if earlier is None:
                require(event['cause']=='ISSUE' and event['state']=='ISSUED','RECOVERY_JOURNAL_ISSUE_MISSING')
            else:
                require(self.kernel.advance(earlier['state'],event['cause'])==event['state'],
                        'RECOVERY_JOURNAL_NATIVE_TRANSITION_CHANGED')
                require(earlier['capture']==snapshot['capture'],'RECOVERY_JOURNAL_BOUND_OPERATION_CHANGED')
            latest[event['operation']]=snapshot
            prior=hashlib.sha256(canonical(event)).hexdigest()
        self.body,self.latest=body,latest
        self.persisted=restore_archive(archive(envelope))

    def _save(self):
        if self.poisoned: refuse('RECOVERY_JOURNAL_DURABILITY_UNKNOWN')
        try:
            require(os.path.lexists(self.path),'RECOVERY_PRIOR_JOURNAL_MISSING')
            require(exact_json(private_bytes(self.path))==self.persisted,'RECOVERY_PRIOR_JOURNAL_CUSTODY_CHANGED')
            save(self.path,{'body':self.body,'mac':self._mac(self.body)})
            # Readback full bytes, not merely an existence or digest check.
            envelope=exact_json(private_bytes(self.path))
            require(envelope=={'body':self.body,'mac':self._mac(self.body)},'RECOVERY_JOURNAL_READBACK_CHANGED')
            self.persisted=restore_archive(archive(envelope))
        except BaseException:
            self.poisoned=True
            raise

    def append(self,snapshot,cause,boundary):
        if self.poisoned: refuse('RECOVERY_JOURNAL_DURABILITY_UNKNOWN')
        # Detach the complete snapshot before any subsequent external API can
        # mutate Gate pending data or prepared transaction dictionaries.
        snapshot=restore_archive(archive(snapshot))
        operation=snapshot['capture']['pending']['operation_id']
        before=self.latest.get(operation)
        if before is None:
            require(cause=='ISSUE' and snapshot['state']=='ISSUED','RECOVERY_ISSUE_STATE_INVALID')
        else:
            require(before['capture']==snapshot['capture'],'RECOVERY_OPERATION_BOUND_CAPTURE_CHANGED')
            require(self.kernel.advance(before['state'],cause)==snapshot['state'],'RECOVERY_NATIVE_PROTOCOL_TRANSITION_REFUSED')
        prior='GENESIS' if not self.body['events'] else hashlib.sha256(canonical(self.body['events'][-1])).hexdigest()
        self.body['events'].append({'prior':prior,'operation':operation,'state':snapshot['state'],
            'cause':cause,'boundary':boundary,'snapshot':archive(snapshot).hex()})
        self._save(); self.latest[operation]=snapshot
        return snapshot


class ProtectedRecoveryPrincipal:
    def __init__(self,gate,controller,*,startup_lease):
        require(type(gate) is Gate,'RECOVERY_ACTUAL_GATE_REQUIRED')
        self.gate=gate
        self.capture=ProtectedCapture(gate,controller,startup_lease=startup_lease)
        self.protocol=RecoveryProtocolKernel(controller.core)
        from worldline.recovery_authority_kernel_v3 import RecoveryAuthorityKernelV3
        self.relation=RecoveryAuthorityKernelV3(controller.core)
        self.journal=ProtectedJournal(gate,self.protocol,startup_lease=startup_lease)
        from worldline.protected_capability_uses import ProtectedUseReservations
        self.uses=ProtectedUseReservations(gate,self.capture,startup_lease=startup_lease)
        self.capture.use_reservations=self.uses
        self.capture.principal=self
        self.alarm=None

    def _peer(self,connection):
        require(type(connection) is socket.socket and connection.family==socket.AF_UNIX,
                'RECOVERY_UNIX_PEER_REQUIRED')
        pid,uid,gid=_UCRED.unpack(connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,_UCRED.size))
        require(uid==self.gate.config['requester_uid'],'RECOVERY_REQUESTER_PEER_REFUSED')
        return {'pid':pid,'uid':uid,'gid':gid}

    def _append(self,row,cause,boundary,**results):
        updated=restore_archive(archive(row))
        updated['state']=self.protocol.advance(row['state'],cause)
        updated['boundaries'].append({'name':boundary,'results':results})
        return self.journal.append(updated,cause,boundary)

    def _quarantine(self,row,exc):
        # If persisting fails, no new effect is issued; the prior durable intent
        # and process alarm remain. Restart re-observes it, never assumes abort.
        self.alarm={'operation':row['capture']['pending']['operation_id'],
                    'code':getattr(exc,'code',str(exc))}
        try: return self._append(row,'UNKNOWN_OBSERVATION','QUARANTINE',reason=self.alarm)
        except BaseException: raise Refusal('RECOVERY_QUARANTINE_DURABILITY_UNKNOWN') from exc

    def _pending(self,capture):
        pending=self.gate.journal['pending']
        require(type(pending) is dict and pending['operation_id']==capture['pending']['operation_id'] and
                pending['request_id']==capture['pending']['request_id'] and
                pending['capability']==capture['pending']['capability'] and
                pending['resource']['reservation']==capture['pending']['resource']['reservation'] and
                pending['universe_event_head']==capture['pending']['universe_event_head'],
                'RECOVERY_PROTECTED_PENDING_CHANGED')
        return pending

    def issue(self,connection,transaction_id):
        peer=self._peer(connection)
        with self.gate.mutex:
            require(not any(row['state'] not in ('SETTLED','ABORTED') for row in self.journal.latest.values()),
                    'RECOVERY_UNRESOLVED_OPERATION')
            pending=self.gate.journal['pending']
            require(type(pending) is dict and pending['op']=='promote','RECOVERY_PROTECTED_OPERATION_ABSENT')
            require(pending['operation_id'] not in self.journal.latest,'RECOVERY_OPERATION_ALREADY_ISSUED')
            require(self.gate.capability_still_eligible(pending),'RECOVERY_CURRENT_CAPABILITY_REFUSED')
            capture=self.capture.capture(pending,peer,transaction_id)
            # Native complete-binding equality also rejects every missing field.
            binding=self.capture.historical(capture); native,_facts=self.capture.observe_effect()
            action,_state=self.relation.decide(state='ISSUED',issued=binding,recovered=binding,
                fresh='AUTHORIZED',historical='UNESTABLISHED',grant_eligible=True,native=native)
            require(action=='INVOKE_ACTUATOR','RECOVERY_COMPLETE_ISSUE_BINDING_REFUSED')
            return self.journal.append({'state':'ISSUED','capture':capture,'boundaries':[]},'ISSUE','ISSUE')

    @staticmethod
    def _boundary(row,name):
        values=[item['results'] for item in row['boundaries'] if item['name']==name]
        require(bool(values),'RECOVERY_RETAINED_BOUNDARY_ABSENT')
        require(all(value==values[0] for value in values),'RECOVERY_RETAINED_BOUNDARY_CHANGED')
        return values[0]

    def _abort_record(self,capture):
        record=self.capture.tx._load_record(capture['record']['transactionId'])
        for field in ('transactionId','candidateWorld','beforeRoot','candidateRoot','stagedRoot','preparedPath','preparedMapping'):
            require(record[field]==capture['record'][field],'RECOVERY_ABORT_TRANSACTION_BINDING_CHANGED')
        return record

    def _closed_abort(self,row):
        # No resource, broker or use release is issued here. Only exact protected
        # closed history and already durable native transaction state reconcile
        # a lost close acknowledgement. Legacy/incomplete history refuses.
        self.capture.intact();self.uses._intact();capture=row['capture'];operation=capture['pending']['operation_id']
        self.capture.historical(capture)
        require(exact_json(private_bytes(self.gate.state_path))==self.gate.journal,
                'RECOVERY_ABORT_GATE_DURABLE_READBACK_CHANGED')
        history=[item for item in self.gate.journal['history'] if item.get('operation_id')==operation]
        require(len(history)==1 and history[0].get('outcome')=='RECOVERY_NOT_EFFECTED' and
                history[0].get('recovery_operation')==operation and
                history[0].get('capability')==capture['pending']['capability'] and
                history[0].get('request_id')==capture['pending']['request_id'] and
                history[0].get('universe_event_head')==capture['pending']['universe_event_head'] and
                history[0].get('resource',{}).get('reservation')==capture['pending']['resource']['reservation'],
                'RECOVERY_CLOSED_ABORT_HISTORY_UNESTABLISHED')
        done={item['name'] for item in row['boundaries']}
        require({'ABORT_INTENT','ABORT_BROKER_ACK','ABORT_NO_EFFECT_ACK','ABORT_RESOURCE_ACK',
                 'ABORT_USE_ACK','ABORT_WORLDLINE_ACK','ABORT_GATE_CLOSE_INTENT'}<=done,
                'RECOVERY_CLOSED_ABORT_ACKS_INCOMPLETE')
        expected={name:self._boundary(row,name) for name in
                  ('ABORT_BROKER_ACK','ABORT_NO_EFFECT_ACK','ABORT_RESOURCE_ACK','ABORT_USE_ACK','ABORT_WORLDLINE_ACK')}
        require(history[0].get('recovery_abort_evidence')==expected,
                'RECOVERY_CLOSED_ABORT_RELEASE_EVIDENCE_CHANGED')
        require(expected['ABORT_BROKER_ACK']['abandoned']=={'state':'ABANDONED','operation_id':operation},
                'RECOVERY_CLOSED_ABORT_BROKER_EVIDENCE_CHANGED')
        resource=expected['ABORT_RESOURCE_ACK']['resource']
        require(resource['status']=='RELEASED' and
                resource['reservation_id']==capture['pending']['resource']['reservation']['reservation_id'],
                'RECOVERY_CLOSED_ABORT_RESOURCE_EVIDENCE_CHANGED')
        require(self._abort_record(capture)['state']=='ABORTED','RECOVERY_CLOSED_ABORT_TRANSACTION_NOT_ABORTED')
        use=expected['ABORT_USE_ACK']['use']
        if use is None:
            require(operation not in self.uses.rows and self.gate.issuer.store.recorded_use(operation) is None,
                    'RECOVERY_CLOSED_ABORT_UNRESERVED_USE_CHANGED')
        else:
            require(operation in self.uses.rows and self.uses.rows[operation]['state']=='RELEASED' and
                    self.uses.rows[operation]['bound']==self.uses._bound(capture,fresh=False) and
                    use['bound']==self.uses.rows[operation]['bound'] and
                    self.gate.issuer.store.recorded_use(operation) is None,
                    'RECOVERY_CLOSED_ABORT_USE_EVIDENCE_CHANGED')
        if row['state']=='ABORTED':return row
        if 'ABORT_GATE_CLOSE_ACK' not in done:
            row=self._append(row,'REPLAY','ABORT_GATE_CLOSE_ACK',history=history[0])
        return self._append(row,'NO_EFFECT_RELEASED','ABORT_RELEASE_ACK',evidence=expected)

    def _abort(self,row):
        capture=row['capture'];operation=capture['pending']['operation_id']
        if self.gate.journal['pending'] is None:return self._closed_abort(row)
        pending=self._pending(capture);done={item['name'] for item in row['boundaries']}
        if 'ABORT_INTENT' not in done:row=self._append(row,'REPLAY','ABORT_INTENT')
        # Same actual broker interface as Gate.release_if_uncommitted. Here the
        # complete release answer is retained before Gate.pending can be closed.
        if 'ABORT_BROKER_ACK' not in done:
            row=self._append(row,'REPLAY','ABORT_BROKER_INTENT')
            abandoned=broker_rpc(self.gate.broker_socket,'abandon',operation_id=operation)
            require(abandoned=={'state':'ABANDONED','operation_id':operation},
                    'RECOVERY_BROKER_ABANDON_UNESTABLISHED')
            pending['broker_abandoned']=True;save(self.gate.state_path,self.gate.journal)
            row=self._append(row,'REPLAY','ABORT_BROKER_ACK',abandoned=abandoned)
        require(self.gate.proves_no_commit(pending),'RECOVERY_NO_EFFECT_RELEASE_UNESTABLISHED')
        facts=self.gate.facts();artifacts=self.gate.commit_artifacts()
        native,effect=self.capture.observe_effect();binding=self.capture.historical(capture)
        action,_state=self.relation.decide(state=('ISSUED' if row['state']=='ISSUED' else 'CLAIMED'),
            issued=binding,recovered=binding,fresh='REFUSED',historical='HISTORICALLY_AUTHORIZED',
            grant_eligible=False,native=native)
        require(action=='ABORT_USE','RECOVERY_ABORT_ACTUAL_NATIVE_EFFECT_UNKNOWN')
        if 'ABORT_NO_EFFECT_ACK' not in done:
            row=self._append(row,'REPLAY','ABORT_NO_EFFECT_ACK',facts=facts,artifacts=artifacts,effect=effect)
        if 'ABORT_RESOURCE_ACK' not in done:
            row=self._append(row,'REPLAY','ABORT_RESOURCE_INTENT')
            resources=self.gate.settle_resources(pending,'release')
            require(type(resources) is dict and resources.get('status')=='RELEASED' and
                    resources.get('reservation_id')==pending['resource']['reservation']['reservation_id'],
                    'RECOVERY_ABORT_RESOURCE_RELEASE_UNESTABLISHED')
            row=self._append(row,'REPLAY','ABORT_RESOURCE_ACK',resource=resources)
        if 'ABORT_USE_ACK' not in done:
            row=self._append(row,'REPLAY','ABORT_USE_INTENT')
            if operation in self.uses.rows:use=self.uses.release(capture)
            else:
                require(self.gate.issuer.store.recorded_use(operation) is None,
                        'RECOVERY_UNRESERVED_ABORT_HAS_RECORDED_USE')
                use=None # exact protected journal absence, no invented reserve
            row=self._append(row,'REPLAY','ABORT_USE_ACK',use=use)
        if 'ABORT_WORLDLINE_ACK' not in done:
            row=self._append(row,'REPLAY','ABORT_WORLDLINE_INTENT')
            record=self._abort_record(capture)
            if record['state'] in ('PREPARED','AUTHORIZED','DENIED'):
                self.capture.tx._set_state(record,'ABORTED',error={'code':'RECOVERY_FRESH_DENIED'})
            require(record['state']=='ABORTED','RECOVERY_ABORT_TRANSACTION_STATE')
            row=self._append(row,'REPLAY','ABORT_WORLDLINE_ACK',record=record)
        evidence={name:self._boundary(row,name) for name in
                  ('ABORT_BROKER_ACK','ABORT_NO_EFFECT_ACK','ABORT_RESOURCE_ACK','ABORT_USE_ACK','ABORT_WORLDLINE_ACK')}
        row=self._append(row,'REPLAY','ABORT_GATE_CLOSE_INTENT')
        self.gate.close_pending(pending,'RECOVERY_NOT_EFFECTED',recovery_operation=operation,
                                recovery_abort_evidence=evidence)
        row=self._append(row,'REPLAY','ABORT_GATE_CLOSE_ACK',history=self.gate.journal['history'][-1])
        return self._append(row,'NO_EFFECT_RELEASED','ABORT_RELEASE_ACK',evidence=evidence)

    def claim(self,connection,operation):
        peer=self._peer(connection)
        with self.gate.mutex:
            row=self.journal.latest[operation]
            require(peer['uid']==row['capture']['peer']['uid'] and peer['gid']==row['capture']['peer']['gid'],
                    'RECOVERY_BOUND_REQUESTER_CHANGED')
            require(row['state']=='ISSUED','RECOVERY_ONESHOT_CLAIM_REFUSED')
            try:
                pending=self._pending(row['capture'])
                fresh=self.capture.capture(pending,peer,row['capture']['record']['transactionId'],flush=True)
                issued=self.capture.historical(row['capture']); recovered=self.capture.historical(fresh)
                native,_facts=self.capture.observe_effect()
                eligible=self.gate.capability_still_eligible(pending)
                action,_state=self.relation.decide(state='ISSUED',issued=issued,recovered=recovered,
                    fresh='AUTHORIZED',historical='UNESTABLISHED',grant_eligible=eligible,native=native)
                if action=='ABORT_USE': return self._abort(row)
                require(action=='INVOKE_ACTUATOR','RECOVERY_FRESH_COMPLETE_BINDING_CHANGED')
                # Native full-history reservation is durably retained under
                # the actual protected issuer lock before any exchange.
                reservation=self.capture.claim_capability_use(fresh)
                row=self._append(row,'FRESH_CLAIM','EFFECT_INTENT',capability_reservation=reservation,
                                 fresh_packet=fresh['packet'],fresh_native=fresh['native'])
                require(self.gate.capability_still_eligible(pending),'RECOVERY_CAPABILITY_CHANGED_BEFORE_EFFECT')
                final_reservation=self.uses.reserve(fresh)
                require(final_reservation['status']=='RESERVED_REPLAY','RECOVERY_FINAL_USE_RESERVATION_CHANGED')
                row=self._append(row,'REPLAY','FINAL_CAPABILITY_RESERVATION_ACK',reservation=final_reservation)
                self.capture.dispatch(fresh)
                return self._recover(row)
            except BaseException as exc:
                self._quarantine(self.journal.latest.get(operation,row),exc)
                raise

    def _settle(self,row):
        capture=row['capture']
        if self.gate.journal['pending'] is None:
            history=[item for item in self.gate.journal['history'] if item.get('operation_id')==capture['pending']['operation_id']]
            require(len(history)==1 and history[0].get('outcome')=='RECOVERY_COMMITTED' and
                    history[0].get('recovery_operation')==capture['pending']['operation_id'] and
                    history[0].get('capability')==capture['pending']['capability'] and
                    history[0].get('resource',{}).get('reservation')==capture['pending']['resource']['reservation'],
                    'RECOVERY_CLOSED_OPERATION_HISTORY_UNESTABLISHED')
            done={item['name'] for item in row['boundaries']}
            require({'RECEIPT_ACK','UNIVERSE_ACK','RESOURCE_ACK','GRANT_ACK','GATE_CLOSE_INTENT'}<=done,
                    'RECOVERY_CLOSED_OPERATION_SETTLEMENT_INCOMPLETE')
            if capture.get('owner_binding') is not None:
                from worldline.protected_owner import installed_owner
                owner=installed_owner(self.capture.controller)
                result=owner.finish_collapse(self,row)
                if 'OWNER_SETTLEMENT_ACK' not in done:
                    row=self._append(row,'REPLAY','OWNER_SETTLEMENT_ACK',owner=result)
            if 'GATE_CLOSE_ACK' not in done: row=self._append(row,'REPLAY','GATE_CLOSE_ACK',history=history[0])
            return self._append(row,'SETTLEMENT_COMPLETE','SETTLED')
        pending=self._pending(capture)
        # After native historical authorization and authenticated effect, fresh
        # policy denial/revocation is deliberately not consulted. Every call
        # below is same-operation settlement and cannot issue a new exchange.
        done={item['name'] for item in row['boundaries']}
        if 'RECEIPT_ACK' not in done:
            row=self._append(row,'REPLAY','RECEIPT_INTENT')
            receipt=self.capture.finish_receipt(capture)
            row=self._append(row,'REPLAY','RECEIPT_ACK',receipt=receipt)
        txid=capture['record']['transactionId']
        facts=self.gate.facts(check_universe=False); transaction=facts['broker'].get('transaction')
        require(facts['broker'].get('phase')=='COMMITTED' and type(transaction) is dict and
                transaction.get('id')==txid and transaction.get('promotion_operation_id')==pending['operation_id'],
                'RECOVERY_UNIVERSE_ACTUATOR_CROSSWALK_UNESTABLISHED')
        # The old protected broker is already COMMITTED for this exact effect.
        # Its recover may reconcile receipt custody; it cannot issue promotion.
        recovered=broker_rpc(self.gate.broker_socket,'recover')
        accepted=self.gate.verify_accepted_effect(recovered,pending,txid)
        if 'UNIVERSE_ACK' not in done:
            row=self._append(row,'REPLAY','UNIVERSE_INTENT')
            universe=self.gate.complete_universe_effect(accepted,pending)
            row=self._append(row,'REPLAY','UNIVERSE_ACK',universe=universe)
        if 'RESOURCE_ACK' not in done:
            row=self._append(row,'REPLAY','RESOURCE_INTENT')
            resources=self.gate.settle_resources(pending,'consume')
            require(type(resources) is dict and resources.get('status')=='CONSUMED','RECOVERY_RESOURCE_CONSUME_UNESTABLISHED')
            row=self._append(row,'REPLAY','RESOURCE_ACK',resource=resources)
        if 'GRANT_ACK' not in done:
            row=self._append(row,'REPLAY','GRANT_INTENT')
            # Retained exact use tuple survives Universe head advancement and
            # revocation. ProtectedIssuer.use detects identical ALREADY and
            # refuses same-operation changed fields; no extra grant event.
            use=self.uses.consume(capture)
            require(use['issuer_use'].get('recorded') in ('NEW','ALREADY') and
                    use['reservation']['status'] in ('CONSUMED_NEW','CONSUMED_REPLAY'),
                    'RECOVERY_CAPABILITY_USE_ACK_UNESTABLISHED')
            row=self._append(row,'REPLAY','GRANT_ACK',issuer=use)
        # The close is itself journaled and idempotent on the Gate's retained
        # operation history. A lost close ack cannot create a new pending use.
        if capture.get('owner_binding') is not None:
            from worldline.protected_owner import installed_owner
            owner=installed_owner(self.capture.controller)
            owner_result=owner.finish_collapse(self,row)
            if 'OWNER_SETTLEMENT_ACK' not in done:
                row=self._append(row,'REPLAY','OWNER_SETTLEMENT_ACK',owner=owner_result)
        row=self._append(row,'REPLAY','GATE_CLOSE_INTENT')
        self.gate.close_pending(pending,'RECOVERY_COMMITTED',recovery_operation=pending['operation_id'])
        row=self._append(row,'REPLAY','GATE_CLOSE_ACK')
        return self._append(row,'SETTLEMENT_COMPLETE','SETTLED')

    def _recover(self,row):
        if row['state']=='QUARANTINED': raise Refusal('RECOVERY_OWNER_RESOLUTION_REQUIRED')
        if row['state']=='ABORTED':return self._closed_abort(row)
        capture=row['capture']; binding=self.capture.historical(capture)
        native,facts=self.capture.observe_effect()
        relation_state={'ISSUED':'ISSUED','EFFECT_INTENT':'CLAIMED','EFFECT_OBSERVED':'CLAIMED',
                        'SETTLED':'COMPLETED','ABORTED':'DENIED'}[row['state']]
        # Fresh denial is safe before effect. No recovery path invokes another
        # exchange: CLAIMED+Before_Effect is aborted/released, never redispatched.
        action,_state=self.relation.decide(state=relation_state,issued=binding,recovered=binding,
            fresh='REFUSED',historical='HISTORICALLY_AUTHORIZED',grant_eligible=False,native=native)
        if action=='REPLAY': return row
        if action=='ABORT_USE': return self._abort(row)
        require(action=='SETTLE','RECOVERY_EFFECT_OBSERVATION_UNESTABLISHED')
        operation=capture['pending']['operation_id']
        require(operation in self.uses.rows and self.uses.rows[operation]['state'] in ('RESERVED','CONSUMED') and
                self.uses.rows[operation]['bound']==self.uses._bound(capture,fresh=False),
                'RECOVERY_AUTHENTICATED_USE_RESERVATION_UNESTABLISHED')
        if row['state']=='EFFECT_INTENT': row=self._append(row,'HISTORICAL_EFFECT','EFFECT_OBSERVED',observation=facts)
        require(row['state']=='EFFECT_OBSERVED','RECOVERY_EFFECT_NOT_DURABLY_OBSERVED')
        return self._settle(row)

    def recover(self,connection,operation):
        self._peer(connection)
        with self.gate.mutex:
            row=self.journal.latest[operation]
            try: return self._recover(row)
            except BaseException as exc:
                self._quarantine(self.journal.latest.get(operation,row),exc)
                raise

    def restart(self):
        """Per-operation startup diagnosis does not suppress daemon startup."""
        results={}
        with self.gate.mutex:
            for operation,row in list(self.journal.latest.items()):
                try: results[operation]=self._recover(row)['state']
                except BaseException as exc:
                    try: self._quarantine(self.journal.latest.get(operation,row),exc)
                    except BaseException: pass
                    results[operation]='QUARANTINED'
        return {'operations':results,'alarm':self.alarm,'release_gate':'BLOCKED'}

    def resolve(self,connection,operation,request):
        peer=self._peer(connection)
        with self.gate.mutex:
            row=self.journal.latest[operation]
            require(row['state']=='QUARANTINED','RECOVERY_RESOLUTION_NOT_QUARANTINED')
            # Current interface refuses: UID/root proximity cannot stand for
            # K4's authenticated owner authorization and recorded observations.
            resolution=self.capture.owner_resolution(peer,row,request)
            refuse('RECOVERY_OWNER_RESOLUTION_PROTOCOL_UNINTEGRATED')
