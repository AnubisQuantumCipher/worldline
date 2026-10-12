"""Actual V3 six-descriptor owner; immutable V1/V2 remain separate inputs.

The owned measurement channel is serialized under the protected producer order.
The trusted child sends its sole packet and waits; extra/changed queued extent
refuses. Actual full native/durable execution and proof controls remain UNRUN.
"""
from __future__ import annotations
from pathlib import Path
import array,asyncio,fcntl,hashlib,os,select,socket,stat,struct,subprocess,shutil
from .protected_resource_runtime import private,canonical,digest,kernel_bytes,identity_record,require,ResourceProducerRefusal
HEADER=b'WL-RESOURCE-SUPERVISOR-v3\n'

class OwnedSupervisorV3:
    """A real kernel channel/namespace/pidfd owner, never a reconstructed DTO."""
    def __init__(self,principal,row,dispatch,listener):
        self.principal,self.row,self.dispatch,self.listener=principal,row,dispatch,listener
        self.connection=None;self.namespace_fd=None;self.namespace_pidfd=None;self.helper_pidfd=None
        self.credential_receiver=None;self.actor_pidfd=None;self.credential_committed=None;
        self.stdout_fd=None;self.stderr_fd=None;self.stdout=None;self.stderr=None;self.pipe_transports=[]
        self.stdin_fd=None;self.stdin_binding=None;self.stdin_started=False;self.stdin_complete=None;self.stdin_fault=None
        self.credential_ack_event=None
        self.held=None;self.closed=None;self.closed_event=None;self.started=False;self.failed=False
    def manager(self):
        p=self.principal
        names=('Id','MainPID','InvocationID','ControlGroup','Delegate','ActiveState','SubState')
        answer=subprocess.run([p.cfg['systemctl'],'--system','show',self.row.planned_unit.decode('ascii'),
            '--no-pager',*(('--property='+name) for name in names)],stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,env={'PATH':'/usr/bin:/bin','LANG':'C'})
        require(answer.returncode==0,'RESOURCE_ACTUAL_MANAGER_OBSERVATION_UNAVAILABLE')
        parts=answer.stdout.splitlines();parsed={}
        for raw in parts:
            name,separator,value=raw.partition(b'=');require(separator and name.decode('ascii') in names
                and name not in parsed,'RESOURCE_MANAGER_PROPERTY_INVALID');parsed[name]=value
        require(set(parsed)=={name.encode('ascii') for name in names}
            and parsed[b'Id']==self.row.planned_unit,'RESOURCE_MANAGER_UNIT_CHANGED')
        return parsed,{'stdout':answer.stdout.hex(),'stderr':answer.stderr.hex(),'returncode':answer.returncode}
    @staticmethod
    def number(raw):
        require(raw and raw.isdigit() and str(int(raw)).encode('ascii')==raw,'RESOURCE_KERNEL_DECIMAL_INVALID')
        return int(raw)
    @staticmethod
    def pidfd_state(fd):
        poll=select.poll();poll.register(fd,select.POLLIN|select.POLLHUP|select.POLLERR)
        events=poll.poll(0)
        require(not any(mask&select.POLLERR for _fd,mask in events),'RESOURCE_PIDFD_STATUS_UNKNOWN')
        return b'PIDFD_TERMINAL' if events else b'PIDFD_LIVE'
    @staticmethod
    def fd_pid(fd):
        raw=kernel_bytes('/proc/self/fdinfo/'+str(fd));matches=[line.removeprefix(b'Pid:\t') for line in raw.splitlines() if line.startswith(b'Pid:\t')]
        require(len(matches)==1,'RESOURCE_ACTUAL_PIDFD_UNAVAILABLE');return OwnedSupervisorV3.number(matches[0]),raw
    def accept_held(self):
        p=self.principal;p.intact();connection,_address=self.listener.accept()
        self.connection=connection
        owned=[]
        try:
            raw_peer=connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('@iII'))
            helper_pid,uid,gid=struct.unpack('@iII',raw_peer)
            require(helper_pid>0 and uid==0,'RESOURCE_SUPERVISOR_KERNEL_PEER_REFUSED')
            body,control,flags,_address=connection.recvmsg(p.channel_extent(),socket.CMSG_SPACE(array.array('i').itemsize*6),socket.MSG_CMSG_CLOEXEC)
            unknown_control=False
            for level,kind,raw in control:
                if level!=socket.SOL_SOCKET or kind!=socket.SCM_RIGHTS:
                    unknown_control=True;continue
                rights=array.array('i');extent=len(raw)-len(raw)%rights.itemsize
                rights.frombytes(raw[:extent]);owned.extend(rights)
                if extent!=len(raw):unknown_control=True
            require(not flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC),'RESOURCE_SUPERVISOR_FRAME_TRUNCATED')
            require(not unknown_control,'RESOURCE_SUPERVISOR_CONTROL_UNKNOWN')
            require(len(owned)==6,'RESOURCE_SUPERVISOR_DESCRIPTOR_ROSTER_INVALID')
            parts=body.split(b'\n')
            require(len(parts)==5 and parts[:2]==[HEADER.removesuffix(b'\n'),b'HELD'] and parts[2]==self.dispatch['payload']['ticket'].encode('ascii')
                and parts[-1]==b'','RESOURCE_SUPERVISOR_HELD_FRAME_INVALID')
            init_pid=self.number(parts[3]);require(init_pid>0,'RESOURCE_SUPERVISOR_INIT_PID_INVALID')
            ns,pidfd,out,err,credential,stdin_writer=owned;
            self.credential_receiver=socket.socket(fileno=credential)
            # A successfully constructed socket owns this descriptor. Remove
            # it from the raw roster before any subsequent validation can fail.
            owned.remove(credential)
            require(self.credential_receiver.family==socket.AF_UNIX and self.credential_receiver.getsockopt(socket.SOL_SOCKET,socket.SO_TYPE)==socket.SOCK_SEQPACKET
                and self.credential_receiver.getsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED)==1,'RESOURCE_ACTUAL_CREDENTIAL_CHANNEL_REQUIRED')
            self.namespace_fd,self.namespace_pidfd=ns,pidfd
            self.stdout_fd,self.stderr_fd,self.stdin_fd=out,err,stdin_writer;owned=[]
            require(stat.S_ISFIFO(os.fstat(stdin_writer).st_mode)
                and fcntl.fcntl(stdin_writer,fcntl.F_GETFL)&os.O_ACCMODE==os.O_WRONLY,
                'RESOURCE_ACTUAL_V3_STDIN_WRITER_REQUIRED')
            require(all(fcntl.fcntl(fd,fcntl.F_GETFL)&os.O_ACCMODE==os.O_RDONLY for fd in (out,err)),
                'RESOURCE_ACTUAL_V3_OUTPUT_READERS_REQUIRED')
            require(stat.S_ISFIFO(os.fstat(out).st_mode) and stat.S_ISFIFO(os.fstat(err).st_mode),
                'RESOURCE_SUPERVISOR_ACTUAL_OUTPUT_PIPE_REQUIRED')
            actual_pid,raw_fd=self.fd_pid(pidfd);require(actual_pid==init_pid,'RESOURCE_SUPERVISOR_PIDFD_BINDING_CHANGED')
            actual_ns=os.open('/proc/'+str(init_pid)+'/ns/pid',os.O_RDONLY|os.O_CLOEXEC)
            try:require(identity_record(os.fstat(ns))==identity_record(os.fstat(actual_ns)),'RESOURCE_SUPERVISOR_NAMESPACE_BINDING_CHANGED')
            finally:os.close(actual_ns)
            self.helper_pidfd=os.pidfd_open(helper_pid,0)
            helper_again,helper_fd=self.fd_pid(self.helper_pidfd);require(helper_again==helper_pid,'RESOURCE_SUPERVISOR_PEER_PIDFD_CHANGED')
            properties,manager=self.manager()
            require(self.number(properties[b'MainPID'])==helper_pid and properties[b'InvocationID']
                and properties[b'ControlGroup'].startswith(b'/'),'RESOURCE_MANAGER_HELPER_BINDING_CHANGED')
            image=Path(os.readlink('/proc/'+str(helper_pid)+'/exe'))
            require(image==p.helper and digest(private(image))==p.cfg['helper_sha256'],'RESOURCE_ACTUAL_SUPERVISOR_IMAGE_CHANGED')
            maps=kernel_bytes('/proc/'+str(helper_pid)+'/maps')
            for line in maps.splitlines():
                pieces=line.split(None,5)
                if len(pieces)==6 and pieces[5].startswith(b'/'):
                    mapped=Path(os.fsdecode(pieces[5]));require(mapped in p.lease.allowed,'RESOURCE_SUPERVISOR_MAPPED_RUNTIME_UNPINNED');private(mapped)
            proc_cgroup=kernel_bytes('/proc/'+str(helper_pid)+'/cgroup')
            require(proc_cgroup==b'0::'+properties[b'ControlGroup']+b'\n','RESOURCE_HELPER_CGROUP_BINDING_CHANGED')
            command_line=kernel_bytes('/proc/'+str(helper_pid)+'/cmdline')
            require(command_line==b'\0'.join(os.fsencode(word) for word in self.dispatch['payload']['helper_arguments'])+b'\0',
                'RESOURCE_ACTUAL_SUPERVISOR_COMMAND_CHANGED')
            namespace=canonical(identity_record(os.fstat(ns)));peer=raw_peer
            challenge=hashlib.sha256(canonical({'dispatch':self.dispatch,'held_frame':body.hex(),'peer':peer.hex(),
                'namespace':namespace.hex(),'manager':manager,'maps':maps.hex(),'proc_cgroup':proc_cgroup.hex()})).digest()
            self.held={'frame':body.hex(),'peer':peer.hex(),'helper_pid':helper_pid,'init_pid':init_pid,'namespace':namespace.hex(),
                'pidfd_info':raw_fd.hex(),'helper_pidfd_info':helper_fd.hex(),'manager':manager,'properties':{name.decode():value.hex() for name,value in properties.items()},
                'maps':maps.hex(),'proc_cgroup':proc_cgroup.hex(),'cmdline':command_line.hex(),'challenge':challenge.hex(),'helper_sha256':p.cfg['helper_sha256'],
                'stdout_identity':identity_record(os.fstat(out)),'stderr_identity':identity_record(os.fstat(err)),
                'stdin_identity':identity_record(os.fstat(stdin_writer)),
                'stdin_flags':fcntl.fcntl(stdin_writer,fcntl.F_GETFL),
                'stdin_fdinfo':kernel_bytes('/proc/self/fdinfo/'+str(stdin_writer)).hex()}
            event=p.journal.append('HELD',self.row.bound.reservation.hex(),self.held)
            p.sync_launch_journal(event)
            self.held_event=event;connection.setblocking(False);return self.observe()
        except BaseException:
            self.failed=True
            for fd in owned:os.close(fd)
            self.close()
            raise
    def poll_closed(self):
        if self.closed is not None or self.failed:return
        try:body,control,flags,_address=self.connection.recvmsg(self.principal.channel_extent(),socket.CMSG_SPACE(array.array('i').itemsize),socket.MSG_CMSG_CLOEXEC)
        except BlockingIOError:return
        owned=[]
        try:
            for level,kind,raw in control:
                if level==socket.SOL_SOCKET and kind==socket.SCM_RIGHTS:
                    rights=array.array('i');extent=len(raw)-len(raw)%rights.itemsize
                    rights.frombytes(raw[:extent]);owned.extend(rights)
                    require(extent==len(raw),'RESOURCE_SUPERVISOR_RIGHTS_INVALID')
            require(body and not control and not flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC),'RESOURCE_SUPERVISOR_CLOSURE_UNAVAILABLE')
            parts=body.split(b'\n')
            require(len(parts)==7 and parts[:2]==[HEADER.removesuffix(b'\n'),b'CLOSED']
                and parts[2]==self.dispatch['payload']['ticket'].encode('ascii') and self.number(parts[3])==self.held['init_pid']
                and parts[5:]==[b'ECHILD',b''],'RESOURCE_SUPERVISOR_CLOSURE_INVALID')
            status=self.number(parts[4]);require(os.WIFEXITED(status) or os.WIFSIGNALED(status),'RESOURCE_SUPERVISOR_MAIN_WAIT_INVALID')
            require(self.pidfd_state(self.namespace_pidfd)==b'PIDFD_TERMINAL','RESOURCE_SUPERVISOR_NAMESPACE_NOT_TERMINAL')
            raw_peer=self.connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('@iII'))
            require(raw_peer.hex()==self.held['peer'],'RESOURCE_SUPERVISOR_CLOSED_PEER_CHANGED')
            self.closed={'frame':body.hex(),'peer':raw_peer.hex(),'namespace':canonical(identity_record(os.fstat(self.namespace_fd))).hex(),
                'held':digest(canonical(self.held_event)),'main_wait_status':status}
            self.closed_event=self.principal.journal.append('CLOSED',self.row.bound.reservation.hex(),self.closed)
            self.principal.sync_launch_journal(self.closed_event)
            self.connection.sendall(b'A')
        except BaseException:
            self.failed=True;raise
        finally:
            for fd in owned:os.close(fd)
    def cgroup(self,raw_path):
        require(raw_path.startswith(b'/') and b'..' not in raw_path.split(b'/') and b'\0' not in raw_path,'RESOURCE_KERNEL_CGROUP_PATH_INVALID')
        path=Path('/sys/fs/cgroup')/os.fsdecode(raw_path.removeprefix(b'/'));private(path,directory=True)
        # Every ancestor and every retained subgroup lacks an unprivileged
        # migration write. No delegated user manager is used for this launch.
        for root,directories,files in os.walk(path,followlinks=False):
            private(root,directory=True)
            for name in ('cgroup.procs','cgroup.threads','cgroup.subtree_control'):
                selected=Path(root)/name
                if selected.exists():private(selected)
        info=path.lstat();events=kernel_bytes(path/'cgroup.events');kind=kernel_bytes(path/'cgroup.type')
        return info,events,kind,{'path':str(path),'identity':identity_record(info),'events':events.hex(),'type':kind.hex()}
    def observe(self):
        p=self.principal;p.intact();require(self.held is not None and not self.failed,'RESOURCE_OWNED_SUPERVISOR_OBSERVATION_UNAVAILABLE')
        self.poll_closed();properties,manager=self.manager()
        retained=self.held['properties'];cg=bytes.fromhex(retained['ControlGroup']);inv=bytes.fromhex(retained['InvocationID'])
        require(properties[b'InvocationID']==inv and properties[b'ControlGroup']==cg,'RESOURCE_MANAGER_INVOCATION_CHANGED')
        info,events,kind,cgroup=self.cgroup(cg)
        peer=self.connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('@iII'))
        require(peer.hex()==self.held['peer'],'RESOURCE_OWNED_SUPERVISOR_PEER_CHANGED')
        namespace=canonical(identity_record(os.fstat(self.namespace_fd)))
        require(namespace.hex()==self.held['namespace'],'RESOURCE_OWNED_NAMESPACE_CHANGED')
        namespace_wait=self.pidfd_state(self.namespace_pidfd);helper_wait=self.pidfd_state(self.helper_pidfd)
        if helper_wait==b'PIDFD_LIVE':
            require(self.number(properties[b'MainPID'])==self.held['helper_pid'],'RESOURCE_MANAGER_LIVE_HELPER_CHANGED')
            actual_image=Path(os.readlink('/proc/'+str(self.held['helper_pid'])+'/exe'))
            require(actual_image==p.helper and digest(private(actual_image))==p.cfg['helper_sha256'],'RESOURCE_LIVE_SUPERVISOR_IMAGE_CHANGED')
        else:require(properties[b'MainPID']==b'0','RESOURCE_MANAGER_TERMINAL_HELPER_CHANGED')
        phase='NAMESPACE_CLOSED' if self.closed is not None else 'NAMESPACE_HELD'
        raw={'held':self.held,'closed':self.closed,'manager':manager,'cgroup':cgroup,'namespace_wait':namespace_wait.hex(),'helper_wait':helper_wait.hex()}
        native={'dispatch':bytes.fromhex(digest(canonical(self.dispatch))),'actual_unit':properties[b'Id'],'cgroup':cg,'invocation':inv,
            'namespace':namespace,'held_namespace':bytes.fromhex(self.held['namespace']),'peer':peer,'held_peer':bytes.fromhex(self.held['peer']),
            'helper_image':bytes.fromhex(p.cfg['helper_sha256']),'expected_helper_image':bytes.fromhex(p.cfg['helper_sha256']),
            'challenge':bytes.fromhex(self.held['challenge']),'held_challenge':bytes.fromhex(self.held['challenge']),
            'protocol':b'CLOSED_ECHILD' if self.closed is not None else b'HELD',
            'closed_event':bytes.fromhex(digest(canonical(self.closed_event))) if self.closed_event is not None else None,
            'namespace_wait':namespace_wait,'helper_wait':helper_wait,'cgroup_events':events,'cgroup_type':kind,'manager_delegate':properties[b'Delegate'],
            'cgroup_owner':info.st_uid,'cgroup_group_write':info.st_mode&stat.S_IWGRP,'cgroup_other_write':info.st_mode&stat.S_IWOTH,'phase':phase}
        return {'native_fields':native,'raw':raw}
    def go(self):
        # The exact protected producer owns native current/use/physical checks
        # and the durable witness; generic parser/ACK bytes grant nothing.
        return self.principal.go_scoped(self)
    def bind_actor_stdin(self,process):
        """Actual held writer -> measured live child fd0, before credential ACK."""
        p=self.principal;p.intact()
        require(self.stdin_fd is not None and self.stdin_binding is None
            and self.held is not None and self.credential_committed is None
            and self.pidfd_state(self.actor_pidfd)==b'PIDFD_LIVE',
            'RESOURCE_V3_PREACK_ACTUAL_ACTOR_STDIN_REQUIRED')
        writer=identity_record(os.fstat(self.stdin_fd))
        require(writer==self.held['stdin_identity']
            and fcntl.fcntl(self.stdin_fd,fcntl.F_GETFL)&os.O_ACCMODE==os.O_WRONLY,
            'RESOURCE_V3_HELD_STDIN_WRITER_CHANGED')
        root=Path('/proc')/str(process['pid'])
        before=kernel_bytes(root/'fdinfo/0')
        flags=[line.split(b'\t',1)[1] for line in before.splitlines() if line.startswith(b'flags:\t')]
        require(len(flags)==1 and int(flags[0],8)&os.O_ACCMODE==os.O_RDONLY,
            'RESOURCE_V3_MEASURED_ACTOR_STDIN_READ_ENDPOINT_REQUIRED')
        fd=os.open(root/'fd/0',os.O_PATH|os.O_CLOEXEC)
        try:
            info=os.fstat(fd)
            require(stat.S_ISFIFO(info.st_mode) and identity_record(info)==writer,
                'RESOURCE_V3_ACTOR_STDIN_PIPE_BINDING_CHANGED')
        finally:os.close(fd)
        after=kernel_bytes(root/'fdinfo/0')
        require(after==before and self.pidfd_state(self.actor_pidfd)==b'PIDFD_LIVE',
            'RESOURCE_V3_ACTOR_STDIN_CAPTURE_CHANGED')
        self.stdin_binding={'schema':'worldline.actual-v3-actor-stdin-binding-v1',
            'held':self.held_event,'dispatch':self.dispatch,'writer':writer,
            'writer_fdinfo':kernel_bytes('/proc/self/fdinfo/'+str(self.stdin_fd)),
            'actor_pid':process['pid'],'actor_fdinfo':before,'actor_pidfd_info':process['fdinfo'],
            'actor_namespace':process['namespace'],'actor_wait':process['wait']}
        return self.stdin_binding
    def _input_commit(self):
        """Full authentic native witness + actual sent ACK; no Boolean shortcut."""
        from . import resource_scoped_run_ledger as S
        p=self.principal;p.intact()
        require(self.started and not self.failed and self.credential_committed is not None
            and self.credential_ack_event is not None and self.stdin_binding is not None,
            'RESOURCE_V3_FULL_DURABLE_CREDENTIAL_ACK_REQUIRED')
        with p.gate.mutex,p.order:
            p.observations.load();events=p.observations.events
            require(self.credential_committed in events and self.credential_ack_event in events,
                'RESOURCE_V3_FULL_AUTHENTIC_ACK_HISTORY_CHANGED')
            witness=S.restore(self.credential_committed['payload'])
            ack=S.restore(self.credential_ack_event['payload'])
            require(self.credential_committed['cause']=='ACTOR_NATIVE_COMMITTED'
                and self.credential_ack_event['cause']=='ACTOR_ACK_SENT'
                and self.credential_ack_event['reservation']==self.row.bound.reservation.hex()
                and ack['committed_event']==self.credential_committed
                and witness['input_transport']==self.stdin_binding
                and witness['held_event']==self.held_event and witness['dispatch']==self.dispatch,
                'RESOURCE_V3_DURABLE_INPUT_ACTOR_OR_ACK_BINDING_CHANGED')
            native=p.actor_kernel.check(witness['packet'],witness['actor'],witness['capabilities'],
                witness['groups'],witness['proc_groups'])
            composite=p.execution_kernel.check(witness['packet'],witness['actor'],witness['capabilities'],
                witness['groups'],witness['proc_groups'],witness['crosswalk'],
                witness['authority']['authority_snapshot'])
            require(native==witness['native'] and composite==witness['composite']
                and native.status=='READY_CONJUNCT' and composite.status=='READY_VALUE_CONJUNCTION',
                'RESOURCE_V3_FULL_NATIVE_INPUT_EXECUTION_REDECISION_REFUSED')
            return witness
    def _close_owned_input(self,fd):
        canonical=getattr(self.principal.lease,'canonical_operation_principal',None)
        owner=getattr(canonical,'root_worker_process',None) or getattr(canonical,'root_worker',None)
        if owner is None:
            self.stdin_fd=None;os.close(fd)
            return
        from .root_worker_root_evidence import close_owned_stdin
        return close_owned_stdin(self,fd)

    def close_empty_input(self):
        # Preserve original root helper empty stdin after full native/durable
        # ACK. It is never the original WORLDLINE adapter mission route.
        self._input_commit()
        require(not self.stdin_started and self.stdin_fd is not None,
            'RESOURCE_V3_STDIN_ALREADY_DELIVERED_OR_CLOSED')
        self.stdin_started=True;p=self.principal;fd=self.stdin_fd;intent=None
        try:
            intent=p.observations.append('ACTOR_STDIN_INTENT',self.row.bound.reservation.hex(),
                {'payload':b'','input_transport':self.stdin_binding,
                 'actor_commit':self.credential_committed,'ack':self.credential_ack_event,
                 'kind':'original-root-empty-EOF'})
            self._close_owned_input(fd)
            self.stdin_complete=p.observations.append('ACTOR_STDIN_COMPLETE',self.row.bound.reservation.hex(),
                {'intent':intent,'written':0,'payload':b'','EOF_close_returned':True})
        except BaseException as exc:
            self.stdin_fault=exc
            try:p.observations.append('ACTOR_STDIN_UNKNOWN',self.row.bound.reservation.hex(),
                {'intent':intent,'written':0,'payload':b'','exception_text':str(exc)})
            except BaseException as retention:exc.add_note('empty EOF fault retention also failed: '+repr(retention))
            if self.stdin_fd is not None:
                try:self._close_owned_input(fd)
                except BaseException as close_error:exc.add_note('empty owned input close also failed: '+repr(close_error))
            raise
    async def stop_owned_transport(self,reason):
        # Genuine original owner cleanup only. An actual root manager answer
        # and raw main/namespace/helper waits remain independent obligations.
        p=self.principal;p.intact()
        require(p.slots.get(self.row.bound.reservation.hex()) is self and self.held is not None,
            'RESOURCE_V3_ACTUAL_ORIGINAL_STOP_OWNER_REQUIRED')
        properties,before=self.manager()
        require(properties[b'InvocationID']==bytes.fromhex(self.held['properties']['InvocationID'])
            and properties[b'ControlGroup']==bytes.fromhex(self.held['properties']['ControlGroup']),
            'RESOURCE_V3_STOP_INVOCATION_CHANGED')
        intent=p.observations.append('ACTOR_TRANSPORT_STOP_INTENT',self.row.bound.reservation.hex(),
            {'held':self.held_event,'dispatch':self.dispatch,'manager':before,
             'reason_type':[type(reason).__module__,type(reason).__name__],'reason_text':str(reason)})
        answer=await asyncio.to_thread(subprocess.run,
            [p.cfg['systemctl'],'--system','stop',self.row.planned_unit.decode('ascii')],
            stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,
            env={'PATH':'/usr/bin:/bin','LANG':'C'})
        event=p.observations.append('ACTOR_TRANSPORT_STOP_REPLY',self.row.bound.reservation.hex(),
            {'intent':intent,'stdout':answer.stdout,'stderr':answer.stderr,'returncode':answer.returncode})
        require(answer.returncode==0,'RESOURCE_V3_OWNED_MANAGER_STOP_UNKNOWN')
        return event
    async def write_input(self,payload):
        require(type(payload) is bytes,'RESOURCE_V3_FULL_INPUT_BYTES_REQUIRED')
        witness=self._input_commit()
        require(self.stdout is not None and self.stderr is not None
            and not self.stdin_started and self.stdin_fd is not None,
            'RESOURCE_V3_OUTPUT_OWNERSHIP_BEFORE_SINGLE_INPUT_REQUIRED')
        require(identity_record(os.fstat(self.stdin_fd))==self.held['stdin_identity'],
            'RESOURCE_V3_INPUT_DESCRIPTOR_REPLACED')
        self.stdin_started=True;p=self.principal;offset=0
        # Full lossless payload is retained before writes; this observation is
        # not a new native grant, use, exchange, terminal verdict or retry.
        intent=None;fd=self.stdin_fd
        try:
            intent=p.observations.append('ACTOR_STDIN_INTENT',self.row.bound.reservation.hex(),
                {'payload':payload,'input_transport':self.stdin_binding,
                 'actor_commit':self.credential_committed,'ack':self.credential_ack_event,
                 'authority':witness['authority']})
            loop=asyncio.get_running_loop();os.set_blocking(fd,False)
            view=memoryview(payload)
            while offset<len(view):
                try:
                    written=os.write(fd,view[offset:])
                    require(written>0,'RESOURCE_V3_INPUT_WRITE_NO_PROGRESS');offset+=written
                except InterruptedError:continue
                except BlockingIOError:
                    ready=loop.create_future()
                    def writable():
                        if not ready.done():ready.set_result(None)
                    loop.add_writer(fd,writable)
                    try:await ready
                    finally:loop.remove_writer(fd)
            # Close the sole writer exactly once for EOF. Failed close is an
            # input fault; it never erases a genuine CLOSED/main failure record.
            self._close_owned_input(fd)
            complete=p.observations.append('ACTOR_STDIN_COMPLETE',self.row.bound.reservation.hex(),
                {'intent':intent,'written':offset,'payload':payload,'EOF_close_returned':True})
            self.stdin_complete=complete;return complete
        except BaseException as exc:
            self.stdin_fault=exc
            try:
                p.observations.append('ACTOR_STDIN_UNKNOWN',self.row.bound.reservation.hex(),
                    {'intent':intent,'written':offset,'payload':payload,
                     'exception_type':[type(exc).__module__,type(exc).__name__],
                     'exception_text':str(exc)})
            except BaseException as retention:
                exc.add_note('full input fault retention also failed: '+repr(retention))
            if self.stdin_fd is not None:
                try:self._close_owned_input(fd)
                except BaseException as close_error:exc.add_note('owned input close also failed: '+repr(close_error))
            # Do not set failed: authentic owned CLOSED/ECHILD with nonzero raw
            # main status remains observable and is not a successful mission.
            raise
    async def capture_owned_failure(self,primary,*,output_tasks=None,input_task=None,wait_task=None):
        """Own all post-launch refusal paths; this never settles/releases a row.

        Stop replies, local closes and pipe EOF remain factual observations.
        Only actual CLOSED/ECHILD/init/helper waits may establish owned closure.
        Missing/replaced custody, persistence or physical closure stays UNKNOWN.
        """
        p=self.principal
        require(p.slots.get(self.row.bound.reservation.hex()) is self and self.held is not None,
            'RESOURCE_V3_FAILURE_ACTUAL_OWNED_SLOT_REQUIRED')
        record={'schema':'worldline.actual-owned-v3-failure-capture-v1',
            'primary_type':[type(primary).__module__,type(primary).__name__],
            'primary_text':str(primary),'held':self.held_event,'dispatch':self.dispatch,
            'credential_commit':self.credential_committed,'ack':self.credential_ack_event,
            'input_transport':self.stdin_binding,'input_complete':self.stdin_complete,
            'original_output_pending_reads':dict(getattr(self,'original_output_reads',{})),
            'stdin_close_returned':None,'stop':None,'wait':None,'closed':None,
            'closed_event':None,'output_eof':{'stdout':None,'stderr':None},
            'errors':[],'status':'UNKNOWN','resource_release_or_charge':False}
        self.failure_capture=record;self.failure_result_event=None
        def failure(label,error):
            item={'site':label,'type':[type(error).__module__,type(error).__name__],
                'text':str(error)};record['errors'].append(item)
            primary.add_note(label+' also failed: '+repr(error))
        def retain(kind,payload):
            try:return p.observations.append(kind,self.row.bound.reservation.hex(),payload)
            except BaseException as error:failure('failure capture retention',error);return None
        retain('ACTOR_TRANSPORT_FAILURE',record)
        # Cancel the sole active writer before closing that owned endpoint.
        # write_input's cancellation retains the full original partial payload.
        if input_task is not None:
            if not input_task.done():input_task.cancel()
            answers=await asyncio.gather(input_task,return_exceptions=True)
            if isinstance(answers[0],BaseException) and answers[0] is not primary:
                failure('owned input termination',answers[0])
        fd,self.stdin_fd=self.stdin_fd,None
        if fd is not None:
            try:os.close(fd);record['stdin_close_returned']=True
            except BaseException as error:record['stdin_close_returned']=False;failure('owned stdin close',error)
        record['input_complete']=self.stdin_complete
        # Attach only missing actual output readers. A partial normal attachment
        # is reused; no competing reader or guessed/raw-path fallback is made.
        loop=asyncio.get_running_loop();outputs=dict(output_tasks or {})
        fallback=set()
        async def drain_failure(name):
            reader=getattr(self,name);occurrence=0
            while True:
                chunk=await reader.read(shutil.COPY_BUFSIZE)
                payload={'failure':record['primary_type'],'held':self.held_event,
                    'dispatch':self.dispatch,'stream':name,'occurrence':occurrence,
                    'bytes':chunk,'read_returned':True,'EOF_observed':chunk==b''}
                # Keep this complete read in owned memory before persistence.
                # Persistence failure does not become EOF/full-retention credit.
                self.failure_pending_read=payload
                event=p.observations.append('ACTOR_TRANSPORT_FAILURE_OUTPUT',self.row.bound.reservation.hex(),payload)
                self.failure_pending_read=None;occurrence+=1
                if chunk==b'':record['output_eof'][name]=event;return event
        for name,fd in (('stdout',self.stdout_fd),('stderr',self.stderr_fd)):
            task=outputs.get(name)
            if task is not None and not task.done():continue
            if task is not None and not task.cancelled() and task.exception() is None:
                record['output_eof'][name]='original complete raw-file drain returned';continue
            if task is not None and not task.cancelled():failure('original '+name+' drain',task.exception())
            try:
                if getattr(self,name) is None:
                    require(fd is not None,'RESOURCE_V3_FAILURE_ACTUAL_OUTPUT_ABSENT')
                    reader=asyncio.StreamReader();protocol=asyncio.StreamReaderProtocol(reader)
                    handle=os.fdopen(os.dup(fd),'rb',buffering=0)
                    try:transport,_protocol=await loop.connect_read_pipe(lambda:protocol,handle)
                    except BaseException:handle.close();raise
                    self.pipe_transports.append(transport);setattr(self,name,reader)
                outputs[name]=asyncio.create_task(drain_failure(name));fallback.add(name)
            except BaseException as error:failure('owned '+name+' attachment',error)
        stopped=False
        try:record['stop']=await self.stop_owned_transport(primary);stopped=True
        except BaseException as error:failure('owned manager stop',error)
        self.failure_tasks=tuple(outputs.values())
        if stopped:
            try:
                if wait_task is None:wait_task=asyncio.create_task(self.wait())
                answers=await asyncio.gather(wait_task,return_exceptions=True)
                if isinstance(answers[0],BaseException):raise answers[0]
                record['wait']=answers[0];record['closed']=self.closed;record['closed_event']=self.closed_event
                require(self.closed is not None and self.closed_event is not None,
                    'RESOURCE_V3_FAILURE_ACTUAL_CLOSED_REQUIRED')
                record['status']='OWNED_CLOSED_RAW_FAILURE_RETAINED'
            except BaseException as error:failure('owned full namespace/helper wait',error)
            # Real stop supplies neither EOF nor closure. Join each real reader
            # and recover a failed original persistence/parser tail exactly once.
            for name,task in tuple(outputs.items()):
                answer=(await asyncio.gather(task,return_exceptions=True))[0]
                if isinstance(answer,BaseException):
                    failure('owned '+name+' drain',answer)
                    if name not in fallback:
                        outputs[name]=asyncio.create_task(drain_failure(name));fallback.add(name)
                        tail=(await asyncio.gather(outputs[name],return_exceptions=True))[0]
                        if isinstance(tail,BaseException):failure('owned '+name+' failure tail',tail)
                        else:record['output_eof'][name]=tail
                elif name not in fallback:record['output_eof'][name]='original complete raw-file drain returned'
        else:
            # Unknown stop never permits an unbounded fabricated wait or EOF.
            # Cancel observers only; retain the actual slot, all descriptors,
            # unread stream buffers and full resource rows for owner recovery.
            pending=[task for task in outputs.values() if not task.done()]
            if wait_task is not None and not wait_task.done():pending.append(wait_task)
            for task in pending:task.cancel()
            await asyncio.gather(*pending,return_exceptions=True)
        self.failure_tasks=tuple(outputs.values())
        record['input_fault']=None if self.stdin_fault is None else {
            'type':[type(self.stdin_fault).__module__,type(self.stdin_fault).__name__],
            'text':str(self.stdin_fault)}
        # A failure of durable capture/full output remains UNKNOWN even when a
        # separate authentic CLOSED was physically observed. Keep both facts.
        if record['errors'] or any(value is None for value in record['output_eof'].values()):record['status']='UNKNOWN'
        result_event=retain('ACTOR_TRANSPORT_FAILURE_RESULT',record)
        self.failure_result_event=result_event
        if result_event is None:
            # Final durable result is independent of authentic physical CLOSED.
            # Its append failure was retained in errors by retain above; the
            # actual raw wait/closed evidence remains unchanged and held.
            record['status']='UNKNOWN'
        return record
    async def attach_output(self):
        """Original complete actor bytes through owned real pipes, not journalctl."""
        require(self.stdout is None and self.stderr is None,'RESOURCE_OUTPUT_ALREADY_OWNED')
        loop=asyncio.get_running_loop()
        for name,fd in (('stdout',self.stdout_fd),('stderr',self.stderr_fd)):
            require(fd is not None,'RESOURCE_ACTUAL_OUTPUT_DESCRIPTOR_ABSENT')
            reader=asyncio.StreamReader();protocol=asyncio.StreamReaderProtocol(reader)
            handle=os.fdopen(os.dup(fd),'rb',buffering=0)
            try:transport,_protocol=await loop.connect_read_pipe(lambda:protocol,handle)
            except BaseException:handle.close();raise
            self.pipe_transports.append(transport);setattr(self,name,reader)
        return self
    async def wait(self):
        """Waits real closure and owned helper pidfd; no launcher/EOF verdict."""
        require(self.started and not self.failed,'RESOURCE_ACTUAL_RUNNING_WAIT_REQUIRED')
        loop=asyncio.get_running_loop()
        async def readable(fd):
            future=loop.create_future()
            def ready():
                if not future.done():future.set_result(None)
            loop.add_reader(fd,ready)
            try:await future
            finally:loop.remove_reader(fd)
        while self.closed is None:
            await readable(self.connection.fileno());self.poll_closed()
        if self.pidfd_state(self.helper_pidfd)!=b'PIDFD_TERMINAL':await readable(self.helper_pidfd)
        require(self.pidfd_state(self.namespace_pidfd)==b'PIDFD_TERMINAL'
            and self.pidfd_state(self.helper_pidfd)==b'PIDFD_TERMINAL','RESOURCE_WAIT_TERMINAL_OWNERSHIP_UNKNOWN')
        return os.waitstatus_to_exitcode(self.closed['main_wait_status'])
    def close(self):
        # Closing descriptors never classifies a workload as reaped or releases
        # capacity. A helper losing its channel before GO kills its namespace
        # init; after GO closure can become unobservable. A failed main can
        # still have genuine fully waited CLOSED/ECHILD evidence. Only that
        # actual evidence may classify closure; closing here proves none.
        transports,self.pipe_transports=self.pipe_transports,[]
        for transport in transports:transport.close()
        for name in ('namespace_fd','namespace_pidfd','helper_pidfd','actor_pidfd','stdout_fd','stderr_fd','stdin_fd'):
            fd=getattr(self,name);setattr(self,name,None)
            if fd is not None:os.close(fd)
        for name in ('connection','listener','credential_receiver'):
            channel=getattr(self,name);setattr(self,name,None)
            if channel is not None:channel.close()
        self.failed=True
