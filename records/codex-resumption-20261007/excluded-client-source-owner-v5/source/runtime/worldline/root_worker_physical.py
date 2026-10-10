"""Fresh root-helper/namespace observations from actual held kernel descriptors.

A prior manager/result/packet is history. Current show/proc/nsfs/pidfd/cgroup and
owned channel captures are read again; full raw data accompanies every native
fact. Helper executable and privileged handler executable remain distinct.
"""
import hashlib,os,socket,stat,struct,subprocess
from pathlib import Path
from .protected_startup import require,private_bytes,digest
from .root_worker_credentials import _number
from .root_worker_custody import identity

def manager(owner,unit):
    path=owner.plan['native_components']['systemctl'];owner.source_lease.file(path,('EXECUTABLE',))
    names=('Id','MainPID','InvocationID','ControlGroup','Delegate','ActiveState','SubState','Result','ExecMainCode','ExecMainStatus')
    reply=subprocess.run([path,'--system','show',unit.decode('ascii'),'--no-pager',
        *(('--property='+name) for name in names)],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,check=False,env={'PATH':'/usr/bin:/bin','LANG':'C'})
    require(reply.returncode==0,'ROOT_PHYSICAL_ACTUAL_MANAGER_UNAVAILABLE')
    words={}
    for line in reply.stdout.splitlines():
        name,separator,value=line.partition(b'=')
        require(separator and name.decode('ascii') in names and name not in words,
                'ROOT_PHYSICAL_FULL_MANAGER_ROSTER_INVALID')
        words[name]=value
    require(set(words)=={name.encode('ascii') for name in names} and words[b'Id']==unit,
            'ROOT_PHYSICAL_SELECTED_MANAGER_UNIT_CHANGED')
    return words,{'argv':reply.args,'stdout':reply.stdout,'stderr':reply.stderr,'returncode':reply.returncode}

