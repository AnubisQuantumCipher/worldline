"""Concrete scoped root launch route; confined actor route stays unchanged.

The root hold is the original native reservation and use. Genuine whole scoped
lifecycle, machine admission, measured privileged process and fresh complete
Root_Controller native admission precede exec. The selected registered handler
receives its complete original request through later OFD custody transfer.
"""
import asyncio,hashlib,os,socket,stat,subprocess
from pathlib import Path
from .protected_startup import require,protected,private_bytes,digest
from .root_worker_codec import archive
from .root_worker_plan import handler_plan
from .root_worker_credentials import wait_observation
from .root_worker_process_capture import RootProcessCapture
from .protected_root_supervisor import OwnedRootSupervisor
from .canonical_actor_execution import scoped_components
from .admission import ResourcePolicy

class RootResourceRoute:
    def __init__(self,front):
        from .protected_root_worker import RootWorkerFront
        require(type(front) is RootWorkerFront,'ROOT_RESOURCE_ACTUAL_SELECTED_FRONT_REQUIRED')
        self.front=front;self.p=front.principal;self.resource=scoped_components(self.p)
    def intact(self):
        self.front.intact();require(self.p.resources is self.resource,'ROOT_RESOURCE_PRODUCER_REPLACED')
        self.resource.intact()
    async def launch_root_worker(self,pending,request,reservation):
        from .protected_root_worker import RootWorkerSlot
        from .client_peer import RequestPeer
        from . import resource_scoped_run_ledger as S
        from .protected_resource_runtime import canonical
        self.intact();p=self.p;resource=self.resource
        require(type(request) is RequestPeer and pending is p.pending_for_operation(pending['operation']),
                'ROOT_RESOURCE_REAL_ORIGINAL_PENDING_REQUEST_REQUIRED')
        operation=pending['operation'];capture=p.journal.rows[operation]['capture']
        require(capture['resource_intent'].reservation==reservation and capture['request']==request.observation()
            and p.active_peers.get(operation) is request,'ROOT_RESOURCE_RETAINED_FULL_OPERATION_CHANGED')
        plan=handler_plan(self.front,capture['resource_intent'].bound)
        original_plan=p.policy['plans'][capture['document']['op']]
        require(self.front.plan['cost_key']==original_plan['cost_key'],
                'ROOT_RESOURCE_OWNER_OPERATION_COST_CROSSWALK_UNAVAILABLE')
        before=resource.reconcile_context();rows=[row for row in before.rows if row.bound.reservation==reservation]
        require(len(rows)==1 and rows[0].state=='RESERVED' and rows[0].parent is None,
                'ROOT_RESOURCE_ACTUAL_ORIGINAL_ROOT_RESERVATION_REQUIRED')
        resource.journal.load();retained=resource.journal.rows.get(reservation.hex())
        require(retained is not None and retained['phase']=='NEVER_DISPATCHED'
            and retained['prepared']['payload']['original_request']==request.observation()
            and reservation.hex() not in resource.slots,
                'ROOT_RESOURCE_DISPATCH_REPLAY_OR_UNKNOWN')
        policy=ResourcePolicy.from_mapping(plan['policy'])
        machine=resource.machine_admission(reservation,policy,'DISPATCH')
        unit=b'worldline-root-worker-'+reservation.hex().encode('ascii')+b'.service'
        launch_packet=resource.lifecycle_packet(request,reservation,'RECORD_LAUNCH_INTENT',
            {'state':'LAUNCH_INTENT','planned_unit':unit})
        launch_reply=resource.submit_bound(pending,launch_packet,request)
        row=next(row for row in resource.current_snapshot().rows if row.bound.reservation==reservation)
        directory=Path(self.front.spec['paths']['runtime'])/'root-worker-supervisor'
        protected(directory,directory=True)
        endpoint=directory/reservation.hex();require(not os.path.lexists(endpoint),
            'ROOT_RESOURCE_PRIOR_SUPERVISOR_ENDPOINT_REQUIRES_OWNER_DIAGNOSIS')
        listener=socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET|socket.SOCK_CLOEXEC)
        slot=None
        try:
            listener.bind(str(endpoint));os.chmod(endpoint,0o600);listener.listen()
            ticket=digest(canonical({'row':S.L.dto_record(row),'request':request.observation(),
                                     'launch_head':resource.journal.head}))
            arguments=[self.front.plan['helper'],str(endpoint),ticket,'0','0',plan['cwd'],'--',*plan['argv']]
            command=[self.front.plan['native_components']['systemd_run'],'--system','--no-block',
                '--unit='+unit.decode('ascii'),'--property=Type=exec','--property=RemainAfterExit=yes',
                '--property=Delegate=no','--property=User=root','--property=Group=root',
                *(('--property='+word) for word in plan['systemd_properties']),'--',*arguments]
            for word in (arguments[0],command[0]):self.front.source_lease.file(word,('EXECUTABLE',))
            payload={'ticket':ticket,'endpoint':str(endpoint),'row':S.L.dto_record(row),'plan':plan,
                'launch_intent_packet':S.record(launch_packet),'launch_reply':launch_reply,
                'machine_admission':machine,'helper_arguments':arguments}
            if resource.separate_workload:
                # Complete original requester observation is retained. Root UID
                # is the coordinator credential, never the original requester.
                payload['credential_join']=retained['prepared']['payload']['credential_join']
            dispatch_event=resource.journal.append('DISPATCH_INTENT',reservation.hex(),payload)
            resource.sync_launch_journal(dispatch_event)
            dispatch={'operation':operation,'ticket':ticket,'helper_arguments':arguments,
                'launcher_arguments':command,'resource_dispatch':dispatch_event}
            slot=OwnedRootSupervisor(self.front,row,dispatch,listener,request)
            resource.slots[reservation.hex()]=slot
            root_slot=RootWorkerSlot(self.front,slot,operation,request);self.front.slots[operation]=root_slot
            # Independent custody state survives subsequent target DB closure.
            from .root_worker_root_evidence import append,capture_effect
            events=p.journal.body['events']
            reserved=next(event for event in events if event['operation']==operation and event['cause']=='RESERVED')
            intent=next(event for event in reversed(events) if event['operation']==operation and event['cause']=='EFFECT_INTENT')
            append(self.front,operation,'PREPARED',{'full_launch_packet':launch_packet,
                'full_launch_reply':launch_reply,'full_dispatch':dispatch,'full_original_request':request.observation()},
                {'prepared':{'reserved':reserved,'intent':intent}})
            slot.launcher_effects=[]
            def launch_effect(call,args,fn):
                try:value,receipt=capture_effect(self.front.source_lease,call,args,fn)
                except OSError as error:
                    slot.launcher_effects.append(error.custody_receipt)
                    raise
                slot.launcher_effects.append(receipt)
                return value
            launch_dir=Path(self.front.spec['paths']['runtime'])/'root-launch'/operation
            launch_effect('mkdir',{'path':str(launch_dir),'mode':0o700,'parents':True,'exist_ok':False},
                lambda:launch_dir.mkdir(mode=0o700,parents=True,exist_ok=False))
            protected(launch_dir,directory=True)
            outputs=[]
            launch_error=None;slot.launcher_cleanup_errors=[]
            try:
                for name in ('stdout','stderr'):
                    output_path=launch_dir/(name+'.bin')
                    flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC
                    outputs.append(launch_effect('open',{'path':str(output_path),'flags':flags,'mode':0o600},
                        lambda:os.open(output_path,flags,0o600)))
                def create_launcher():
                    slot.launcher=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=outputs[0],stderr=outputs[1],
                        close_fds=True,env={'PATH':'/usr/bin:/bin','LANG':'C'})
                    return slot.launcher.pid
                launch_effect('Popen',{'argv':command,'stdin':subprocess.DEVNULL,'stdout':outputs[0],
                    'stderr':outputs[1],'close_fds':True,'env':{'PATH':'/usr/bin:/bin','LANG':'C'}},create_launcher)
                slot.launcher_capture={'paths':tuple(str(launch_dir/(name+'.bin')) for name in ('stdout','stderr')),
                    'argv':command,'actual_pid':slot.launcher.pid}
            except BaseException as error:
                launch_error=error
                raise
            finally:
                close_errors=[]
                for fd in outputs:
                    try:launch_effect('close',{'fd':fd},lambda:os.close(fd))
                    except BaseException as error:
                        close_errors.append(error)
                        slot.launcher_cleanup_errors.append({'type':type(error).__qualname__,
                            'module':type(error).__module__,'message':str(error),'args':error.args,
                            'errno':getattr(error,'errno',None)})
                if close_errors:
                    if launch_error is None:raise close_errors[0]
                    for error in close_errors:launch_error.add_note('Original launcher descriptor close: '+str(error))
            # Actual --no-block transport wait is retained but never establishes
            # workload terminal state. Namespace ECHILD/helper pidfd and later
            # true outer wait remain independent obligations.
            from .root_worker_root_evidence import wait_launcher
            launch_wait,slot.launcher_wait_receipt=await asyncio.to_thread(wait_launcher,self.front,slot.launcher)
            require(launch_wait==0,'ROOT_RESOURCE_ACTUAL_DISPATCH_TRANSPORT_FAILED')
            slot.machine_dispatch=machine
            await asyncio.to_thread(slot.accept_held)
            held=slot.observe();held_event=resource.journal.append('HELD',reservation.hex(),
                {'root_held':S.record(slot.held),'full_physical':S.record(held)})
            resource.sync_launch_journal(held_event)
            physical=held['native_fields']
            running=resource.lifecycle_packet(request,reservation,'RECORD_RUNNING',{'state':'RUNNING',
                'actual_unit':physical['actual_unit'],'cgroup':physical['cgroup'],'invocation':physical['invocation']})
            running_reply=resource.submit_bound(pending,running,request)
            slot.row=next(row for row in resource.current_snapshot().rows if row.bound.reservation==reservation)
            resource.actor_slots[reservation]={'original_request':request,'pending':pending,'plan':plan}
            # Raw streams are owned before GO or exec; no pipe-pressure gap can
            # strand the held worker while native/custody checks are performed.
            await slot.start_raw_drains()
            machine=resource.machine_admission(reservation,policy,'GO')
            go_event=resource.journal.append('GO_INTENT',reservation.hex(),
                {'root_running_packet':S.record(running),'root_running_reply':running_reply,
                 'machine_admission':machine,'root_owner_journal':slot.held_event})
            resource.sync_launch_journal(go_event)
            from .root_worker_root_evidence import scoped_commit
            slot.begin_go({'packet':running,'reply':running_reply,'launch_event':go_event},machine,
                scoped_commit(resource,running))
            measured=await asyncio.to_thread(wait_observation,slot.credential_receiver,ticket.encode('ascii'))
            require(measured.sender_real_uid==0 and measured.uids==(0,0,0),
                    'ROOT_RESOURCE_GENUINE_PRIVILEGED_MEASURED_WORKER_REQUIRED')
            slot.worker_pidfd=os.pidfd_open(measured.host_pid,0)
            host_proc=os.open('/proc',os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
            try:
                source_id=hashlib.sha256(canonical(S.record(self.front.spec))).digest()
                process,process_raw=RootProcessCapture(host_proc,slot.worker_pidfd,slot.namespace_fd,
                    self.front.source_lease).capture(slot.row.actual_unit,slot.row.invocation,source_id)
            finally:os.close(host_proc)
            slot.bind_actual_worker(process,process_raw,measured)
            material=self.front.capture_root_material(slot.complete_capture(),slot.custody_channel,request)
            native=self.front.authority.decide(material)
            self.front.retain_native('ROOT_NATIVE_BEFORE_COORDINATOR_EXEC',material,native)
            slot.commit_execution(material,native,measured,process)
            return slot
        except BaseException as error:
            if slot is not None:await slot.retain_and_stop_unknown(error,None)
            else:
                resource.journal.append('UNKNOWN',reservation.hex(),{'cause':type(error).__name__,
                    'message':str(error),'endpoint':str(endpoint)})
            # Complete launch intent, original hold and endpoint stay retained.
            raise
    def detach_state_for_exec(self,offer,*,close_state=True):
        from .root_worker_custody import CustodyOffer
        require(type(offer) is CustodyOffer and offer.p is self.p,
                'ROOT_RESOURCE_EXACT_CUSTODY_OFFER_REQUIRED')
        require(self.front.phase=='FRONT_CLOSE_INTENDED' and self.front.operation==offer.slot.operation,
                'ROOT_RESOURCE_RELINQUISH_SEQUENCE_CHANGED')
        self.front.lease.intact();self.resource.intact();resource=self.resource
        require(offer.owned_roster.front is self.front and offer.owned_roster.producer is resource,
                'ROOT_RESOURCE_COMPLETE_OTHER_LIVE_DESCRIPTOR_ESCROW_REQUIRED')
        offer.owned_roster.intact()
        resource.journal.load();resource.scoped_service.snapshot()
        # Close state owners only. Original OFDs remain in lease+offer escrow;
        # independent root journal and all actual transport descriptors survive.
        if close_state:
            resource.observations.close();resource.journal.db.close();resource.poisoned=True
