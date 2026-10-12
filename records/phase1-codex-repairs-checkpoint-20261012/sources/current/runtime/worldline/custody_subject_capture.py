"""Actual Linux subject transcripts; native custody owns every lifecycle decision.

No receipt is produced before its operation. Errors retain their raw errno;
None operands mean genuinely unavailable kernel objects, never omitted fields.
"""
from __future__ import annotations
import array,ctypes,errno,fcntl,hashlib,os,platform,socket,stat
from pathlib import Path
from .client_peer import UCRED
from .protected_startup import require

_LIBC=ctypes.CDLL(None,use_errno=True)
_LIBC.getsockopt.argtypes=(ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint))
_LIBC.getsockopt.restype=ctypes.c_int
_LIBC.getpeername.argtypes=(ctypes.c_int,ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint))
_LIBC.getpeername.restype=ctypes.c_int
_LIBC.close.argtypes=(ctypes.c_int,)
_LIBC.close.restype=ctypes.c_int
_LIBC.flock.argtypes=(ctypes.c_int,ctypes.c_int)
_LIBC.flock.restype=ctypes.c_int
_LIBC.syscall.restype=ctypes.c_long

def fd_identity(fd):
    value=os.fstat(fd)
    return {'device':value.st_dev,'inode':value.st_ino,'mode':value.st_mode,
        'uid':value.st_uid,'gid':value.st_gid,'size':value.st_size,
        'fdinfo':Path('/proc/self/fdinfo/'+str(fd)).read_bytes()}

def actor_identity(channel=None):
    pid=os.getpid();raw=Path('/proc/self/stat').read_bytes()
    tail=raw[raw.rfind(b')')+2:].split()
    namespaces={}
    for entry in sorted(Path('/proc/self/ns').iterdir()):
        observed=entry.stat()
        namespaces[entry.name]={'link':os.readlink(entry),
            'identity':{'device':observed.st_dev,'inode':observed.st_ino,'mode':observed.st_mode}}
    return {'boot':Path('/proc/sys/kernel/random/boot_id').read_bytes(),
        'pid':pid,'start_tick':int(tail[19]),'stat':raw,
        'credentials':UCRED.pack(pid,os.getuid(),os.getgid()),
        'channel':None if channel is None else fd_identity(channel.fileno()),
        'status':Path('/proc/self/status').read_bytes(),
        'uid_map':Path('/proc/self/uid_map').read_bytes(),
        'gid_map':Path('/proc/self/gid_map').read_bytes(),'namespaces':namespaces}

def syscall(owner,call,args,fn):
    source=owner.source_lease.check()
    receipt={'call':call,'args':args,'source':source}
    try:value=fn()
    except OSError as error:
        receipt.update(result=-1,errno=error.errno,message=str(error));return None,receipt
    # This records the actual Python API return as well as its kernel-success
    # convention; it never converts a failed operation into a successful call.
    result=value if type(value) is int else 0
    receipt.update(result=result,errno=0,api_result=value)
    return value,receipt

def _getopt(fd,option,length,source):
    buffer=ctypes.create_string_buffer(length);actual=ctypes.c_uint(length)
    ctypes.set_errno(0)
    result=_LIBC.getsockopt(fd,socket.SOL_SOCKET,option,buffer,ctypes.byref(actual))
    return {'call':'getsockopt','fd':fd,'level':socket.SOL_SOCKET,'option':option,
        'requested':length,'length':actual.value,'result':result,
        'errno':ctypes.get_errno() if result<0 else 0,
        'raw':bytes(buffer.raw[:actual.value]),'source':source}

