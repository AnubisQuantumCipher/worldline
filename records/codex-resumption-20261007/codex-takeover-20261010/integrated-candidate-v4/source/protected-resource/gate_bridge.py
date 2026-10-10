"""Concrete additive adapter for the inspected protected intent_gate.Gate API.

The existing bounded promotion budget is retained. This bridge calls the new
root peer endpoint for workload lifecycle records, binds each full record to the
actual pending protected Gate journal, and durably records an intent before
submission. It must run inside Gate's existing ordered request critical section.
No controller packet or ordinary manager observation becomes protected authority.
"""
from __future__ import annotations
import hashlib,json,os,socket,struct
from pathlib import Path
import intent_gate
from worldline.resource_run_ledger import dto_record,restore_dto,RunRequest

def detached(value):
    return json.loads(intent_gate.canonical(value))

def gate_bytes(path):
    """Whole existing private journal; never recreate a deleted history."""
    import stat
    intent_gate.protected(path,private=True)
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        info=os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid!=0 or info.st_nlink!=1:
            raise intent_gate.Refusal('FULL_RESOURCE_GATE_JOURNAL_CUSTODY')
        with os.fdopen(os.dup(fd),'rb') as source:raw=source.read()
        after=os.fstat(fd)
        if (info.st_size,info.st_mtime_ns,info.st_ctime_ns)!=(after.st_size,after.st_mtime_ns,after.st_ctime_ns):
            raise intent_gate.Refusal('FULL_RESOURCE_GATE_JOURNAL_CHANGED')
        parsed=json.loads(raw)
        if raw not in (intent_gate.canonical(parsed),intent_gate.canonical(parsed)+b'\n'):
            raise intent_gate.Refusal('FULL_RESOURCE_GATE_JOURNAL_NONCANONICAL')
        return raw,parsed
    finally:os.close(fd)