def _observe_host(owner,row,dispatch,held,rights,host_proc,*,closed=None,outer=None):
    from .protected_root_supervisor import OwnedRootSupervisor
    from .protected_resource_runtime import canonical,identity_record,kernel_bytes
    owner.source_lease.check()
    channel=socket.socket(fileno=os.dup(rights['supervisor_channel']))
    try:
        require(channel.family==socket.AF_UNIX and channel.getsockopt(socket.SOL_SOCKET,socket.SO_TYPE)==socket.SOCK_SEQPACKET,
                'ROOT_PHYSICAL_REAL_SUPERVISOR_CHANNEL_REQUIRED')
        relative_peer=channel.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('@iII'))
        from .root_worker_host_peer import host_peer
        if OwnedRootSupervisor.pidfd_state(rights['helper_pidfd'])==b'PIDFD_LIVE':
            peer,peer_source=host_peer(host_proc,channel,owner.source_lease)
        else:
            # The actual outside collector reads its original cached host peer
            # after terminal. A PID-zero relative view cannot invent a host
            # peer or terminal receipt; all owned waits remain independently
            # required and that unsupported view refuses this projection.
            peer=relative_peer;peer_source={'actual_cached_credentials':relative_peer}
    finally:channel.close()
    require(peer==held['peer'],'ROOT_PHYSICAL_ORIGINAL_HELPER_PEER_CHANGED')
    properties,raw_manager=manager(owner,row.planned_unit)
    cg=held['properties'][b'ControlGroup'];invocation=held['properties'][b'InvocationID']
    require(properties[b'ControlGroup']==cg and properties[b'InvocationID']==invocation,
            'ROOT_PHYSICAL_ORIGINAL_CGROUP_OR_INVOCATION_CHANGED')
    namespace=canonical(identity_record(os.fstat(rights['worker_namespace'])))
    require((os.fstat(rights['worker_namespace']).st_dev,os.fstat(rights['worker_namespace']).st_ino)==
        (held['namespace_identity']['device'],held['namespace_identity']['inode']),
            'ROOT_PHYSICAL_HELD_NAMESPACE_CHANGED')
    namespace_wait=OwnedRootSupervisor.pidfd_state(rights['namespace_pidfd'])
    helper_wait=OwnedRootSupervisor.pidfd_state(rights['helper_pidfd'])
    path=Path('/sys/fs/cgroup')/os.fsdecode(cg).lstrip('/')
    require(cg.startswith(b'/') and not any(item in ('.','..') for item in Path(os.fsdecode(cg)).parts),
            'ROOT_PHYSICAL_CGROUP_PATH_CHANGED')
    info=path.lstat();events=kernel_bytes(path/'cgroup.events');kind=kernel_bytes(path/'cgroup.type')
    require(stat.S_ISDIR(info.st_mode) and not path.is_symlink(),'ROOT_PHYSICAL_ACTUAL_CGROUP_DIRECTORY_REQUIRED')
    source={'path':str(path),'identity':identity_record(info),'events':events,'type':kind}
    helper_source=None
    if helper_wait==b'PIDFD_LIVE':
        from .root_worker_host_peer import host_fdinfo
        helper,_fdinfo=host_fdinfo(host_proc,rights['helper_pidfd'])
        require(helper==held['helper_pid'] and _number(properties[b'MainPID'])==helper,
                'ROOT_PHYSICAL_LIVE_MANAGER_HELPER_CHANGED')
        from .root_worker_process_capture import _read_at
        root=os.open(str(helper),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=host_proc)
        try:
            image=Path(os.readlink('exe',dir_fd=root))
            require(str(image)==owner.plan['helper'] and private_bytes(image)==owner.source_lease.file(str(image),('EXECUTABLE',)),
                    'ROOT_PHYSICAL_CURRENT_HELPER_IMAGE_CHANGED')
            helper_source={name:_read_at(root,name) for name in ('status','stat','cgroup','maps','cmdline')}
        finally:os.close(root)
        require(helper_source['cgroup']==b'0::'+cg+b'\n' and helper_source['cmdline']==
            b'\0'.join(os.fsencode(word) for word in dispatch['helper_arguments'])+b'\0',
                'ROOT_PHYSICAL_CURRENT_HELPER_COMMAND_OR_MEMBERSHIP_CHANGED')
        for line in helper_source['maps'].splitlines():
            parts=line.split(None,5)
            if len(parts)==6 and parts[5].startswith(b'/'):
                owner.source_lease.file(os.fsdecode(parts[5]),('EXECUTABLE','EXTENSION'))
    else:require(properties[b'MainPID']==b'0','ROOT_PHYSICAL_TERMINAL_MANAGER_HELPER_CHANGED')
    # Complete retained dispatch is transport provenance, never authorization.
    dispatch_id=hashlib.sha256(canonical(dispatch['resource_dispatch'])).digest()
    image_id=bytes.fromhex(digest(owner.source_lease.file(owner.plan['helper'],('EXECUTABLE',))))
    challenge=bytes.fromhex(dispatch['ticket'])
    facts={'dispatch':dispatch_id,'actual_unit':properties[b'Id'],'cgroup':cg,'invocation':invocation,
        'namespace':namespace,'held_namespace':namespace,'peer':peer,'held_peer':held['peer'],
        'helper_image':image_id,'expected_helper_image':image_id,'challenge':challenge,'held_challenge':challenge,
        'protocol':b'CLOSED_ECHILD' if closed is not None and outer is not None else b'HELD',
        'closed_event':None if closed is None or outer is None else bytes.fromhex(outer['event_id']),
        'namespace_wait':namespace_wait,'helper_wait':helper_wait,'cgroup_events':events,'cgroup_type':kind,
        'manager_delegate':properties[b'Delegate'],'cgroup_owner':info.st_uid,
        'cgroup_group_write':info.st_mode&stat.S_IWGRP,'cgroup_other_write':info.st_mode&stat.S_IWOTH,
        'phase':'NAMESPACE_CLOSED' if closed is not None and outer is not None else 'NAMESPACE_HELD'}
    return {'native_fields':facts,'raw':{'held':held,'dispatch':dispatch,'manager':raw_manager,
        'helper_proc':helper_source,'peer_source':peer_source,'relative_peer':relative_peer,'host_proc':identity(host_proc),'cgroup':source,'namespace_wait':namespace_wait,'helper_wait':helper_wait,
        'closed':closed,'outer':outer,'rights':{name:identity(fd) for name,fd in rights.items()},
        'current_source':owner.source_lease.check()}}


def observe(owner,row,dispatch,held,rights,*,closed=None,outer=None):
    # Actual transferred host proc is mandatory inside the worker namespace.
    # The original front owns its host proc directly; neither source accepts a
    # caller-selected fake directory or substitutes its current /proc for the
    # sealed received host-proc role.
    from .protected_root_worker import RootWorkerFront,RootWorkerProcess,RootWorkerIntake
    require(type(owner) in (RootWorkerFront,RootWorkerProcess,RootWorkerIntake),
            'ROOT_PHYSICAL_EXACT_CURRENT_SOURCE_OWNER_REQUIRED')
    if type(owner) is RootWorkerFront:
        host=os.open('/proc',os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
        try:return _observe_host(owner,row,dispatch,held,rights,host,closed=closed,outer=outer)
        finally:os.close(host)
    require(owner.custody.origins.get('host_proc') is not None,
            'ROOT_PHYSICAL_GENUINE_TRANSFERRED_HOST_PROC_REQUIRED')
    return _observe_host(owner,row,dispatch,held,rights,owner.custody.origins['host_proc'],closed=closed,outer=outer)