def socket_capture(fd,source):
    identity=fd_identity(fd)
    buffer=ctypes.create_string_buffer(128);extent=ctypes.c_uint(len(buffer))
    ctypes.set_errno(0);result=_LIBC.getpeername(fd,buffer,ctypes.byref(extent))
    peer_errno=ctypes.get_errno() if result<0 else 0
    return {'fd':fd,'source':source,
        'fstat':{'call':'fstat','args':{'fd':fd},'fd':fd,'result':0,'errno':0,
            'identity':identity,'source':source},
        'peercred':_getopt(fd,socket.SO_PEERCRED,UCRED.size,source),
        'domain':_getopt(fd,socket.SO_DOMAIN,4,source),
        'type':_getopt(fd,socket.SO_TYPE,4,source),
        'peername':{'call':'getpeername','fd':fd,'result':result,
            'errno':peer_errno,
            'raw':bytes(buffer.raw[:extent.value]),'source':source}}

def socket_document(capture):
    pid,uid,gid=UCRED.unpack(capture['peercred']['raw']);identity=capture['fstat']['identity']
    return {'peer':{'source':'linux.SO_PEERCRED','rawUcred':capture['peercred']['raw'].hex(),
        'pid':pid,'uid':uid,'gid':gid,'socketIdentity':{name:identity[name]
            for name in ('device','inode','mode')}}}

def kcmp(front_pid,worker_pid,front_fd,worker_fd,source):
    numbers={'aarch64':272,'x86_64':312}
    machine=platform.machine();require(machine in numbers,'CUSTODY_KCMP_SYSCALL_ARCH_UNAVAILABLE')
    ctypes.set_errno(0)
    result=_LIBC.syscall(ctypes.c_long(numbers[machine]),ctypes.c_int(front_pid),
        ctypes.c_int(worker_pid),ctypes.c_int(0),ctypes.c_ulong(front_fd),ctypes.c_ulong(worker_fd))
    return {'call':'kcmp','args':{'pid1':front_pid,'pid2':worker_pid,'type':0,
        'idx1':front_fd,'idx2':worker_fd},'result':result,
        'errno':ctypes.get_errno() if result<0 else 0,'source':source}

def close_descriptor(fd,source):
    ctypes.set_errno(0);result=_LIBC.close(fd)
    receipt={'call':'close','fd':fd,'args':{'fd':fd},'result':result,
        'errno':ctypes.get_errno() if result<0 else 0,'source':source}
    try:identity=fd_identity(fd)
    except OSError as error:
        readback={'call':'fstat','fd':fd,'result':-1,'errno':error.errno,'source':source}
    else:readback={'call':'fstat','fd':fd,'result':0,'errno':0,'identity':identity,'source':source}
    receipt['readback']=readback
    return receipt

def original_roles(descriptors,source,front_actor,worker_pidfd,lock_paths):
    """Enumerate every actual supplied role, without a fixed role/count ceiling."""
    require(len(set(descriptors.values()))==len(descriptors),'CUSTODY_DESCRIPTOR_ROLE_FD_ALIAS')
    result=[]
    for role,fd in descriptors.items():
        identity=fd_identity(fd)
        captured=socket_capture(fd,source) if stat.S_ISSOCK(identity['mode']) else None
        result.append({'role':role,'fd':fd,'identity':identity,'front_actor':front_actor,
            'worker_pidfd':worker_pidfd,'lock_path':lock_paths.get(role),
            'socket_document':None if captured is None else {
                'schema':'worldline.custody-role-socket-v1','socket':captured}})
    return result

def role_roster(original,descriptors,source,worker_pid=None):
    require(set(descriptors)=={row['role'] for row in original},'CUSTODY_COMPLETE_ROLE_SET_CHANGED')
    result=[]
    for row in original:
        fd=descriptors[row['role']];current=fd_identity(fd)
        received=worker_pid is not None
        lock=None
        if received and row['lock_path'] is not None:
            ctypes.set_errno(0);value=_LIBC.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            lock={'call':'flock','args':{'fd':fd,'operation':fcntl.LOCK_EX|fcntl.LOCK_NB},
                'result':value,'errno':ctypes.get_errno() if value<0 else 0,'source':source}
        result.append({'role':row['role'],'origin':row['identity'],'current':current,
            'front_fd':row['fd'],'worker_fd':fd if received else None,
            'front_actor':row['front_actor'],'worker_pidfd':row['worker_pidfd'],
            'lock_path':row['lock_path'],'flock':lock,
            'kcmp':None if not received else kcmp(row['front_actor']['pid'],worker_pid,row['fd'],fd,source),
            'fstat':{'call':'fstat','args':{'fd':fd},'fd':fd,'result':0,'errno':0,
                'identity':current,'source':source},
            'socket':socket_capture(fd,source) if stat.S_ISSOCK(current['mode']) else None})
    return result