class FullResourceGateBridge:
    def __init__(self,gate):
        if os.geteuid()!=0 or type(gate) is not intent_gate.Gate:raise intent_gate.Refusal('FULL_RESOURCE_GATE_PRINCIPAL_UNAVAILABLE')
        if gate.ledger_socket is None:raise intent_gate.Refusal('FULL_RESOURCE_LEDGER_UNBOUND')
        self.gate=gate;self.socket=gate.ledger_socket.with_name('run-request-v1.sock')
        self.poisoned=False
    def _begin(self):
        if self.poisoned:raise intent_gate.Refusal('FULL_RESOURCE_GATE_DURABILITY_UNKNOWN')
        self.persisted,current=gate_bytes(self.gate.state_path)
        if current!=self.gate.journal:raise intent_gate.Refusal('FULL_RESOURCE_GATE_MEMORY_DIVERGED')
        if type(current.get('full_resource_history_v2')) is not list:
            # This additive history is imported/provisioned by an explicit owner
            # Genesis/migration, never inferred fresh because a key is missing.
            raise intent_gate.Refusal('FULL_RESOURCE_OWNER_HISTORY_PROVISIONING_REQUIRED')
        return self._history()
    def _save(self):
        if gate_bytes(self.gate.state_path)[0]!=self.persisted:
            self.poisoned=True;raise intent_gate.Refusal('FULL_RESOURCE_GATE_PRIOR_HISTORY_CHANGED')
        try:
            intent_gate.save(self.gate.state_path,self.gate.journal)
            raw,current=gate_bytes(self.gate.state_path)
            if current!=self.gate.journal:raise intent_gate.Refusal('FULL_RESOURCE_GATE_READBACK_CHANGED')
            self.persisted=raw
        except BaseException:self.poisoned=True;raise
    def _packet(self,proposed,rows,request):
        if type(request) is not RunRequest:raise intent_gate.Refusal('FULL_RESOURCE_INTENT_INVALID')
        return {'schema':'worldline.protected-resource-request-v1','proposed':dto_record(proposed),
                'rows':[dto_record(row) for row in rows],'request':dto_record(request)}
    def _binding(self,packet,pending):
        request=restore_dto(packet['request'])
        if type(request) is not RunRequest:raise intent_gate.Refusal('FULL_RESOURCE_INTENT_INVALID')
        if not isinstance(pending,dict):raise intent_gate.Refusal('FULL_RESOURCE_PENDING_ABSENT')
        # These are actual Gate-owned operation/Universe/candidate records. Epoch,
        # policy, capability and native records require separately installed full
        # binding crosswalks; this bridge never fills missing fields by assertion.
        def hex_bytes(value):
            if type(value) is not str:return None
            try:encoded=bytes.fromhex(value)
            except ValueError:return None
            return encoded if encoded.hex()==value else None
        operation=hex_bytes(pending.get('operation_id'))
        original_binding=pending.get('resource',{}).get('reserve',{}).get('binding',{})
        universe=hex_bytes(original_binding.get('universe_id'))
        head=hex_bytes(original_binding.get('universe_head'))
        payload=hex_bytes(original_binding.get('candidate_digest'))
        if (operation is None or universe is None or head is None or payload is None
            or request.operation_id!=operation or request.bound.operation!=operation
            or request.scope.universe!=universe or request.bound.universe_head!=head
            or request.bound.payload!=payload):raise intent_gate.Refusal('FULL_RESOURCE_GATE_BINDING_MISMATCH')
        binding=pending.get('full_resource_binding_v1')
        if pending.get('full_resource_scope_v1')!=dto_record(request.scope):
            raise intent_gate.Refusal('FULL_RESOURCE_PROTECTED_SCOPE_UNAVAILABLE')
        if binding!=dto_record(request.bound):raise intent_gate.Refusal('FULL_RESOURCE_PROTECTED_BINDING_UNAVAILABLE')
    def _answer(self,packet,answer):
        request=restore_dto(packet['request'])
        if (type(answer) is not dict or set(answer)!={'status','request_id','state','rows','event_sha256'} or
            answer['status']!='READY' or answer['request_id']!=request.request_id.hex() or
            answer['state']!=packet['proposed'] or answer['rows']!=packet['rows'] or
            type(answer['event_sha256']) is not str):raise intent_gate.Refusal('FULL_RESOURCE_NATIVE_DECISION_REFUSED')
        try:encoded=bytes.fromhex(answer['event_sha256'])
        except ValueError:raise intent_gate.Refusal('FULL_RESOURCE_NATIVE_EVENT_DIGEST_INVALID')
        if encoded.hex()!=answer['event_sha256'] or len(encoded)!=hashlib.sha256().digest_size:
            raise intent_gate.Refusal('FULL_RESOURCE_NATIVE_EVENT_DIGEST_INVALID')
        return detached(answer)
    def _history(self):
        completed={};outstanding=None;dispatched={};prior='GENESIS'
        for event in self.gate.journal['full_resource_history_v2']:
            if (type(event) is not dict or set(event)!={'prior','cause','packet','packet_sha256','result','legacy'} or
                event['prior']!=prior or event['packet_sha256']!=hashlib.sha256(intent_gate.canonical(event['packet'])).hexdigest()):
                raise intent_gate.Refusal('FULL_RESOURCE_INTENT_HISTORY_DIVERGED')
            packet=event['packet'];request=restore_dto(packet['request']);key=request.request_id.hex()
            cause=event['cause']
            if cause in ('SUBMIT','IMPORT_V1'):
                if outstanding is not None or key in completed or event['result'] is not None:
                    raise intent_gate.Refusal('FULL_RESOURCE_INTENT_ORDER_DIVERGED')
                if cause=='IMPORT_V1':
                    legacy=event['legacy']
                    if (type(legacy) is not dict or set(legacy) not in ({'request','sha256'},{'request','sha256','result'}) or
                        legacy['request']!=packet or legacy['sha256']!=event['packet_sha256']):
                        raise intent_gate.Refusal('FULL_RESOURCE_LEGACY_IMPORT_CHANGED')
                elif event['legacy'] is not None:raise intent_gate.Refusal('FULL_RESOURCE_INTENT_HISTORY_DIVERGED')
                outstanding=event
            elif cause=='ACKNOWLEDGE':
                if outstanding is None or outstanding['packet']!=packet or event['legacy'] is not None:
                    raise intent_gate.Refusal('FULL_RESOURCE_ACK_ORDER_DIVERGED')
                answer=self._answer(packet,event['result'])
                legacy=outstanding['legacy']
                if legacy is not None and 'result' in legacy and legacy['result']!=answer:
                    raise intent_gate.Refusal('FULL_RESOURCE_LEGACY_RESULT_CHANGED')
                completed[key]={'packet':packet,'result':answer,'legacy':outstanding['legacy']};outstanding=None
            elif cause=='DISPATCH_INTENT':
                if key not in completed or completed[key]['packet']!=packet or key in dispatched or event['result'] is not None or event['legacy'] is not None:
                    raise intent_gate.Refusal('FULL_RESOURCE_DISPATCH_ORDER_DIVERGED')
                if request.kind!='RECORD_LAUNCH_INTENT':raise intent_gate.Refusal('FULL_RESOURCE_LAUNCH_INTENT_REQUIRED')
                dispatched[key]='INTENDED'
            elif cause in ('DISPATCH_RETURNED','DISPATCH_UNKNOWN'):
                if dispatched.get(key)!='INTENDED' or completed[key]['packet']!=packet or event['legacy'] is not None or type(event['result']) is not dict:
                    raise intent_gate.Refusal('FULL_RESOURCE_DISPATCH_ORDER_DIVERGED')
                dispatched[key]=cause
            else:raise intent_gate.Refusal('FULL_RESOURCE_INTENT_CAUSE_INVALID')
            prior=hashlib.sha256(intent_gate.canonical(event)).hexdigest()
        return completed,outstanding,dispatched
    def _append(self,cause,packet,*,result=None,legacy=None):
        events=self.gate.journal['full_resource_history_v2']
        event={'prior':hashlib.sha256(intent_gate.canonical(events[-1])).hexdigest() if events else 'GENESIS',
               'cause':cause,'packet':detached(packet),'packet_sha256':hashlib.sha256(intent_gate.canonical(packet)).hexdigest(),
               'result':detached(result),'legacy':detached(legacy)}
        events.append(event);self._history();self._save()
    def _rpc(self,packet,*,recover=False,current=False):
        # root_rpc's historical fixed response length would narrow full magnitudes;
        # use its actual root peer credential protocol with unbounded owned framing.
        with socket.socket(socket.AF_UNIX) as connection:
            connection.connect(str(self.socket))
            pid,uid,_gid=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('3i')))
            if pid<=0 or uid!=0:raise intent_gate.Refusal('FULL_RESOURCE_PEER_UNTRUSTED')
            message=({'schema':'worldline.protected-resource-current-v1','request':packet} if current else
                     {'schema':'worldline.protected-resource-recover-v1','request':packet} if recover else packet)
            connection.sendall(intent_gate.canonical(message)+b'\n')
            with connection.makefile('rb') as stream:raw=stream.readline()
        answer=json.loads(raw)
        if raw!=intent_gate.canonical(answer)+b'\n':raise intent_gate.Refusal('FULL_RESOURCE_PEER_RESPONSE_NONCANONICAL')
        if current:return answer
        if recover and answer=={'status':'NOT_COMMITTED'}:return answer
        return self._answer(packet,answer)
    def _reconcile_outstanding(self,outstanding):
        answer=self._rpc(outstanding['packet'],recover=True)
        if answer=={'status':'NOT_COMMITTED'}:raise intent_gate.Refusal('FULL_RESOURCE_INTENT_NOT_COMMITTED_RECONCILIATION_REQUIRED')
        self._append('ACKNOWLEDGE',outstanding['packet'],result=answer)
        return answer
    def _import_legacy(self,packet):
        # Search genuine retained Gate pending/closed history, never an ordinary
        # supplied legacy record. Preserve full old result-bearing row unchanged.
        owners=[*self.gate.journal.get('history',[]),self.gate.journal.get('pending')]
        for owner in owners:
            if not isinstance(owner,dict):continue
            legacy=owner.get('full_resource_intent_v1')
            if not isinstance(legacy,dict) or legacy.get('request')!=packet:continue
            self._binding(packet,owner)
            self._append('IMPORT_V1',packet,legacy=legacy)
            return self._reconcile_outstanding(self._history()[1])
        return None
    def _submit_locked(self,packet):
        completed,outstanding,_dispatched=self._begin()
        key=restore_dto(packet['request']).request_id.hex()
        if key in completed:
            retained=completed[key]
            if retained['packet']!=packet:raise intent_gate.Refusal('FULL_RESOURCE_REQUEST_ID_CONFLICT')
            answer=self._rpc(packet,recover=True)
            if answer!=retained['result']:raise intent_gate.Refusal('FULL_RESOURCE_RETAINED_RESULT_CHANGED')
            return answer
        if outstanding is not None:
            if restore_dto(outstanding['packet']['request']).request_id.hex()==key:
                if outstanding['packet']!=packet:raise intent_gate.Refusal('FULL_RESOURCE_REQUEST_ID_CONFLICT')
                return self._reconcile_outstanding(outstanding)
            self._reconcile_outstanding(outstanding)
        imported=self._import_legacy(packet)
        if imported is not None:return imported
        pending=self.gate.journal.get('pending');self._binding(packet,pending)
        if restore_dto(packet['request']).scope.universe.hex()!=self.gate.config['universe_id']:
            raise intent_gate.Refusal('FULL_RESOURCE_GATE_UNIVERSE_CHANGED')
        # A successful completed ACK permits the next native-checked transition;
        # old completed records remain immutable global history even after Gate
        # closes/clears its current pending operation.
        self._append('SUBMIT',packet)
        answer=self._rpc(packet)
        self._append('ACKNOWLEDGE',packet,result=answer)
        return answer
    def submit(self,*,proposed,rows,request):
        with self.gate.mutex:return self._submit_locked(self._packet(proposed,rows,request))
    def recover(self,*,proposed,rows,request):
        with self.gate.mutex:
            packet=self._packet(proposed,rows,request);completed,outstanding,_dispatched=self._begin()
            key=request.request_id.hex()
            if key in completed:
                if completed[key]['packet']!=packet:raise intent_gate.Refusal('FULL_RESOURCE_REQUEST_ID_CONFLICT')
                answer=self._rpc(packet,recover=True)
                if answer!=completed[key]['result']:raise intent_gate.Refusal('FULL_RESOURCE_RETAINED_RESULT_CHANGED')
                return answer
            if outstanding is not None:
                if outstanding['packet']!=packet:raise intent_gate.Refusal('FULL_RESOURCE_OUTSTANDING_INTENT_CONFLICT')
                return self._reconcile_outstanding(outstanding)
            answer=self._import_legacy(packet)
            if answer is None:raise intent_gate.Refusal('FULL_RESOURCE_PROTECTED_INTENT_ABSENT')
            return answer
    def launch_after_intent(self,*,proposed,rows,request,manager,instance_id,argv,**options):
        from worldline.linux.systemd import SystemdAdapter
        if type(manager) is not SystemdAdapter:raise intent_gate.Refusal('FULL_RESOURCE_MANAGER_UNAVAILABLE')
        if request.kind!='RECORD_LAUNCH_INTENT':raise intent_gate.Refusal('FULL_RESOURCE_LAUNCH_INTENT_REQUIRED')
        planned=('worldline-'+instance_id+'.service').encode('ascii')
        matches=[row for row in rows if row.bound.reservation==request.reservation]
        if len(matches)!=1 or matches[0].planned_unit!=planned:
            raise intent_gate.Refusal('FULL_RESOURCE_PLANNED_UNIT_MISMATCH')
        packet=self._packet(proposed,rows,request)
        with self.gate.mutex:
            self._submit_locked(packet)
            completed,_outstanding,dispatched=self._history();key=request.request_id.hex()
            if key in dispatched:raise intent_gate.Refusal('FULL_RESOURCE_LAUNCH_ALREADY_INTENDED_RECONCILIATION_REQUIRED')
            if completed[key]['legacy'] is not None:
                raise intent_gate.Refusal('FULL_RESOURCE_LEGACY_LAUNCH_CUSTODY_UNKNOWN')
            current=self._rpc(packet,current=True)
            if (type(current) is not dict or set(current)!={'schema','intent_result','state','rows'} or
                current['schema']!='worldline.protected-resource-current-v1' or
                self._answer(packet,current['intent_result'])!=completed[key]['result']):
                raise intent_gate.Refusal('FULL_RESOURCE_CURRENT_LEDGER_UNAVAILABLE')
            state=restore_dto(current['state']);current_rows=tuple(restore_dto(row) for row in current['rows'])
            selected=[row for row in current_rows if row.bound.reservation==request.reservation]
            expected=[row for row in rows if row.bound.reservation==request.reservation]
            if (state.scope!=request.scope or state.universe_head!=request.bound.universe_head or
                len(selected)!=1 or selected!=expected or selected[0].state!='LAUNCH_INTENT'):
                raise intent_gate.Refusal('FULL_RESOURCE_LAUNCH_ROW_CHANGED')
            self._append('DISPATCH_INTENT',packet)
        # This names the real current SystemdAdapter.launch API. Its returned
        # process remains operational data; capture/protected native observation
        # and the later RECORD_RUNNING decision are separate obligations.
            try:
                process=manager.launch(instance_id,argv,**options)
                process.capture_workload_identity()
                from dataclasses import asdict
                self._append('DISPATCH_RETURNED',packet,result={'kind':'OPERATIONAL_RETURN',
                    'unit':process.unit,'identity':asdict(process.workload_identity) if process.workload_identity is not None else None})
                return process
            except BaseException as exc:
                if not self.poisoned:self._append('DISPATCH_UNKNOWN',packet,result={'reason':str(exc)})
                raise

