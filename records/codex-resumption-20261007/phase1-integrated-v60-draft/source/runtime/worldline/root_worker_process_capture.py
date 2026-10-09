"""Actual full host-proc/pidfd observations for the selected privileged handler.

A received host-proc FD is root-only custody, never actor delegation. Parsed
fields are factual projections; full raw before/after records and original FD
identities accompany the native record. There is no PID/start/UID magnitude cap.
"""
import os,stat,struct
from .protected_startup import require
from .root_worker_custody import identity
from .root_worker_credentials import _number
from .root_worker_codec import archive

def _read_at(directory,name):
    fd=os.open(name,os.O_RDONLY|os.O_CLOEXEC,dir_fd=directory)
    try:
        with os.fdopen(os.dup(fd),'rb') as stream:return stream.read()
    finally:os.close(fd)

def _stat(raw):
    # Exact offsets used by original linux/kernel_role_observer.process_identity.
    leader,mark,tail=raw.rpartition(b') ');pid,opening,_comm=leader.partition(b' (');fields=tail.split()
    require(mark and opening and pid.isdigit() and len(fields)>=20
        and fields[1].isdigit() and fields[19].isdigit(),'ROOT_WORKER_ACTUAL_PROC_STAT_INCOMPLETE')
    return {'pid':_number(pid),'parent':_number(fields[1]),'start':_number(fields[19])}

def _status(raw):
    fields={}
    for line in raw.splitlines():
        name,sep,value=line.partition(b':')
        require(sep and name not in fields,'ROOT_WORKER_ACTUAL_PROC_STATUS_DUPLICATE')
        fields[name]=value.strip()
    require(all(name in fields for name in (b'Pid',b'PPid',b'Uid',b'Gid',b'NSpid')),
            'ROOT_WORKER_COMPLETE_PROC_CREDENTIALS_REQUIRED')
    uids=tuple(_number(word) for word in fields[b'Uid'].split())
    gids=tuple(_number(word) for word in fields[b'Gid'].split())
    require(len(uids)==4 and len(gids)==4,'ROOT_WORKER_COMPLETE_PROC_UID_GID_ROSTERS_REQUIRED')
    return fields,uids,gids

class RootProcessCapture:
    def __init__(self,host_proc,worker_pidfd,namespace,source_lease):
        self.host_proc,self.worker_pidfd,self.namespace=host_proc,worker_pidfd,namespace
        self.source=source_lease
        require(stat.S_ISDIR(os.fstat(host_proc).st_mode),'ROOT_WORKER_ACTUAL_HOST_PROC_DIRECTORY_REQUIRED')
    def capture(self,unit,invocation,source_id):
        from .protected_root_supervisor import OwnedRootSupervisor
        from .resource_child_schema import ProcessObservation
        self.source.check()
        from .root_worker_host_peer import host_fdinfo
        pid,fdinfo=host_fdinfo(self.host_proc,self.worker_pidfd)
        require(OwnedRootSupervisor.pidfd_state(self.worker_pidfd)==b'PIDFD_LIVE',
                'ROOT_WORKER_ACTUAL_HANDLER_NOT_LIVE')
        process=os.open(str(pid),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=self.host_proc)
        try:
            names=('status','stat','cgroup','maps','cmdline')
            before={name:_read_at(process,name) for name in names};parsed=_stat(before['stat'])
            fields,uids,gids=_status(before['status'])
            require(parsed['pid']==pid and _number(fields[b'Pid'])==pid
                and parsed['parent']==_number(fields[b'PPid']),
                'ROOT_WORKER_FULL_HOST_PID_PROC_CROSSWALK_CHANGED')
            parent_raw=_read_at(self.host_proc,str(parsed['parent'])+'/stat');parent=_stat(parent_raw)
            require(parent['pid']==parsed['parent'],'ROOT_WORKER_ACTUAL_PARENT_SOURCE_CHANGED')
            ns=os.open('ns/pid',os.O_RDONLY|os.O_CLOEXEC,dir_fd=process)
            try:
                ns_identity=identity(ns)
                require((os.fstat(ns).st_dev,os.fstat(ns).st_ino)==
                    (os.fstat(self.namespace).st_dev,os.fstat(self.namespace).st_ino),
                    'ROOT_WORKER_ACTUAL_HANDLER_NAMESPACE_CHANGED')
            finally:os.close(ns)
            image=os.readlink('exe',dir_fd=process)
            image_bytes=self.source.file(image,('INTERPRETER','EXECUTABLE'))
            for line in before['maps'].splitlines():
                pieces=line.split(None,5)
                if len(pieces)==6 and pieces[5].startswith(b'/'):
                    self.source.file(os.fsdecode(pieces[5]),('INTERPRETER','EXECUTABLE','EXTENSION','DATA'))
            after={name:_read_at(process,name) for name in names}
            parent_after=_read_at(self.host_proc,str(parsed['parent'])+'/stat')
            after_stat=_stat(after['stat']);after_fields,after_uids,after_gids=_status(after['status'])
            # Keep every before/after byte. CPU counters/context switches are
            # observed data, not process identity. Stable actual PID/start/PPID,
            # credential rosters, namespace, cgroup, execution and source must
            # stay identical across this factual observation interval.
            require(after_stat==parsed and _stat(parent_after)==parent
                and tuple(after_fields[name] for name in (b'Pid',b'PPid',b'NSpid'))==
                    tuple(fields[name] for name in (b'Pid',b'PPid',b'NSpid'))
                and after_uids==uids and after_gids==gids
                and all(after[name]==before[name] for name in ('cgroup','maps','cmdline'))
                and OwnedRootSupervisor.pidfd_state(self.worker_pidfd)==b'PIDFD_LIVE',
                    'ROOT_WORKER_CURRENT_PROC_IDENTITY_OR_EXECUTION_CHANGED')
            cg=before['cgroup'];require(cg.startswith(b'0::/') and cg.endswith(b'\n')
                and len(cg.splitlines())==1,'ROOT_WORKER_ACTUAL_UNIFIED_CGROUP_REQUIRED')
            # FD positions/numbers are raw provenance, not namespace identity.
            from .protected_resource_runtime import canonical,identity_record
            namespace=canonical(identity_record(os.fstat(self.namespace)))
            result=ProcessObservation(raw_status=before['status'],raw_stat=before['stat'],raw_cgroup=cg,
                raw_maps=before['maps'],raw_cmdline=before['cmdline'],raw_pidfd_info=fdinfo,namespace=namespace,
                cgroup=cg.removeprefix(b'0::').removesuffix(b'\n'),actual_unit=unit,invocation=invocation,
                source_lease=source_id,pidfd_wait=b'PIDFD_LIVE',host_pid=pid,start_tick=parsed['start'],
                parent_pid=parsed['parent'],parent_start_tick=parent['start'],real_uid=uids[0],effective_uid=uids[1],
                saved_uid=uids[2],real_gid=gids[0],effective_gid=gids[1],saved_gid=gids[2])
            return result,{'raw':before,'after':after,'parent_stat':parent_raw,'parent_after':parent_after,'source':self.source.check(),
                'host_proc_identity':identity(self.host_proc),'worker_pidfd_identity':identity(self.worker_pidfd),
                'namespace_identity':ns_identity,'image':image,'image_bytes':image_bytes}
        finally:os.close(process)