def stream_send(channel,raw,descriptors,source):
    rights=array.array('i',descriptors);credentials=UCRED.pack(os.getpid(),os.getuid(),os.getgid())
    parts=[];position=0
    receipt={'fd':channel.fileno(),'frame':raw,'rights':rights.tobytes(),'flags':socket.MSG_NOSIGNAL,
        'source':source,'parts':parts,'sender':credentials,'result':0,'errno':0}
    while position<len(raw):
        try:
            sent=(channel.sendmsg([raw[position:]],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,rights),
                (socket.SOL_SOCKET,socket.SCM_CREDENTIALS,credentials)],socket.MSG_NOSIGNAL)
                if position==0 else channel.send(raw[position:],socket.MSG_NOSIGNAL))
        except OSError as error:
            receipt.update(result=-1,errno=error.errno);error.custody_receipt=receipt;raise
        part={'fd':channel.fileno(),'raw':raw[position:position+sent],'result':sent,'errno':0,'source':source}
        parts.append(part);require(sent>0,'CUSTODY_STREAM_SEND_UNKNOWN');position+=sent
    receipt['result']=position
    return receipt

def stream_receive(channel,length,source):
    """Receive a bounded stream frame and ALL descriptor/control receipts."""
    parts=[];controls=[];descriptors=[];credentials=[];raw=bytearray();flags=0
    try:
        first,ancillary,returned,_=channel.recvmsg(min(length,65536),
            socket.CMSG_SPACE(253*array.array('i').itemsize)+socket.CMSG_SPACE(UCRED.size),
            socket.MSG_CMSG_CLOEXEC)
        controls.extend((level,kind,bytes(value)) for level,kind,value in ancillary);flags|=returned
        for level,kind,value in ancillary:
            if (level,kind)==(socket.SOL_SOCKET,socket.SCM_RIGHTS):
                rights=array.array('i');whole=len(value)-len(value)%rights.itemsize
                rights.frombytes(value[:whole]);descriptors.extend(rights)
                require(whole==len(value),'CUSTODY_RIGHTS_PARTIAL_INTEGER')
            elif (level,kind)==(socket.SOL_SOCKET,socket.SCM_CREDENTIALS):credentials.append(bytes(value))
            else:require(False,'CUSTODY_UNKNOWN_ANCILLARY')
        raw.extend(first);parts.append({'fd':channel.fileno(),'raw':first,'result':len(first),'errno':0,'source':source})
        require(first and not flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC),'CUSTODY_STREAM_RECEIVE_UNKNOWN')
        while len(raw)<length:
            piece=channel.recv(min(65536,length-len(raw)))
            parts.append({'fd':channel.fileno(),'raw':piece,'result':len(piece),'errno':0,'source':source})
            require(piece,'CUSTODY_STREAM_EOF_AMBIGUOUS');raw.extend(piece)
        require(len(credentials)==1 and len(credentials[0])==UCRED.size,'CUSTODY_SENDER_RAW12_REQUIRED')
        receipt={'fd':channel.fileno(),'frame':bytes(raw),'rights':array.array('i',descriptors).tobytes(),
            'flags':flags,'input_flags':socket.MSG_CMSG_CLOEXEC,'source':source,'parts':parts,
            'result':len(raw),'errno':0,'controls':controls}
        return bytes(raw),descriptors,credentials[0],receipt
    except BaseException:
        for fd in descriptors:os.close(fd)
        raise

def socket_cookie(fd,source):
    receipt=_getopt(fd,getattr(socket,'SO_COOKIE',57),8,source)
    return (receipt['raw'] if receipt['result']==0 else None),receipt
