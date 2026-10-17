"""Actual seven-FD privileged worker supervisor and independent CLOSED custody.

This owner never claims confined Actor K.Check for the coordinator. Full selected
Root_Controller native admission, existing original resource Running and numeric
machine gates are required before GO/exec by the dispatch producer. Transport
closure is retained independently of target Store/Gate/Controller DB owners.
"""
from __future__ import annotations
import array,asyncio,fcntl,os,select,socket,stat,struct,subprocess,termios
from pathlib import Path
from .protected_startup import require,private_bytes,digest,protected
from .root_worker_custody import identity,channel_source
from .root_worker_codec import archive,restore_archive
from .root_worker_credentials import wait_observation,send_committed_ack,_number
HEADER=b'WL-ROOT-WORKER-SUPERVISOR-v1\n'

class OwnedRootSupervisor:
    def __init__(self,front,row,dispatch,listener,request):
        from .protected_root_worker import RootWorkerFront
        from .client_peer import RequestPeer
        require(type(front) is RootWorkerFront and type(request) is RequestPeer,
                'ROOT_SUPERVISOR_EXACT_SELECTED_FRONT_REQUEST_REQUIRED')
        self.front,self.principal,self.request=front,front.principal,request
        self.operation=dispatch['operation'];self.row,self.dispatch,self.listener=row,dispatch,listener
        self.journal=front.custody_journal;self.source=front.source_lease
        # Retain an independently owned duplicate of the genuine original
        # socket through detached lifetime, even after daemon RequestPeer.close.
        # This is original observation custody, never another grant or exchange.
        self.retained_peer=RequestPeer(request.peer.duplicate(),request.observation())
        self.connection=None;self.custody_channel=None;self.credential_receiver=None
        self.namespace_fd=None;self.namespace_pidfd=None;self.helper_pidfd=None;self.worker_pidfd=None
        self.stdout_fd=None;self.stderr_fd=None;self.stdin_fd=None
        self.held=None;self.closed=None;self.outer=None;self.failed=False;self.execution_ack=None
        self.launcher=None;self.raw_tasks=();self.raw_readers=();self.raw_transports=[];self.raw_result=None
        self.original_result=None;self.original_result_seen=False;self.handler_terminal=None;self.custody_ack=None;self.reader_task=None
        self.original_output_transports=[];self.original_response_transport=None;self.original_failure_transport=None
        self.worker_host_pid=None;self.worker_start=None;self.worker_pidfd_origin=None
        self.held_event=None;self.running_event=None;self.execution_event=None;self.launcher_wait_receipt=None
        self.original_use=self.principal._original_native_use(self.principal.journal.rows[self.operation])
    @staticmethod
    def pidfd_state(fd):
        poll=select.poll();poll.register(fd,select.POLLIN|select.POLLHUP|select.POLLERR)
        events=poll.poll(0)
        require(not any(mask&select.POLLERR for _fd,mask in events),'ROOT_SUPERVISOR_PIDFD_UNKNOWN')
        return b'PIDFD_TERMINAL' if events else b'PIDFD_LIVE'
    @staticmethod
    def fd_pid(fd):
        raw=Path('/proc/self/fdinfo/'+str(fd)).read_bytes()
        matches=[line.removeprefix(b'Pid:\t') for line in raw.splitlines() if line.startswith(b'Pid:\t')]
        require(len(matches)==1,'ROOT_SUPERVISOR_FULL_PIDFD_PID_UNAVAILABLE')
        return _number(matches[0]),raw
    def manager(self):
        # Selected executable is pinned before every actual read-only manager
        # observation. Commands do not define liveness or permission in Python.
        path=self.front.plan['native_components']['systemctl']
        self.source.file(path,('EXECUTABLE',))
        names=('Id','MainPID','InvocationID','ControlGroup','Delegate','ActiveState','SubState','Result','ExecMainCode','ExecMainStatus')
        answer=subprocess.run([path,'--system','show',self.row.planned_unit.decode('ascii'),
            '--no-pager',*(('--property='+name) for name in names)],stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,env={'PATH':'/usr/bin:/bin','LANG':'C'})
        require(answer.returncode==0,'ROOT_SUPERVISOR_ACTUAL_MANAGER_READ_FAILED')
        parsed={}
        for raw in answer.stdout.splitlines():
            name,sep,value=raw.partition(b'=')
            require(sep and name.decode('ascii') in names and name not in parsed,
                    'ROOT_SUPERVISOR_COMPLETE_MANAGER_PROPERTIES_MALFORMED')
            parsed[name]=value
        require(set(parsed)=={name.encode('ascii') for name in names} and parsed[b'Id']==self.row.planned_unit,
                'ROOT_SUPERVISOR_ACTUAL_UNIT_CHANGED')
        return parsed,{'argv':answer.args,'stdout':answer.stdout,'stderr':answer.stderr,'returncode':answer.returncode}
    def intact(self):
        self.source.check();self.journal.intact()
        require(not self.failed and self.held is not None,'ROOT_SUPERVISOR_CUSTODY_UNAVAILABLE')
        require(self.connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('@iII'))==self.held['peer'],
                'ROOT_SUPERVISOR_KERNEL_OWNER_PEER_CHANGED')
        require(identity(self.namespace_fd)==self.held['namespace_identity'],
                'ROOT_SUPERVISOR_OWNED_NAMESPACE_CHANGED')
        if self.held_event is not None:self.journal.require_event(self.held_event)
    def accept_held(self):
        self.source.check();connection,_address=self.listener.accept();self.connection=connection
        owned=[]
        try:
            peer=connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('@iII'))
            helper,uid,_gid=struct.unpack('@iII',peer)
            require(helper>0 and uid==0,'ROOT_SUPERVISOR_ACTUAL_HELPER_PEER_REQUIRED')
            extent=array.array('i',[0]);fcntl.ioctl(connection.fileno(),termios.FIONREAD,extent,True)
            require(extent[0]>0,'ROOT_SUPERVISOR_COMPLETE_HELD_PACKET_ABSENT')
            body,controls,flags,_address=connection.recvmsg(extent[0],socket.CMSG_SPACE(array.array('i').itemsize*7),socket.MSG_CMSG_CLOEXEC)
            invalid=False
            for level,kind,raw in controls:
                if (level,kind)!=(socket.SOL_SOCKET,socket.SCM_RIGHTS):invalid=True;continue
                rights=array.array('i');full=len(raw)-len(raw)%rights.itemsize;rights.frombytes(raw[:full]);owned.extend(rights)
                invalid|=full!=len(raw)
            require(len(body)==extent[0] and not flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC)
                and not invalid and len(owned)==7,'ROOT_SUPERVISOR_COMPLETE_SEVEN_RIGHTS_REQUIRED')
            parts=body.split(b'\n')
            require(len(parts)==5 and parts[:2]==[HEADER.removesuffix(b'\n'),b'HELD'] and parts[-1]==b''
                and parts[2]==self.dispatch['ticket'].encode('ascii'),'ROOT_SUPERVISOR_HELD_ORIGINAL_DISPATCH_CHANGED')
            init_pid=_number(parts[3]);ns,pidfd,out,err,credential,stdin,custody=owned
            self.credential_receiver=socket.socket(fileno=credential);owned.remove(credential)
            self.custody_channel=socket.socket(fileno=custody);owned.remove(custody)
            self.namespace_fd,self.namespace_pidfd,self.stdout_fd,self.stderr_fd,self.stdin_fd=ns,pidfd,out,err,stdin;owned=[]
            require(self.credential_receiver.getsockopt(socket.SOL_SOCKET,socket.SO_TYPE)==socket.SOCK_SEQPACKET
                and self.credential_receiver.getsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED)==1,
                'ROOT_SUPERVISOR_ACTUAL_MEASUREMENT_CHANNEL_REQUIRED')
            channel_source(self.custody_channel)
            require(self.custody_channel.getsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED)==1,
                'ROOT_SUPERVISOR_ACTUAL_CUSTODY_CREDENTIALS_REQUIRED')
            require(all(stat.S_ISFIFO(os.fstat(fd).st_mode) for fd in (out,err,stdin))
                and all(fcntl.fcntl(fd,fcntl.F_GETFL)&os.O_ACCMODE==os.O_RDONLY for fd in (out,err))
                and fcntl.fcntl(stdin,fcntl.F_GETFL)&os.O_ACCMODE==os.O_WRONLY,
                'ROOT_SUPERVISOR_ACTUAL_OWNED_STDIO_REQUIRED')
            actual,fdinfo=self.fd_pid(pidfd);require(actual==init_pid,'ROOT_SUPERVISOR_INIT_PIDFD_CHANGED')
            actual_ns=os.open('/proc/'+str(init_pid)+'/ns/pid',os.O_RDONLY|os.O_CLOEXEC)
            try:require(os.fstat(actual_ns)==os.fstat(ns),'ROOT_SUPERVISOR_ACTUAL_INIT_NAMESPACE_CHANGED')
            finally:os.close(actual_ns)
            self.helper_pidfd=os.pidfd_open(helper,0);properties,manager=self.manager()
            require(_number(properties[b'MainPID'])==helper and properties[b'InvocationID']
                and properties[b'Delegate']==b'no' and properties[b'ControlGroup'].startswith(b'/'),
                'ROOT_SUPERVISOR_COMPLETE_MANAGER_HELPER_CGROUP_CHANGED')
            root=Path('/proc')/str(helper);image=Path(os.readlink(root/'exe'))
            require(str(image)==self.front.plan['helper'] and
                private_bytes(image)==self.source.file(str(image),('EXECUTABLE',)),
                'ROOT_SUPERVISOR_SELECTED_REAL_HELPER_CHANGED')
            capture={name:(root/name).read_bytes() for name in ('status','stat','cgroup','maps','cmdline')}
            require(capture['cmdline']==b'\0'.join(os.fsencode(word) for word in self.dispatch['helper_arguments'])+b'\0'
                and capture['cgroup']==b'0::'+properties[b'ControlGroup']+b'\n',
                'ROOT_SUPERVISOR_ACTUAL_ORIGINAL_COMMAND_OR_CGROUP_CHANGED')
            for line in capture['maps'].splitlines():
                pieces=line.split(None,5)
                if len(pieces)==6 and pieces[5].startswith(b'/'):
                    selected=os.fsdecode(pieces[5]);self.source.file(selected,('EXECUTABLE','EXTENSION'))
            self.held={'frame':body,'peer':peer,'init_pid':init_pid,'helper_pid':helper,'pidfd_info':fdinfo,
                'namespace_identity':identity(ns),'helper_pidfd_info':self.fd_pid(self.helper_pidfd)[1],
                'properties':properties,'manager':manager,'helper_proc':capture,
                'descriptors':tuple(identity(fd) for fd in (ns,pidfd,out,err,self.credential_receiver.fileno(),stdin,self.custody_channel.fileno())),
                'source':self.source.check(),'dispatch':self.dispatch}
            from .root_worker_root_evidence import append,process_identity,poll_receipt,scoped_capture,native_item
            packet,classification,consistent,raw=scoped_capture(self.principal.resources,self.row.bound.reservation)
            self.init_identity=process_identity(init_pid)
            self.namespace_pidfd_origin=identity(pidfd);self.helper_pidfd_origin=identity(self.helper_pidfd)
            self.held_event=append(self.front,self.operation,'HELD',self.held,
                {'held':self.held,'machine':self.machine_dispatch,'init_identity':self.init_identity,
                 'helper_pidfd_origin':self.helper_pidfd_origin,'init_held_poll':poll_receipt(self.front,pidfd)},
                native=(native_item('scoped-classify',packet,classification,raw),
                    native_item('scoped-validate',packet,consistent,raw)))
            self.connection.setblocking(False);return self.complete_capture()
        except BaseException:
            self.failed=True
            for fd in owned:os.close(fd)
            self.close_received_rights();raise
    def complete_capture(self):
        self.intact();properties,manager=self.manager()
        require(properties[b'ControlGroup']==self.held['properties'][b'ControlGroup']
            and properties[b'InvocationID']==self.held['properties'][b'InvocationID'],
            'ROOT_SUPERVISOR_CURRENT_ORIGINAL_MANAGER_CHANGED')
        return {'held':self.held,'held_event':self.held_event,'current_manager':manager,
            'current_properties':properties,'namespace_wait':self.pidfd_state(self.namespace_pidfd),
            'helper_wait':self.pidfd_state(self.helper_pidfd),'current_source':self.source.check(),
            'execution_ack':self.execution_ack,'closed':self.closed,'outer':self.outer,
            'custody_channel':channel_source(self.custody_channel)}
    def observe(self):
        from .root_worker_physical import observe
        self.intact()
        rights={'supervisor_channel':self.connection.fileno(),'worker_namespace':self.namespace_fd,
            'namespace_pidfd':self.namespace_pidfd,'helper_pidfd':self.helper_pidfd}
        return observe(self.front,self.row,self.dispatch,self.held,rights,closed=self.closed,outer=self.outer)
    def begin_go(self,running_event,machine_event,committed):
        from .root_worker_root_evidence import append,capture_effect
        self.intact();require(self.execution_ack is None,'ROOT_SUPERVISOR_GO_REPLAY')
        self.running_event=append(self.front,self.operation,'RUNNING',
            {'resource_event':running_event,'machine':machine_event,'physical':self.complete_capture()},
            {'held_event':self.held_event['event_id'],'running':committed})
        _result,self.go_receipt=capture_effect(self.front.source_lease,'sendall',
            {'fd':self.connection.fileno(),'body':b'G','flags':0},
            lambda:self.connection.sendall(b'G'))
    def commit_execution(self,material,native,measured,process):
        self.intact();require(native.status=='ROOT_READY_CONJUNCTION' and self.execution_ack is None,
                'ROOT_SUPERVISOR_COMPLETE_ROOT_NATIVE_EXECUTION_REQUIRED')
        full={'material':material,'native':native,'measured':measured.record(),'process':process,
            'physical':self.complete_capture(),'original_request':self.request.observation()}
        from .root_worker_root_evidence import append,native_item,execution_ack,process_identity
        capture=self.front._root_capture
        provenance=capture.provenance
        before_exec={'measured':measured.record(),'process':process,'request':self.request.observation(),
            'dispatch':self.dispatch,'ticket':measured.ticket,'channel':channel_source(self.credential_receiver),
            'source':self.source.check()}
        self.worker_identity=process_identity(self.worker_host_pid,self.worker_start)
        event=append(self.front,self.operation,'EXECUTION_NATIVE',full,
            {'running_event':self.running_event['event_id'],'worker_identity':self.worker_identity,
             'worker_pidfd_origin':identity(self.worker_pidfd),
             'execution':{'material':material,'observation':native,'provenance':provenance,'before_exec':before_exec,
                 'go':self.go_receipt,'launch':tuple(self.launcher_effects)}},
            native=(native_item('root-execution',material,native,provenance),))
        self.execution_event=event
        self.journal.require_event(event)
        # Real fresh full native replay is performed before the sealed ACK.
        require(self.front.authority.decide(material)==native,'ROOT_SUPERVISOR_DURABLE_NATIVE_REPLAY_CHANGED')
        body,ack=execution_ack(self.front,self,measured,event)
        self.execution_ack=append(self.front,self.operation,'EXECUTION_ACK',{'event':event,'ack':body},{'ack':ack})
        if self.stdin_fd is not None:self.close_input()
        return self.execution_ack
    def close_input(self):
        from .root_worker_root_evidence import close_owned_stdin
        return close_owned_stdin(self,self.stdin_fd)
    def poll_closed(self):
        self.intact()
        if self.closed is not None:return self.closed
        try:
            extent=array.array('i',[0]);fcntl.ioctl(self.connection.fileno(),termios.FIONREAD,extent,True)
            if extent[0]==0:return None
            body,controls,flags,_=self.connection.recvmsg(extent[0],socket.CMSG_SPACE(array.array('i').itemsize),socket.MSG_CMSG_CLOEXEC)
        except BlockingIOError:return None
        owned=[]
        try:
            for level,kind,raw in controls:
                if (level,kind)==(socket.SOL_SOCKET,socket.SCM_RIGHTS):
                    rights=array.array('i');rights.frombytes(raw[:len(raw)-len(raw)%rights.itemsize]);owned.extend(rights)
            require(len(body)==extent[0] and not controls and not flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC),
                'ROOT_SUPERVISOR_CLOSED_UNKNOWN_CONTROL')
            parts=body.split(b'\n')
            require(len(parts)==7 and parts[:2]==[HEADER.removesuffix(b'\n'),b'CLOSED']
                and parts[2]==self.dispatch['ticket'].encode('ascii') and _number(parts[3])==self.held['init_pid']
                and parts[5:]==[b'ECHILD',b''],'ROOT_SUPERVISOR_CLOSED_ORIGINAL_NAMESPACE_CHANGED')
            status=_number(parts[4]);require(os.WIFEXITED(status) or os.WIFSIGNALED(status),
                'ROOT_SUPERVISOR_MAIN_WAIT_RAW_STATUS_UNKNOWN')
            require(self.pidfd_state(self.namespace_pidfd)==b'PIDFD_TERMINAL',
                'ROOT_SUPERVISOR_ACTUAL_NAMESPACE_NOT_TERMINAL')
            from .root_worker_root_evidence import append,process_wait,syscall
            record={'frame':body,'held':self.held_event,'actual_capture':self.complete_capture(),'raw_main_wait':status}
            namespace_wait=process_wait(self.front,self.namespace_pidfd,self.namespace_pidfd_origin,self.init_identity)
            sent,ack=syscall(self.front,'send',{'fd':self.connection.fileno(),'body':b'A','flags':socket.MSG_NOSIGNAL},
                lambda:self.connection.send(b'A',socket.MSG_NOSIGNAL))
            require(sent==1,'ROOT_SUPERVISOR_NAMESPACE_ACK_SEND_UNKNOWN')
            event=append(self.front,self.operation,'CLOSED_NS',record,
                {'closed_ns':{'held_event':self.held_event['event_id'],'frame':body,
                    'raw_main_wait':status,'namespace_wait':namespace_wait,'ack':ack}})
            self.journal.require_event(event);self.closed=event
            return event
        finally:
            for fd in owned:os.close(fd)
    async def actual_closed_and_outer_wait(self):
        # No EOF, launcher return or absent cgroup substitutes for this protocol.
        loop=asyncio.get_running_loop()
        async def ready(fd):
            future=loop.create_future()
            def observed():
                if not future.done():future.set_result(None)
            loop.add_reader(fd,observed)
            try:await future
            finally:loop.remove_reader(fd)
        while self.poll_closed() is None:await ready(self.connection.fileno())
        if self.pidfd_state(self.helper_pidfd)!=b'PIDFD_TERMINAL':await ready(self.helper_pidfd)
        require(type(self.launcher) is subprocess.Popen and self.launcher.args==self.dispatch['launcher_arguments'],
                'ROOT_SUPERVISOR_ACTUAL_OWNED_OUTER_WAITER_UNAVAILABLE')
        require(self.launcher_wait_receipt is not None,'ROOT_SUPERVISOR_ORIGINAL_WAITPID_RECEIPT_ABSENT')
        launcher_wait=self.launcher.returncode
        properties,manager=self.manager()
        require(properties[b'MainPID']==b'0','ROOT_SUPERVISOR_OUTER_MANAGER_STILL_LIVE')
        from .root_worker_root_evidence import append,process_wait
        record={'namespace_event':self.closed,
            'outer_pidfd_wait':self.pidfd_state(self.helper_pidfd),'actual_launcher_wait':launcher_wait,'manager':manager,
            'actual_namespace_wait':self.pidfd_state(self.namespace_pidfd),'source':self.source.check()}
        self.outer=append(self.front,self.operation,'CLOSED_OUTER',record,
            {'closed_outer':{'namespace_event':self.closed['event_id'],
                'helper_wait':process_wait(self.front,self.helper_pidfd,self.helper_pidfd_origin),
                'launcher_wait':self.launcher_wait_receipt,'manager':manager,'actual_launcher_wait':launcher_wait,
                'namespace_wait':process_wait(self.front,self.namespace_pidfd,self.namespace_pidfd_origin,self.init_identity)}})
        return self.outer
    async def start_raw_drains(self):
        self.intact();require(not self.raw_tasks,'ROOT_SUPERVISOR_RAW_READERS_REPLAY')
        directory=Path(self.front.spec['paths']['runtime'])/'root-worker'/self.operation
        from .root_worker_root_evidence import capture_effect
        _,mkdir=capture_effect(self.source,'mkdir',
            {'path':str(directory),'mode':0o700,'parents':True,'exist_ok':False},
            lambda:directory.mkdir(mode=0o700,parents=True,exist_ok=False))
        protected(directory,directory=True)
        loop=asyncio.get_running_loop();tasks=[];readers=[];self.raw_profiles={}
        try:
            for name in ('stdout','stderr'):
                descriptor=getattr(self,name+'_fd');require(descriptor is not None,'ROOT_SUPERVISOR_REAL_RAW_PIPE_ABSENT')
                reader,duplicated=capture_effect(self.source,'dup',{'fd':descriptor},lambda:os.dup(descriptor))
                readers.append(reader)
                _,nonblocking=capture_effect(self.source,'set_blocking',{'fd':reader,'blocking':False},
                    lambda:os.set_blocking(reader,False))
                flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC
                output,opened=capture_effect(self.source,'open',
                    {'path':str(directory/(name+'.bin')),'flags':flags,'mode':0o600},
                    lambda:os.open(directory/(name+'.bin'),flags,0o600))
                profile={'stream':name,'mkdir':mkdir,'dup':duplicated,'set_blocking':nonblocking,
                    'open':opened,'read_fd':reader,'write_fd':output,'reads':[],'writes':[],'close':[]}
                self.raw_profiles[name]=profile
                async def drain(reader=reader,output=output,name=name,profile=profile):
                    total=0;failure=None
                    try:
                        while True:
                            try:
                                raw,read=capture_effect(self.source,'read',{'fd':reader,'count':65536},
                                    lambda:os.read(reader,65536))
                                profile['reads'].append(read)
                            except BlockingIOError as error:
                                profile['reads'].append(error.custody_receipt)
                                ready=loop.create_future()
                                def observed():
                                    if not ready.done():ready.set_result(None)
                                loop.add_reader(reader,observed)
                                try:await ready
                                finally:loop.remove_reader(reader)
                                continue
                            if not raw:
                                profile['eof']=read
                                break
                            position=0
                            while position<len(raw):
                                fragment=memoryview(raw)[position:]
                                amount,write=capture_effect(self.source,'write',
                                    {'fd':output,'raw':bytes(fragment)},lambda:os.write(output,fragment))
                                profile['writes'].append(write)
                                require(amount>0,'ROOT_SUPERVISOR_RAW_CAPTURE_WRITE_UNKNOWN');position+=amount
                            total+=len(raw)
                        _,fsync=capture_effect(self.source,'fsync',{'fd':output},lambda:os.fsync(output))
                        original={'stream':name,'bytes':total,'identity':identity(output),
                            'path':str(directory/(name+'.bin'))}
                        profile.update(original);profile.update(raw=private_bytes(directory/(name+'.bin')),fsync=fsync)
                        return original
                    except BaseException as error:
                        failure=error
                        profile['error']={'type':type(error).__qualname__,'module':type(error).__module__,
                            'message':str(error),'args':error.args,'errno':getattr(error,'errno',None),
                            'receipt':getattr(error,'custody_receipt',None)}
                        raise
                    finally:
                        closing=[]
                        for fd in (reader,output):
                            try:
                                _,close=capture_effect(self.source,'close',{'fd':fd},lambda:os.close(fd))
                                profile['close'].append(close)
                            except OSError as error:
                                profile['close'].append(error.custody_receipt);closing.append(error)
                        if closing:
                            if failure is None:raise closing[0]
                            for error in closing:failure.add_note('Actual raw descriptor close also failed: '+str(error))
                tasks.append(asyncio.create_task(drain()))
            self.raw_readers=tuple(readers);self.raw_tasks=tuple(tasks)
        except BaseException as error:
            # Every already attached reader remains owned on a preflight fault.
            self.raw_readers=tuple(readers);self.raw_tasks=tuple(tasks)
            await self.retain_and_stop_unknown(error,None);raise
    async def complete_raw_drains(self):
        require(self.raw_tasks,'ROOT_SUPERVISOR_FULL_RAW_READERS_ABSENT')
        results=await asyncio.gather(*self.raw_tasks,return_exceptions=True)
        errors=[{'type':type(value).__name__,'message':str(value)} for value in results if isinstance(value,BaseException)]
        record={'results':tuple(value if not isinstance(value,BaseException) else None for value in results),'errors':errors}
        if errors:
            from .root_worker_root_evidence import unknown
            unknown(self.front,self.operation,record,RuntimeError('raw retention failed'),
                {'expected':{'stdout':'EOF and fsync','stderr':'EOF and fsync'},'actual':record})
            require(False,'ROOT_SUPERVISOR_ACTUAL_RAW_RETENTION_FAILED')
        from .root_worker_root_evidence import append
        self.raw_result=append(self.front,self.operation,'CLOSED_RAW',{'actual_closed':self.outer,'complete_raw':record},
            {'closed_raw':{'streams':tuple(self.raw_profiles[name] for name in ('stdout','stderr')),
                'result':record}})
        return self.raw_result
    def bind_actual_worker(self,process,raw,measured):
        from .resource_child_schema import ProcessObservation
        require(type(process) is ProcessObservation and self.worker_host_pid is None
            and self.worker_pidfd is not None and self.pidfd_state(self.worker_pidfd)==b'PIDFD_LIVE'
            and self.fd_pid(self.worker_pidfd)[0]==process.host_pid,
            'ROOT_SUPERVISOR_GENUINE_WORKER_PIDFD_CAPTURE_REQUIRED')
        self.worker_host_pid=process.host_pid;self.worker_start=process.start_tick
        self.worker_pidfd_origin={'descriptor':identity(self.worker_pidfd),'process':process,'raw':raw}
        stat_raw=(Path('/proc')/str(process.host_pid)/'stat').read_bytes()
        self.worker_actor={'boot':Path('/proc/sys/kernel/random/boot_id').read_bytes(),
            'pid':process.host_pid,'start_tick':process.start_tick,'stat':stat_raw,
            'credentials':measured.raw_sender_credentials,'channel':identity(self.custody_channel.fileno())}
        return self.worker_pidfd_origin
    def _sender_owned(self,raw):
        # Real SCM credentials are joined to the host PID captured while the
        # same held pidfd was LIVE. Queued terminal messages may arrive after
        # exit, when fdinfo Pid becomes absent; PID reuse alone is not accepted.
        require(self.worker_host_pid is not None and self.worker_pidfd_origin is not None,
                'ROOT_SUPERVISOR_MEASURED_WORKER_ORIGIN_ABSENT')
        sender,uid,_gid=struct.unpack('@iII',raw['sender_credentials'])
        require(sender==self.worker_host_pid and uid==0,
                'ROOT_SUPERVISOR_ORIGINAL_RESULT_SENDER_CHANGED')
        return raw
    async def receive_full_custody_ack(self):
        from .root_worker_result_channel import receive_event
        roster,roster_raw=await asyncio.to_thread(receive_event,self.custody_channel,self.journal,self)
        self._sender_owned(roster_raw)
        require(roster['kind']=='ROSTER_EVIDENCE' and roster['operation']==self.operation,
                'ROOT_SUPERVISOR_ACTUAL_FRONT_ROSTER_REQUIRED')
        self.roster_event=roster;self.roster_transport=roster_raw
        event,raw=await asyncio.to_thread(receive_event,self.custody_channel,self.journal,self)
        self._sender_owned(raw)
        require(self.worker_pidfd is not None
            and event['kind']=='CUSTODY_ACK' and event['operation']==self.operation,
            'ROOT_SUPERVISOR_AUTHENTIC_MEASURED_WORKER_ACK_REQUIRED')
        self.custody_ack=event
        return event
    def verify_full_custody_ack(self,event,frame,intent):
        self.journal.require_event(event);self.journal.require_event(intent)
        require(event is self.custody_ack and event['record']['frame']==frame,
                'ROOT_SUPERVISOR_COMPLETE_CUSTODY_FRAME_CHANGED')
        retained=event['record'];native=retained['native']
        # Historical exact redecision transports no fresh permission after the
        # front has relinquished state. The actual receiver did fresh admission.
        require(self.front.authority.kernel.root_controller(**retained['native_material'])==native
            and native.status=='ROOT_READY_CONJUNCTION','ROOT_SUPERVISOR_FULL_WORKER_NATIVE_ACK_REPLAY_CHANGED')
    async def receive_original_result(self,context):
        from .root_worker_result_channel import receive_event
        while not self.original_result_seen:
            event,raw=await asyncio.to_thread(receive_event,self.custody_channel,self.journal,self)
            self._sender_owned(raw)
            require(event['operation']==self.operation,'ROOT_SUPERVISOR_ORIGINAL_RESULT_OPERATION_CHANGED')
            if event['kind'] in ('INPUT_EOF_PREPARE','INPUT_EOF_RECEIVED','INPUT_EOF_CANCEL','INPUT_EOF'):continue
            if event['kind']=='ORIGINAL_PROGRESS':
                self.original_output_transports.append({'event':event,'transport':raw,'output':raw['worker_output']})
            elif event['kind']=='ORIGINAL_RESULT':
                self.original_result=event['record']['value'];self.original_result_seen=True
                self.original_response_transport={'event':event,'transport':raw,'output':raw['worker_output']}
            elif event['kind']=='UNKNOWN':
                self.original_failure_transport={'event':event,'transport':raw,'output':raw.get('worker_output')}
                require(False,'ROOT_SUPERVISOR_WORKER_REPORTED_UNKNOWN')
            else:require(False,'ROOT_SUPERVISOR_ORIGINAL_RESULT_ORDER_UNKNOWN')
        return self.original_result
    async def receive_handler_terminal(self,context):
        from .root_worker_result_channel import receive_event
        require(self.original_result_seen and self.handler_terminal is None,
                'ROOT_SUPERVISOR_TERMINAL_BEFORE_INITIAL_RESULT_OR_REPLAY')
        while self.handler_terminal is None:
            event,raw=await asyncio.to_thread(receive_event,self.custody_channel,self.journal,self)
            self._sender_owned(raw)
            if event['kind'] in ('INPUT_EOF_PREPARE','INPUT_EOF_RECEIVED','INPUT_EOF_CANCEL','INPUT_EOF'):
                require(event['operation']==self.operation,'ROOT_SUPERVISOR_STDIN_EOF_OPERATION_CHANGED')
                continue
            require(event['operation']==self.operation and
                event['record']['original_request']==self.retained_peer.observation(),
                    'ROOT_SUPERVISOR_TERMINAL_ORIGINAL_REQUEST_CHANGED')
            if event['kind']=='ORIGINAL_PROGRESS':
                self.original_output_transports.append({'event':event,'transport':raw,'output':raw['worker_output']})
            elif event['kind']=='HANDLER_TERMINAL':
                value=event['record']['value']
                require(type(value) is dict and set(value)=={'result','failures','owner_state',
                    'native_event','original_native_use'},'ROOT_SUPERVISOR_COMPLETE_TERMINAL_CAPTURE_REQUIRED')
                retained=value['native_event']
                require(retained['observation'].status=='ROOT_READY_CONJUNCTION'
                    and self.front.authority.kernel.root_controller(**retained['material'])==retained['observation'],
                        'ROOT_SUPERVISOR_ORIGINAL_OWNER_CLOSE_NATIVE_CHANGED')
                self.handler_terminal=event;self.terminal_transport=raw
            elif event['kind']=='UNKNOWN':
                require(False,'ROOT_SUPERVISOR_TERMINAL_REPORTED_UNKNOWN_HOLD_RETAINED')
            else:require(False,'ROOT_SUPERVISOR_TERMINAL_ORDER_UNKNOWN')
        return self.handler_terminal

    def failed_intact(self):
        from .root_worker_failed_closure import intact
        return intact(self)

    def failed_complete_capture(self):
        self.failed_intact();properties,manager=self.manager()
        require(properties[b'ControlGroup']==self.held['properties'][b'ControlGroup']
            and properties[b'InvocationID']==self.held['properties'][b'InvocationID'],
            'ROOT_SUPERVISOR_CURRENT_ORIGINAL_MANAGER_CHANGED')
        return {'held':self.held,'held_event':self.held_event,'current_manager':manager,
            'current_properties':properties,'namespace_wait':self.pidfd_state(self.namespace_pidfd),
            'helper_wait':self.pidfd_state(self.helper_pidfd),'current_source':self.source.check(),
            'execution_ack':self.execution_ack,'closed':self.closed,'outer':self.outer,
            'custody_channel':channel_source(self.custody_channel)}

    def failed_observe(self):
        from .root_worker_physical import observe
        self.failed_intact()
        rights={'supervisor_channel':self.connection.fileno(),'worker_namespace':self.namespace_fd,
            'namespace_pidfd':self.namespace_pidfd,'helper_pidfd':self.helper_pidfd}
        return observe(self.front,self.row,self.dispatch,self.held,rights,closed=self.closed,outer=self.outer)

    def failed_poll_closed(self):
        self.failed_intact()
        if self.closed is not None:return self.closed
        attempt={'call':'recvmsg','source':self.source.check(),'fd':self.connection.fileno(),
            'body':None,'controls':None,'flags':None,'acquired_rights':[],'close_attempts':[]}
        observations=getattr(self,'failed_closed_observations',None)
        if observations is None:observations=[];self.failed_closed_observations=observations
        observations.append(attempt)
        try:
            extent=array.array('i',[0]);fcntl.ioctl(self.connection.fileno(),termios.FIONREAD,extent,True)
            attempt['extent']=extent[0]
            if extent[0]==0:return None
            body,controls,flags,_=self.connection.recvmsg(extent[0],socket.CMSG_SPACE(array.array('i').itemsize),socket.MSG_CMSG_CLOEXEC)
            attempt.update(body=body,controls=tuple(controls),flags=flags)
        except BlockingIOError as error:
            attempt.update(errno=error.errno,error=repr(error));return None
        except BaseException as error:
            attempt.update(errno=getattr(error,'errno',None),error=repr(error));raise
        owned=[]
        try:
            for level,kind,raw in controls:
                if (level,kind)==(socket.SOL_SOCKET,socket.SCM_RIGHTS):
                    rights=array.array('i');rights.frombytes(raw[:len(raw)-len(raw)%rights.itemsize]);owned.extend(rights);attempt['acquired_rights'].extend(rights)
            require(len(body)==extent[0] and not controls and not flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC),
                'ROOT_SUPERVISOR_CLOSED_UNKNOWN_CONTROL')
            parts=body.split(b'\n')
            require(len(parts)==7 and parts[:2]==[HEADER.removesuffix(b'\n'),b'CLOSED']
                and parts[2]==self.dispatch['ticket'].encode('ascii') and _number(parts[3])==self.held['init_pid']
                and parts[5:]==[b'ECHILD',b''],'ROOT_SUPERVISOR_CLOSED_ORIGINAL_NAMESPACE_CHANGED')
            status=_number(parts[4]);require(os.WIFEXITED(status) or os.WIFSIGNALED(status),
                'ROOT_SUPERVISOR_MAIN_WAIT_RAW_STATUS_UNKNOWN')
            require(self.pidfd_state(self.namespace_pidfd)==b'PIDFD_TERMINAL',
                'ROOT_SUPERVISOR_ACTUAL_NAMESPACE_NOT_TERMINAL')
            from .root_worker_root_evidence import append,process_wait,syscall
            record={'frame':body,'held':self.held_event,'actual_capture':self.failed_complete_capture(),'raw_main_wait':status}
            namespace_wait=process_wait(self.front,self.namespace_pidfd,self.namespace_pidfd_origin,self.init_identity)
            sent,ack=syscall(self.front,'send',{'fd':self.connection.fileno(),'body':b'A','flags':socket.MSG_NOSIGNAL},
                lambda:self.connection.send(b'A',socket.MSG_NOSIGNAL))
            attempt['ack']={'sent':sent,'receipt':ack}
            require(sent==1,'ROOT_SUPERVISOR_NAMESPACE_ACK_SEND_UNKNOWN')
            event=append(self.front,self.operation,'CLOSED_NS',record,
                {'closed_ns':{'held_event':self.held_event['event_id'],'frame':body,
                    'raw_main_wait':status,'namespace_wait':namespace_wait,'ack':ack}},actor_role='FRONT')
            attempt['native_event']=event
            self.journal.require_event(event);self.closed=event
            return event
        except BaseException as error:
            attempt['refusal']={'type':type(error).__qualname__,'message':str(error)}
            raise
        finally:
            errors=[]
            while owned:
                fd=owned.pop();closing={'fd':fd};attempt['close_attempts'].append(closing)
                try:os.close(fd)
                except OSError as close_error:
                    closing.update(result=-1,errno=close_error.errno,message=str(close_error));errors.append(close_error)
                else:closing.update(result=0,errno=0)
            if errors:
                active=__import__('sys').exception()
                if active is None:raise errors[0]
                for close_error in errors:active.add_note('Actual refused CLOSED right close: '+repr(close_error))


    async def failed_actual_closed_and_outer_wait(self):
        # No EOF, launcher return or absent cgroup substitutes for this protocol.
        loop=asyncio.get_running_loop()
        async def ready(fd):
            future=loop.create_future()
            def observed():
                if not future.done():future.set_result(None)
            loop.add_reader(fd,observed)
            try:await future
            finally:loop.remove_reader(fd)
        while self.failed_poll_closed() is None:await ready(self.connection.fileno())
        if self.pidfd_state(self.helper_pidfd)!=b'PIDFD_TERMINAL':await ready(self.helper_pidfd)
        require(type(self.launcher) is subprocess.Popen and self.launcher.args==self.dispatch['launcher_arguments'],
                'ROOT_SUPERVISOR_ACTUAL_OWNED_OUTER_WAITER_UNAVAILABLE')
        require(self.launcher_wait_receipt is not None,'ROOT_SUPERVISOR_ORIGINAL_WAITPID_RECEIPT_ABSENT')
        launcher_wait=self.launcher.returncode
        properties,manager=self.manager()
        require(properties[b'MainPID']==b'0','ROOT_SUPERVISOR_OUTER_MANAGER_STILL_LIVE')
        from .root_worker_root_evidence import append,process_wait
        record={'namespace_event':self.closed,
            'outer_pidfd_wait':self.pidfd_state(self.helper_pidfd),'actual_launcher_wait':launcher_wait,'manager':manager,
            'actual_namespace_wait':self.pidfd_state(self.namespace_pidfd),'source':self.source.check()}
        self.outer=append(self.front,self.operation,'CLOSED_OUTER',record,
            {'closed_outer':{'namespace_event':self.closed['event_id'],
                'helper_wait':process_wait(self.front,self.helper_pidfd,self.helper_pidfd_origin),
                'launcher_wait':self.launcher_wait_receipt,'manager':manager,'actual_launcher_wait':launcher_wait,
                'namespace_wait':process_wait(self.front,self.namespace_pidfd,self.namespace_pidfd_origin,self.init_identity)}},actor_role='FRONT')
        return self.outer

    async def failed_complete_raw_drains(self):
        require(self.raw_tasks,'ROOT_SUPERVISOR_FULL_RAW_READERS_ABSENT')
        results=await asyncio.gather(*self.raw_tasks,return_exceptions=True)
        errors=[{'type':type(value).__name__,'message':str(value)} for value in results if isinstance(value,BaseException)]
        record={'results':tuple(value if not isinstance(value,BaseException) else None for value in results),'errors':errors}
        self.failed_raw_observation=record
        if errors:
            from .root_worker_root_evidence import unknown
            unknown(self.front,self.operation,record,RuntimeError('raw retention failed'),
                {'expected':{'stdout':'EOF and fsync','stderr':'EOF and fsync'},'actual':record})
            require(False,'ROOT_SUPERVISOR_ACTUAL_RAW_RETENTION_FAILED')
        from .root_worker_root_evidence import append
        self.raw_result=append(self.front,self.operation,'CLOSED_RAW',{'actual_closed':self.outer,'complete_raw':record},
            {'closed_raw':{'streams':tuple(self.raw_profiles[name] for name in ('stdout','stderr')),
                'result':record}},actor_role='FRONT')
        return self.raw_result

    async def retain_and_stop_unknown(self,error,offer):
        # Ownership/capture errors never imply release. A failed append is itself
        # retained in the live owner object; root hold/escrow cannot be dropped.
        self.failed=True;self.failure={'type':type(error).__name__,'message':str(error),'offer_state':None if offer is None else offer.state}
        from .root_worker_root_evidence import unknown
        raw=getattr(error,'custody_receipts',None)
        try:
            if self.journal.poisoned:
                uncertainty=self.journal.capture_uncertainty()
                self.failure_uncertainty=uncertainty
                # A poisoned owner must not retry or clear itself. Preserve its
                # actual failed native input for the independent ECR owner.
                self.failure_event=None
            else:
                from .root_worker_handoff_failure import retain
                self.failure_event=None
                try:
                    self.failure_event=retain(self,error,offer)
                except BaseException as handoff_error:
                    self.failure['handoff_error']={'type':type(handoff_error).__qualname__,
                        'module':type(handoff_error).__module__,'message':str(handoff_error),
                        'args':handoff_error.args,'errno':getattr(handoff_error,'errno',None)}
                    error.add_note('Actual native failed-handoff capture: '+repr(handoff_error))
                if self.failure_event is None:
                    if self.journal.poisoned:
                        self.failure_uncertainty=self.journal.capture_uncertainty()
                    else:
                        self.failure_event=unknown(self.front,self.operation,self.failure,error,
                            {'expected':'complete native original root custody','actual':self.failure if raw is None else raw})
        except BaseException as commit_error:
            self.failure['durable_error']={'type':type(commit_error).__name__,'message':str(commit_error)}
        if self.failure_event is not None and self.failure_event['kind'] in ('HANDOFF_ABORT','FRONT_RETAINED_ESCROW'):
            from .root_worker_failed_closure import collect_failed_and_reconstruct
            try:
                require(self.operation not in self.front.collectors,'ROOT_FAILED_COLLECTOR_REPLAY')
                task=asyncio.create_task(collect_failed_and_reconstruct(self.front,offer,error))
                self.front.collectors[self.operation]=task
                self.failed_collector_task=task
                await asyncio.shield(task)
                return
            except BaseException as collection_error:
                self.failure['physical_collection_error']={'type':type(collection_error).__qualname__,
                    'message':str(collection_error)}
                error.add_note('Actual failed physical collection: '+repr(collection_error))
                if getattr(self,'failed_collector_task',None) is not None and not self.failed_collector_task.done():
                    # The same bounded task owns cleanup. Never race its real
                    # worker/namespace protocol with a second whole-unit stop.
                    self.failure['retained_live_physical_collector']={'task_id':id(self.failed_collector_task),
                        'done':self.failed_collector_task.done(),'cancelled':self.failed_collector_task.cancelled()}
                    return
        # Actual selected system manager stops the owned unit; its return is not
        # terminal authority. Namespace/outer wait and complete raw drain remain
        # required; missing actual CLOSED continues UNKNOWN with accounting held.
        path=self.front.plan['native_components']['systemctl'];self.source.file(path,('EXECUTABLE',))
        stop_source=self.source.check()
        stop_args=[path,'--system','stop',self.row.planned_unit.decode('ascii')]
        stop_receipt={'call':'subprocess.run','args':{'argv':stop_args,'stdin':subprocess.DEVNULL,
            'stdout':subprocess.PIPE,'stderr':subprocess.PIPE,'check':False,
            'env':{'PATH':'/usr/bin:/bin','LANG':'C'}},'source':stop_source}
        self.failure_control_receipts=[stop_receipt]
        try:
            stopped=await asyncio.to_thread(subprocess.run,stop_args,
                stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,
                env={'PATH':'/usr/bin:/bin','LANG':'C'})
        except OSError as stop_error:
            stop_receipt.update(result=-1,errno=stop_error.errno,message=str(stop_error))
            raise
        stop_receipt.update(result=stopped.returncode,errno=0,stdout=stopped.stdout,stderr=stopped.stderr)
        self.failure['actual_stop']={'argv':stopped.args,'returncode':stopped.returncode,'stdout':stopped.stdout,'stderr':stopped.stderr}
        if self.launcher is not None:self.failure['actual_outer_wait']=await asyncio.to_thread(self.launcher.wait)
        # Real pipe readers remain retained; EOF alone gives no CLOSED verdict.
        if self.raw_tasks:self.failure['actual_raw']=await asyncio.gather(*self.raw_tasks,return_exceptions=True)

    def close_received_rights(self):
        if self.stdin_fd is not None:self.close_input()
        for name in ('credential_receiver','custody_channel','connection'):
            owner=getattr(self,name,None)
            if owner is not None:owner.close();setattr(self,name,None)
        for name in ('namespace_fd','namespace_pidfd','helper_pidfd','worker_pidfd','stdout_fd','stderr_fd'):
            fd=getattr(self,name,None)
            if fd is not None:os.close(fd);setattr(self,name,None)
