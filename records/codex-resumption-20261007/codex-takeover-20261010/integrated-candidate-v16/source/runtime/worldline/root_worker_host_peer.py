"""Kernel-backed host namespace peer/process projection from retained proc FD.

SO_PEERPIDFD is observed from the selected installed Linux header, not a guessed
PID, DTO or parent verdict. Runtime support is required and may refuse. A mount
of proc belonging to the host namespace renders pidfd fdinfo in that namespace;
the worker's replacement /proc must not relabel the original process identity.
All raw credentials/fdinfo/header/OFD observations remain retained. This factual
producer still needs complete native/source/custody/body correspondence proof.
"""
import os,socket,struct
from .protected_startup import require,digest
from .root_worker_credentials import _number
from .root_worker_custody import identity
HEADER_PATH='/usr/include/asm-generic/socket.h'
HEADER_SHA='e833d32d3d8d03732021da6968665431d693ab4effdd4d39965ff05115a4ed21'
# Installed source observation, retained separately with exact bytes/mode.
SO_PEERPIDFD=77

def host_fdinfo(host_proc,descriptor):
    # `self` resolves within this retained procfs mount, rather than the newly
    # mounted worker /proc. Both PID and complete raw bytes are retained.
    fd=os.open('self/fdinfo/'+str(descriptor),os.O_RDONLY|os.O_CLOEXEC,dir_fd=host_proc)
    try:
        with os.fdopen(os.dup(fd),'rb') as stream:raw=stream.read()
    finally:os.close(fd)
    matches=[line.removeprefix(b'Pid:\t') for line in raw.splitlines() if line.startswith(b'Pid:\t')]
    require(len(matches)==1,'ROOT_HOST_ACTUAL_PIDFD_PID_UNAVAILABLE')
    return _number(matches[0]),raw

def host_peer(host_proc,channel,source):
    from .protected_root_supervisor import OwnedRootSupervisor
    observed=source.file(HEADER_PATH,('DATA',))
    require(digest(observed)==HEADER_SHA,'ROOT_HOST_SELECTED_PEERPIDFD_HEADER_CHANGED')
    original=channel.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('@iII'))
    _relative,uid,gid=struct.unpack('@iII',original)
    descriptor=None
    try:
        returned=channel.getsockopt(socket.SOL_SOCKET,SO_PEERPIDFD,struct.calcsize('@i'))
        require(len(returned)==struct.calcsize('@i'),'ROOT_HOST_PEERPIDFD_RECORD_INCOMPLETE')
        descriptor=struct.unpack('@i',returned)[0]
        require(descriptor>=0,'ROOT_HOST_KERNEL_PEERPIDFD_UNAVAILABLE')
        os.set_inheritable(descriptor,False)
        require(OwnedRootSupervisor.pidfd_state(descriptor)==b'PIDFD_LIVE',
                'ROOT_HOST_GENUINE_CURRENT_PEER_NOT_LIVE')
        pid,raw=host_fdinfo(host_proc,descriptor)
        require(pid>0,'ROOT_HOST_KERNEL_PEER_HOST_PID_ABSENT')
        canonical=struct.pack('@iII',pid,uid,gid)
        return canonical,{'relative_kernel_credentials':original,'host_credentials':canonical,
            'host_pidfd_info':raw,'peer_pidfd':identity(descriptor),
            'host_proc':identity(host_proc),'selected_header':observed}
    except OSError as error:
        raise RuntimeError('ROOT_HOST_GENUINE_PEERPIDFD_KERNEL_CAPTURE_UNAVAILABLE') from error
    finally:
        if descriptor is not None:os.close(descriptor)