def submit_from_existing_gate(config,packet):
    """Owned standalone entry when the real Gate daemon is stopped.

    This uses the Gate's actual instance lock. A running Gate refuses this
    second principal process; its in-process ordered handler uses the bridge
    directly. The full startup/Controller lease remains a separate obligation.
    """
    import fcntl
    cfg=json.loads(intent_gate.read(config,private=True))
    root=Path(cfg['root'])
    journal=root/'authority/gate/state/journal.json'
    intent_gate.read(journal,private=True)  # missing state cannot become empty genesis
    descriptor=os.open(root/'authority/gate/state/gate.lock',os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        fcntl.flock(descriptor,fcntl.LOCK_EX|fcntl.LOCK_NB)
        gate=intent_gate.Gate(config)
        request=restore_dto(packet['request'])
        proposed=restore_dto(packet['proposed'])
        rows=tuple(restore_dto(row) for row in packet['rows'])
        return FullResourceGateBridge(gate).submit(proposed=proposed,rows=rows,request=request)
    finally:os.close(descriptor)

def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--gate-config',type=Path,required=True)
    parser.add_argument('--protected-intent',type=Path,required=True)
    args=parser.parse_args()
    packet=json.loads(intent_gate.read(args.protected_intent,private=True))
    answer=submit_from_existing_gate(args.gate_config,packet)
    print(intent_gate.canonical(answer).decode('ascii'))

if __name__=='__main__':main()
